"""Anthropic API integration for recipe generation"""

from anthropic import Anthropic
from typing import List, Dict, Optional
import json
import re
from .config import (
    ANTHROPIC_API_KEY,
    MODEL_NAME,
    PREFERENCES_FILE,
    USER_DATA_DIR,
    USER_PREFERENCES_FILE,
)


def load_allergies() -> list:
    """Load allergy list from user config. Returns empty list if none."""
    config_file = USER_DATA_DIR / "config.json"
    if not config_file.exists():
        return []
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("allergies", {}).get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


class RecipeGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.preferences = self._load_preferences()
        self.allergies = load_allergies()

    def _load_preferences(self) -> str:
        """Load preferences.md, checking user dir first, then project root."""
        # User-generated preferences (from onboarding)
        if USER_PREFERENCES_FILE.exists():
            with open(USER_PREFERENCES_FILE, "r", encoding="utf-8") as f:
                return f.read()

        # Fall back to project preferences.md (backward compat for existing users)
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                "preferences.md not found. Run onboarding or create one in the project root."
            )

    def generate_recipes(
        self,
        ingredients: List[str],
        recent_cuisines: List[str] = None,
        constraints: str = None
    ) -> Dict:
        """
        Generate recipe options based on ingredients and preferences

        Args:
            ingredients: List of available ingredients
            recent_cuisines: Cuisines cooked recently (to avoid repetition)
            constraints: Additional constraints (time, equipment, etc.)

        Returns:
            Dict with 'recipes' (list of 3 options) and 'recommendation'
        """

        prompt = self._build_prompt(ingredients, recent_cuisines, constraints)

        message = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return self._parse_response(message.content[0].text)

    def _build_prompt(
        self,
        ingredients: List[str],
        recent_cuisines: Optional[List[str]],
        constraints: Optional[str]
    ) -> str:
        """Build the prompt for recipe generation"""

        # Normalize and dedupe recent cuisines
        avoided_cuisines = list(set(recent_cuisines)) if recent_cuisines else []

        prompt = f"""You are a personal chef assistant for Matt and Jennifer Pressberg. Generate exactly 3 dinner recipe options based on the available ingredients and their detailed preferences below.

"""

        # Allergy section goes first — highest priority
        if self.allergies:
            allergy_lines = "\n".join(f"- {item}" for item in self.allergies)
            prompt += f"""## CRITICAL SAFETY - ALLERGIES
The user has confirmed allergies. NEVER suggest recipes containing:
{allergy_lines}

This is a safety requirement, not a preference. Do not include these ingredients under any circumstances.

"""

        prompt += f"""## AVAILABLE INGREDIENTS
{', '.join(ingredients)}

Note: Interpret ingredient inputs generously (e.g., "turkey" means ground turkey is acceptable, "greens" could mean spinach/kale/chard). The pantry staples listed in preferences are ALWAYS available—do not ask for them.

## USER PREFERENCES
{self.preferences}

"""

        if avoided_cuisines:
            prompt += f"""## CUISINE RESTRICTIONS
Do NOT suggest recipes from these cuisines (recently cooked): {', '.join(avoided_cuisines)}
Choose from other cuisines in their preference list instead.

"""

        if constraints:
            prompt += f"""## ADDITIONAL CONSTRAINTS
{constraints}

"""

        prompt += """## SPECIAL INSTRUCTIONS

### For Fish and Shrimp Recipes
Include specific technique guidance to prevent overcooking:
- Target internal temperatures or visual doneness indicators
- Timing guidance (e.g., "3-4 minutes per side for 1-inch thick salmon")
- Carryover cooking warnings where relevant
- Equipment-specific tips (e.g., cast iron vs. non-stick behavior)

### For All Recipes
- Mark pantry staples with an asterisk (*) in the ingredients list
- Prioritize bold, flavorful preparations over bland/simple ones
- Match equipment suggestions to what they own (see preferences)
- Default to 2 servings; note if a recipe scales poorly

## OUTPUT FORMAT

Respond with ONLY valid JSON. No markdown code blocks, no commentary, no explanation outside the JSON structure.

{
  "recipes": [
    {
      "name": "Recipe Name",
      "cuisine": "Cuisine Type",
      "description": "One-sentence description emphasizing what makes this appealing",
      "ingredients": [
        "1 lb ground turkey",
        "4 cloves garlic, minced*",
        "2 tbsp soy sauce*"
      ],
      "instructions": [
        "Step 1 with specific detail",
        "Step 2 with timing and visual cues"
      ],
      "equipment": ["Instant Pot"],
      "active_time_minutes": 30,
      "total_time_minutes": 45,
      "difficulty": "Easy|Medium|Hard",
      "technique_notes": "Key tips for success, especially for proteins",
      "why_this_works": "Brief note on why this matches their preferences"
    }
  ],
  "recommendation": {
    "recipe_index": 0,
    "reasoning": "One sentence on why this is the best choice given ingredients and recent meals"
  }
}
"""

        return prompt

    def _parse_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response with robust extraction"""

        # First, try direct parsing (ideal case)
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        code_block_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, response_text)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Try to find JSON object by matching braces
        try:
            start = response_text.index('{')
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(response_text[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = response_text[start:i+1]
                        return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            pass

        # If all else fails, raise without leaking API response content
        raise ValueError(
            "Could not parse recipe data from the API response. "
            "Try running again."
        )

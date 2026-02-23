"""
Onboarding flow for new users.
Collects name, API key, and allergies, then runs preference interview.
"""

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .config import MODEL_NAME, USER_DATA_DIR

console = Console()

CONFIG_FILE = USER_DATA_DIR / "config.json"
ENV_FILE = USER_DATA_DIR / ".env"


def is_onboarding_complete() -> bool:
    """Check if onboarding has been completed."""
    try:
        config = load_user_config()
        return config.get("onboarding_complete", False)
    except (json.JSONDecodeError, OSError):
        return False


def load_user_config() -> dict:
    """Load and return config.json contents."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_config(config: dict):
    """Save config dict to config.json."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def collect_name() -> str:
    """Prompt user for their name."""
    console.print(
        Panel.fit(
            "[bold cyan]Welcome to Pressberg Kitchen![/bold cyan]\n"
            "[dim]Let's get you set up.[/dim]",
            border_style="cyan",
        )
    )
    name = Prompt.ask("\n[yellow]What's your name?[/yellow]")
    return name.strip()


def collect_api_key() -> str:
    """Prompt for Anthropic API key, validate it, and save to .env."""
    console.print(
        "\n[yellow]This app uses Claude to generate recipes.[/yellow]\n"
        "You'll need an Anthropic API key.\n"
        "If you don't have one, sign up at: [bold cyan]https://console.anthropic.com[/bold cyan]\n"
        "Then go to Settings > API Keys and create one."
    )

    while True:
        key = Prompt.ask("\n[yellow]Paste your API key[/yellow]").strip()

        if not key:
            console.print("[red]No key entered. Try again.[/red]")
            continue

        if not key.startswith("sk-ant-"):
            console.print("[red]That doesn't look like a valid Anthropic API key (should start with sk-ant-).[/red]")
            continue

        # Validate by making a minimal API call
        console.print("[dim]Validating key...[/dim]")
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=key)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            console.print("[green]Key is valid.[/green]")
        except Exception:
            console.print("[red]That key didn't work. Check it and try again.[/red]")
            continue

        # Save to ~/.dinner-assistant/.env
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"ANTHROPIC_API_KEY={key}\n")

        return key


COMMON_ALLERGIES = [
    ("Tree nuts", "almonds, walnuts, pecans, etc."),
    ("Peanuts", ""),
    ("Shellfish", "shrimp, crab, lobster"),
    ("Fish", ""),
    ("Dairy/Lactose", ""),
    ("Eggs", ""),
    ("Gluten/Wheat", ""),
    ("Soy", ""),
]


def collect_allergies() -> dict:
    """Prompt user for food allergies. Returns dict with allergy info."""
    console.print(
        "\n[yellow]Before we get to the fun stuff, let's talk safety.[/yellow]\n"
        "Do you have any food allergies or ingredients you must [bold red]NEVER[/bold red] eat?"
    )

    # Show numbered options
    console.print()
    for i, (name, examples) in enumerate(COMMON_ALLERGIES, 1):
        label = f"  {i}. {name}"
        if examples:
            label += f" [dim]({examples})[/dim]"
        console.print(label)
    console.print(f"  {len(COMMON_ALLERGIES) + 1}. [dim]None of these[/dim]")

    # Multi-select
    console.print(
        "\n[dim]Enter numbers separated by commas (e.g. 1,3), "
        f"or {len(COMMON_ALLERGIES) + 1} for none.[/dim]"
    )
    selection = Prompt.ask("[yellow]Your selections[/yellow]")

    items = []
    none_option = str(len(COMMON_ALLERGIES) + 1)

    for num in selection.split(","):
        num = num.strip()
        if num == none_option:
            items = []
            break
        try:
            idx = int(num) - 1
            if 0 <= idx < len(COMMON_ALLERGIES):
                items.append(COMMON_ALLERGIES[idx][0].lower())
        except ValueError:
            continue

    # Free text for additional allergies
    console.print()
    extra = Prompt.ask(
        "[yellow]Any other allergies or ingredients to always avoid?[/yellow]",
        default="",
    ).strip()

    if extra:
        for item in extra.split(","):
            item = item.strip().lower()
            if item and item not in items:
                items.append(item)

    return {"items": items}


def confirm_allergies(allergies: list) -> bool:
    """Show allergy list and get confirmation. Returns True if confirmed."""
    if not allergies:
        return True

    console.print("\n[bold yellow]I'll NEVER suggest recipes containing:[/bold yellow]")
    for item in allergies:
        console.print(f"  [red]- {item}[/red]")

    return Confirm.ask("\n[yellow]Is this correct?[/yellow]", default=True)


INTERVIEW_SYSTEM_PROMPT = """\
You are a friendly culinary assistant helping a new user set up their recipe preferences. \
Your job is to learn about their cooking style through a natural conversation.

Ask ONE question at a time. Be warm and conversational, not robotic.
If an answer is vague, ask a brief follow-up to clarify.

Topics to cover (in roughly this order):
1. Cuisine preferences — what do they love? what do they never want?
2. Spice tolerance — from mild to very hot
3. Protein preferences — vegetarian? seafood? red meat frequency?
4. Cooking skill level — beginner/intermediate/advanced
5. Weeknight time constraints — how long can they spend cooking?
6. Weekend cooking — more elaborate meals?
7. Kitchen equipment — what do they have? (Instant Pot, air fryer, grill, wok, cast iron, etc.)
8. Household size — how many people typically eating?
9. Dietary goals — low-carb, heart-healthy, no restrictions?

After covering all topics, say "INTERVIEW_COMPLETE" on its own line, then provide a JSON summary \
of what you learned in this exact format:

```json
{
  "cuisines_loved": ["Italian", "Mexican"],
  "cuisines_avoided": ["British"],
  "spice_level": "medium-high",
  "proteins": {"loves": ["chicken", "fish"], "avoids": ["lamb"], "vegetarian": false},
  "skill_level": "intermediate",
  "weeknight_time": "30-45 minutes",
  "weekend_time": "up to 90 minutes",
  "equipment": ["Instant Pot", "cast iron", "air fryer"],
  "household_size": 2,
  "dietary_goals": ["none"]
}
```

Keep the whole interview to 8-12 exchanges. Be efficient but friendly.
"""

MAX_INTERVIEW_TURNS = 12


def _extract_interview_json(text: str) -> dict:
    """Extract the JSON summary from the interview completion message."""
    # Try code block first
    match = re.search(r"```json?\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try raw JSON after INTERVIEW_COMPLETE
    after = text.split("INTERVIEW_COMPLETE", 1)[-1]
    try:
        start = after.index("{")
        depth = 0
        for i, char in enumerate(after[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(after[start : i + 1])
    except (ValueError, json.JSONDecodeError):
        pass

    return {}


def run_interview(api_key: str, user_name: str) -> dict:
    """Run a multi-turn interview with Claude to learn cooking preferences."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    messages = []

    console.print(
        f"\n[cyan]Great, {user_name}! Let's learn about your cooking style.[/cyan]"
        "\n[dim]Answer naturally. This takes about 2 minutes.[/dim]\n"
    )

    for turn in range(MAX_INTERVIEW_TURNS):
        try:
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=500,
                system=INTERVIEW_SYSTEM_PROMPT,
                messages=messages,
            )
        except Exception:
            console.print("[red]API error during interview. Retrying...[/red]")
            try:
                response = client.messages.create(
                    model=MODEL_NAME,
                    max_tokens=500,
                    system=INTERVIEW_SYSTEM_PROMPT,
                    messages=messages,
                )
            except Exception:
                console.print("[red]Interview failed. Using defaults.[/red]")
                return {}

        assistant_text = response.content[0].text

        if "INTERVIEW_COMPLETE" in assistant_text:
            # Show any text before the signal
            visible = assistant_text.split("INTERVIEW_COMPLETE")[0].strip()
            if visible:
                console.print(f"[green]Chef Claude:[/green] {visible}\n")
            console.print("[green]Got it, thanks![/green]")
            return _extract_interview_json(assistant_text)

        # Display question
        console.print(f"[green]Chef Claude:[/green] {assistant_text}\n")

        # Get user answer
        user_input = Prompt.ask("[yellow]You[/yellow]")

        messages.append({"role": "assistant", "content": assistant_text})
        messages.append({"role": "user", "content": user_input})

    # Hit max turns — ask Claude to wrap up
    messages.append({"role": "assistant", "content": "Thanks for sharing all that!"})
    messages.append(
        {"role": "user", "content": "Please summarize what you've learned so far."}
    )
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=800,
            system=INTERVIEW_SYSTEM_PROMPT
            + "\n\nThe interview is over. Output INTERVIEW_COMPLETE and the JSON summary now.",
            messages=messages,
        )
        return _extract_interview_json(response.content[0].text)
    except Exception:
        return {}


PREFERENCES_SYSTEM_PROMPT = """\
Based on the interview data and allergy information below, generate a preferences.md file \
for a recipe assistant. This file will be injected into every recipe generation prompt, so \
make it specific and actionable.

Follow this exact structure:

# [User Name]'s Kitchen - Recipe Preferences

## Household
- Users, default servings, leftover philosophy

## CRITICAL - Allergies & Restrictions
[If allergies exist, list them prominently with a warning that these must NEVER appear in recipes. \
If no allergies, note "No confirmed allergies."]

## Cuisine preferences
### Tier 1 (weekly rotation)
### Tier 2 (regular rotation)
### Tier 3 (occasional)
### Avoid

## Flavor profile
### Strong preferences
### Spice tolerance
### Hard restrictions (non-allergy)

## Proteins
### Regular rotation
### Want more of
### Avoid

## Equipment
### Primary (use frequently)
### Available (situational)
### Philosophy

## Pantry staples
[Make reasonable assumptions based on their cuisine preferences — oils, sauces, spices, etc.]

## Time constraints
### Weeknight default
### Weekend

## Output preferences
- Default to [household_size] servings
- Include active time and total time
- Mark pantry staples with asterisk (*) in ingredient lists
- Include technique tips for proteins

Write in a direct, practical style. Use the interview data to fill in real preferences. \
Do not use generic placeholders. Output ONLY the markdown, no preamble or explanation.
"""

USER_PREFERENCES_FILE = USER_DATA_DIR / "preferences.md"


def generate_preferences_md(api_key: str, config: dict) -> str:
    """Generate a preferences.md file from interview data and allergies."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    user_data = json.dumps(
        {
            "user_name": config.get("user_name", "User"),
            "allergies": config.get("allergies", {}).get("items", []),
            "interview": config.get("interview_data", {}),
        },
        indent=2,
    )

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=3000,
        system=PREFERENCES_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Here is the user data:\n\n{user_data}"}],
    )

    return response.content[0].text.strip()


def show_preferences_summary(preferences_md: str) -> str:
    """
    Show a summary of generated preferences and ask user to confirm.

    Returns: "yes", "edit", or "redo"
    """
    console.print("\n[bold cyan]Here's what I learned about your kitchen:[/bold cyan]\n")

    # Extract and display key sections (show first ~40 lines as a preview)
    lines = preferences_md.split("\n")
    preview = "\n".join(lines[:40])
    if len(lines) > 40:
        preview += f"\n[dim]...and {len(lines) - 40} more lines[/dim]"
    console.print(preview)

    console.print(
        "\n[yellow]Does this look right?[/yellow]\n"
        "  1. [green]Yes, save it[/green]\n"
        "  2. [yellow]Show full text so I can review[/yellow]\n"
        "  3. [red]Redo the interview[/red]"
    )
    choice = Prompt.ask("Your choice", choices=["1", "2", "3"], default="1")

    if choice == "1":
        return "yes"
    elif choice == "2":
        console.print(f"\n{'─' * 60}")
        console.print(preferences_md)
        console.print(f"{'─' * 60}\n")
        if Confirm.ask("[yellow]Save this?[/yellow]", default=True):
            return "yes"
        return "redo"
    else:
        return "redo"


def save_preferences(preferences_md: str):
    """Save preferences.md to the user data directory."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USER_PREFERENCES_FILE, "w", encoding="utf-8") as f:
        f.write(preferences_md)


def backup_preferences():
    """Back up existing preferences.md if it exists."""
    if USER_PREFERENCES_FILE.exists():
        backup = USER_PREFERENCES_FILE.with_suffix(".md.backup")
        shutil.copy2(USER_PREFERENCES_FILE, backup)
        console.print("[dim]Backed up existing preferences.[/dim]")


def run_preferences_update(api_key: str, user_name: str):
    """Re-run allergies + interview + preferences without touching name/API key."""
    config = load_user_config()

    # Collect allergies
    while True:
        allergy_info = collect_allergies()
        if confirm_allergies(allergy_info["items"]):
            break

    now = datetime.now(timezone.utc).isoformat()
    config["allergies"] = {
        "items": allergy_info["items"],
        "confirmed": True,
        "confirmed_at": now,
    }
    save_user_config(config)

    # Interview + preferences generation
    while True:
        interview_data = run_interview(api_key, user_name)
        config["interview_data"] = interview_data
        save_user_config(config)

        console.print("\n[dim]Generating your preference profile...[/dim]")
        try:
            preferences_md = generate_preferences_md(api_key, config)
        except Exception:
            console.print("[red]Failed to generate preferences. Retrying...[/red]")
            continue

        result = show_preferences_summary(preferences_md)
        if result == "yes":
            save_preferences(preferences_md)
            break

    # Clean up
    config.pop("interview_data", None)
    config["preferences_updated_at"] = datetime.now(timezone.utc).isoformat()
    save_user_config(config)

    console.print(f"\n[green]Preferences updated, {user_name}![/green]\n")


def run_onboarding() -> bool:
    """Main onboarding flow. Returns True if successful."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Back up existing preferences if re-running setup
    backup_preferences()

    # Collect name
    name = collect_name()

    # Collect API key
    api_key = collect_api_key()

    # Collect allergies (loop until confirmed)
    while True:
        allergy_info = collect_allergies()
        if confirm_allergies(allergy_info["items"]):
            break

    # Save config so far
    config = load_user_config()
    now = datetime.now(timezone.utc).isoformat()
    config.update(
        {
            "user_name": name,
            "allergies": {
                "items": allergy_info["items"],
                "confirmed": True,
                "confirmed_at": now,
            },
            "created_at": config.get("created_at", now),
            "onboarding_complete": False,
        }
    )
    save_user_config(config)

    # Run preference interview and generate preferences.md
    while True:
        interview_data = run_interview(api_key, name)
        config["interview_data"] = interview_data
        save_user_config(config)

        console.print("\n[dim]Generating your preference profile...[/dim]")
        try:
            preferences_md = generate_preferences_md(api_key, config)
        except Exception:
            console.print("[red]Failed to generate preferences. Retrying...[/red]")
            continue

        result = show_preferences_summary(preferences_md)
        if result == "yes":
            save_preferences(preferences_md)
            break
        # "redo" loops back to interview

    # Clean up interview data and mark complete
    config.pop("interview_data", None)
    config["onboarding_complete"] = True
    config["onboarding_completed_at"] = datetime.now(timezone.utc).isoformat()
    save_user_config(config)

    console.print(
        f"\n[green]Setup complete, {name}! You're ready to generate recipes.[/green]\n"
    )
    return True

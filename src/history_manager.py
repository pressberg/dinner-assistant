"""Recipe and meal history tracking for cuisine variety and saved recipes"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from .config import DATA_DIR, RECENT_MEALS_DAYS, MAX_HISTORY_RECIPES


class HistoryManager:
    def __init__(self):
        self.recipe_history_file = DATA_DIR / "recipe_history.json"
        self.recent_meals_file = DATA_DIR / "recent_meals.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create history files if they don't exist"""
        if not self.recipe_history_file.exists():
            self._save_json(self.recipe_history_file, {"recipes": []})
        if not self.recent_meals_file.exists():
            self._save_json(self.recent_meals_file, {"meals": []})

    def _load_json(self, filepath: Path) -> dict:
        """Load JSON from file with error handling"""
        try:
            with open(filepath, 'r', encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file—reset it
            default = {"recipes": []} if "recipe" in filepath.name else {"meals": []}
            self._save_json(filepath, default)
            return default

    def _save_json(self, filepath: Path, data: dict):
        """Save JSON to file"""
        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_recipe(self, recipe: Dict) -> bool:
        """
        Save a recipe to history.

        Args:
            recipe: Recipe dict from generator output

        Returns:
            True if saved successfully
        """
        try:
            data = self._load_json(self.recipe_history_file)

            # Add metadata
            recipe_entry = {
                **recipe,
                'saved_at': datetime.now().isoformat(),
                'id': len(data['recipes']) + 1,
                'times_made': 0
            }

            data['recipes'].append(recipe_entry)

            # Enforce max history
            if len(data['recipes']) > MAX_HISTORY_RECIPES:
                data['recipes'] = data['recipes'][-MAX_HISTORY_RECIPES:]

            self._save_json(self.recipe_history_file, data)
            return True
        except Exception as e:
            print(f"Error saving recipe: {e}")
            return False

    def log_meal(self, recipe_name: str, cuisine_type: str) -> bool:
        """
        Log that a meal was made (for cuisine variety tracking).

        Args:
            recipe_name: Name of the recipe
            cuisine_type: Cuisine category (e.g., "Italian", "Japanese")

        Returns:
            True if logged successfully
        """
        try:
            data = self._load_json(self.recent_meals_file)

            meal = {
                'recipe_name': recipe_name,
                'cuisine_type': cuisine_type.strip().title(),  # Normalize
                'date': datetime.now().isoformat()
            }

            data['meals'].append(meal)

            # Prune old meals
            cutoff = datetime.now() - timedelta(days=RECENT_MEALS_DAYS)
            data['meals'] = [
                m for m in data['meals']
                if datetime.fromisoformat(m['date']) > cutoff
            ]

            self._save_json(self.recent_meals_file, data)

            # Also increment times_made on the saved recipe if it exists
            self._increment_times_made(recipe_name)

            return True
        except Exception as e:
            print(f"Error logging meal: {e}")
            return False

    def _increment_times_made(self, recipe_name: str):
        """Increment the times_made counter for a saved recipe"""
        try:
            data = self._load_json(self.recipe_history_file)
            for recipe in data['recipes']:
                if recipe['name'].lower() == recipe_name.lower():
                    recipe['times_made'] = recipe.get('times_made', 0) + 1
                    break
            self._save_json(self.recipe_history_file, data)
        except Exception:
            pass  # Non-critical, don't fail the meal logging

    def get_recent_meals(self) -> List[Dict]:
        """Get meals from the last RECENT_MEALS_DAYS days"""
        try:
            data = self._load_json(self.recent_meals_file)
            cutoff = datetime.now() - timedelta(days=RECENT_MEALS_DAYS)

            return [
                m for m in data['meals']
                if datetime.fromisoformat(m['date']) > cutoff
            ]
        except Exception as e:
            print(f"Error getting recent meals: {e}")
            return []

    def get_recipe_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get saved recipes, most recent first.

        Args:
            limit: Max number to return (None for all)
        """
        try:
            data = self._load_json(self.recipe_history_file)
            recipes = list(reversed(data['recipes']))
            if limit:
                recipes = recipes[:limit]
            return recipes
        except Exception as e:
            print(f"Error getting recipe history: {e}")
            return []

    def get_recent_cuisines(self) -> List[str]:
        """Get list of cuisines cooked recently (for variety enforcement)"""
        meals = self.get_recent_meals()
        return [m['cuisine_type'] for m in meals if 'cuisine_type' in m]

    def find_recipe_by_name(self, search_term: str) -> List[Dict]:
        """
        Search saved recipes by name (case-insensitive partial match).

        Args:
            search_term: Partial name to search for

        Returns:
            List of matching recipes
        """
        recipes = self.get_recipe_history()
        search_lower = search_term.lower()
        return [r for r in recipes if search_lower in r['name'].lower()]

    def get_favorites(self, min_times_made: int = 2) -> List[Dict]:
        """Get recipes that have been made multiple times"""
        recipes = self.get_recipe_history()
        return [r for r in recipes if r.get('times_made', 0) >= min_times_made]

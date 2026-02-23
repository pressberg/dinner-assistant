"""Configuration management for Pressberg Kitchen Recipe Assistant"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PREFERENCES_FILE = PROJECT_ROOT / "preferences.md"

# User data lives in ~/.dinner-assistant/ (separate from app code)
USER_DATA_DIR = Path.home() / ".dinner-assistant"
DATA_DIR = USER_DATA_DIR / "data"

# Create user data directories if they don't exist
USER_DATA_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Migrate old data from project ./data/ to ~/.dinner-assistant/data/
_OLD_DATA_DIR = PROJECT_ROOT / "data"
for _filename in ("recipe_history.json", "recent_meals.json"):
    _old_file = _OLD_DATA_DIR / _filename
    _new_file = DATA_DIR / _filename
    if _old_file.exists() and not _new_file.exists():
        shutil.copy2(_old_file, _new_file)
        print(f"Migrated {_filename} to ~/.dinner-assistant/")

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found. "
        "Create a .env file with your API key or set the environment variable."
    )

# Model configuration
MODEL_NAME = "claude-sonnet-4-20250514"

# History settings
RECENT_MEALS_DAYS = 14  # How far back to look for cuisine variety
MAX_HISTORY_RECIPES = 100  # Cap on stored recipes

# Display settings
RECIPE_PREVIEW_STEPS = 3  # How many instruction steps to show in preview

"""Configuration management for Pressberg Kitchen Recipe Assistant"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

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


def get_api_key() -> str:
    """
    Get Anthropic API key, checking multiple sources.

    Priority:
    1. ~/.dinner-assistant/.env (set during onboarding)
    2. Project .env (backward compatibility)
    3. ANTHROPIC_API_KEY environment variable

    Raises ValueError if no key found.
    """
    # Check user data dir .env first (onboarding writes here)
    user_env = USER_DATA_DIR / ".env"
    if user_env.exists():
        load_dotenv(user_env)
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            return key

    # Fall back to project .env
    load_dotenv(PROJECT_ROOT / ".env")
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key

    raise ValueError(
        "ANTHROPIC_API_KEY not found. Run the app to complete onboarding, "
        "or set the environment variable."
    )


# API Configuration — lazy so the module can import before onboarding
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Try loading from user .env if not already set
if not ANTHROPIC_API_KEY:
    _user_env = USER_DATA_DIR / ".env"
    if _user_env.exists():
        load_dotenv(_user_env)
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Fall back to project .env
if not ANTHROPIC_API_KEY:
    load_dotenv(PROJECT_ROOT / ".env")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Preferences — user-generated lives in ~/.dinner-assistant/, project file is fallback
USER_PREFERENCES_FILE = USER_DATA_DIR / "preferences.md"


def has_user_preferences() -> bool:
    """Check if a user-generated preferences.md exists."""
    return USER_PREFERENCES_FILE.exists()


# Model configuration
MODEL_NAME = "claude-sonnet-4-20250514"

# History settings
RECENT_MEALS_DAYS = 14  # How far back to look for cuisine variety
MAX_HISTORY_RECIPES = 100  # Cap on stored recipes

# Display settings
RECIPE_PREVIEW_STEPS = 3  # How many instruction steps to show in preview

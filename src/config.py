"""Configuration management for Pressberg Kitchen Recipe Assistant"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PREFERENCES_FILE = PROJECT_ROOT / "preferences.md"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

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

# Project Context: Pressberg Kitchen Recipe Assistant

## Overview
A personalized CLI tool that generates dinner recipe suggestions using Claude AI, tailored to the cooking preferences, equipment, and dietary restrictions of Matt and Jennifer Pressberg. Built in Python with the Anthropic API.

## Architecture

### Entry Point
- `python -m src.dinner` — Click-based CLI with interactive prompts via Rich

### Core Modules
- **`src/dinner.py`** — CLI entry point and all display/interaction logic. Handles recipe generation flow, history viewing, search, favorites, and marking meals as made.
- **`src/recipe_generator.py`** — Anthropic API integration. Builds a detailed prompt from available ingredients, user preferences (`preferences.md`), recent cuisine history, and optional constraints. Parses structured JSON responses with fallback extraction.
- **`src/history_manager.py`** — JSON file-based persistence for saved recipes (`data/recipe_history.json`) and recent meal tracking (`data/recent_meals.json`). Handles cuisine variety enforcement by tracking what's been cooked in the last 14 days.
- **`src/config.py`** — Central configuration: API key loading (from `.env`), paths, model selection, and tunable constants.

### Data Flow
1. User provides ingredients and optional constraints via CLI prompts
2. `HistoryManager` supplies recent cuisines to avoid repetition
3. `RecipeGenerator` builds a prompt combining ingredients + preferences + cuisine restrictions
4. Claude returns structured JSON with 3 recipe options and a recommendation
5. Recipes are displayed with Rich formatting; user picks a preferred option, can view full instructions, export to Word doc, save to collection, or log as made

### Key Design Decisions
- **Preferences as markdown**: `preferences.md` is injected directly into the prompt, making it easy to edit without code changes
- **JSON file storage**: No database dependency; `data/` directory holds recipe history and meal logs
- **Robust JSON parsing**: Response parser handles raw JSON, markdown code blocks, and brace-matching extraction
- **Cuisine variety**: Automatic 14-day lookback prevents suggesting recently-cooked cuisine types
- **Word doc export**: Recipes can be exported as `.docx` files to `recipe-book/` with a Notes section for handwritten additions

## Configuration
- **Model**: `claude-sonnet-4-20250514` (set in `src/config.py`)
- **API key**: Via `ANTHROPIC_API_KEY` environment variable (`.env` file)
- **History cap**: 100 saved recipes max
- **Variety window**: 14 days for cuisine deduplication

## Dependencies
- `anthropic` — Claude API client
- `python-dotenv` — Environment variable loading
- `click` — CLI framework
- `rich` — Terminal formatting and interactive prompts
- `python-docx` — Word document generation for recipe export

## CLI Commands
| Command | Description |
|---|---|
| `python -m src.dinner` | Generate recipes (default interactive flow) |
| `--history` | View saved recipe history table |
| `--recent` | View meals cooked in last 14 days |
| `--made` | Interactively mark a saved recipe as made |
| `--favorites` | View recipes made 2+ times |
| `--search "term"` | Search saved recipes by name |

# Pressberg Kitchen Recipe Assistant - Project context

## Last updated
2026-02-23

## Recent changes

### Session: 2026-02-23 - Onboarding flow (name, API key, allergies)
- New `src/onboarding.py` handles first-time user setup
  - `is_onboarding_complete()` checks config.json for completion flag
  - `collect_name()` and `collect_api_key()` with validation (makes test API call)
  - `collect_allergies()` with numbered common-allergy picker and free text
  - `confirm_allergies()` loop until user confirms the list
  - API key saved to `~/.dinner-assistant/.env`, config to `config.json`
- `config.py` updated: `get_api_key()` checks user .env, project .env, env var in order; module no longer crashes if no key at import time
- `dinner.py` calls `run_onboarding()` before anything else if onboarding incomplete
- `recipe_generator.py` loads allergies from config and injects a CRITICAL SAFETY section at the top of every prompt, before preferences
- Allergies are safety-critical: always confirmed by user, never overridden by preferences

#### config.json schema
```json
{
  "user_name": "Matt",
  "allergies": {
    "items": ["shellfish", "tree nuts"],
    "confirmed": true,
    "confirmed_at": "2026-02-23T10:35:00+00:00"
  },
  "onboarding_complete": false,
  "created_at": "2026-02-23T10:30:00+00:00"
}
```

### Session: 2026-02-23 - Move user data to home directory
- User data (recipe_history.json, recent_meals.json) now stored in `~/.dinner-assistant/data/`
- On first run, existing data is automatically migrated from `./data/` to the new location
- `config.py` exports `USER_DATA_DIR` (home dir) and `DATA_DIR` (home dir/data) alongside `PROJECT_ROOT`
- `preferences.md` still lives in the project directory (will move in a later commit)
- Fixed `encoding="utf-8"` on file ops in `history_manager.py` (Silvio finding)

### Session: 2026-02-18 - Clean rewrite of GUI
- Rewrote `src/gui.py` from scratch with simplified architecture
  - Single `DinnerAssistantApp` class, no separate screen classes or custom widget subclasses
  - One `main_frame` holds all content; `_clear()` destroys all children before each screen transition
  - Screens: welcome, ingredients (quick-add grid + custom entry), constraints (checkboxes), loading (animated dots), results (scrollable cards), full recipe view, history, recent meals
  - Retro Mac OS 8/9 styling: gray #DDDDDD background, Geneva font, raised #CCCCCC buttons
  - Threaded recipe generation keeps UI responsive
  - Uses existing `RecipeGenerator` and `HistoryManager`

## Architecture
- `src/onboarding.py` - First-time user setup (name, API key, allergies)
- `src/recipe_generator.py` - Claude API integration for recipe generation
- `src/history_manager.py` - JSON-based recipe history and meal logging
- `src/config.py` - Configuration, paths, preferences and API key resolution
- `src/dinner.py` - CLI entry point (triggers onboarding if needed)
- `src/gui.py` - Tkinter GUI (retro Mac OS 8/9 style)
- `run_gui.py` - GUI launcher

## Data storage
- User config: `~/.dinner-assistant/config.json` (name, allergies, onboarding state)
- API key: `~/.dinner-assistant/.env` (written during onboarding)
- User data: `~/.dinner-assistant/data/` (recipe_history.json, recent_meals.json)
- Preferences: `preferences.md` in project root (will move to ~/.dinner-assistant/ later)
- Migration: on startup, old `./data/*.json` files are copied to the new location if they don't already exist there

## Known issues (from Silvio review)
- ~~Error messages could leak API response internals (medium)~~ Fixed 2026-02-23
- ~~`history_manager.py` missing `encoding="utf-8"` on file ops (medium)~~ Fixed 2026-02-23
- No input length validation on custom constraint/ingredient fields (low)

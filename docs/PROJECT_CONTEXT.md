# Pressberg Kitchen Recipe Assistant - Project context

## Last updated
2026-02-23

## Recent changes

### Session: 2026-02-23 - Flask web interface
- New `src/web.py` provides a browser-based UI at http://localhost:5000
- `run_web.py` launcher in project root
- Retro Mac OS 8/9 styling with `src/static/style.css`
- Full onboarding flow in browser: name, API key, allergies (with confirm), chat-style AI interview, preference review
- Recipe flow: ingredient selection (quick-add grid + custom), constraint checkboxes, async generation with loading screen, recipe cards with save/make-tonight actions, full recipe view
- History, recent meals and settings pages
- All templates in `src/templates/` extending `base.html` (retro window chrome)
- Interview uses fetch-based chat UI posting to `/onboarding/interview/message` AJAX endpoint
- Generation uses `/generate/run` AJAX endpoint with loading screen polling
- Shares same backend as CLI and Tkinter GUI: `RecipeGenerator`, `HistoryManager`, onboarding functions
- Flask session stores ingredients, constraints, recipes and interview state
- Added `flask>=3.0.0` to requirements.txt

#### Web routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Welcome/home (redirects to onboarding if needed) |
| `/ingredients` | GET | Ingredient selection |
| `/constraints` | GET/POST | Constraint checkboxes |
| `/generate` | POST | Start generation (shows loading page) |
| `/generate/run` | POST | AJAX: runs recipe generation |
| `/results` | GET | Recipe cards |
| `/recipe/<index>` | GET | Full recipe view |
| `/save` | POST | AJAX: save recipe |
| `/history` | GET | Saved recipes |
| `/mark-made` | POST | AJAX: log meal |
| `/recent` | GET | Recent meals |
| `/settings` | GET | User settings |
| `/onboarding/name` | GET/POST | Name input |
| `/onboarding/api-key` | GET/POST | API key input + validation |
| `/onboarding/allergies` | GET/POST | Allergy selection |
| `/onboarding/allergies/confirm` | GET/POST | Confirm allergies |
| `/onboarding/interview` | GET | Chat-style interview page |
| `/onboarding/interview/message` | POST | AJAX: interview turn |
| `/onboarding/review` | GET | Review generated preferences |
| `/onboarding/complete` | POST | Finalize onboarding |

### Session: 2026-02-23 - Update preferences option
- New CLI flags: `--setup` (re-run full onboarding) and `--update-preferences` (allergies + interview + prefs only)
- Both back up existing `preferences.md` to `preferences.md.backup` before overwriting
- `--update-preferences` skips name and API key collection, keeps existing config
- `backup_preferences()` and `run_preferences_update()` added to `onboarding.py`
- Recipe history and recent meals are preserved during re-setup

### Session: 2026-02-23 - AI interview and preferences generation
- `run_interview()` conducts 8-12 turn conversation with Claude to learn cooking preferences
  - Covers: cuisines, spice tolerance, proteins, skill level, time constraints, equipment, household size, dietary goals
  - System prompt enforces one-question-at-a-time, conversational style
  - Capped at 12 exchanges; forces wrap-up if Claude doesn't finish naturally
  - Single retry on API errors, returns empty dict as fallback
- `generate_preferences_md()` sends interview data + allergies to Claude to produce a full preferences.md
- `show_preferences_summary()` previews the generated file; user can accept, view full text, or redo the interview
- `save_preferences()` writes to `~/.dinner-assistant/preferences.md`
- `recipe_generator.py` now checks `~/.dinner-assistant/preferences.md` first, falls back to project `preferences.md` for existing users
- `config.py` adds `USER_PREFERENCES_FILE` and `has_user_preferences()` helper
- On completion: `interview_data` is removed from config.json, `onboarding_complete` set to True
- Updated config.json schema now includes `onboarding_completed_at` timestamp

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
- `src/onboarding.py` - First-time user setup (name, API key, allergies, AI interview, preferences generation)
- `src/recipe_generator.py` - Claude API integration for recipe generation
- `src/history_manager.py` - JSON-based recipe history and meal logging
- `src/config.py` - Configuration, paths, preferences and API key resolution
- `src/dinner.py` - CLI entry point (triggers onboarding if needed)
- `src/gui.py` - Tkinter GUI (retro Mac OS 8/9 style)
- `src/web.py` - Flask web interface (retro Mac OS 8/9 style)
- `run_gui.py` - GUI launcher
- `run_web.py` - Flask web launcher (port 5000)

## Data storage
- User config: `~/.dinner-assistant/config.json` (name, allergies, onboarding state)
- API key: `~/.dinner-assistant/.env` (written during onboarding)
- User data: `~/.dinner-assistant/data/` (recipe_history.json, recent_meals.json)
- Preferences: `~/.dinner-assistant/preferences.md` (generated during onboarding); falls back to project `preferences.md` for existing users
- Migration: on startup, old `./data/*.json` files are copied to the new location if they don't already exist there

## Known issues (from Silvio review)
- ~~Error messages could leak API response internals (medium)~~ Fixed 2026-02-23
- ~~`history_manager.py` missing `encoding="utf-8"` on file ops (medium)~~ Fixed 2026-02-23
- No input length validation on custom constraint/ingredient fields (low)

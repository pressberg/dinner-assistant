# Pressberg Kitchen Recipe Assistant - Project context

## Last updated
2026-02-18

## Recent changes

### Session: 2026-02-18 - Clean rewrite of GUI
- Rewrote `src/gui.py` from scratch with simplified architecture
  - Single `DinnerAssistantApp` class, no separate screen classes or custom widget subclasses
  - One `main_frame` holds all content; `_clear()` destroys all children before each screen transition
  - Screens: welcome, ingredients (quick-add grid + custom entry), constraints (checkboxes), loading (animated dots), results (scrollable cards), full recipe view, history, recent meals
  - Retro Mac OS 8/9 styling: gray #DDDDDD background, Geneva font, raised #CCCCCC buttons
  - Threaded recipe generation keeps UI responsive
  - Uses existing `RecipeGenerator` and `HistoryManager`

## Architecture
- `src/recipe_generator.py` - Claude API integration for recipe generation
- `src/history_manager.py` - JSON-based recipe history and meal logging
- `src/config.py` - Configuration and preferences
- `src/dinner.py` - CLI entry point
- `src/gui.py` - Tkinter GUI (retro Mac OS 8/9 style)
- `run_gui.py` - GUI launcher

## Known issues (from Silvio review)
- Error messages could leak API response internals (medium)
- `history_manager.py` missing `encoding="utf-8"` on file ops (medium)
- No input length validation on custom constraint/ingredient fields (low)

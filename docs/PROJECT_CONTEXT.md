# Pressberg Kitchen Recipe Assistant - Project context

## Last updated
2026-02-18

## Recent changes

### Session: 2026-02-18 - Retro Mac GUI
- Added `src/gui.py`: Full tkinter GUI with Mac OS 8/9 retro styling
  - Wizard flow: Welcome -> Ingredients -> Constraints -> Loading -> Results
  - Quick-add ingredient buttons (proteins, vegetables, starches)
  - Constraint checkboxes (time, equipment, dietary preferences)
  - Recipe results with View Full, Save and Make Tonight actions
  - History browser and recent meals screens
  - Threaded recipe generation to keep UI responsive
- Added `run_gui.py`: Root-level launcher script

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

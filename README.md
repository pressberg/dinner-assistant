# Pressberg Kitchen Recipe Assistant

A personalized CLI tool for generating dinner recipes based on available ingredients, cooking preferences, and equipment. Built for Matt and Jennifer Pressberg.

## Features

- **Smart Recipe Generation**: Uses Claude AI to generate 3 personalized recipe options
- **Preference-Aware**: Considers cuisine preferences, dietary restrictions, equipment, and time constraints
- **Variety Tracking**: Avoids suggesting recently-cooked cuisines
- **Recipe History**: Save and search your favorite recipes
- **Technique Guidance**: Special attention to seafood cooking techniques

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/pressberg/dinner-assistant.git
cd dinner-assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Run the assistant
```bash
python -m src.dinner
```

## Usage

### Generate Recipes (default)
```bash
python -m src.dinner
```

You'll be prompted for:
- Available ingredients (comma-separated)
- Any constraints (time, equipment, etc.)

### View Saved Recipes
```bash
python -m src.dinner --history
```

### View Recent Meals
```bash
python -m src.dinner --recent
```

### Mark a Recipe as Made
```bash
python -m src.dinner --made
```

### View Favorites
```bash
python -m src.dinner --favorites
```

### Search Recipes
```bash
python -m src.dinner --search "salmon"
```

## Customizing Preferences

Edit `preferences.md` to update:
- Cuisine preferences and rankings
- Dietary restrictions
- Equipment list
- Pantry staples
- Time constraints

Changes take effect on the next recipe generation—no code changes needed.

## For Jennifer

To use on your laptop:

1. Clone the repository (same steps as above)
2. Use the same API key in your `.env` file
3. Recipe history syncs if you commit/push the `data/` folder

## Project Structure
```
dinner-assistant/
├── src/
│   ├── dinner.py          # CLI entry point
│   ├── recipe_generator.py # AI integration
│   ├── history_manager.py  # Recipe/meal tracking
│   └── config.py          # Configuration
├── data/                   # Auto-generated history files
├── preferences.md          # Your cooking preferences
└── requirements.txt        # Python dependencies
```

## License

Private project for personal use.

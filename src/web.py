"""
Flask web interface for Pressberg Kitchen Recipe Assistant
"""

import json
import secrets
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from .onboarding import (
    is_onboarding_complete, load_user_config, save_user_config,
    run_interview, generate_preferences_md, save_preferences, backup_preferences,
    COMMON_ALLERGIES, INTERVIEW_SYSTEM_PROMPT, MAX_INTERVIEW_TURNS,
    _extract_interview_json,
)
from .config import get_api_key, USER_DATA_DIR, MODEL_NAME
from .recipe_generator import RecipeGenerator
from .history_manager import HistoryManager

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Same quick ingredients and constraints as the GUI
QUICK_INGREDIENTS = [
    "Chicken", "Ground Turkey", "Salmon", "Shrimp", "Tofu",
    "Rice", "Pasta", "Potatoes", "Bread",
    "Broccoli", "Spinach", "Bell Peppers", "Onions", "Tomatoes",
    "Cheese", "Eggs", "Beans", "Mushrooms",
]

CONSTRAINT_OPTIONS = [
    ("Under 30 minutes", "under 30 minutes"),
    ("Weeknight easy", "weeknight easy, minimal cleanup"),
    ("Use Instant Pot", "use instant pot"),
    ("Use cast iron", "use cast iron skillet"),
    ("No pasta", "no pasta"),
    ("Low carb", "low carb"),
    ("One pot meal", "one pot meal"),
    ("Kid friendly", "kid friendly"),
]

# Lazy-loaded singletons
_generator = None
_history_manager = None


def get_generator():
    global _generator
    if _generator is None:
        _generator = RecipeGenerator()
    return _generator


def get_history_manager():
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager


# ── Main routes ──────────────────────────────────────────────────


@app.route("/")
def index():
    if not is_onboarding_complete():
        return redirect(url_for("onboarding_name"))
    config = load_user_config()
    return render_template("welcome.html", user_name=config.get("user_name", ""))


@app.route("/ingredients")
def ingredients():
    return render_template("ingredients.html", quick_ingredients=QUICK_INGREDIENTS)


@app.route("/constraints", methods=["GET", "POST"])
def constraints():
    if request.method == "POST":
        # Save ingredients from form
        selected = request.form.getlist("ingredients")
        custom = request.form.get("custom_ingredients", "").strip()
        if custom:
            for item in custom.split(","):
                item = item.strip()
                if item and item not in selected:
                    selected.append(item)
        session["ingredients"] = selected

    if not session.get("ingredients"):
        return redirect(url_for("ingredients"))

    return render_template("constraints.html", constraint_options=CONSTRAINT_OPTIONS)


@app.route("/generate", methods=["POST"])
def generate():
    # Collect constraints
    selected_constraints = request.form.getlist("constraints")
    custom_constraint = request.form.get("custom_constraint", "").strip()
    if custom_constraint:
        selected_constraints.append(custom_constraint)
    constraints_text = ", ".join(selected_constraints) if selected_constraints else None

    ingredients = session.get("ingredients", [])
    if not ingredients:
        return redirect(url_for("ingredients"))

    session["constraints"] = constraints_text
    return render_template("loading.html")


@app.route("/generate/run", methods=["POST"])
def generate_run():
    """AJAX endpoint that actually runs recipe generation."""
    ingredients = session.get("ingredients", [])
    constraints = session.get("constraints")

    if not ingredients:
        return jsonify({"error": "No ingredients selected"}), 400

    try:
        generator = get_generator()
        hm = get_history_manager()
        recent_cuisines = hm.get_recent_cuisines()
        result = generator.generate_recipes(
            ingredients=ingredients,
            recent_cuisines=recent_cuisines,
            constraints=constraints,
        )
        session["recipes"] = result
        return jsonify({"status": "done"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results")
def results():
    result = session.get("recipes")
    if not result:
        return redirect(url_for("ingredients"))

    recipes = result.get("recipes", [])
    recommendation = result.get("recommendation", {})
    rec_index = recommendation.get("recipe_index", 0)

    return render_template(
        "results.html",
        recipes=recipes,
        recommendation=recommendation,
        rec_index=rec_index,
    )


@app.route("/recipe/<int:index>")
def recipe_view(index):
    result = session.get("recipes")
    if not result:
        return redirect(url_for("ingredients"))

    recipes = result.get("recipes", [])
    if index < 0 or index >= len(recipes):
        return redirect(url_for("results"))

    return render_template("recipe.html", recipe=recipes[index], index=index)


@app.route("/save", methods=["POST"])
def save_recipe():
    data = request.get_json()
    if not data or "recipe" not in data:
        return jsonify({"error": "No recipe data"}), 400

    recipe = data["recipe"]
    make_tonight = data.get("make_tonight", False)

    hm = get_history_manager()
    saved = hm.save_recipe(recipe)

    if not saved:
        return jsonify({"error": "Failed to save recipe"}), 500

    if make_tonight:
        cuisine = recipe.get("cuisine", "Unknown")
        hm.log_meal(recipe["name"], cuisine)

    return jsonify({"status": "ok"})


@app.route("/history")
def history():
    hm = get_history_manager()
    recipes = hm.get_recipe_history(limit=25)
    return render_template("history.html", recipes=recipes)


@app.route("/mark-made", methods=["POST"])
def mark_made():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    hm = get_history_manager()
    hm.log_meal(data.get("name", ""), data.get("cuisine", "Unknown"))
    return jsonify({"status": "ok"})


@app.route("/recent")
def recent():
    hm = get_history_manager()
    meals = hm.get_recent_meals()
    # Reverse so most recent is first
    meals = list(reversed(meals))
    cuisines = list(set(m.get("cuisine_type", "?") for m in meals))
    return render_template("recent.html", meals=meals, cuisines=cuisines)


@app.route("/settings")
def settings():
    config = load_user_config()
    return render_template("settings.html", config=config)


# ── Onboarding routes ────────────────────────────────────────────


@app.route("/onboarding/name", methods=["GET", "POST"])
def onboarding_name():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("onboarding/name.html", error="Please enter your name.")
        session["onboarding_name"] = name
        return redirect(url_for("onboarding_api_key"))
    return render_template("onboarding/name.html")


@app.route("/onboarding/api-key", methods=["GET", "POST"])
def onboarding_api_key():
    if request.method == "POST":
        key = request.form.get("api_key", "").strip()
        if not key:
            return render_template("onboarding/api_key.html", error="Please enter your API key.")
        if not key.startswith("sk-ant-"):
            return render_template(
                "onboarding/api_key.html",
                error="That doesn't look like a valid Anthropic API key (should start with sk-ant-).",
            )

        # Validate key
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=key)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
        except Exception:
            return render_template(
                "onboarding/api_key.html",
                error="That key didn't work. Check it and try again.",
            )

        # Save to .env
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        env_file = USER_DATA_DIR / ".env"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"ANTHROPIC_API_KEY={key}\n")

        session["onboarding_api_key"] = key
        return redirect(url_for("onboarding_allergies"))

    return render_template("onboarding/api_key.html")


@app.route("/onboarding/allergies", methods=["GET", "POST"])
def onboarding_allergies():
    update_mode = request.args.get("update") == "true"

    if request.method == "POST":
        selected = request.form.getlist("allergies")
        extra = request.form.get("extra_allergies", "").strip()

        items = []
        none_option = str(len(COMMON_ALLERGIES) + 1)
        if none_option not in selected:
            for num in selected:
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(COMMON_ALLERGIES):
                        items.append(COMMON_ALLERGIES[idx][0].lower())
                except ValueError:
                    continue

        if extra:
            for item in extra.split(","):
                item = item.strip().lower()
                if item and item not in items:
                    items.append(item)

        session["onboarding_allergies"] = items
        session["onboarding_update_mode"] = update_mode
        return redirect(url_for("onboarding_allergies_confirm"))

    return render_template(
        "onboarding/allergies.html",
        common_allergies=COMMON_ALLERGIES,
        update_mode=update_mode,
    )


@app.route("/onboarding/allergies/confirm", methods=["GET", "POST"])
def onboarding_allergies_confirm():
    allergies = session.get("onboarding_allergies", [])

    if request.method == "POST":
        action = request.form.get("action")
        if action == "confirm":
            # Save allergies to config
            config = load_user_config()
            now = datetime.now(timezone.utc).isoformat()

            # Save name if from full onboarding
            name = session.get("onboarding_name")
            if name:
                config["user_name"] = name

            config["allergies"] = {
                "items": allergies,
                "confirmed": True,
                "confirmed_at": now,
            }
            config["created_at"] = config.get("created_at", now)
            config["onboarding_complete"] = False
            save_user_config(config)

            return redirect(url_for("onboarding_interview"))
        else:
            update_mode = session.get("onboarding_update_mode", False)
            return redirect(url_for("onboarding_allergies", update="true" if update_mode else None))

    return render_template("onboarding/confirm_allergies.html", allergies=allergies)


@app.route("/onboarding/interview")
def onboarding_interview():
    # Initialize interview conversation
    session["interview_messages"] = []
    return render_template("onboarding/interview.html")


@app.route("/onboarding/interview/message", methods=["POST"])
def onboarding_interview_message():
    """AJAX endpoint for interview chat."""
    data = request.get_json()
    user_message = data.get("message", "").strip() if data else ""

    messages = session.get("interview_messages", [])

    # Add user message if provided (not for first turn)
    if user_message:
        messages.append({"role": "user", "content": user_message})

    # Get API key
    try:
        api_key = session.get("onboarding_api_key") or get_api_key()
    except ValueError:
        return jsonify({"error": "No API key configured"}), 400

    # Call Claude
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=500,
            system=INTERVIEW_SYSTEM_PROMPT,
            messages=messages,
        )
        assistant_text = response.content[0].text
    except Exception:
        return jsonify({"error": "API error. Please try again."}), 500

    if "INTERVIEW_COMPLETE" in assistant_text:
        # Extract data and store
        interview_data = _extract_interview_json(assistant_text)
        config = load_user_config()
        config["interview_data"] = interview_data
        save_user_config(config)

        visible = assistant_text.split("INTERVIEW_COMPLETE")[0].strip()
        session["interview_messages"] = messages
        return jsonify({"message": visible or "Got it, thanks!", "complete": True})

    # Check if we've hit max turns
    turn_count = len([m for m in messages if m["role"] == "user"])
    if turn_count >= MAX_INTERVIEW_TURNS:
        # Force wrap-up
        messages.append({"role": "assistant", "content": assistant_text})
        messages.append({"role": "user", "content": "Please summarize what you've learned so far."})
        try:
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=800,
                system=INTERVIEW_SYSTEM_PROMPT
                + "\n\nThe interview is over. Output INTERVIEW_COMPLETE and the JSON summary now.",
                messages=messages,
            )
            final_text = response.content[0].text
            interview_data = _extract_interview_json(final_text)
        except Exception:
            interview_data = {}

        config = load_user_config()
        config["interview_data"] = interview_data
        save_user_config(config)

        session["interview_messages"] = messages
        return jsonify({"message": "Thanks for all that info!", "complete": True})

    # Normal turn — save and return
    messages.append({"role": "assistant", "content": assistant_text})
    session["interview_messages"] = messages
    return jsonify({"message": assistant_text, "complete": False})


@app.route("/onboarding/review")
def onboarding_review():
    # Generate preferences
    try:
        api_key = session.get("onboarding_api_key") or get_api_key()
    except ValueError:
        return redirect(url_for("onboarding_api_key"))

    config = load_user_config()
    try:
        preferences_md = generate_preferences_md(api_key, config)
    except Exception:
        preferences_md = None

    session["generated_preferences"] = preferences_md
    return render_template(
        "onboarding/review.html",
        preferences=preferences_md,
        user_name=config.get("user_name", ""),
    )


@app.route("/onboarding/complete", methods=["POST"])
def onboarding_complete():
    action = request.form.get("action")

    if action == "redo":
        return redirect(url_for("onboarding_interview"))

    # Save preferences
    preferences_md = session.get("generated_preferences")
    if preferences_md:
        save_preferences(preferences_md)

    config = load_user_config()
    config.pop("interview_data", None)
    config["onboarding_complete"] = True
    config["onboarding_completed_at"] = datetime.now(timezone.utc).isoformat()
    save_user_config(config)

    # Clear onboarding session data
    for key in ["onboarding_name", "onboarding_api_key", "onboarding_allergies",
                "onboarding_update_mode", "interview_messages", "generated_preferences"]:
        session.pop(key, None)

    # Reset generator so it picks up new preferences
    global _generator
    _generator = None

    return redirect(url_for("index"))

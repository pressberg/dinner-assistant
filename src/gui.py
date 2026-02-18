"""Retro Mac OS 8/9 styled GUI for Pressberg Kitchen Recipe Assistant"""

import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime
from .recipe_generator import RecipeGenerator
from .history_manager import HistoryManager


# Style constants
BG_COLOR = "#DDDDDD"
BTN_COLOR = "#CCCCCC"
FONT_FAMILY = "Geneva"
FONT = (FONT_FAMILY, 12)
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")

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


class DinnerAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pressberg Kitchen")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("700x750")
        self.root.resizable(True, True)

        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        self.history_manager = HistoryManager()
        self.generator = None
        self.selected_ingredients = []
        self.result = None

        self.show_welcome()

    def _clear(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _make_button(self, parent, text, command, width=20):
        return tk.Button(
            parent, text=text, command=command,
            font=FONT, bg=BTN_COLOR, relief=tk.RAISED, bd=2,
            activebackground="#BBBBBB", width=width,
        )

    def _make_label(self, parent, text, font=FONT, anchor="w", **kwargs):
        return tk.Label(
            parent, text=text, font=font, bg=BG_COLOR, anchor=anchor, **kwargs
        )

    # ── Welcome screen ──────────────────────────────────────────────

    def show_welcome(self):
        self._clear()

        self._make_label(
            self.main_frame, "Pressberg Kitchen", font=FONT_TITLE, anchor="center"
        ).pack(pady=(30, 5))

        self._make_label(
            self.main_frame, "Recipe Assistant", font=FONT_HEADING, anchor="center"
        ).pack(pady=(0, 30))

        self._make_label(
            self.main_frame,
            "What would you like to do?",
            font=FONT, anchor="center",
        ).pack(pady=(0, 20))

        btn_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        btn_frame.pack()

        self._make_button(
            btn_frame, "New dinner", self.show_ingredients, width=24
        ).pack(pady=6)

        self._make_button(
            btn_frame, "Saved recipes", self.show_history, width=24
        ).pack(pady=6)

        self._make_button(
            btn_frame, "Recent meals", self.show_recent_meals, width=24
        ).pack(pady=6)

    # ── Ingredients screen ───────────────────────────────────────────

    def show_ingredients(self):
        self._clear()
        self.selected_ingredients = []

        self._make_label(
            self.main_frame, "What ingredients do you have?", font=FONT_HEADING
        ).pack(anchor="w", pady=(0, 10))

        self._make_label(
            self.main_frame,
            "Tap to add, or type your own below. Pantry staples are assumed.",
            font=FONT_SMALL,
        ).pack(anchor="w", pady=(0, 10))

        # Quick-add grid
        grid_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        grid_frame.pack(fill=tk.X, pady=(0, 10))

        self.ingredient_buttons = {}
        cols = 4
        for i, ing in enumerate(QUICK_INGREDIENTS):
            btn = tk.Button(
                grid_frame, text=ing, font=FONT_SMALL,
                bg=BTN_COLOR, relief=tk.RAISED, bd=2,
                activebackground="#BBBBBB",
                command=lambda name=ing: self._toggle_ingredient(name),
            )
            btn.grid(row=i // cols, column=i % cols, padx=3, pady=3, sticky="ew")
            self.ingredient_buttons[ing] = btn

        for c in range(cols):
            grid_frame.columnconfigure(c, weight=1)

        # Custom entry
        entry_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        entry_frame.pack(fill=tk.X, pady=(5, 5))

        self._make_label(entry_frame, "Other:", font=FONT_SMALL).pack(side=tk.LEFT)

        self.custom_entry = tk.Entry(entry_frame, font=FONT, width=30)
        self.custom_entry.pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(
            entry_frame, text="Add", font=FONT_SMALL,
            bg=BTN_COLOR, relief=tk.RAISED, bd=2,
            command=self._add_custom_ingredient,
        ).pack(side=tk.LEFT)

        # Selected display
        self._make_label(
            self.main_frame, "Selected:", font=FONT_BOLD
        ).pack(anchor="w", pady=(10, 2))

        self.selected_label = self._make_label(
            self.main_frame, "(none yet)", font=FONT_SMALL
        )
        self.selected_label.pack(anchor="w", pady=(0, 10))

        # Nav buttons
        nav = tk.Frame(self.main_frame, bg=BG_COLOR)
        nav.pack(fill=tk.X, pady=(10, 0))

        self._make_button(nav, "Back", self.show_welcome, width=10).pack(side=tk.LEFT)
        self._make_button(nav, "Next →", self.show_constraints, width=10).pack(side=tk.RIGHT)

    def _toggle_ingredient(self, name):
        btn = self.ingredient_buttons[name]
        if name in self.selected_ingredients:
            self.selected_ingredients.remove(name)
            btn.configure(relief=tk.RAISED, bg=BTN_COLOR)
        else:
            self.selected_ingredients.append(name)
            btn.configure(relief=tk.SUNKEN, bg="#AACCAA")
        self._update_selected_label()

    def _add_custom_ingredient(self):
        text = self.custom_entry.get().strip()
        if text and text not in self.selected_ingredients:
            self.selected_ingredients.append(text)
            self.custom_entry.delete(0, tk.END)
            self._update_selected_label()

    def _update_selected_label(self):
        if self.selected_ingredients:
            self.selected_label.configure(text=", ".join(self.selected_ingredients))
        else:
            self.selected_label.configure(text="(none yet)")

    # ── Constraints screen ───────────────────────────────────────────

    def show_constraints(self):
        if not self.selected_ingredients:
            messagebox.showwarning("No ingredients", "Please select at least one ingredient.")
            return

        self._clear()

        self._make_label(
            self.main_frame, "Any constraints?", font=FONT_HEADING
        ).pack(anchor="w", pady=(0, 10))

        self._make_label(
            self.main_frame, "Check all that apply, or skip to generate.",
            font=FONT_SMALL,
        ).pack(anchor="w", pady=(0, 10))

        self.constraint_vars = {}
        for label, value in CONSTRAINT_OPTIONS:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.main_frame, text=label, variable=var,
                font=FONT, bg=BG_COLOR, activebackground=BG_COLOR,
                anchor="w",
            )
            cb.pack(anchor="w", padx=10, pady=2)
            self.constraint_vars[value] = var

        # Nav
        nav = tk.Frame(self.main_frame, bg=BG_COLOR)
        nav.pack(fill=tk.X, pady=(20, 0))

        self._make_button(nav, "← Back", self.show_ingredients, width=10).pack(side=tk.LEFT)
        self._make_button(nav, "Generate!", self._run_generation, width=14).pack(side=tk.RIGHT)

    def _get_constraints_text(self):
        active = [k for k, v in self.constraint_vars.items() if v.get()]
        return ", ".join(active) if active else None

    # ── Loading screen ───────────────────────────────────────────────

    def show_loading(self):
        self._clear()

        self._make_label(
            self.main_frame, "Generating recipes...", font=FONT_HEADING, anchor="center"
        ).pack(pady=(80, 20))

        self._make_label(
            self.main_frame,
            "Consulting Claude with your ingredients\nand preferences. One moment.",
            font=FONT, anchor="center", justify=tk.CENTER,
        ).pack()

        self.loading_dots = self._make_label(
            self.main_frame, "", font=FONT_TITLE, anchor="center"
        )
        self.loading_dots.pack(pady=20)

        self._animate_dots(0)

    def _animate_dots(self, count):
        if not self.loading_dots.winfo_exists():
            return
        dots = "." * ((count % 3) + 1)
        self.loading_dots.configure(text=dots)
        self.root.after(500, self._animate_dots, count + 1)

    def _run_generation(self):
        constraints = self._get_constraints_text()
        self.show_loading()

        def generate():
            try:
                if self.generator is None:
                    self.generator = RecipeGenerator()
                recent_cuisines = self.history_manager.get_recent_cuisines()
                result = self.generator.generate_recipes(
                    ingredients=self.selected_ingredients,
                    recent_cuisines=recent_cuisines,
                    constraints=constraints,
                )
                self.root.after(0, self.show_results, result)
            except Exception as e:
                self.root.after(0, self._show_error, str(e))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _show_error(self, msg):
        self._clear()
        self._make_label(
            self.main_frame, "Something went wrong", font=FONT_HEADING
        ).pack(anchor="w", pady=(20, 10))

        self._make_label(self.main_frame, msg, font=FONT_SMALL, wraplength=650).pack(
            anchor="w", pady=(0, 20)
        )

        self._make_button(self.main_frame, "Back to start", self.show_welcome).pack()

    # ── Results screen ───────────────────────────────────────────────

    def show_results(self, result):
        self._clear()
        self.result = result

        recipes = result.get("recipes", [])
        recommendation = result.get("recommendation", {})
        rec_index = recommendation.get("recipe_index", 0)

        self._make_label(
            self.main_frame, "Your dinner options", font=FONT_HEADING
        ).pack(anchor="w", pady=(0, 5))

        if recommendation.get("reasoning"):
            self._make_label(
                self.main_frame,
                f"Recommended: Option {rec_index + 1} — {recommendation['reasoning']}",
                font=FONT_SMALL, wraplength=650,
            ).pack(anchor="w", pady=(0, 10))

        # Scrollable area
        canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120 or event.delta), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        for i, recipe in enumerate(recipes):
            is_rec = i == rec_index
            border_color = "#336633" if is_rec else "#999999"

            card = tk.Frame(
                scroll_frame, bg="#EEEEEE", relief=tk.RIDGE, bd=2,
                highlightbackground=border_color, highlightthickness=2 if is_rec else 0,
            )
            card.pack(fill=tk.X, pady=6, padx=4)

            # Header
            star = "★ " if is_rec else ""
            header = f"{star}Option {i + 1}: {recipe['name']}"
            tk.Label(
                card, text=header, font=FONT_BOLD, bg="#EEEEEE", anchor="w"
            ).pack(fill=tk.X, padx=8, pady=(6, 0))

            # Meta line
            meta = (
                f"{recipe.get('cuisine', '')} · "
                f"{recipe.get('difficulty', '')} · "
                f"{recipe.get('active_time_minutes', '?')} min active / "
                f"{recipe.get('total_time_minutes', '?')} min total"
            )
            tk.Label(
                card, text=meta, font=FONT_SMALL, bg="#EEEEEE", anchor="w", fg="#555555"
            ).pack(fill=tk.X, padx=8)

            # Description
            if recipe.get("description"):
                tk.Label(
                    card, text=recipe["description"], font=FONT_SMALL,
                    bg="#EEEEEE", anchor="w", wraplength=600, justify=tk.LEFT,
                ).pack(fill=tk.X, padx=8, pady=(4, 0))

            # Ingredients preview
            ings = recipe.get("ingredients", [])
            if ings:
                ing_text = "Ingredients: " + ", ".join(
                    ing.rstrip("*") for ing in ings[:6]
                )
                if len(ings) > 6:
                    ing_text += f"  ...and {len(ings) - 6} more"
                tk.Label(
                    card, text=ing_text, font=FONT_SMALL,
                    bg="#EEEEEE", anchor="w", wraplength=600, justify=tk.LEFT,
                ).pack(fill=tk.X, padx=8, pady=(4, 0))

            # Action buttons
            btn_row = tk.Frame(card, bg="#EEEEEE")
            btn_row.pack(fill=tk.X, padx=8, pady=6)

            tk.Button(
                btn_row, text="View full recipe", font=FONT_SMALL,
                bg=BTN_COLOR, relief=tk.RAISED, bd=2,
                command=lambda r=recipe: self._show_full_recipe(r),
            ).pack(side=tk.LEFT, padx=(0, 6))

            tk.Button(
                btn_row, text="Save to collection", font=FONT_SMALL,
                bg=BTN_COLOR, relief=tk.RAISED, bd=2,
                command=lambda r=recipe: self._save_recipe(r),
            ).pack(side=tk.LEFT, padx=(0, 6))

            tk.Button(
                btn_row, text="Making this!", font=FONT_SMALL,
                bg=BTN_COLOR, relief=tk.RAISED, bd=2,
                command=lambda r=recipe: self._log_and_save(r),
            ).pack(side=tk.LEFT)

        # Bottom nav
        bottom = tk.Frame(scroll_frame, bg=BG_COLOR)
        bottom.pack(fill=tk.X, pady=(10, 0))

        self._make_button(bottom, "Start over", self.show_welcome, width=12).pack(side=tk.LEFT)

    def _show_full_recipe(self, recipe):
        self._clear()

        self._make_label(
            self.main_frame, recipe["name"], font=FONT_TITLE
        ).pack(anchor="w", pady=(0, 5))

        meta = (
            f"{recipe.get('cuisine', '')} · "
            f"{recipe.get('difficulty', '')} · "
            f"{recipe.get('total_time_minutes', '?')} min total"
        )
        self._make_label(self.main_frame, meta, font=FONT_SMALL).pack(anchor="w", pady=(0, 10))

        # Scrollable body
        canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
        body = tk.Frame(canvas, bg=BG_COLOR)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120 or event.delta), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Ingredients
        tk.Label(body, text="Ingredients", font=FONT_BOLD, bg=BG_COLOR, anchor="w").pack(
            fill=tk.X, pady=(0, 4)
        )
        for ing in recipe.get("ingredients", []):
            clean = ing.rstrip("*")
            pantry = " (pantry)" if ing.endswith("*") else ""
            tk.Label(
                body, text=f"  • {clean}{pantry}", font=FONT_SMALL, bg=BG_COLOR, anchor="w"
            ).pack(fill=tk.X)

        # Equipment
        equipment = recipe.get("equipment", [])
        if equipment:
            tk.Label(body, text="Equipment", font=FONT_BOLD, bg=BG_COLOR, anchor="w").pack(
                fill=tk.X, pady=(10, 4)
            )
            tk.Label(
                body, text="  " + ", ".join(equipment), font=FONT_SMALL, bg=BG_COLOR, anchor="w"
            ).pack(fill=tk.X)

        # Instructions
        tk.Label(body, text="Instructions", font=FONT_BOLD, bg=BG_COLOR, anchor="w").pack(
            fill=tk.X, pady=(10, 4)
        )
        for j, step in enumerate(recipe.get("instructions", []), 1):
            tk.Label(
                body, text=f"  {j}. {step}", font=FONT_SMALL, bg=BG_COLOR,
                anchor="w", wraplength=600, justify=tk.LEFT,
            ).pack(fill=tk.X, pady=2)

        # Technique notes
        if recipe.get("technique_notes"):
            tk.Label(body, text="Technique notes", font=FONT_BOLD, bg=BG_COLOR, anchor="w").pack(
                fill=tk.X, pady=(10, 4)
            )
            tk.Label(
                body, text=recipe["technique_notes"], font=FONT_SMALL, bg=BG_COLOR,
                anchor="w", wraplength=600, justify=tk.LEFT,
            ).pack(fill=tk.X)

        # Bottom buttons
        btn_row = tk.Frame(body, bg=BG_COLOR)
        btn_row.pack(fill=tk.X, pady=(16, 0))

        self._make_button(btn_row, "← Back", lambda: self.show_results(self.result), width=10).pack(
            side=tk.LEFT
        )
        self._make_button(
            btn_row, "Save to collection", lambda: self._save_recipe(recipe), width=18
        ).pack(side=tk.LEFT, padx=6)
        self._make_button(
            btn_row, "Making this!", lambda: self._log_and_save(recipe), width=14
        ).pack(side=tk.LEFT)

    def _save_recipe(self, recipe):
        if self.history_manager.save_recipe(recipe):
            messagebox.showinfo("Saved", f"'{recipe['name']}' saved to your collection.")
        else:
            messagebox.showerror("Error", "Failed to save recipe.")

    def _log_and_save(self, recipe):
        self.history_manager.save_recipe(recipe)
        cuisine = recipe.get("cuisine", "Unknown")
        self.history_manager.log_meal(recipe["name"], cuisine)
        messagebox.showinfo("Logged", f"'{recipe['name']}' saved and logged. Enjoy!")

    # ── History screen ───────────────────────────────────────────────

    def show_history(self):
        self._clear()

        self._make_label(
            self.main_frame, "Saved recipes", font=FONT_HEADING
        ).pack(anchor="w", pady=(0, 10))

        recipes = self.history_manager.get_recipe_history(limit=25)

        if not recipes:
            self._make_label(
                self.main_frame, "No saved recipes yet. Generate some first!", font=FONT
            ).pack(anchor="w", pady=20)
        else:
            canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
            scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
            list_frame = tk.Frame(canvas, bg=BG_COLOR)

            list_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=list_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10))
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))

            def _on_mousewheel(event):
                canvas.yview_scroll(-1 * (event.delta // 120 or event.delta), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            for recipe in recipes:
                row = tk.Frame(list_frame, bg="#EEEEEE", relief=tk.RIDGE, bd=1)
                row.pack(fill=tk.X, pady=3, padx=4)

                times = recipe.get("times_made", 0)
                times_str = f" (made {times}x)" if times > 0 else ""
                saved = recipe.get("saved_at", "")[:10]

                tk.Label(
                    row,
                    text=f"{recipe['name']}  —  {recipe.get('cuisine', '?')}{times_str}",
                    font=FONT, bg="#EEEEEE", anchor="w",
                ).pack(side=tk.LEFT, padx=8, pady=6)

                tk.Label(
                    row, text=saved, font=FONT_SMALL, bg="#EEEEEE", fg="#777777"
                ).pack(side=tk.RIGHT, padx=8)

        # Nav
        nav = tk.Frame(self.main_frame, bg=BG_COLOR)
        nav.pack(fill=tk.X, side=tk.BOTTOM)

        self._make_button(nav, "← Back", self.show_welcome, width=10).pack(side=tk.LEFT)

    # ── Recent meals screen ──────────────────────────────────────────

    def show_recent_meals(self):
        self._clear()

        self._make_label(
            self.main_frame, "Recent meals (last 14 days)", font=FONT_HEADING
        ).pack(anchor="w", pady=(0, 10))

        meals = self.history_manager.get_recent_meals()

        if not meals:
            self._make_label(
                self.main_frame, "No meals logged in the last 14 days.", font=FONT
            ).pack(anchor="w", pady=20)
        else:
            for meal in reversed(meals):
                row = tk.Frame(self.main_frame, bg="#EEEEEE", relief=tk.RIDGE, bd=1)
                row.pack(fill=tk.X, pady=3)

                date_str = meal.get("date", "")[:10]
                tk.Label(
                    row, text=date_str, font=FONT_SMALL, bg="#EEEEEE", fg="#555555", width=12
                ).pack(side=tk.LEFT, padx=(8, 4), pady=6)

                tk.Label(
                    row,
                    text=f"{meal.get('recipe_name', '?')}  ({meal.get('cuisine_type', '?')})",
                    font=FONT, bg="#EEEEEE", anchor="w",
                ).pack(side=tk.LEFT, padx=4, pady=6)

            # Cuisine summary
            cuisines = list(set(m.get("cuisine_type", "?") for m in meals))
            self._make_label(
                self.main_frame,
                f"Cuisines to avoid for variety: {', '.join(cuisines)}",
                font=FONT_SMALL,
            ).pack(anchor="w", pady=(10, 0))

        # Nav
        nav = tk.Frame(self.main_frame, bg=BG_COLOR)
        nav.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self._make_button(nav, "← Back", self.show_welcome, width=10).pack(side=tk.LEFT)


def main():
    root = tk.Tk()
    DinnerAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

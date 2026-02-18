"""
Pressberg Kitchen Recipe Assistant - Retro Mac GUI
A nostalgic journey back to Mac OS 8/9 aesthetics
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from typing import Optional, Dict, List
from .recipe_generator import RecipeGenerator
from .history_manager import HistoryManager


# ============================================================
# RETRO MAC COLOR PALETTE & STYLING
# ============================================================

class RetroMacStyle:
    """Mac OS 8/9 inspired color palette and styling constants"""

    # Colors
    WINDOW_BG = "#DDDDDD"
    BUTTON_BG = "#CCCCCC"
    BUTTON_ACTIVE = "#BBBBBB"
    TEXT_BG = "#FFFFFF"
    TEXT_FG = "#000000"
    LABEL_FG = "#000000"
    ACCENT = "#000099"
    BORDER = "#888888"
    HIGHLIGHT = "#FFFFCC"

    # Fonts
    FONT_MAIN = ("Geneva", 12)
    FONT_BOLD = ("Geneva", 12, "bold")
    FONT_TITLE = ("Geneva", 16, "bold")
    FONT_SMALL = ("Geneva", 10)
    FONT_MONO = ("Monaco", 11)


# ============================================================
# MAIN APPLICATION
# ============================================================

class DinnerAssistantApp:
    """Main application controller"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pressberg Kitchen Recipe Assistant")
        self.root.geometry("700x650")
        self.root.configure(bg=RetroMacStyle.WINDOW_BG)
        self.root.minsize(600, 500)

        # Main container - all screens go here
        self.container = tk.Frame(self.root, bg=RetroMacStyle.WINDOW_BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Initialize managers
        self.history_manager = HistoryManager()
        self.generator: Optional[RecipeGenerator] = None

        # State
        self.ingredients: List[str] = []
        self.constraints: Optional[str] = None

        # Show welcome screen
        self._show_welcome()

    def _clear_screen(self):
        """Clear all widgets from container"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def _show_welcome(self):
        """Show the welcome screen"""
        self._clear_screen()

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Logo
        logo_text = """
+=============================+
|    PRESSBERG KITCHEN        |
|      Recipe Assistant       |
+=============================+
        """
        tk.Label(
            frame,
            text=logo_text,
            font=RetroMacStyle.FONT_MONO,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.ACCENT,
            justify=tk.CENTER
        ).pack(pady=(40, 20))

        tk.Label(
            frame,
            text="What would you like to do?",
            font=RetroMacStyle.FONT_BOLD,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(pady=(10, 20))

        # Buttons
        btn_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        btn_frame.pack(pady=20)

        self._make_button(btn_frame, "Generate Recipes", self._show_ingredients, width=25).pack(pady=8)
        self._make_button(btn_frame, "View Recipe History", self._show_history, width=25).pack(pady=8)
        self._make_button(btn_frame, "Recent Meals", self._show_recent, width=25).pack(pady=8)

        # Version
        tk.Label(
            frame,
            text="Version 1.0 - Matt & Jennifer Pressberg",
            font=RetroMacStyle.FONT_SMALL,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.BORDER
        ).pack(side=tk.BOTTOM, pady=10)

    def _show_ingredients(self):
        """Show ingredient input screen"""
        self._clear_screen()
        self.ingredients = []

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            frame,
            text="What's in Your Kitchen?",
            font=RetroMacStyle.FONT_TITLE,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(pady=(10, 5))

        tk.Label(
            frame,
            text="Click ingredients below or type your own.\nPantry staples (garlic, soy sauce, etc.) are assumed.",
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(pady=(0, 15))

        # Quick ingredients
        quick_frame = tk.LabelFrame(
            frame,
            text=" Quick Add ",
            font=RetroMacStyle.FONT_BOLD,
            bg=RetroMacStyle.WINDOW_BG,
            relief=tk.GROOVE,
            borderwidth=2
        )
        quick_frame.pack(fill=tk.X, pady=10, padx=10)

        quick_ingredients = [
            ["Chicken", "Ground Turkey", "Ground Beef", "Salmon", "Shrimp", "Steak"],
            ["Spinach", "Kale", "Broccoli", "Mushrooms", "Bell Peppers", "Tomatoes"],
            ["Rice", "Pasta", "Potatoes", "Beans", "Tofu", "Eggs"],
        ]

        for row in quick_ingredients:
            row_frame = tk.Frame(quick_frame, bg=RetroMacStyle.WINDOW_BG)
            row_frame.pack(fill=tk.X, padx=10, pady=3)
            for ingredient in row:
                btn = tk.Button(
                    row_frame,
                    text=ingredient,
                    font=RetroMacStyle.FONT_SMALL,
                    bg=RetroMacStyle.BUTTON_BG,
                    relief=tk.RAISED,
                    borderwidth=1,
                    padx=6,
                    pady=2,
                    command=lambda i=ingredient: self._add_ingredient(i)
                )
                btn.pack(side=tk.LEFT, padx=2)

        # Manual entry
        entry_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        entry_frame.pack(fill=tk.X, pady=15, padx=10)

        tk.Label(
            entry_frame,
            text="Or type ingredients:",
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(anchor=tk.W)

        entry_row = tk.Frame(entry_frame, bg=RetroMacStyle.WINDOW_BG)
        entry_row.pack(fill=tk.X, pady=5)

        self.ingredient_entry = tk.Entry(
            entry_row,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.TEXT_BG,
            relief=tk.SUNKEN,
            borderwidth=2,
            width=40
        )
        self.ingredient_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ingredient_entry.bind("<Return>", lambda e: self._add_from_entry())

        self._make_button(entry_row, "Add", self._add_from_entry, width=8).pack(side=tk.LEFT)

        # Selected ingredients
        selected_frame = tk.LabelFrame(
            frame,
            text=" Selected Ingredients ",
            font=RetroMacStyle.FONT_BOLD,
            bg=RetroMacStyle.WINDOW_BG,
            relief=tk.GROOVE,
            borderwidth=2
        )
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.selected_listbox = tk.Listbox(
            selected_frame,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.TEXT_BG,
            relief=tk.SUNKEN,
            borderwidth=2,
            height=6
        )
        self.selected_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))

        self._make_button(selected_frame, "Remove Selected", self._remove_ingredient, width=15).pack(pady=(0, 10))

        # Navigation
        nav_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        nav_frame.pack(fill=tk.X, pady=15)

        self._make_button(nav_frame, "< Back", self._show_welcome, width=10).pack(side=tk.LEFT)
        self._make_button(nav_frame, "Next >", self._on_ingredients_next, width=10).pack(side=tk.RIGHT)

    def _add_ingredient(self, ingredient: str):
        """Add ingredient to list"""
        ingredient = ingredient.strip().lower()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            self.selected_listbox.insert(tk.END, f"  {ingredient.title()}")

    def _add_from_entry(self):
        """Add from text entry"""
        text = self.ingredient_entry.get().strip()
        if text:
            for item in text.split(","):
                self._add_ingredient(item)
            self.ingredient_entry.delete(0, tk.END)

    def _remove_ingredient(self):
        """Remove selected ingredient"""
        selection = self.selected_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_listbox.delete(index)
            del self.ingredients[index]

    def _on_ingredients_next(self):
        """Validate and proceed"""
        if not self.ingredients:
            messagebox.showwarning("No Ingredients", "Please add at least one ingredient.")
            return
        self._show_constraints()

    def _show_constraints(self):
        """Show constraints screen"""
        self._clear_screen()

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            frame,
            text="Any Constraints Tonight?",
            font=RetroMacStyle.FONT_TITLE,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(pady=(10, 20))

        # Variables
        self.weeknight = tk.BooleanVar(value=True)
        self.quick = tk.BooleanVar(value=False)
        self.instant_pot = tk.BooleanVar(value=False)
        self.cast_iron = tk.BooleanVar(value=False)
        self.wok = tk.BooleanVar(value=False)
        self.air_fryer = tk.BooleanVar(value=False)
        self.no_pasta = tk.BooleanVar(value=False)
        self.extra_spicy = tk.BooleanVar(value=False)
        self.custom_var = tk.StringVar()

        # Time
        time_frame = tk.LabelFrame(frame, text=" Time ", font=RetroMacStyle.FONT_BOLD,
                                    bg=RetroMacStyle.WINDOW_BG, relief=tk.GROOVE, borderwidth=2)
        time_frame.pack(fill=tk.X, pady=10, padx=10)

        tk.Checkbutton(time_frame, text="Weeknight mode (45 min active or less)",
                       variable=self.weeknight, font=RetroMacStyle.FONT_MAIN,
                       bg=RetroMacStyle.WINDOW_BG).pack(anchor=tk.W, padx=20, pady=2)
        tk.Checkbutton(time_frame, text="Quick meal (under 30 min total)",
                       variable=self.quick, font=RetroMacStyle.FONT_MAIN,
                       bg=RetroMacStyle.WINDOW_BG).pack(anchor=tk.W, padx=20, pady=2)

        # Equipment
        equip_frame = tk.LabelFrame(frame, text=" Prefer Equipment ", font=RetroMacStyle.FONT_BOLD,
                                     bg=RetroMacStyle.WINDOW_BG, relief=tk.GROOVE, borderwidth=2)
        equip_frame.pack(fill=tk.X, pady=10, padx=10)

        equip_row = tk.Frame(equip_frame, bg=RetroMacStyle.WINDOW_BG)
        equip_row.pack(fill=tk.X, padx=20, pady=5)

        for text, var in [("Instant Pot", self.instant_pot), ("Cast Iron", self.cast_iron),
                          ("Wok", self.wok), ("Air Fryer", self.air_fryer)]:
            tk.Checkbutton(equip_row, text=text, variable=var, font=RetroMacStyle.FONT_MAIN,
                           bg=RetroMacStyle.WINDOW_BG).pack(side=tk.LEFT, padx=10)

        # Other
        other_frame = tk.LabelFrame(frame, text=" Other ", font=RetroMacStyle.FONT_BOLD,
                                     bg=RetroMacStyle.WINDOW_BG, relief=tk.GROOVE, borderwidth=2)
        other_frame.pack(fill=tk.X, pady=10, padx=10)

        other_row = tk.Frame(other_frame, bg=RetroMacStyle.WINDOW_BG)
        other_row.pack(fill=tk.X, padx=20, pady=5)

        tk.Checkbutton(other_row, text="No pasta tonight", variable=self.no_pasta,
                       font=RetroMacStyle.FONT_MAIN, bg=RetroMacStyle.WINDOW_BG).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(other_row, text="Extra spicy!", variable=self.extra_spicy,
                       font=RetroMacStyle.FONT_MAIN, bg=RetroMacStyle.WINDOW_BG).pack(side=tk.LEFT, padx=10)

        custom_row = tk.Frame(other_frame, bg=RetroMacStyle.WINDOW_BG)
        custom_row.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(custom_row, text="Custom:", font=RetroMacStyle.FONT_MAIN,
                 bg=RetroMacStyle.WINDOW_BG).pack(side=tk.LEFT)
        tk.Entry(custom_row, textvariable=self.custom_var, font=RetroMacStyle.FONT_MAIN,
                 bg=RetroMacStyle.TEXT_BG, width=30).pack(side=tk.LEFT, padx=10)

        # Navigation
        nav_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        nav_frame.pack(fill=tk.X, pady=20)

        self._make_button(nav_frame, "< Back", self._show_ingredients, width=10).pack(side=tk.LEFT)
        self._make_button(nav_frame, "Generate Recipes >", self._on_constraints_next, width=18).pack(side=tk.RIGHT)

    def _get_constraints(self) -> Optional[str]:
        """Build constraint string"""
        constraints = []
        if self.weeknight.get():
            constraints.append("weeknight (45 min active max)")
        if self.quick.get():
            constraints.append("under 30 minutes total")
        if self.instant_pot.get():
            constraints.append("use Instant Pot")
        if self.cast_iron.get():
            constraints.append("use cast iron skillet")
        if self.wok.get():
            constraints.append("use wok")
        if self.air_fryer.get():
            constraints.append("use air fryer")
        if self.no_pasta.get():
            constraints.append("no pasta")
        if self.extra_spicy.get():
            constraints.append("make it extra spicy")
        custom = self.custom_var.get().strip()
        if custom:
            constraints.append(custom)
        return ", ".join(constraints) if constraints else None

    def _on_constraints_next(self):
        """Generate recipes"""
        self.constraints = self._get_constraints()
        self._show_loading()

    def _show_loading(self):
        """Show loading screen"""
        self._clear_screen()

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True)

        center = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            center,
            text="""
+==============================+
|                              |
|     Consulting Chef...       |
|                              |
+==============================+
            """,
            font=RetroMacStyle.FONT_MONO,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.ACCENT
        ).pack(pady=20)

        self.loading_label = tk.Label(
            center,
            text="Generating recipes...",
            font=RetroMacStyle.FONT_BOLD,
            bg=RetroMacStyle.WINDOW_BG
        )
        self.loading_label.pack()

        self.progress_label = tk.Label(
            center,
            text="[..........]\n",
            font=RetroMacStyle.FONT_MONO,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.ACCENT
        )
        self.progress_label.pack()

        # Start animation and generation
        self.loading_dots = 0
        self.loading_active = True
        self._animate_loading()
        self._generate_recipes()

    def _animate_loading(self):
        """Animate loading indicator"""
        if not self.loading_active:
            return
        self.loading_dots = (self.loading_dots + 1) % 11
        bar = "#" * self.loading_dots + "." * (10 - self.loading_dots)
        self.progress_label.config(text=f"[{bar}]")
        self.root.after(200, self._animate_loading)

    def _generate_recipes(self):
        """Generate recipes in background"""
        def generate():
            try:
                if not self.generator:
                    self.generator = RecipeGenerator()

                recent_cuisines = self.history_manager.get_recent_cuisines()
                results = self.generator.generate_recipes(
                    ingredients=self.ingredients,
                    recent_cuisines=recent_cuisines,
                    constraints=self.constraints
                )
                self.root.after(0, lambda: self._show_results(results))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _show_error(self, error: str):
        """Show error and return to ingredients"""
        self.loading_active = False
        messagebox.showerror("Error", f"Failed to generate recipes:\n{error}\n\nPlease try again.")
        self._show_ingredients()

    def _show_results(self, results: Dict):
        """Show results screen"""
        self.loading_active = False
        self._clear_screen()

        recipes = results.get('recipes', [])
        recommendation = results.get('recommendation', {})
        rec_index = recommendation.get('recipe_index', 0)

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            frame,
            text="Tonight's Options",
            font=RetroMacStyle.FONT_TITLE,
            bg=RetroMacStyle.WINDOW_BG
        ).pack(pady=(10, 10))

        # Recommendation
        if recipes and recommendation.get('reasoning'):
            rec_frame = tk.LabelFrame(frame, text=" Recommended ", font=RetroMacStyle.FONT_BOLD,
                                       bg=RetroMacStyle.WINDOW_BG, relief=tk.GROOVE, borderwidth=2)
            rec_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            tk.Label(rec_frame, text=f"* {recipes[rec_index]['name']}", font=RetroMacStyle.FONT_BOLD,
                     bg=RetroMacStyle.WINDOW_BG, fg=RetroMacStyle.ACCENT).pack(anchor=tk.W, padx=10, pady=(5, 0))
            tk.Label(rec_frame, text=recommendation['reasoning'], font=RetroMacStyle.FONT_SMALL,
                     bg=RetroMacStyle.WINDOW_BG, wraplength=600).pack(anchor=tk.W, padx=10, pady=(0, 5))

        # Scrollable recipe list
        canvas = tk.Canvas(frame, bg=RetroMacStyle.WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=RetroMacStyle.WINDOW_BG)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor=tk.NW, width=640)
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, recipe in enumerate(recipes):
            self._create_recipe_card(scrollable, recipe, i, i == rec_index, results)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Navigation
        nav_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        nav_frame.pack(fill=tk.X, pady=10)

        self._make_button(nav_frame, "< Try Again", self._show_ingredients, width=12).pack(side=tk.LEFT)
        self._make_button(nav_frame, "Home", self._show_welcome, width=10).pack(side=tk.RIGHT)

    def _create_recipe_card(self, parent, recipe: Dict, index: int, is_rec: bool, results: Dict):
        """Create recipe card"""
        card = tk.LabelFrame(
            parent,
            text="",
            bg=RetroMacStyle.WINDOW_BG,
            relief=tk.GROOVE,
            borderwidth=2
        )
        card.pack(fill=tk.X, pady=8, padx=5)

        # Header
        prefix = "* " if is_rec else f"{index + 1}. "
        color = RetroMacStyle.ACCENT if is_rec else RetroMacStyle.LABEL_FG

        tk.Label(card, text=f"{prefix}{recipe['name']}", font=RetroMacStyle.FONT_BOLD,
                 bg=RetroMacStyle.WINDOW_BG, fg=color).pack(anchor=tk.W, padx=10, pady=(10, 0))

        meta = f"{recipe.get('cuisine', '?')} | {recipe.get('difficulty', '?')} | {recipe.get('active_time_minutes', '?')} min active"
        tk.Label(card, text=meta, font=RetroMacStyle.FONT_SMALL,
                 bg=RetroMacStyle.WINDOW_BG).pack(anchor=tk.W, padx=10)

        if recipe.get('description'):
            tk.Label(card, text=recipe['description'], font=RetroMacStyle.FONT_MAIN,
                     bg=RetroMacStyle.WINDOW_BG, wraplength=580).pack(anchor=tk.W, padx=10, pady=5)

        # Buttons
        btn_frame = tk.Frame(card, bg=RetroMacStyle.WINDOW_BG)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self._make_button(btn_frame, "View Full", lambda r=recipe: self._show_full_recipe(r), width=10).pack(side=tk.LEFT, padx=2)
        self._make_button(btn_frame, "Save", lambda r=recipe: self._save_recipe(r, False), width=8).pack(side=tk.LEFT, padx=2)
        self._make_button(btn_frame, "Make Tonight!", lambda r=recipe: self._save_recipe(r, True), width=12).pack(side=tk.LEFT, padx=2)

    def _show_full_recipe(self, recipe: Dict):
        """Show full recipe popup"""
        popup = tk.Toplevel(self.root)
        popup.title(recipe['name'])
        popup.geometry("600x700")
        popup.configure(bg=RetroMacStyle.WINDOW_BG)
        popup.transient(self.root)
        popup.grab_set()

        frame = tk.Frame(popup, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text=recipe['name'], font=RetroMacStyle.FONT_TITLE,
                 bg=RetroMacStyle.WINDOW_BG).pack(anchor=tk.W)
        tk.Label(frame, text=f"{recipe.get('cuisine', '')} | {recipe.get('difficulty', '')} | {recipe.get('total_time_minutes', '?')} min",
                 font=RetroMacStyle.FONT_MAIN, bg=RetroMacStyle.WINDOW_BG).pack(anchor=tk.W, pady=(0, 15))

        text = scrolledtext.ScrolledText(frame, font=RetroMacStyle.FONT_MONO,
                                          bg=RetroMacStyle.TEXT_BG, wrap=tk.WORD, height=25)
        text.pack(fill=tk.BOTH, expand=True)

        content = "INGREDIENTS\n" + "-" * 40 + "\n"
        for ing in recipe.get('ingredients', []):
            marker = " (pantry)" if ing.endswith('*') else ""
            content += f"* {ing.rstrip('*')}{marker}\n"

        content += f"\nEQUIPMENT: {', '.join(recipe.get('equipment', []))}\n"
        content += "\n\nINSTRUCTIONS\n" + "-" * 40 + "\n"
        for i, step in enumerate(recipe.get('instructions', []), 1):
            content += f"\n{i}. {step}\n"

        if recipe.get('technique_notes'):
            content += f"\n\nTECHNIQUE NOTES\n" + "-" * 40 + f"\n{recipe['technique_notes']}"

        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

        self._make_button(frame, "Close", popup.destroy, width=10).pack(pady=15)

    def _save_recipe(self, recipe: Dict, make_tonight: bool):
        """Save recipe"""
        if self.history_manager.save_recipe(recipe):
            if make_tonight:
                self.history_manager.log_meal(recipe['name'], recipe.get('cuisine', 'Unknown'))
                messagebox.showinfo("Saved & Logged!", f"'{recipe['name']}' saved and logged for tonight!\n\nEnjoy your meal!")
            else:
                messagebox.showinfo("Saved!", f"'{recipe['name']}' saved to your collection.")
        else:
            messagebox.showerror("Error", "Failed to save recipe.")

    def _show_history(self):
        """Show history screen"""
        self._clear_screen()

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Recipe History", font=RetroMacStyle.FONT_TITLE,
                 bg=RetroMacStyle.WINDOW_BG).pack(pady=(10, 20))

        recipes = self.history_manager.get_recipe_history(limit=30)

        if not recipes:
            tk.Label(frame, text="No saved recipes yet.\nGenerate some recipes to get started!",
                     font=RetroMacStyle.FONT_MAIN, bg=RetroMacStyle.WINDOW_BG).pack(pady=50)
        else:
            list_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
            list_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.history_listbox = tk.Listbox(list_frame, font=RetroMacStyle.FONT_MAIN,
                                               bg=RetroMacStyle.TEXT_BG, height=15,
                                               yscrollcommand=scrollbar.set)
            self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.history_listbox.yview)

            self.history_recipes = recipes
            for r in recipes:
                times = r.get('times_made', 0)
                times_str = f" (x{times})" if times > 0 else ""
                self.history_listbox.insert(tk.END, f"{r['name']} [{r.get('cuisine', '?')}]{times_str}")

            btn_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
            btn_frame.pack(fill=tk.X, pady=10)
            self._make_button(btn_frame, "Mark as Made", self._mark_history_made, width=15).pack(side=tk.LEFT)

        nav_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        nav_frame.pack(fill=tk.X, pady=10)
        self._make_button(nav_frame, "< Back", self._show_welcome, width=10).pack(side=tk.LEFT)

    def _mark_history_made(self):
        """Mark selected recipe as made"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Recipe", "Please select a recipe first.")
            return
        recipe = self.history_recipes[selection[0]]
        self.history_manager.log_meal(recipe['name'], recipe.get('cuisine', 'Unknown'))
        messagebox.showinfo("Logged!", f"'{recipe['name']}' logged to recent meals.")

    def _show_recent(self):
        """Show recent meals"""
        self._clear_screen()

        frame = tk.Frame(self.container, bg=RetroMacStyle.WINDOW_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Recent Meals (Last 14 Days)", font=RetroMacStyle.FONT_TITLE,
                 bg=RetroMacStyle.WINDOW_BG).pack(pady=(10, 20))

        meals = self.history_manager.get_recent_meals()

        if not meals:
            tk.Label(frame, text="No meals logged recently.\nMark recipes as 'Made Tonight' to track them here.",
                     font=RetroMacStyle.FONT_MAIN, bg=RetroMacStyle.WINDOW_BG).pack(pady=50)
        else:
            list_frame = tk.LabelFrame(frame, text=" Recent Meals ", font=RetroMacStyle.FONT_BOLD,
                                        bg=RetroMacStyle.WINDOW_BG, relief=tk.GROOVE, borderwidth=2)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

            for meal in reversed(meals):
                row = tk.Frame(list_frame, bg=RetroMacStyle.WINDOW_BG)
                row.pack(fill=tk.X, padx=10, pady=3)
                tk.Label(row, text=meal.get('date', '')[:10], font=RetroMacStyle.FONT_BOLD,
                         bg=RetroMacStyle.WINDOW_BG, width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row, text=meal.get('recipe_name', '?'), font=RetroMacStyle.FONT_MAIN,
                         bg=RetroMacStyle.WINDOW_BG).pack(side=tk.LEFT)
                tk.Label(row, text=f"  [{meal.get('cuisine_type', '?')}]", font=RetroMacStyle.FONT_SMALL,
                         bg=RetroMacStyle.WINDOW_BG, fg=RetroMacStyle.BORDER).pack(side=tk.LEFT)

            cuisines = list(set(m.get('cuisine_type', '?') for m in meals))
            tk.Label(frame, text=f"\nCuisines to avoid for variety: {', '.join(cuisines)}",
                     font=RetroMacStyle.FONT_SMALL, bg=RetroMacStyle.WINDOW_BG).pack(pady=10)

        nav_frame = tk.Frame(frame, bg=RetroMacStyle.WINDOW_BG)
        nav_frame.pack(fill=tk.X, pady=10)
        self._make_button(nav_frame, "< Back", self._show_welcome, width=10).pack(side=tk.LEFT)

    def _make_button(self, parent, text: str, command, width: int = 12) -> tk.Button:
        """Create styled button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.BUTTON_BG,
            activebackground=RetroMacStyle.BUTTON_ACTIVE,
            relief=tk.RAISED,
            borderwidth=2,
            width=width,
            cursor="hand2"
        )
        return btn

    def run(self):
        """Start app"""
        self.root.mainloop()


def main():
    """Entry point"""
    app = DinnerAssistantApp()
    app.run()


if __name__ == '__main__':
    main()

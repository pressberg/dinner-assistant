"""
Pressberg Kitchen Recipe Assistant - Retro Mac GUI
A nostalgic journey back to Mac OS 8/9 aesthetics
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
    ACCENT = "#000099"  # Classic Mac blue
    BORDER = "#888888"
    HIGHLIGHT = "#FFFFCC"  # Selection yellow

    # Fonts (using system fonts that evoke the era)
    if tk.TkVersion >= 8.6:
        FONT_MAIN = ("Geneva", 12)
        FONT_BOLD = ("Geneva", 12, "bold")
        FONT_TITLE = ("Geneva", 16, "bold")
        FONT_SMALL = ("Geneva", 10)
        FONT_MONO = ("Monaco", 11)
    else:
        FONT_MAIN = ("Helvetica", 12)
        FONT_BOLD = ("Helvetica", 12, "bold")
        FONT_TITLE = ("Helvetica", 16, "bold")
        FONT_SMALL = ("Helvetica", 10)
        FONT_MONO = ("Courier", 11)


# ============================================================
# RETRO STYLED WIDGETS
# ============================================================

class RetroButton(tk.Button):
    """A button styled like Mac OS 8/9"""

    def __init__(self, parent, text, command=None, width=12, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.BUTTON_BG,
            activebackground=RetroMacStyle.BUTTON_ACTIVE,
            relief=tk.RAISED,
            borderwidth=2,
            width=width,
            cursor="hand2",
            **kwargs
        )

        # Bind hover effects
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _on_hover(self, event):
        self.config(bg=RetroMacStyle.BUTTON_ACTIVE)

    def _on_leave(self, event):
        self.config(bg=RetroMacStyle.BUTTON_BG)


class RetroIngredientButton(tk.Button):
    """Ingredient quick-add button with retro styling"""

    def __init__(self, parent, ingredient: str, callback, **kwargs):
        super().__init__(
            parent,
            text=ingredient.title(),
            command=lambda: callback(ingredient),
            font=RetroMacStyle.FONT_SMALL,
            bg=RetroMacStyle.BUTTON_BG,
            activebackground=RetroMacStyle.BUTTON_ACTIVE,
            relief=tk.RAISED,
            borderwidth=1,
            padx=8,
            pady=4,
            cursor="hand2",
            **kwargs
        )

        self.bind("<Enter>", lambda e: self.config(bg=RetroMacStyle.HIGHLIGHT))
        self.bind("<Leave>", lambda e: self.config(bg=RetroMacStyle.BUTTON_BG))


class RetroLabel(tk.Label):
    """Label with retro Mac styling"""

    def __init__(self, parent, text, bold=False, title=False, **kwargs):
        font = RetroMacStyle.FONT_TITLE if title else (
            RetroMacStyle.FONT_BOLD if bold else RetroMacStyle.FONT_MAIN
        )
        super().__init__(
            parent,
            text=text,
            font=font,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.LABEL_FG,
            **kwargs
        )


class RetroEntry(tk.Entry):
    """Text entry with retro Mac styling"""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.TEXT_BG,
            fg=RetroMacStyle.TEXT_FG,
            relief=tk.SUNKEN,
            borderwidth=2,
            insertbackground=RetroMacStyle.TEXT_FG,
            **kwargs
        )


class RetroText(scrolledtext.ScrolledText):
    """Multi-line text area with retro styling"""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=RetroMacStyle.FONT_MONO,
            bg=RetroMacStyle.TEXT_BG,
            fg=RetroMacStyle.TEXT_FG,
            relief=tk.SUNKEN,
            borderwidth=2,
            insertbackground=RetroMacStyle.TEXT_FG,
            wrap=tk.WORD,
            **kwargs
        )


class RetroFrame(tk.Frame):
    """Frame with retro Mac styling"""

    def __init__(self, parent, raised=False, **kwargs):
        super().__init__(
            parent,
            bg=RetroMacStyle.WINDOW_BG,
            relief=tk.RAISED if raised else tk.FLAT,
            borderwidth=2 if raised else 0,
            **kwargs
        )


class RetroCheckbutton(tk.Checkbutton):
    """Checkbutton with retro Mac styling"""

    def __init__(self, parent, text, variable, **kwargs):
        super().__init__(
            parent,
            text=text,
            variable=variable,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.WINDOW_BG,
            activebackground=RetroMacStyle.WINDOW_BG,
            selectcolor=RetroMacStyle.TEXT_BG,
            **kwargs
        )


# ============================================================
# WIZARD SCREENS
# ============================================================

class WelcomeScreen(RetroFrame):
    """Welcome screen with retro Mac flair"""

    def __init__(self, parent, on_start, on_history, on_recent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title with retro Mac icon aesthetic
        title_frame = RetroFrame(self)
        title_frame.pack(pady=(20, 30))

        # ASCII-style logo
        logo_text = """
   +=============================+
   |    PRESSBERG KITCHEN        |
   |      Recipe Assistant       |
   +=============================+
        """

        logo_label = tk.Label(
            title_frame,
            text=logo_text,
            font=RetroMacStyle.FONT_MONO,
            bg=RetroMacStyle.WINDOW_BG,
            fg=RetroMacStyle.ACCENT,
            justify=tk.CENTER
        )
        logo_label.pack()

        RetroLabel(
            title_frame,
            text="What would you like to do?",
            bold=True
        ).pack(pady=(10, 0))

        # Main action buttons
        button_frame = RetroFrame(self)
        button_frame.pack(pady=20)

        RetroButton(
            button_frame,
            text="Generate Recipes",
            command=on_start,
            width=25
        ).pack(pady=8)

        RetroButton(
            button_frame,
            text="View Recipe History",
            command=on_history,
            width=25
        ).pack(pady=8)

        RetroButton(
            button_frame,
            text="Recent Meals",
            command=on_recent,
            width=25
        ).pack(pady=8)

        # Version info
        RetroLabel(
            self,
            text="Version 1.0 - Matt & Jennifer Pressberg",
            bold=False
        ).pack(side=tk.BOTTOM, pady=10)


class IngredientsScreen(RetroFrame):
    """Ingredient input screen with quick-add buttons"""

    QUICK_INGREDIENTS = [
        # Proteins
        ["Chicken", "Ground Turkey", "Ground Beef", "Salmon", "Shrimp", "Steak"],
        # Vegetables
        ["Spinach", "Kale", "Broccoli", "Mushrooms", "Bell Peppers", "Tomatoes"],
        # Starches & Other
        ["Rice", "Pasta", "Potatoes", "Beans", "Tofu", "Eggs"],
    ]

    def __init__(self, parent, on_next, on_back):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.ingredients: List[str] = []

        # Title
        RetroLabel(self, text="What's in Your Kitchen?", title=True).pack(pady=(10, 20))

        # Instructions
        RetroLabel(
            self,
            text="Click ingredients below or type your own.\nPantry staples (garlic, soy sauce, etc.) are assumed.",
        ).pack(pady=(0, 15))

        # Quick ingredient buttons
        quick_frame = RetroFrame(self, raised=True)
        quick_frame.pack(fill=tk.X, pady=10, padx=10)

        RetroLabel(quick_frame, text="Quick Add:", bold=True).pack(anchor=tk.W, padx=10, pady=(10, 5))

        for row_ingredients in self.QUICK_INGREDIENTS:
            row_frame = RetroFrame(quick_frame)
            row_frame.pack(fill=tk.X, padx=10, pady=3)
            for ingredient in row_ingredients:
                RetroIngredientButton(
                    row_frame,
                    ingredient,
                    self._add_ingredient
                ).pack(side=tk.LEFT, padx=2)

        # Spacer
        tk.Frame(quick_frame, height=10, bg=RetroMacStyle.WINDOW_BG).pack()

        # Manual entry
        entry_frame = RetroFrame(self)
        entry_frame.pack(fill=tk.X, pady=15, padx=10)

        RetroLabel(entry_frame, text="Or type ingredients:").pack(anchor=tk.W)

        self.entry = RetroEntry(entry_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        self.entry.bind("<Return>", lambda e: self._add_from_entry())

        RetroButton(entry_frame, text="Add", command=self._add_from_entry, width=8).pack(side=tk.LEFT)

        # Selected ingredients display
        selected_frame = RetroFrame(self, raised=True)
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        RetroLabel(selected_frame, text="Selected Ingredients:", bold=True).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.selected_listbox = tk.Listbox(
            selected_frame,
            font=RetroMacStyle.FONT_MAIN,
            bg=RetroMacStyle.TEXT_BG,
            fg=RetroMacStyle.TEXT_FG,
            relief=tk.SUNKEN,
            borderwidth=2,
            selectmode=tk.SINGLE,
            height=6
        )
        self.selected_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        remove_btn = RetroButton(selected_frame, text="Remove Selected", command=self._remove_selected, width=15)
        remove_btn.pack(pady=(0, 10))

        # Navigation buttons
        nav_frame = RetroFrame(self)
        nav_frame.pack(fill=tk.X, pady=20)

        RetroButton(nav_frame, text="< Back", command=on_back, width=10).pack(side=tk.LEFT, padx=10)

        self.next_btn = RetroButton(nav_frame, text="Next >", command=lambda: on_next(self.ingredients), width=10)
        self.next_btn.pack(side=tk.RIGHT, padx=10)

    def _add_ingredient(self, ingredient: str):
        """Add an ingredient to the list"""
        ingredient = ingredient.strip().lower()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            self.selected_listbox.insert(tk.END, f"  {ingredient.title()}")

    def _add_from_entry(self):
        """Add ingredients from the text entry"""
        text = self.entry.get().strip()
        if text:
            # Handle comma-separated entries
            for item in text.split(","):
                self._add_ingredient(item)
            self.entry.delete(0, tk.END)

    def _remove_selected(self):
        """Remove the selected ingredient"""
        selection = self.selected_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_listbox.delete(index)
            del self.ingredients[index]


class ConstraintsScreen(RetroFrame):
    """Constraints selection with checkboxes"""

    def __init__(self, parent, on_next, on_back):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Constraint variables
        self.weeknight = tk.BooleanVar(value=True)
        self.quick = tk.BooleanVar(value=False)
        self.instant_pot = tk.BooleanVar(value=False)
        self.cast_iron = tk.BooleanVar(value=False)
        self.wok = tk.BooleanVar(value=False)
        self.air_fryer = tk.BooleanVar(value=False)
        self.no_pasta = tk.BooleanVar(value=False)
        self.extra_spicy = tk.BooleanVar(value=False)
        self.custom_constraint = tk.StringVar()

        # Title
        RetroLabel(self, text="Any Constraints Tonight?", title=True).pack(pady=(10, 20))

        # Time constraints
        time_frame = RetroFrame(self, raised=True)
        time_frame.pack(fill=tk.X, pady=10, padx=10)

        RetroLabel(time_frame, text="Time:", bold=True).pack(anchor=tk.W, padx=10, pady=(10, 5))

        RetroCheckbutton(time_frame, "Weeknight mode (45 min active or less)", self.weeknight).pack(anchor=tk.W, padx=20)
        RetroCheckbutton(time_frame, "Quick meal (under 30 min total)", self.quick).pack(anchor=tk.W, padx=20)

        tk.Frame(time_frame, height=10, bg=RetroMacStyle.WINDOW_BG).pack()

        # Equipment preferences
        equip_frame = RetroFrame(self, raised=True)
        equip_frame.pack(fill=tk.X, pady=10, padx=10)

        RetroLabel(equip_frame, text="Prefer Equipment:", bold=True).pack(anchor=tk.W, padx=10, pady=(10, 5))

        equip_row1 = RetroFrame(equip_frame)
        equip_row1.pack(fill=tk.X, padx=20)
        RetroCheckbutton(equip_row1, "Instant Pot", self.instant_pot).pack(side=tk.LEFT, padx=(0, 20))
        RetroCheckbutton(equip_row1, "Cast Iron", self.cast_iron).pack(side=tk.LEFT, padx=(0, 20))
        RetroCheckbutton(equip_row1, "Wok", self.wok).pack(side=tk.LEFT)

        equip_row2 = RetroFrame(equip_frame)
        equip_row2.pack(fill=tk.X, padx=20)
        RetroCheckbutton(equip_row2, "Air Fryer", self.air_fryer).pack(side=tk.LEFT)

        tk.Frame(equip_frame, height=10, bg=RetroMacStyle.WINDOW_BG).pack()

        # Other constraints
        other_frame = RetroFrame(self, raised=True)
        other_frame.pack(fill=tk.X, pady=10, padx=10)

        RetroLabel(other_frame, text="Other:", bold=True).pack(anchor=tk.W, padx=10, pady=(10, 5))

        other_row = RetroFrame(other_frame)
        other_row.pack(fill=tk.X, padx=20)
        RetroCheckbutton(other_row, "No pasta tonight", self.no_pasta).pack(side=tk.LEFT, padx=(0, 20))
        RetroCheckbutton(other_row, "Extra spicy!", self.extra_spicy).pack(side=tk.LEFT)

        tk.Frame(other_frame, height=5, bg=RetroMacStyle.WINDOW_BG).pack()

        custom_row = RetroFrame(other_frame)
        custom_row.pack(fill=tk.X, padx=20, pady=(5, 10))
        RetroLabel(custom_row, text="Custom:").pack(side=tk.LEFT)
        RetroEntry(custom_row, textvariable=self.custom_constraint, width=35).pack(side=tk.LEFT, padx=10)

        # Navigation
        nav_frame = RetroFrame(self)
        nav_frame.pack(fill=tk.X, pady=20)

        RetroButton(nav_frame, text="< Back", command=on_back, width=10).pack(side=tk.LEFT, padx=10)
        RetroButton(nav_frame, text="Generate Recipes >", command=lambda: on_next(self._get_constraints()), width=18).pack(side=tk.RIGHT, padx=10)

    def _get_constraints(self) -> str:
        """Build constraint string from selections"""
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

        custom = self.custom_constraint.get().strip()
        if custom:
            constraints.append(custom)

        return ", ".join(constraints) if constraints else None


class LoadingScreen(RetroFrame):
    """Retro loading screen with animated dots"""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.dots = 0
        self.running = True

        # Center content
        center_frame = RetroFrame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Retro "loading" aesthetic
        self.loading_art = tk.Label(
            center_frame,
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
        )
        self.loading_art.pack(pady=20)

        self.status_label = RetroLabel(center_frame, text="Generating recipes", bold=True)
        self.status_label.pack()

        self.dots_label = RetroLabel(center_frame, text="")
        self.dots_label.pack()

        # Progress bar (retro style)
        self.progress_frame = RetroFrame(center_frame)
        self.progress_frame.pack(pady=20)

        self.progress_blocks = []
        for i in range(10):
            block = tk.Label(
                self.progress_frame,
                text=".",
                font=RetroMacStyle.FONT_MONO,
                bg=RetroMacStyle.WINDOW_BG,
                fg=RetroMacStyle.BORDER
            )
            block.pack(side=tk.LEFT)
            self.progress_blocks.append(block)

        self._animate()

    def _animate(self):
        """Animate the loading indicator"""
        if not self.running:
            return

        # Animate dots
        self.dots = (self.dots + 1) % 4
        self.dots_label.config(text="." * self.dots)

        # Animate progress blocks
        for i, block in enumerate(self.progress_blocks):
            if i <= (self.dots * 2 + 1) % 10:
                block.config(text="#", fg=RetroMacStyle.ACCENT)
            else:
                block.config(text=".", fg=RetroMacStyle.BORDER)

        self.after(300, self._animate)

    def stop(self):
        """Stop animation"""
        self.running = False


class ResultsScreen(RetroFrame):
    """Recipe results display"""

    def __init__(self, parent, results: Dict, on_save, on_back, on_home):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.results = results
        self.recipes = results.get('recipes', [])
        self.recommendation = results.get('recommendation', {})
        self.on_save = on_save

        # Title
        RetroLabel(self, text="Tonight's Options", title=True).pack(pady=(10, 15))

        # Recommendation banner
        rec_index = self.recommendation.get('recipe_index', 0)
        if self.recipes and self.recommendation.get('reasoning'):
            rec_name = self.recipes[rec_index]['name']
            rec_frame = RetroFrame(self, raised=True)
            rec_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            RetroLabel(
                rec_frame,
                text=f"* Recommended: {rec_name}",
                bold=True
            ).pack(anchor=tk.W, padx=10, pady=(10, 0))

            RetroLabel(
                rec_frame,
                text=self.recommendation['reasoning']
            ).pack(anchor=tk.W, padx=10, pady=(0, 10))

        # Recipe cards in a scrollable frame
        canvas = tk.Canvas(self, bg=RetroMacStyle.WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = RetroFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, recipe in enumerate(self.recipes):
            self._create_recipe_card(scrollable_frame, recipe, i, i == rec_index)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Navigation
        nav_frame = RetroFrame(self)
        nav_frame.pack(fill=tk.X, pady=15)

        RetroButton(nav_frame, text="< Try Again", command=on_back, width=12).pack(side=tk.LEFT, padx=10)
        RetroButton(nav_frame, text="Home", command=on_home, width=10).pack(side=tk.RIGHT, padx=10)

    def _create_recipe_card(self, parent, recipe: Dict, index: int, is_recommended: bool):
        """Create a recipe card widget"""

        # Card frame
        card = RetroFrame(parent, raised=True)
        card.pack(fill=tk.X, pady=8, padx=5)

        # Header
        header_frame = RetroFrame(card)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        prefix = "* " if is_recommended else f"{index + 1}. "
        title_color = RetroMacStyle.ACCENT if is_recommended else RetroMacStyle.LABEL_FG

        title_label = tk.Label(
            header_frame,
            text=f"{prefix}{recipe['name']}",
            font=RetroMacStyle.FONT_BOLD,
            bg=RetroMacStyle.WINDOW_BG,
            fg=title_color
        )
        title_label.pack(anchor=tk.W)

        # Metadata
        meta_text = f"{recipe.get('cuisine', '?')} | {recipe.get('difficulty', '?')} | {recipe.get('active_time_minutes', '?')} min active"
        RetroLabel(header_frame, text=meta_text).pack(anchor=tk.W)

        # Description
        if recipe.get('description'):
            RetroLabel(card, text=recipe['description']).pack(anchor=tk.W, padx=10, pady=5)

        # Why this works
        if recipe.get('why_this_works'):
            why_label = tk.Label(
                card,
                text=f"-> {recipe['why_this_works']}",
                font=RetroMacStyle.FONT_SMALL,
                bg=RetroMacStyle.WINDOW_BG,
                fg=RetroMacStyle.BORDER
            )
            why_label.pack(anchor=tk.W, padx=10)

        # Action buttons
        btn_frame = RetroFrame(card)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        RetroButton(
            btn_frame,
            text="View Full",
            command=lambda r=recipe: self._show_full_recipe(r),
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))

        RetroButton(
            btn_frame,
            text="Save",
            command=lambda r=recipe: self.on_save(r, make_tonight=False),
            width=10
        ).pack(side=tk.LEFT, padx=5)

        RetroButton(
            btn_frame,
            text="Make Tonight!",
            command=lambda r=recipe: self.on_save(r, make_tonight=True),
            width=14
        ).pack(side=tk.LEFT, padx=5)

    def _show_full_recipe(self, recipe: Dict):
        """Show full recipe in a popup window"""
        popup = tk.Toplevel(self)
        popup.title(recipe['name'])
        popup.geometry("600x700")
        popup.configure(bg=RetroMacStyle.WINDOW_BG)

        # Make it modal
        popup.transient(self)
        popup.grab_set()

        # Content
        content = RetroFrame(popup)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        RetroLabel(content, text=recipe['name'], title=True).pack(anchor=tk.W)
        RetroLabel(content, text=f"{recipe.get('cuisine', '')} | {recipe.get('difficulty', '')} | {recipe.get('total_time_minutes', '?')} min total").pack(anchor=tk.W, pady=(0, 15))

        # Scrollable text area
        text_area = RetroText(content, height=30, width=65)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Build recipe text
        recipe_text = "INGREDIENTS\n"
        recipe_text += "-" * 40 + "\n"
        for ing in recipe.get('ingredients', []):
            marker = "(pantry)" if ing.endswith('*') else ""
            clean = ing.rstrip('*')
            recipe_text += f"* {clean} {marker}\n"

        recipe_text += f"\nEQUIPMENT: {', '.join(recipe.get('equipment', []))}\n"

        recipe_text += "\n\nINSTRUCTIONS\n"
        recipe_text += "-" * 40 + "\n"
        for i, step in enumerate(recipe.get('instructions', []), 1):
            recipe_text += f"\n{i}. {step}\n"

        if recipe.get('technique_notes'):
            recipe_text += f"\n\nTECHNIQUE NOTES\n"
            recipe_text += "-" * 40 + "\n"
            recipe_text += recipe['technique_notes']

        text_area.insert(tk.END, recipe_text)
        text_area.config(state=tk.DISABLED)

        # Close button
        RetroButton(content, text="Close", command=popup.destroy, width=10).pack(pady=15)


class HistoryScreen(RetroFrame):
    """Recipe history browser"""

    def __init__(self, parent, history_manager: HistoryManager, on_back):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.history_manager = history_manager

        # Title
        RetroLabel(self, text="Recipe History", title=True).pack(pady=(10, 20))

        # Recipe list
        recipes = history_manager.get_recipe_history(limit=30)

        if not recipes:
            RetroLabel(self, text="No saved recipes yet.\nGenerate some recipes to get started!").pack(pady=50)
        else:
            # Listbox with scrollbar
            list_frame = RetroFrame(self)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.recipe_listbox = tk.Listbox(
                list_frame,
                font=RetroMacStyle.FONT_MAIN,
                bg=RetroMacStyle.TEXT_BG,
                fg=RetroMacStyle.TEXT_FG,
                relief=tk.SUNKEN,
                borderwidth=2,
                selectmode=tk.SINGLE,
                height=15,
                yscrollcommand=scrollbar.set
            )
            self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.recipe_listbox.yview)

            for recipe in recipes:
                times = recipe.get('times_made', 0)
                times_str = f" (x{times})" if times > 0 else ""
                self.recipe_listbox.insert(
                    tk.END,
                    f"{recipe['name']} [{recipe.get('cuisine', '?')}]{times_str}"
                )

            # Action buttons
            action_frame = RetroFrame(self)
            action_frame.pack(fill=tk.X, pady=15)

            RetroButton(
                action_frame,
                text="Mark as Made",
                command=lambda: self._mark_made(recipes),
                width=15
            ).pack(side=tk.LEFT, padx=5)

        # Back button
        nav_frame = RetroFrame(self)
        nav_frame.pack(fill=tk.X, pady=10)
        RetroButton(nav_frame, text="< Back", command=on_back, width=10).pack(side=tk.LEFT, padx=10)

    def _mark_made(self, recipes):
        """Mark selected recipe as made"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Recipe", "Please select a recipe first.")
            return

        recipe = recipes[selection[0]]
        self.history_manager.log_meal(recipe['name'], recipe.get('cuisine', 'Unknown'))
        messagebox.showinfo("Logged!", f"'{recipe['name']}' logged to recent meals.")


class RecentMealsScreen(RetroFrame):
    """Recent meals display"""

    def __init__(self, parent, history_manager: HistoryManager, on_back):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        RetroLabel(self, text="Recent Meals (Last 14 Days)", title=True).pack(pady=(10, 20))

        meals = history_manager.get_recent_meals()

        if not meals:
            RetroLabel(self, text="No meals logged recently.\nMark recipes as 'Made Tonight' to track them here.").pack(pady=50)
        else:
            # Meals list
            list_frame = RetroFrame(self, raised=True)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

            for meal in reversed(meals):
                meal_frame = RetroFrame(list_frame)
                meal_frame.pack(fill=tk.X, padx=10, pady=5)

                date_str = meal.get('date', '')[:10]
                RetroLabel(meal_frame, text=date_str, bold=True).pack(side=tk.LEFT)
                RetroLabel(meal_frame, text=f"  {meal.get('recipe_name', '?')}").pack(side=tk.LEFT)
                RetroLabel(meal_frame, text=f"  [{meal.get('cuisine_type', '?')}]").pack(side=tk.LEFT)

            # Cuisine summary
            cuisines = list(set(m.get('cuisine_type', '?') for m in meals))
            RetroLabel(
                self,
                text=f"\nCuisines to avoid for variety: {', '.join(cuisines)}"
            ).pack(pady=10)

        # Back button
        nav_frame = RetroFrame(self)
        nav_frame.pack(fill=tk.X, pady=10)
        RetroButton(nav_frame, text="< Back", command=on_back, width=10).pack(side=tk.LEFT, padx=10)


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

        # Prevent resizing below minimum
        self.root.minsize(600, 500)

        # Initialize managers
        self.history_manager = HistoryManager()
        self.generator: Optional[RecipeGenerator] = None

        # State
        self.current_screen: Optional[tk.Frame] = None
        self.ingredients: List[str] = []
        self.constraints: Optional[str] = None

        # Show welcome screen
        self._show_welcome()

    def _clear_screen(self):
        """Clear current screen"""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def _show_welcome(self):
        """Show the welcome screen"""
        self._clear_screen()
        self.current_screen = WelcomeScreen(
            self.root,
            on_start=self._show_ingredients,
            on_history=self._show_history,
            on_recent=self._show_recent
        )

    def _show_ingredients(self):
        """Show ingredient input screen"""
        self._clear_screen()
        self.current_screen = IngredientsScreen(
            self.root,
            on_next=self._on_ingredients_next,
            on_back=self._show_welcome
        )

    def _on_ingredients_next(self, ingredients: List[str]):
        """Handle ingredients submission"""
        if not ingredients:
            messagebox.showwarning("No Ingredients", "Please add at least one ingredient.")
            return
        self.ingredients = ingredients
        self._show_constraints()

    def _show_constraints(self):
        """Show constraints screen"""
        self._clear_screen()
        self.current_screen = ConstraintsScreen(
            self.root,
            on_next=self._on_constraints_next,
            on_back=self._show_ingredients
        )

    def _on_constraints_next(self, constraints: Optional[str]):
        """Handle constraints and generate recipes"""
        self.constraints = constraints
        self._generate_recipes()

    def _generate_recipes(self):
        """Generate recipes in background thread"""
        self._clear_screen()
        loading = LoadingScreen(self.root)
        self.current_screen = loading

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

                # Update UI on main thread
                self.root.after(0, lambda: self._show_results(results, loading))

            except Exception as e:
                self.root.after(0, lambda: self._handle_generation_error(e, loading))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _show_results(self, results: Dict, loading: LoadingScreen):
        """Show results screen"""
        loading.stop()
        self._clear_screen()
        self.current_screen = ResultsScreen(
            self.root,
            results=results,
            on_save=self._save_recipe,
            on_back=self._show_ingredients,
            on_home=self._show_welcome
        )

    def _handle_generation_error(self, error: Exception, loading: LoadingScreen):
        """Handle recipe generation error"""
        loading.stop()
        self._clear_screen()
        messagebox.showerror("Error", f"Failed to generate recipes:\n{str(error)}\n\nPlease try again.")
        self._show_ingredients()

    def _save_recipe(self, recipe: Dict, make_tonight: bool):
        """Save a recipe and optionally log as made"""
        if self.history_manager.save_recipe(recipe):
            if make_tonight:
                self.history_manager.log_meal(recipe['name'], recipe.get('cuisine', 'Unknown'))
                messagebox.showinfo(
                    "Saved & Logged!",
                    f"'{recipe['name']}' saved to your collection and logged for tonight.\n\nEnjoy your meal!"
                )
            else:
                messagebox.showinfo(
                    "Saved!",
                    f"'{recipe['name']}' saved to your collection."
                )
        else:
            messagebox.showerror("Error", "Failed to save recipe.")

    def _show_history(self):
        """Show recipe history"""
        self._clear_screen()
        self.current_screen = HistoryScreen(
            self.root,
            self.history_manager,
            on_back=self._show_welcome
        )

    def _show_recent(self):
        """Show recent meals"""
        self._clear_screen()
        self.current_screen = RecentMealsScreen(
            self.root,
            self.history_manager,
            on_back=self._show_welcome
        )

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Entry point for GUI application"""
    app = DinnerAssistantApp()
    app.run()


if __name__ == '__main__':
    main()

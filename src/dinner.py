"""Main CLI entry point for Pressberg Kitchen Recipe Assistant"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from typing import List, Optional
from .recipe_generator import RecipeGenerator
from .history_manager import HistoryManager
from .config import RECIPE_PREVIEW_STEPS

console = Console()


@click.command()
@click.option('--history', is_flag=True, help='View saved recipe history')
@click.option('--recent', is_flag=True, help='View recent meals (last 14 days)')
@click.option('--made', is_flag=True, help='Mark a saved recipe as made')
@click.option('--favorites', is_flag=True, help='View frequently-made recipes')
@click.option('--search', help='Search saved recipes by name')
def main(history: bool, recent: bool, made: bool, favorites: bool, search: str):
    """
    Pressberg Kitchen Recipe Assistant

    Generate personalized dinner recipes based on available ingredients.
    """

    history_manager = HistoryManager()

    if history:
        show_recipe_history(history_manager)
    elif recent:
        show_recent_meals(history_manager)
    elif made:
        mark_recipe_made_interactive(history_manager)
    elif favorites:
        show_favorites(history_manager)
    elif search:
        search_recipes(history_manager, search)
    else:
        generate_recipes_flow(history_manager)


def generate_recipes_flow(history_manager: HistoryManager):
    """Main flow for generating recipes"""

    console.print(Panel.fit(
        "[bold cyan]Pressberg Kitchen Recipe Assistant[/bold cyan]\n"
        "[dim]Let's figure out what to make for dinner.[/dim]",
        border_style="cyan"
    ))

    # Get ingredients
    console.print("\n[yellow]What ingredients do you have?[/yellow]")
    console.print("[dim]Comma-separated. Pantry staples (garlic, soy sauce, etc.) are assumed.[/dim]")
    ingredients_input = Prompt.ask("Ingredients")

    if not ingredients_input.strip():
        console.print("[red]No ingredients provided. Exiting.[/red]")
        return

    ingredients = [i.strip() for i in ingredients_input.split(',') if i.strip()]

    # Get constraints
    console.print("\n[yellow]Any constraints?[/yellow]")
    console.print("[dim]e.g., 'weeknight', 'under 30 min', 'use instant pot', 'no pasta'[/dim]")
    constraints = Prompt.ask("Constraints", default="").strip() or None

    # Get recent cuisines for variety
    recent_cuisines = history_manager.get_recent_cuisines()
    if recent_cuisines:
        unique_recent = list(set(recent_cuisines))
        console.print(f"\n[dim]Recently cooked: {', '.join(unique_recent)} (will suggest alternatives)[/dim]")

    # Generate recipes
    console.print("\n[cyan]Generating recipe options...[/cyan]\n")

    try:
        generator = RecipeGenerator()
        result = generator.generate_recipes(
            ingredients=ingredients,
            recent_cuisines=recent_cuisines,
            constraints=constraints
        )

        display_recipes(result)
        post_generation_flow(history_manager, result)

    except FileNotFoundError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
    except ValueError as e:
        console.print(f"[red]Error parsing recipes: {e}[/red]")
        console.print("[dim]Try running again—occasionally the AI response needs a retry.[/dim]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


def display_recipes(result: dict):
    """Display generated recipes with formatting"""

    recipes = result.get('recipes', [])
    recommendation = result.get('recommendation', {})

    if not recipes:
        console.print("[red]No recipes generated. Try different ingredients.[/red]")
        return

    recommended_index = recommendation.get('recipe_index', 0)

    for i, recipe in enumerate(recipes):
        is_recommended = (i == recommended_index)

        # Header
        prefix = "🌟 " if is_recommended else ""
        style = "bold green" if is_recommended else "bold cyan"
        console.print(f"\n[{style}]{prefix}Option {i + 1}: {recipe['name']}[/{style}]")

        # Metadata line
        difficulty_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red"}
        diff_color = difficulty_colors.get(recipe.get('difficulty', 'Medium'), 'white')

        console.print(
            f"[dim]{recipe.get('cuisine', 'Fusion')}[/dim] · "
            f"[{diff_color}]{recipe.get('difficulty', 'Medium')}[/{diff_color}] · "
            f"[dim]{recipe.get('active_time_minutes', '?')} min active / "
            f"{recipe.get('total_time_minutes', '?')} min total[/dim]"
        )

        # Description
        if recipe.get('description'):
            console.print(f"\n{recipe['description']}")

        # Why this works (preference match)
        if recipe.get('why_this_works'):
            console.print(f"[dim italic]↳ {recipe['why_this_works']}[/dim italic]")

        # Ingredients
        console.print("\n[yellow]Ingredients:[/yellow]")
        for ing in recipe.get('ingredients', []):
            if ing.endswith('*'):
                console.print(f"  [dim]{ing[:-1]} (pantry)[/dim]")
            else:
                console.print(f"  {ing}")

        # Equipment
        equipment = recipe.get('equipment', [])
        if equipment:
            console.print(f"\n[yellow]Equipment:[/yellow] {', '.join(equipment)}")

        # Instructions preview
        instructions = recipe.get('instructions', [])
        if instructions:
            console.print(f"\n[yellow]Instructions:[/yellow]")
            for j, step in enumerate(instructions[:RECIPE_PREVIEW_STEPS], 1):
                console.print(f"  {j}. {step}")
            remaining = len(instructions) - RECIPE_PREVIEW_STEPS
            if remaining > 0:
                console.print(f"  [dim]...and {remaining} more step{'s' if remaining > 1 else ''}[/dim]")

        # Technique notes
        if recipe.get('technique_notes'):
            console.print(f"\n[yellow]💡 Technique:[/yellow] {recipe['technique_notes']}")

        console.print("\n" + "─" * 60)

    # Recommendation callout
    if recommendation.get('reasoning'):
        rec_name = recipes[recommended_index]['name'] if recipes else "Unknown"
        console.print(f"\n[bold green]🌟 Recommended:[/bold green] {rec_name}")
        console.print(f"[dim]{recommendation['reasoning']}[/dim]")


def post_generation_flow(history_manager: HistoryManager, result: dict):
    """Handle post-generation actions: save, mark as made"""

    recipes = result.get('recipes', [])
    if not recipes:
        return

    console.print()

    if not Confirm.ask("[yellow]Save a recipe to your collection?[/yellow]", default=False):
        console.print("[dim]No problem. Enjoy your dinner![/dim]")
        return

    # Select recipe
    console.print("\n[yellow]Which recipe?[/yellow]")
    for i, recipe in enumerate(recipes, 1):
        console.print(f"  {i}. {recipe['name']}")

    choice = Prompt.ask(
        "Enter number",
        choices=[str(i) for i in range(1, len(recipes) + 1)],
        default="1"
    )
    chosen_recipe = recipes[int(choice) - 1]

    # Save it
    if history_manager.save_recipe(chosen_recipe):
        console.print(f"[green]✓ Saved '{chosen_recipe['name']}' to your collection.[/green]")
    else:
        console.print("[red]Failed to save recipe.[/red]")
        return

    # Ask if making tonight
    if Confirm.ask("\n[yellow]Making this tonight?[/yellow]", default=True):
        cuisine = chosen_recipe.get('cuisine', 'Unknown')
        history_manager.log_meal(chosen_recipe['name'], cuisine)
        console.print(f"[green]✓ Logged to recent meals. Enjoy![/green]")

    # Show full instructions option
    if Confirm.ask("\n[yellow]View full instructions?[/yellow]", default=False):
        show_full_recipe(chosen_recipe)


def show_full_recipe(recipe: dict):
    """Display complete recipe with all instructions"""

    console.print(f"\n[bold cyan]{'═' * 60}[/bold cyan]")
    console.print(f"[bold cyan]{recipe['name']}[/bold cyan]")
    console.print(f"[bold cyan]{'═' * 60}[/bold cyan]")

    # Full ingredients
    console.print("\n[bold yellow]INGREDIENTS[/bold yellow]")
    for ing in recipe.get('ingredients', []):
        marker = "[dim](pantry)[/dim]" if ing.endswith('*') else ""
        clean_ing = ing.rstrip('*')
        console.print(f"  • {clean_ing} {marker}")

    # Full instructions
    console.print("\n[bold yellow]INSTRUCTIONS[/bold yellow]")
    for i, step in enumerate(recipe.get('instructions', []), 1):
        console.print(f"\n  [bold]{i}.[/bold] {step}")

    # Technique notes
    if recipe.get('technique_notes'):
        console.print(f"\n[bold yellow]TECHNIQUE NOTES[/bold yellow]")
        console.print(f"  {recipe['technique_notes']}")

    console.print()


def mark_recipe_made_interactive(history_manager: HistoryManager):
    """Interactive flow to mark a saved recipe as made"""

    recipes = history_manager.get_recipe_history(limit=20)

    if not recipes:
        console.print("[yellow]No saved recipes yet. Generate some first![/yellow]")
        return

    console.print("\n[bold cyan]Recent Saved Recipes[/bold cyan]\n")
    for i, recipe in enumerate(recipes, 1):
        times = recipe.get('times_made', 0)
        times_str = f" [dim](made {times}x)[/dim]" if times > 0 else ""
        console.print(f"  {i}. {recipe['name']} [{recipe.get('cuisine', '?')}]{times_str}")

    console.print(f"  0. [dim]Cancel[/dim]")

    choice = Prompt.ask(
        "\nWhich recipe did you make?",
        choices=[str(i) for i in range(0, len(recipes) + 1)],
        default="0"
    )

    if choice == "0":
        console.print("[dim]Cancelled.[/dim]")
        return

    recipe = recipes[int(choice) - 1]
    cuisine = recipe.get('cuisine', 'Unknown')

    history_manager.log_meal(recipe['name'], cuisine)
    console.print(f"[green]✓ Logged '{recipe['name']}' ({cuisine}) to recent meals.[/green]")


def show_recipe_history(history_manager: HistoryManager):
    """Display saved recipe history in a table"""

    recipes = history_manager.get_recipe_history(limit=25)

    if not recipes:
        console.print("[yellow]No saved recipes yet.[/yellow]")
        return

    table = Table(title="Saved Recipes", show_lines=False)
    table.add_column("#", style="dim", width=4)
    table.add_column("Recipe", style="cyan", min_width=30)
    table.add_column("Cuisine", style="yellow", width=15)
    table.add_column("Difficulty", width=10)
    table.add_column("Made", style="green", width=6)
    table.add_column("Saved", style="dim", width=12)

    for i, recipe in enumerate(recipes, 1):
        diff = recipe.get('difficulty', '?')
        diff_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red"}
        diff_styled = f"[{diff_colors.get(diff, 'white')}]{diff}[/{diff_colors.get(diff, 'white')}]"

        times_made = recipe.get('times_made', 0)
        times_str = str(times_made) if times_made > 0 else "-"

        saved_date = recipe.get('saved_at', '')[:10]

        table.add_row(
            str(i),
            recipe.get('name', 'Unknown'),
            recipe.get('cuisine', '?'),
            diff_styled,
            times_str,
            saved_date
        )

    console.print()
    console.print(table)


def show_recent_meals(history_manager: HistoryManager):
    """Display recent meals log"""

    meals = history_manager.get_recent_meals()

    if not meals:
        console.print("[yellow]No meals logged in the last 14 days.[/yellow]")
        return

    table = Table(title="Recent Meals (Last 14 Days)")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Recipe", style="green", min_width=30)
    table.add_column("Cuisine", style="yellow", width=15)

    for meal in reversed(meals):
        date_str = meal.get('date', '')[:10]
        table.add_row(
            date_str,
            meal.get('recipe_name', 'Unknown'),
            meal.get('cuisine_type', '?')
        )

    console.print()
    console.print(table)

    # Show cuisine summary
    cuisines = [m.get('cuisine_type', '?') for m in meals]
    unique = list(set(cuisines))
    console.print(f"\n[dim]Cuisines to avoid for variety: {', '.join(unique)}[/dim]")


def show_favorites(history_manager: HistoryManager):
    """Display frequently-made recipes"""

    favorites = history_manager.get_favorites(min_times_made=2)

    if not favorites:
        console.print("[yellow]No favorites yet. Make a recipe at least twice to see it here.[/yellow]")
        return

    # Sort by times made
    favorites.sort(key=lambda r: r.get('times_made', 0), reverse=True)

    console.print("\n[bold cyan]⭐ Household Favorites[/bold cyan]\n")
    for recipe in favorites[:10]:
        times = recipe.get('times_made', 0)
        console.print(f"  {recipe['name']} [dim]({recipe.get('cuisine', '?')})[/dim] — made {times}x")


def search_recipes(history_manager: HistoryManager, search_term: str):
    """Search saved recipes by name"""

    matches = history_manager.find_recipe_by_name(search_term)

    if not matches:
        console.print(f"[yellow]No recipes found matching '{search_term}'[/yellow]")
        return

    console.print(f"\n[bold cyan]Search Results for '{search_term}'[/bold cyan]\n")
    for recipe in matches:
        times = recipe.get('times_made', 0)
        times_str = f" (made {times}x)" if times > 0 else ""
        console.print(f"  • {recipe['name']} [{recipe.get('cuisine', '?')}]{times_str}")
        if recipe.get('description'):
            console.print(f"    [dim]{recipe['description']}[/dim]")


if __name__ == '__main__':
    main()

"""
Onboarding flow for new users.
Collects name, API key, and allergies, then runs preference interview.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .config import USER_DATA_DIR

console = Console()

CONFIG_FILE = USER_DATA_DIR / "config.json"
ENV_FILE = USER_DATA_DIR / ".env"


def is_onboarding_complete() -> bool:
    """Check if onboarding has been completed."""
    try:
        config = load_user_config()
        return config.get("onboarding_complete", False)
    except (json.JSONDecodeError, OSError):
        return False


def load_user_config() -> dict:
    """Load and return config.json contents."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_config(config: dict):
    """Save config dict to config.json."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def collect_name() -> str:
    """Prompt user for their name."""
    console.print(
        Panel.fit(
            "[bold cyan]Welcome to Pressberg Kitchen![/bold cyan]\n"
            "[dim]Let's get you set up.[/dim]",
            border_style="cyan",
        )
    )
    name = Prompt.ask("\n[yellow]What's your name?[/yellow]")
    return name.strip()


def collect_api_key() -> str:
    """Prompt for Anthropic API key, validate it, and save to .env."""
    console.print(
        "\n[yellow]This app uses Claude to generate recipes.[/yellow]\n"
        "You'll need an Anthropic API key.\n"
        "If you don't have one, sign up at: [bold cyan]https://console.anthropic.com[/bold cyan]\n"
        "Then go to Settings > API Keys and create one."
    )

    while True:
        key = Prompt.ask("\n[yellow]Paste your API key[/yellow]").strip()

        if not key:
            console.print("[red]No key entered. Try again.[/red]")
            continue

        if not key.startswith("sk-ant-"):
            console.print("[red]That doesn't look like a valid Anthropic API key (should start with sk-ant-).[/red]")
            continue

        # Validate by making a minimal API call
        console.print("[dim]Validating key...[/dim]")
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=key)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            console.print("[green]Key is valid.[/green]")
        except Exception:
            console.print("[red]That key didn't work. Check it and try again.[/red]")
            continue

        # Save to ~/.dinner-assistant/.env
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"ANTHROPIC_API_KEY={key}\n")

        return key


COMMON_ALLERGIES = [
    ("Tree nuts", "almonds, walnuts, pecans, etc."),
    ("Peanuts", ""),
    ("Shellfish", "shrimp, crab, lobster"),
    ("Fish", ""),
    ("Dairy/Lactose", ""),
    ("Eggs", ""),
    ("Gluten/Wheat", ""),
    ("Soy", ""),
]


def collect_allergies() -> dict:
    """Prompt user for food allergies. Returns dict with allergy info."""
    console.print(
        "\n[yellow]Before we get to the fun stuff, let's talk safety.[/yellow]\n"
        "Do you have any food allergies or ingredients you must [bold red]NEVER[/bold red] eat?"
    )

    # Show numbered options
    console.print()
    for i, (name, examples) in enumerate(COMMON_ALLERGIES, 1):
        label = f"  {i}. {name}"
        if examples:
            label += f" [dim]({examples})[/dim]"
        console.print(label)
    console.print(f"  {len(COMMON_ALLERGIES) + 1}. [dim]None of these[/dim]")

    # Multi-select
    console.print(
        "\n[dim]Enter numbers separated by commas (e.g. 1,3), "
        f"or {len(COMMON_ALLERGIES) + 1} for none.[/dim]"
    )
    selection = Prompt.ask("[yellow]Your selections[/yellow]")

    items = []
    none_option = str(len(COMMON_ALLERGIES) + 1)

    for num in selection.split(","):
        num = num.strip()
        if num == none_option:
            items = []
            break
        try:
            idx = int(num) - 1
            if 0 <= idx < len(COMMON_ALLERGIES):
                items.append(COMMON_ALLERGIES[idx][0].lower())
        except ValueError:
            continue

    # Free text for additional allergies
    console.print()
    extra = Prompt.ask(
        "[yellow]Any other allergies or ingredients to always avoid?[/yellow]",
        default="",
    ).strip()

    if extra:
        for item in extra.split(","):
            item = item.strip().lower()
            if item and item not in items:
                items.append(item)

    return {"items": items}


def confirm_allergies(allergies: list) -> bool:
    """Show allergy list and get confirmation. Returns True if confirmed."""
    if not allergies:
        return True

    console.print("\n[bold yellow]I'll NEVER suggest recipes containing:[/bold yellow]")
    for item in allergies:
        console.print(f"  [red]- {item}[/red]")

    return Confirm.ask("\n[yellow]Is this correct?[/yellow]", default=True)


def run_onboarding() -> bool:
    """Main onboarding flow. Returns True if successful."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Collect name
    name = collect_name()

    # Collect API key
    api_key = collect_api_key()

    # Collect allergies (loop until confirmed)
    while True:
        allergy_info = collect_allergies()
        if confirm_allergies(allergy_info["items"]):
            break

    # Save config
    config = load_user_config()
    now = datetime.now(timezone.utc).isoformat()
    config.update(
        {
            "user_name": name,
            "allergies": {
                "items": allergy_info["items"],
                "confirmed": True,
                "confirmed_at": now,
            },
            "created_at": config.get("created_at", now),
            "onboarding_complete": False,
        }
    )
    save_user_config(config)

    console.print(f"\n[green]All set, {name}. Let's cook.[/green]\n")
    return True

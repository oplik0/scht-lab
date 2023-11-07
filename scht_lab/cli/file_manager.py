from pathlib import Path
import json
from typing import TYPE_CHECKING

from rich import print
from typer import Context, Typer

from scht_lab.cli.flows import flows_app
from typer import get_app_dir


if TYPE_CHECKING:
    from scht_lab.models.flow import Flow


@flows_app.command("load")
def load_flows_from_file(ctx: Context, filename: str):
    """Load flows from a JSON file."""
    path = Path(get_app_dir("scht_lab")) / "resources" / filename
    if not path.exists():
        print(f"File not found: {path}")
        return

    with open(path, 'r') as file:
        try:
            flows_data = json.load(file)
            print("Loaded flows from the JSON file:")
            print(flows_data)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")

@flows_app.command("save")
def save_flows_to_file(ctx: Context, filename: str, flows: list[Flow]):
    """Save flows to a JSON file."""
    path = Path(get_app_dir("scht_lab")) / "resources" / filename

    with open(path, 'w') as file:
        try:
            json.dump(flows, file, indent=4)
            print(f"Flows saved to {path}")
        except Exception as e:
            print(f"Error saving flows to JSON file: {e}")

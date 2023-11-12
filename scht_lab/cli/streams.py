import json
from pathlib import Path
from typing import Annotated
from pydantic import ValidationError

from rich import print
from typer import Argument, Context, Typer, get_app_dir

from scht_lab.models.flow import Flow
from scht_lab.models.stream import Streams
from scht_lab.helpers.jsonl import jsonl_to_keyed

streams_app = Typer(name="streams")

@streams_app.command("load")
def load_streams_from_file(ctx: Context, path: Annotated[Path, Argument(exists=True, readable=True, resolve_path=True)]):
    """Load streams from a JSON file."""
    with path.open('r') as file:
        try:
            file_data = file.read()
            if not file_data.strip().startswith("{"):
                file_data = jsonl_to_keyed(file_data, "streams")
            streams_data = Streams.model_validate_json(file_data)
            print("Loaded streams:")
            print(streams_data)
            print("Saving streams for future usage...")
            save_streams_to_file("streams.json", streams_data)
        except ValidationError as e:
            print(f"Error loading JSON file: {e}")

def save_streams_to_file(filename: str, streams: Streams):
    """Save flows to a JSON file."""
    path = Path(get_app_dir("scht_lab")) / "resources" / filename

    with path.open('w') as file:
        try:
            file.write(streams.model_dump_json(exclude_unset=True, indent=4))
            print(f"Successfully saved streams")
        except Exception as e:
            print(f"Error saving flows to JSON file: {e}")

@streams_app.command("save")
def load_streams_from_cli(ctx: Context, streams: Annotated[list[str], Argument(help="List of streams to save for future usage")]):
    """Save streams to a JSON file."""
    try:
        streams_str = "\n".join(streams)
        if not streams_str.strip().startswith("{"):
            streams_str = jsonl_to_keyed(streams_str, "streams")
        streams_data = Streams.model_validate_json(streams_str)
        print("Loaded streams:")
        print(streams_data)
        print("Saving streams for future usage...")
        save_streams_to_file("streams.json", streams_data)
    except ValidationError as e:
        print(f"Error loading JSON file: {e}")

@streams_app.command("list")
def list_streams(ctx: Context):
    """List all streams saved from the CLI."""
    path = Path(get_app_dir("scht_lab")) / "resources" / "streams.json"
    with path.open('r') as file:
        try:
            file_data = file.read()
            streams_data = Streams.model_validate_json(file_data)
            print("Loaded streams:")
            print(streams_data)
        except ValidationError as e:
            print(f"Error loading JSON file: {e}")
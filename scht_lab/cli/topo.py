import json
from pathlib import Path
import time
from typing import Annotated, Optional
from pydantic import ValidationError

from rich import print
from typer import Argument, Context, Option, Typer, get_app_dir

from scht_lab.models.flow import Flow
from scht_lab.models.stream import Streams
from scht_lab.helpers.jsonl import jsonl_to_keyed
from scht_lab.topo import default_topo, load_topology_from_file, save_default
from scht_lab.topo_graph import GraphMethod, build_graph, draw_graph

topo_app = Typer(name="topo")

@topo_app.command("load")
async def load_topology(ctx: Context, file: Annotated[Path, Argument(exists=True, readable=True, resolve_path=True)]):
    """Load topology and save it as default."""
    try:
        topo = await load_topology_from_file(file)
        print("Loaded topology:")
        print(topo)
        print("Saving topology as default...")
        await save_default(topo)
    except ValidationError as e:
        print(f"Error loading JSON file: {e}")

@topo_app.command("show", help="Show topology")
async def show_topology(ctx: Context,
                        topology: Annotated[Optional[Path], Option("-t", "--topology", help="JSON file to laod topology from - if not defined will use the default topology", exists=True, readable=True, resolve_path=True)] = None,
                        output: Annotated[Optional[Path], Option(exists=True, readable=True, resolve_path=True)] = None,
                        method: Annotated[GraphMethod, Option("-m", "--method", help="Graphviz layout engine to use for graphing", case_sensitive=False)] = GraphMethod.CIRCO
                        ):
    """Show a graph of the topology."""
    if topology:
        topo = await load_topology_from_file(topology)
    else:
        topo = await default_topo()
    graph, _ = build_graph(topo)
    draw_graph(graph, output, show=output is None, method=method)
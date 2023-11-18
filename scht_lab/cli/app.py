"""Typer-based CLI application."""
from typing import Annotated
from pathlib import Path
from click import Context
from typer import Option, Typer, get_app_dir
from shutil import rmtree

from scht_lab.cli.flows import flows_app
from scht_lab.cli.streams import streams_app
from scht_lab.cli.paths import paths_app
from scht_lab.cli.topo import topo_app

app = Typer()

@app.callback()
def all_commands(
    ctx: Context,
    host: Annotated[str, Option("-h", "--host", help="Host address")]="http://mininet:8181",
    user: Annotated[str, Option("-u", "--user", help="Username")]="karaf",
    password: Annotated[str, Option("-p", "--password", help="Password", hide_input=True)]="karaf"): # noqa: S107
    """Callback with parameters available for all commands."""
    ctx.ensure_object(dict)
    ctx.obj["BASE_URL"] = host
    ctx.obj["USERNAME"] = user
    ctx.obj["PASSWORD"] = password

app.add_typer(flows_app, name="flows", callback=all_commands)
app.add_typer(streams_app, name="streams", callback=all_commands)
app.add_typer(paths_app, name="paths", callback=all_commands)
app.add_typer(topo_app, name="topo", callback=all_commands)


@app.command()
def clean(ctx: Context):
    """Clean cache and save topology data."""
    dir = get_app_dir("scht_lab")
    rmtree(dir)
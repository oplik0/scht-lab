"""Typer-based CLI application."""
from typing import Annotated

from typer import Context, Option, Typer

from scht_lab.cli.flows import flows_app

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
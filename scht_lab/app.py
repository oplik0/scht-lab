from typer import Typer, Option, Context
from typing import Annotated
app = Typer()

@app.callback()
def all_commands(
    ctx: Context,
    host: Annotated[str, Option("-h", "--host", help="Host address")]="http://mininet:8181",
    user: Annotated[str, Option("-u", "--user", help="Username")]="karaf",
    password: Annotated[str, Option("-p", "--password", help="Password", hide_input=True)]="karaf"):
    ctx.ensure_object(dict)
    ctx.obj["BASE_URL"] = host
    ctx.obj["USERNAME"] = user
    ctx.obj["PASSWORD"] = password
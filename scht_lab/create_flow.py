from aiohttp import ClientSession, BasicAuth
from scht_lab.app import app
from scht_lab.client import get_client
from typer import Context

from rich import print

@app.command("test")
async def test_flow(ctx: Context):
    async with get_client(ctx) as client:
        response = await client.get("/onos/v1/flows")
        print(await response.json())
"""aiohttp client wrapper for ONOS API calls."""
from aiohttp import BasicAuth, ClientSession
from typer import Context


def get_client(context: Context, *args, **kwargs):
    """Get an aiohttp client session."""
    return ClientSession(
        context.obj["BASE_URL"], 
        *args, 
        auth=BasicAuth(context.obj["USERNAME"], context.obj["PASSWORD"]), 
        **kwargs,
    )
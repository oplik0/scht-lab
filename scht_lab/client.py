from aiohttp import ClientSession, BasicAuth
from typer import Context
def get_client(context: Context, *args, **kwargs):
    return ClientSession(context.obj["BASE_URL"], *args, auth=BasicAuth(context.obj["USERNAME"], context.obj["PASSWORD"]), **kwargs)
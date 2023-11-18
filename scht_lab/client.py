"""aiohttp client wrapper for ONOS API calls."""
from asyncio import gather
from typing import Iterable
from aiohttp import BasicAuth, ClientError, ClientSession, ContentTypeError
from click import Context

from scht_lab.models.flow import Flow


def get_client(context: Context, *args, **kwargs):
    """Get an aiohttp client session."""
    return ClientSession(
        context.obj["BASE_URL"], 
        *args, 
        auth=BasicAuth(context.obj["USERNAME"], context.obj["PASSWORD"]), 
        **kwargs,
    )


async def activate_defaults(ctx: Context):
    """Activate default setting required for the paths to work correctly."""
    async with get_client(ctx) as client:
        # ensure switch and host discovery works correctly
        default_apps = ["org.onosproject.openflow", "org.onosproject.proxyarp", "org.onosproject.lldpprovider", "org.onosproject.hostprovider"]
        responses = []
        for app in default_apps:
            responses.append(client.post(f"/applications/{app}/active"))
        await gather(*responses)

async def send_flows(ctx: Context, flows: Iterable[Flow]):
    """Send flows to ONOS."""
    async with get_client(ctx) as client:
        async with client.post("/onos/v1/flows?appId=scht_lab", json={"flows":[flow.model_dump(exclude_unset=True, mode="json") for flow in flows]}) as response:
            data = await response.json()
            return data
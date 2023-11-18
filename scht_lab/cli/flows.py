"""Commands directly related to ONOS flows."""
import json
from typing import Annotated, Literal

from aiohttp import ClientError, ContentTypeError
from anyio import Path
from rich import print
from rich.tree import Tree
from typer import Argument, Context, Typer, Option

from scht_lab.client import get_client, send_flows
from scht_lab.models.flow import Flow, Selector, Treatment

flows_app = Typer(name="flows", help="Interact with flows")

@flows_app.command("list")
async def get_flows(ctx: Context, raw: Annotated[bool, Option("-r", "--raw", help="Print raw JSON response")] = False):
    """List all flows in the network."""
    async with get_client(ctx) as client:
        response = await client.get("/onos/v1/flows")
        data = await response.json()
        if not data.get("flows", False):
            msg = f"Response didn't contain valid flows: {data}"
            raise ValueError(msg)
        flows: list[Flow] = data["flows"]

        if raw:
            print(json.dumps(flows, indent=4))
            return

        flows_tree = Tree("flows")
        for flow in sorted(flows, key=lambda flow: flow.deviceId):
            single_flow_tree = flows_tree.add(flow.deviceId, style="cyan")
            instructions = single_flow_tree.add("Instructions", style="default")
            criteria = single_flow_tree.add("Criteria", style="default")
            for instruction in flow.treatment.instructions:
                secondary_key = (set(instruction.keys()) - {"type"}).pop()
                instructions.add(f'{instruction["type"]}: {secondary_key}={instruction[secondary_key]}', style="red")
            for rule in flow.selector.criteria:
                secondary_key = (set(rule.keys()) - {"type"}).pop()
                criteria.add(f'{rule["type"]}: {secondary_key}={rule[secondary_key]}', style="green")
        print(flows_tree)

@flows_app.command("add")
async def add_flow(ctx: Context, device_id: str, in_port: int, out_port: int, ip: str):
    """Manually add a flow to the network."""
    async with get_client(ctx) as client:
        flow: Flow = Flow(
            deviceId=device_id,
            priority=40000,
            timeout=0,
            isPermanent=True,
            treatment=Treatment(
                instructions=[
                    {"type": "OUTPUT", "port": str(out_port)},
                ],
            ),
            selector=Selector(
                criteria=[
                    {"type": "IN_PORT", "port": str(in_port)},
                    {"type": "ETH_TYPE", "ethType": "0x800"},
                    {"type": "IPV4_DST", "ip": ip},
                ],
            ),
        )
        response = await client.post("/onos/v1/flows?appId=scht_lab", json={"flows":[flow.model_dump(exclude_unset=True, mode="json")]})
        try:
            data = await send_flows(ctx, [flow])
            print(data)
        except (ContentTypeError, ClientError):
            print(response.status)


@flows_app.command("load")
async def load_flows_from_file(
    ctx: Context, 
    path: Annotated[Path, Argument(exists=True, readable=True, resolve_path=True)],
    ):
    """Load flows from a JSON file."""
    async with await path.open('r') as file:
        try:
            flows_data = await file.read()
            async with get_client(ctx) as client:
                data: dict[Literal["flows"], list[Flow]] = json.loads(flows_data)
                response = await client.post("/onos/v1/flows?appId=scht_lab", json=data)
                data = await response.json()
                print(data)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")
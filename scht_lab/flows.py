from aiohttp import ClientSession, BasicAuth
from scht_lab.client import get_client
from typer import Context, Typer
from scht_lab.models.flow import Flow

from rich import print
from rich.tree import Tree

flows_app = Typer(name="flows", help="Interact with flows")

@flows_app.command("list")
async def test_flow(ctx: Context):
    async with get_client(ctx) as client:
        response = await client.get("/onos/v1/flows")
        data = await response.json()
        if not data["flows"]:
            raise ValueError(f"Response didn't contain valid flows: {data}")
        flows: list[Flow] = data["flows"]
        flows_tree = Tree("flows")
        for flow in sorted(flows, key=lambda flow: flow["deviceId"]):
            single_flow_tree = flows_tree.add(flow["deviceId"], style="cyan")
            instructions = single_flow_tree.add("Instructions", style="default")
            criteria = single_flow_tree.add("Criteria", style="default")
            for instruction in flow["treatment"]["instructions"]:
                secondary_key = (set(instruction.keys()) - set(["type"])).pop()
                instructions.add(f'{instruction["type"]}: {secondary_key}={instruction[secondary_key]}', style="red")
            for rule in flow["selector"]["criteria"]:
                secondary_key = (set(rule.keys()) - set(["type"])).pop()
                criteria.add(f'{rule["type"]}: {secondary_key}={rule[secondary_key]}', style="green")
        print(flows_tree)

from itertools import chain, pairwise
import json
from pathlib import Path
from typing import Annotated, Literal, Optional, Tuple, cast
from operator import mul
from functools import reduce
from aiohttp import ClientError, ContentTypeError
import re
from math import inf
from rich import print

from pydantic import ValidationError
from rich import print
from typer import Option, Context, Typer, get_app_dir, Exit
from scht_lab.client import activate_defaults, get_client, send_flows

from scht_lab.models.flow import Flow
from scht_lab.models.stream import Requirements, Streams, Priorities
from scht_lab.helpers.jsonl import jsonl_to_keyed
from scht_lab.topo import Link, Location, Topology, load_topology_from_file, default_topo
from scht_lab.topo_graph import build_graph, get_path, paths_to_flows

paths_app = Typer(name="paths")

streams_regex = re.compile(r"^\s*{\s*\"streams\":\s*\[", re.UNICODE)

@paths_app.command("find")
async def find_paths_for_streams(
    ctx: Context,
    file: Annotated[Optional[Path], Option("-f", "--file", exists=True, readable=True, resolve_path=True, help="JSON file with stream specifications")] = None,
    apply: Annotated[bool, Option("-a", "--apply", help="Apply the paths to the network")] = False,
    output: Annotated[Optional[Path], Option("-o", "--output", help="File to output the resulting flows to as JSON")] = None,
    topology: Annotated[Optional[Path], Option("-t", "--topology", help="Topology file to use")] = None,
    max_attempts: Annotated[int, Option("-m", "--max-attempts", help="Maximum number of attempts to find a path")] = 10,
    ):
    """Find paths based on stream specifications. By default it will use streams previously saved from the CLI."""
    target_file = Path(get_app_dir("scht_lab")) / "streams.jsonl"
    if file:
        target_file = file
    with target_file.open('r') as f:
        try:
            file_data = f.read()
            if not streams_regex.match(file_data):
                file_data = jsonl_to_keyed(file_data, "streams")
            streams_data = Streams.model_validate_json(file_data)
        except ValidationError as e:
            print(f"Error loading JSON file:")
            print(e.errors())
            raise Exit(1)
    if topology:
        topo = await load_topology_from_file(topology)
    else:
        topo = await default_topo()
    graph, graph_map = build_graph(topo)
    flows: set[Flow] = set()
    for stream in streams_data.streams:
        source = topo.get_location(stream.src)
        dest = topo.get_location(stream.dst)
        if not source or not dest:
            print(f"Source or destination not found for stream {stream}")
            continue
        priorities = stream.priorities or Priorities()
        requirements = stream.requirements or Requirements()
        for i in chain(range(1, max_attempts+1), [inf]):
            path = get_path(graph, graph_map, topo, source, dest, priorities, requirements)
            link_path = cast(list[Link],list(map(lambda x: topo.get_link(*x), pairwise(path))))
            if not path or None in link_path:
                print(f"Correct path not found for stream {stream}")
                continue
            params = get_path_params(link_path, topo)
            failed = False
            if stream.type == "UDP" and params["bandwidth"] < stream.rate:
                params["loss"] += (stream.rate - params["bandwidth"])/stream.rate
            if requirements.delay and params["delay"] > requirements.delay:
                priorities.delay = priorities.delay * 2**i if priorities.delay else 1
                failed = True
                print(f"Path {path} does not meet delay requirement of {requirements.delay} for stream {stream}. Total delay: {params['delay']}")
            if requirements.jitter and params["jitter"] > requirements.jitter:
                priorities.jitter = priorities.jitter * 2**i if priorities.jitter else 1
                failed = True
                print(f"Path {path} does not meet jitter requirement of {requirements.jitter} for stream {stream}. Total jitter: {params['jitter']}")
            if requirements.loss and params["loss"] > requirements.loss:
                priorities.loss = priorities.loss * 2**i if priorities.loss else 1
                failed = True
                print(f"Path {path} does not meet loss requirement of {requirements.loss} for stream {stream}. Total loss: {params['loss']}")
            if not failed:
                flows.update(paths_to_flows(path, topo))
                flows.update(paths_to_flows(list(reversed(path)), topo)) # also add the return path
                flows.update(*[node.endpoint_flows() for node in path])
                for link in link_path:
                    link.increase_utilization(stream.rate)
                break
    if apply:
        try:
            await activate_defaults(ctx)
            data = await send_flows(ctx, flows)
            print(data)
        except (ContentTypeError, ClientError) as e:
            print(f"Error sending flows: {e}")
    if output:
        with output.open('w') as f:
            json.dump({"flows": [flow.model_dump(exclude_unset=True, mode="json") for flow in flows]}, f, indent=2)
    if not (apply or output):
        print(flows)
    if not file:
        # clean up saved streams after use
        target_file.unlink()
def get_path_params(path: list[Link], topo: Topology) -> dict[Literal["delay", "jitter", "loss", "bandwidth"], float]:
    """Get the bandwidth of a path."""
    delays = []
    success_probabilities = []
    jitters = []
    bandwidths = []
    for link in path:
        delays.append(link.delay_calc())
        success_probabilities.append(1-link.loss_calc())
        jitters.append(link.jitter_calc()) # not sure if the calculation for jitter is correct tbh
        bandwidths.append(link.bandwidth_calc())
    return {
        "delay": sum(delays) if delays else 0.0,
        "jitter": sum(jitters) if jitters else 0.0,
        "loss": 1-reduce(mul, success_probabilities) if success_probabilities else 1.0,
        "bandwidth": min(bandwidths) if bandwidths else 0.0
        }
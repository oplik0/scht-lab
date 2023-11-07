"""Graph utilities for Topology objects."""
from enum import Enum
from functools import wraps
from typing import TYPE_CHECKING, NewType

import rustworkx as rx
from scht_lab.models.stream import Priorities
from scht_lab.cost_calc import get_cost_calc

from scht_lab.topo import Link, Location, Topology
from scht_lab.models.flow import Flow
from itertools import pairwise

from geopy.distance import distance

if TYPE_CHECKING:
    from collections.abc import Callable

def build_graph(topo: Topology):
    """Convert a Topology object to a rustworkx graph."""
    graph = rx.PyGraph()
    graph_map = {topo.locations[i]: i for i in graph.add_nodes_from(topo.locations)}
    for link in topo.links:
        graph.add_edge(graph_map[link.locations[0]], graph_map[link.locations[1]], link)
    return graph, graph_map



NodePaths = NewType("NodePaths", dict[Location, dict[Location, list[Location]]])

def all_paths(
        graph: rx.PyGraph, graph_map: dict[Location, int], 
        priorities: Priorities, topo: Topology) -> NodePaths:
    """Find all shortest paths between all nodes in a graph."""
    inverse_graph_map = {v: k for k, v in graph_map.items()}
    paths: dict[int, dict[int, list[int]]] = rx.all_pairs_dijkstra_shortest_paths(graph, get_cost_calc(priorities)) # type: ignore
    node_paths: NodePaths = {} # type: ignore
    for node, targets in paths.items():
        node_paths.setdefault(inverse_graph_map[node], {})
        for target, path in targets.items():
            node_paths[inverse_graph_map[node]][inverse_graph_map[target]] = [inverse_graph_map[i] for i in path]
    return node_paths

def cost_estimate(src: Location, dst: Location) -> float:
    """Adjust the weight of a node for A*."""
    return Link((src,dst), distance(src.coords, dst.coords).km).delay_calc()

def cost_estimate_fn(dst: Location) -> Callable[[Location], float]:
    """Create a cost estimate function for A*."""
    @wraps(cost_estimate)
    def wrapper(src: Location) -> float:
        return cost_estimate(src, dst)
    return wrapper


def get_path(
        graph: rx.PyGraph, graph_map: dict[Location, int],
        priorities: Priorities, topo: Topology,
        src: Location, dst: Location) -> list[Location]:
    """Find a shortest path between two nodes in a graph."""
    inverse_graph_map = {v: k for k, v in graph_map.items()}
    path = rx.astar_shortest_path(graph, inverse_graph_map[src], lambda node: node.ip == dst.ip, get_cost_calc(priorities), )


def paths_to_flows(paths: NodePaths, topo: Topology) -> list[Flow]:
    """Convert a NodePaths object to a list of unique flows."""
    flows: list[Flow] = []
    for src, targets in paths.items():
        for dst, path in targets.items():
            for current, nexthop in pairwise(path):
                flows.append({
                    "deviceId": current.ofname,
                    "isPermanent": True,
                    "priority": 40000,
                    "timeout": 0,
                    "selector": {
                        "criteria": [
                            {
                                "type": "ETH_TYPE",
                                "ethType": "0x800"
                            },
                            {
                                "type": "IPV4_DST",
                                "ip": dst.ip
                            }, 
                            {
                                "type": "IPV4_SRC",
                                "ip": src.ip
                            }
                        ]
                    },
                    "treatment": {
                        "instructions": [
                            {
                                "type": "OUTPUT",
                                "port": str(topo.port_to(current, nexthop))
                            }
                        ]
                    }
                })
    return flows
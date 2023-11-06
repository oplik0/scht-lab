"""Graph utilities for Topology objects."""
from enum import Enum
from typing import TYPE_CHECKING, NewType

import rustworkx as rx

from scht_lab.topo import Link, Location, Topology
from scht_lab.models.flow import Flow
from itertools import pairwise

if TYPE_CHECKING:
    from collections.abc import Callable

def build_graph(topo: Topology):
    """Convert a Topology object to a rustworkx graph."""
    graph = rx.PyGraph()
    graph_map = {topo.locations[i]: i for i in graph.add_nodes_from(topo.locations)}
    for link in topo.links:
        graph.add_edge(graph_map[link.locations[0]], graph_map[link.locations[1]], link)
    return graph, graph_map


class CostTypes(Enum):
    """Enum for variants of cost estimation for links."""
    delay = 0
    jitter = 1
    bandwidth = 2
    loss = 3
    combined = 4


NodePaths = NewType("NodePaths", dict[Location, dict[Location, list[Location]]])

def get_paths(
        graph: rx.PyGraph, graph_map: dict[Location, int], 
        cost_type: CostTypes) -> NodePaths:
    """Find all shortest paths between all nodes in a graph."""
    cost_fn: Callable[[Link], float] = lambda x: 0.0
    match cost_type:
        case CostTypes.delay:
            cost_fn = lambda edge: edge.delay_calc()
        case CostTypes.jitter:
            cost_fn = lambda edge: edge.jitter_calc()
        case CostTypes.bandwidth:
            cost_fn = lambda edge: edge.bandwidth_calc()
        case CostTypes.loss:
            cost_fn = lambda edge: edge.loss_calc()
        case CostTypes.combined:
            cost_fn = lambda edge: (edge.delay_calc() + 
                                    edge.jitter_calc() * 2 + 
                                    edge.bandwidth_calc() / 100 + 
                                    edge.loss_calc() * 5)
    inverse_graph_map = {v: k for k, v in graph_map.items()}
    paths: dict[int, dict[int, list[int]]] = rx.all_pairs_dijkstra_shortest_paths(graph, cost_fn) # type: ignore
    node_paths: NodePaths = {} # type: ignore
    for node, targets in paths.items():
        node_paths.setdefault(inverse_graph_map[node], {})
        for target, path in targets.items():
            node_paths[inverse_graph_map[node]][inverse_graph_map[target]] = [inverse_graph_map[i] for i in path]
    return node_paths


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
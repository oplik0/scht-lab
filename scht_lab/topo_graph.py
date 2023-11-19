"""Graph utilities for Topology objects."""
from collections.abc import Callable
from enum import Enum
from functools import wraps
from itertools import chain, pairwise, permutations
from pathlib import Path
from typing import NewType, cast

import rustworkx as rx
from geopy.distance import distance

from scht_lab.cost_calc import get_cost_calc
from scht_lab.models.flow import Flow, Selector, Treatment
from scht_lab.models.stream import Priorities, Requirements
from scht_lab.topo import Link, Location, Topology
from rustworkx.visualization import graphviz_draw

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


def goal(node: Location, dst: Location) -> bool:
    """Check if a node is the goal for A*."""
    return node == dst

def goal_fn(dst: Location) -> Callable[[Location], bool]:
    """Create a goal function for A*."""
    @wraps(goal)
    def wrapper(node: Location) -> bool:
        return goal(node, dst)
    return wrapper

def get_path(
        graph: rx.PyGraph, graph_map: dict[Location, int],
        topo: Topology,
        src: Location, dst: Location,
        priorities: Priorities | None, requirements: Requirements | None) -> list[Location]:
    """Find a shortest path between two nodes in a graph."""
    inverse_graph_map = {v: k for k, v in graph_map.items()}
    path: rx.NodeIndices = rx.astar_shortest_path( # type: ignore
        graph,
        graph_map[src], 
        goal_fn(dst), 
        get_cost_calc(priorities, requirements), 
        cost_estimate_fn(dst),
        )
    return [inverse_graph_map[i] for i in path]

def paths_to_flows(paths: NodePaths | list[Location], topo: Topology) -> list[Flow]:
    """Convert a NodePaths object to a list of unique flows."""
    if isinstance(paths, list):
        paths = cast(NodePaths, {paths[0]: {paths[-1]: paths}})
    flows: list[Flow] = []
    for src, targets in paths.items():
        for dst, path in targets.items():
            for current, nexthop in pairwise(path):
                flows.append(Flow(
                    deviceId=current.ofname,
                    isPermanent=True,
                    priority=40000,
                    timeout=0,
                    selector=Selector(
                        criteria=[
                            {
                                "type": "ETH_TYPE",
                                "ethType": "0x800" if dst.ip.version == 4 else "0x86dd",
                            },
                            {
                                "type": "IPV4_DST" if dst.ip.version == 4 else "IPV6_DST",
                                "ip": f"{dst.ip.ip}/{dst.ip.max_prefixlen}",
                            }, 
                            {
                                "type": "IPV4_SRC" if src.ip.version == 4 else "IPV6_SRC",
                                "ip": f"{src.ip.ip}/{src.ip.max_prefixlen}",
                            }, # type: ignore
                        ],
                    ),
                    treatment=Treatment(
                        instructions=[
                            {
                                "type": "OUTPUT",
                                "port": str(topo.port_to(current, nexthop)),
                            },
                        ],
                    ),
                ))
    return flows


class GraphMethod(str, Enum):
    """Which layout method to use for drawing a graph."""
    CIRCO = "circo"
    DOT = "dot"
    FDP = "fdp"
    NEATO = "neato"
    OSAGE = "osage"
    SFDP = "sfdp"

def draw_graph(graph: rx.PyGraph, filename: str | Path | None, show: bool = False, method: GraphMethod = GraphMethod.CIRCO):
    """Draw a graph using graphviz."""
    def node_attr(node: Location) -> dict[str, str]:
        """Get graphviz attributes for a node."""
        return {
            "label": f"{node.name}\n{node.ip}",
            "shape": "ellipse",
            "style": "filled",
            "fillcolor": "lightblue",
        }


    def edge_attr(edge: Link) -> dict[str, str]:
        """Get graphviz attributes for an edge."""
        return {
            "label": f"{edge.distance}km\n{edge.delay_calc()}ms",
            "style": "filled",
            "fillcolor": "lightgrey",
            "len": str(edge.distance),
            "headlabel": f"{edge.ports[1] if edge.ports else 'host'}",
            "taillabel": f"{edge.ports[0] if edge.ports else 'host'}",
        }


    image = graphviz_draw(graph, node_attr_fn=node_attr, edge_attr_fn=edge_attr, method=method.value, filename=filename)
    if not filename and image is not None and show:
        image.show()
    return image
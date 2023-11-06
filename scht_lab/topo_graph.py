from enum import Enum
from typing import Callable
from scht_lab.topo import Topology, Location, Link
import rustworkx as rx

def build_graph(topo: Topology):
    graph = rx.PyGraph()
    graph_map = {topo.locations[i]: i for i in graph.add_nodes_from(topo.locations)}
    for link in topo.links:
        graph.add_edge(graph_map[link.src], graph_map[link.dst], link)
    return graph, graph_map


class CostTypes(Enum):
    delay = 0
    jitter = 1
    bandwidth = 2
    loss = 3
    combined = 4


def get_paths(graph: rx.PyGraph, graph_map: dict[Location, int], cost_type: CostTypes):
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
            cost_fn = lambda edge: edge.delay_calc() + edge.jitter_calc() * 2 + edge.bandwidth_calc() / 100 + edge.loss_calc() * 5
    inverse_graph_map = {v: k for k, v in graph_map.items()}
    paths: dict[int, dict[int, list[int]]] =  rx.all_pairs_dijkstra_shortest_paths(graph, cost_fn) # type: ignore
    node_paths: dict[Location, dict[Location, list[Location]]] = {}
    for node, targets in paths.items():
        for target, path in targets.items():
            node_paths.setdefault(inverse_graph_map[node], {})[inverse_graph_map[target]] = [inverse_graph_map[node] for node in path]
    return node_paths
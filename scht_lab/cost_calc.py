"""Cost calculation functions for pathfinding."""
from functools import wraps
from math import inf

from scht_lab.models.stream import Priorities, Requirements
from scht_lab.topo import Link, Topology


def delay_calc(link: Link, priority: float = 1.0, topo: Topology | None = None) -> float:
    """Calculate delay for a link."""
    normalized_delay = link.delay_calc()/(topo.max_delay if topo else 1)
    return priority/normalized_delay if priority else 0.0

def jitter_calc(link: Link, priority: float = 1.0, topo: Topology | None = None) -> float:
    """Calculate jitter (derivative of delay) for a link."""
    normalized_jitter = link.jitter_calc()/(topo.max_jitter if topo else 1)
    return priority/normalized_jitter if priority else 0.0

def bandwidth_calc(link: Link, priority: float = 1.0, requirement: float = 0.0, topo: Topology | None = None) -> float:
    """Calculate bandwidth for a link."""
    bw = link.bandwidth_calc() 
    if bw - link.utilization < requirement :
        return inf # this link is not usable according to requirements
    normalized_bw = bw/(topo.max_bandwidth if topo else 1)
    return priority*normalized_bw if priority else 0.0

def loss_calc(link: Link, priority: float = 1.0, topo: Topology | None = None) -> float:
    """Calculate loss for a link."""
    normalized_loss = link.loss_calc()/(topo.max_loss if topo else 1)
    return priority/normalized_loss if priority else 0.0

def congestion_calc(link: Link, priority: float = 1.0, topo: Topology | None = None) -> float:
    """Calculate congestion for a link."""
    return (link.utilization * priority)/link.bandwidth_calc() if priority else 0.0


def cost_calc(link: Link, priorities: Priorities | None = None, requirements: Requirements | None = None, topology: Topology | None = None) -> float:
    """Calculate cost for a link."""
    if priorities is None:
        return link.distance
    return (
            delay_calc(link, priorities.delay or 0, topo=topology) + 
            jitter_calc(link, priorities.jitter or 0, topo=topology) + 
            bandwidth_calc(link,  priorities.bandwidth or 0, requirement=requirements.bandwidth if requirements and requirements.bandwidth else 0.0, topo=topology) + 
            loss_calc(link, priorities.loss or 0, topo=topology) +
            congestion_calc(link, priorities.congestion or 0, topo=topology)
            )

def get_cost_calc(priorities: Priorities | None = None, requirements: Requirements | None = None, topology: Topology | None = None):
    """Wrap cost_calc to be used as a cost function."""
    @wraps(cost_calc)
    def wrapped(link: Link):
        return cost_calc(link, priorities, requirements)
    return wrapped
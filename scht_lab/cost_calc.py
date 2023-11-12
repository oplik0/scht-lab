"""Cost calculation functions for pathfinding."""
from functools import wraps
from math import inf

from scht_lab.models.stream import Priorities, Requirements
from scht_lab.topo import Link, Topology


def delay_calc(link: Link, priority: float = 1.0) -> float:
    """Calculate delay for a link."""
    return 1/(link.delay_calc() * priority)

def jitter_calc(link: Link, priority: float = 1.0) -> float:
    """Calculate jitter (derivative of delay) for a link."""
    return 1/(link.jitter_calc() * priority)

def bandwidth_calc(link: Link, priority: float = 1.0, requirement: float = 0.0) -> float:
    """Calculate bandwidth for a link."""
    bw = link.bandwidth_calc() 
    if bw - link.utilization < requirement :
        return inf # this link is not usable according to requirements
    return 1/(bw*priority)

def loss_calc(link: Link, priority: float = 1.0) -> float:
    """Calculate loss for a link."""
    return 1/(link.loss_calc() * priority)

def congestion_calc(link: Link, priority: float = 1.0, topology: Topology | None = None) -> float:
    """Calculate congestion for a link."""
    return (link.utilization * priority)/link.bandwidth_calc()


def cost_calc(link: Link, priorities: Priorities | None = None, requirements: Requirements | None = None, topology: Topology | None = None) -> float:
    """Calculate cost for a link."""
    if priorities is None:
        return link.distance
    return (
            delay_calc(link, priorities.delay or 0) + 
            jitter_calc(link, priorities.jitter or 0) + 
            bandwidth_calc(link,  priorities.bandwidth or 0, requirement=requirements.bandwidth if requirements and requirements.bandwidth else 0.0) + 
            loss_calc(link, priorities.loss or 0) +
            congestion_calc(link, priorities.congestion or 0, topology=topology)
            )

def get_cost_calc(priorities: Priorities | None = None, requirements: Requirements | None = None, topology: Topology | None = None):
    """Wrap cost_calc to be used as a cost function."""
    @wraps(cost_calc)
    def wrapped(link: Link):
        return cost_calc(link, priorities, requirements)
    return wrapped
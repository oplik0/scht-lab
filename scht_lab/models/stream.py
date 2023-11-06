from typing import Annotated, Optional, TypedDict
from enum import Enum


class StreamType(Enum):
    """Enum for variants of cost estimation for links."""
    UDP = "UDP"
    TCP = "TCP"
    QUIC = "QUIC"


class Requirements(TypedDict):
    """Requirements for a stream."""
    delay: Optional[float]
    jitter: Optional[float]
    bandwidth: Optional[float]
    loss: Optional[float]

class Priorities(TypedDict):
    """Priorities for a stream."""
    delay: Optional[float]
    jitter: Optional[float]
    bandwidth: Optional[float]
    loss: Optional[float]
    congestion: Optional[float]

class StreamDef(TypedDict):
    """Definition of a stream for the app to handle."""
    src: str
    dst: str
    type: StreamType
    size: int
    rate: Annotated[int, "expected rate in Mbps"]
    requirements: Optional[Requirements]
    priorities: Optional[Priorities]

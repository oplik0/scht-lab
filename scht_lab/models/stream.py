"""Model for a stream to make a path for."""
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, RootModel


class StreamType(Enum):
    """Enum for variants of cost estimation for links."""
    UDP = "UDP"
    TCP = "TCP"


class Requirements(BaseModel):
    """Requirements for a stream."""
    delay: Optional[float] = None
    jitter: Optional[float] = None
    bandwidth: Optional[float] = None
    loss: Optional[float] = None

class Priorities(BaseModel):
    """Priorities for a stream."""
    delay: Optional[float] = 1.0
    jitter: Optional[float] = None
    bandwidth: Optional[float] = 1.0
    loss: Optional[float] = None
    congestion: Optional[float] = None

class Stream(BaseModel):
    """Definition of a stream for the app to handle."""
    src: str
    dst: str
    type: StreamType
    size: Optional[int] = None
    rate: Annotated[int, "expected rate in Mbps"]
    requirements: Optional[Requirements]
    priorities: Optional[Priorities]

class Streams(BaseModel):
    """Definition of a list of streams for the app to handle."""
    streams: list[Stream]
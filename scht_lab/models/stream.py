"""Model for a stream to make a path for."""
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, RootModel


class StreamType(Enum):
    """Enum for variants of cost estimation for links."""
    UDP = "UDP"
    TCP = "TCP"
    QUIC = "QUIC"


class Requirements(BaseModel):
    """Requirements for a stream."""
    delay: Optional[float]
    jitter: Optional[float]
    bandwidth: Optional[float]
    loss: Optional[float]
    @staticmethod
    def default() -> "Requirements":
        """Get default requirements."""
        return Requirements(
                delay=None,
                jitter=None,
                bandwidth=None,
                loss=None,
                )

class Priorities(BaseModel):
    """Priorities for a stream."""
    delay: Optional[float]
    jitter: Optional[float]
    bandwidth: Optional[float]
    loss: Optional[float]
    congestion: Optional[float]
    @staticmethod
    def default() -> "Priorities":
        """Get default priorities."""
        return Priorities(
                delay=1.0,
                jitter=1.0,
                bandwidth=1.0,
                loss=1.0,
                congestion=1.0,
                )

class Stream(BaseModel):
    """Definition of a stream for the app to handle."""
    src: str
    dst: str
    type: StreamType
    size: int
    rate: Annotated[int, "expected rate in Mbps"]
    requirements: Optional[Requirements]
    priorities: Optional[Priorities]

class Streams(BaseModel):
    """Definition of a list of streams for the app to handle."""
    streams: list[Stream]
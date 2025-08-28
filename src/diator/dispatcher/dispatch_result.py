from dataclasses import dataclass, field
from typing import Protocol, TypeVar

from diator.events.event import Event
from diator.response import TResponse

Res = TypeVar("Res", bound=TResponse | None, covariant=True)

class TDispatchResult(Protocol[Res]):
    pass

@dataclass
class DispatchResult(TDispatchResult[Res]):
    response: Res | None = field(default=None)
    events: list[Event] = field(default_factory=list)

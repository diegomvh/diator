from dataclasses import dataclass, field
from typing import Protocol, TypeVar

from diator.events.event import Event
from diator.responses import IResponse

Res = TypeVar("Res", bound=IResponse | None)

class IDispatchResult(Protocol[Res]):
    response: Res | None
    events: list[Event]

@dataclass
class DispatchResult(IDispatchResult[Res]):
    response: Res | None = field(default=None)
    events: list[Event] = field(default_factory=list)

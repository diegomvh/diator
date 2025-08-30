from dataclasses import dataclass, field
from typing import Protocol, TypeVar
from uuid import UUID, uuid4

from diator.responses import IResponse

Res = TypeVar("Res", bound=IResponse | None, covariant=True)

class IRequest(Protocol[Res]):
    request_id: UUID


@dataclass(kw_only=True)
class Request(IRequest[Res]):
    """
    Base class for request-type objects.

    The request is an input of the request handler.
    Often Request is used for defining queries or commands.

    Usage::

      @dataclass(frozen=True, kw_only=True)
      class JoinMeetingCommand(Request):
          meeting_id: int = field()
          user_id: int = field()

      @dataclass(frozen=True, kw_only=True)
      class ReadMeetingByIdQuery(Request):
          meeting_id: int = field()

    """

    request_id: UUID = field(default_factory=uuid4)

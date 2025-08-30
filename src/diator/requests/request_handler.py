from typing import Protocol, TypeVar

from diator.events.event import Event
from diator.requests.request import IRequest
from diator.responses import IResponse

Req = TypeVar("Req", bound=IRequest, contravariant=True)
Res = TypeVar("Res", bound=IResponse | None, covariant=True)


class IRequestHandler(Protocol[Req, Res]):
    @property
    def events(self) -> list[Event]:
        ...

    async def handle(self, request: Req) -> Res:
        ...

class RequestHandler(IRequestHandler[Req, Res]):
    """
    The request handler interface.

    The request handler is an object, which gets a request as input and may return a response as a result.

    Command handler example::

      class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None])
          def __init__(self, meetings_api: MeetingAPIProtocol) -> None:
              self._meetings_api = meetings_api
              self.events: list[Event] = []

          async def handle(self, request: JoinMeetingCommand) -> None:
              await self._meetings_api.join_user(request.user_id, request.meeting_id)

    Query handler example::

      class ReadMeetingQueryHandler(RequestHandler[ReadMeetingQuery, ReadMeetingQueryResult])
          def __init__(self, meetings_api: MeetingAPIProtocol) -> None:
              self._meetings_api = meetings_api
              self.events: list[Event] = []

          async def handle(self, request: ReadMeetingQuery) -> ReadMeetingQueryResult:
              link = await self._meetings_api.get_link(request.meeting_id)
              return ReadMeetingQueryResult(link=link, meeting_id=request.meeting_id)

    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: Req) -> Res:
        raise NotImplementedError

from dataclasses import dataclass, field
from typing import Any, cast
from uuid import UUID, uuid4

from diator.container.protocol import Container
from diator.dispatcher import DefaultDispatcher
from diator.events import Event
from diator.middlewares import MiddlewareChain
from diator.requests import Request, RequestHandler
from diator.requests.map import RequestMap
from diator.requests.request import TRequest
from diator.response import Response


@dataclass(kw_only=True)
class ReadMeetingDetailsQueryResult(Response):
    meeting_room_id: UUID = field()
    second: str = field(default="")
    third: str = field(default="")

@dataclass(kw_only=True)
class ReadMeetingDetailsQuery(Request[ReadMeetingDetailsQueryResult]):
    meeting_room_id: UUID = field()
    second: str = field(default="")
    third: str = field(default="")

class ReadMeetingDetailsQueryHandler(
    RequestHandler[ReadMeetingDetailsQuery, ReadMeetingDetailsQueryResult]  # type: ignore
):
    def __init__(self) -> None:
        self.called = False
        self._events: list[Event] = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: ReadMeetingDetailsQuery) -> ReadMeetingDetailsQueryResult:
        self.called = True
        return ReadMeetingDetailsQueryResult(meeting_room_id=request.meeting_room_id)

class TestQueryContainer(Container):
    _handler = ReadMeetingDetailsQueryHandler()

    async def resolve(self, type_):
        return self._handler

    @property
    def external_container(self) -> Container | None:
        raise NotImplementedError

    def attach_external_container(self, container: Container) -> None:
        raise NotImplementedError


async def test_default_dispatcher_logic() -> None:
    middleware = FirstMiddleware()
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    middleware_chain = MiddlewareChain()
    middleware_chain.add(middleware)
    dispatcher = DefaultDispatcher(
        request_map=request_map,
        container=TestQueryContainer(),
        middleware_chain=middleware_chain,
    )

    request = ReadMeetingDetailsQuery(meeting_room_id=uuid4())

    result = await dispatcher.dispatch(request)

    assert request.meeting_room_id == "REQ"
    assert result.response is not None 
    assert result.response.meeting_room_id == "RES"


async def test_default_dispatcher_chain_logic() -> None:
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    middleware_chain = MiddlewareChain()
    middleware_chain.set([FirstMiddleware(), SecondMiddleware(), ThirdMiddleware()])
    dispatcher = DefaultDispatcher(
        request_map=request_map,
        container=TestQueryContainer(),
        middleware_chain=middleware_chain,
    )

    request = ReadMeetingDetailsQuery(meeting_room_id=uuid4())

    result = await dispatcher.dispatch(request)

    assert request.meeting_room_id == "REQ"
    assert result.response is not None
    assert result.response.meeting_room_id == "RES"

    assert request.second == "DONE"
    assert result.response is not None
    assert result.response.second == "DONE"

    assert request.third == "DONE"
    assert result.response is not None
    assert result.response.third == "DONE"


class FirstMiddleware:
    async def __call__(self, request: TRequest[Any], handle):
        cast(ReadMeetingDetailsQuery, request).meeting_room_id = uuid4() 
        response = await handle(request)
        response.meeting_room_id = "RES"
        return response


class SecondMiddleware:
    async def __call__(self, request: TRequest[Any], handle):
        cast(ReadMeetingDetailsQuery, request).second = "DONE"
        response = await handle(request)
        response.second = "DONE"
        return response


class ThirdMiddleware:
    async def __call__(self, request: TRequest[Any], handle):
        cast(ReadMeetingDetailsQuery, request).third = "DONE"
        response = await handle(request)
        response.third = "DONE"
        return response

from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

import pytest
from redis import asyncio as redis
from rodi import Container, ServiceLifeStyle

from diator.container.rodi import RodiContainer
from diator.events import EventEmitter, EventMap
from diator.mediator import Mediator
from diator.message_brokers.redis import RedisMessageBroker
from diator.middlewares import MiddlewareChain
from diator.middlewares.base import IMiddleware
from diator.requests import Request, RequestMap
from diator.requests.request import IRequest
from diator.requests.request_handler import RequestHandler
from diator.responses import IResponse


@dataclass(kw_only=True)
class JoinMeetingRoomCommand(Request[None]):
    meeting_id: int
    user_id: int


class JoinMeetingRoomCommandHandler(RequestHandler[JoinMeetingRoomCommand, None]):
    def __init__(self, redis_client: redis.Redis) -> None:
        super().__init__()
        self._redis_client = redis_client

    async def handle(self, request: JoinMeetingRoomCommand) -> None:
        await self._redis_client.set(str(request.meeting_id), str(request.user_id))

Req = TypeVar("Req", bound=IRequest, contravariant=True)
Res = TypeVar("Res", bound=IResponse | None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]

class TestMiddleware(IMiddleware):
    _counter = 0

    async def __call__(self, request: IRequest[Res], handle: HandleType) -> Res:
        self._counter += 5
        return await handle(request)


@pytest.fixture
def mediator() -> Mediator:
    container = Container()
    container.register_factory(
        lambda: redis.Redis.from_url("redis://localhost:6379/0"),
        redis.Redis,
        ServiceLifeStyle.TRANSIENT,
    )
    container.register(JoinMeetingRoomCommandHandler)
    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")
    middleware_chain = MiddlewareChain()
    middleware_chain.add(TestMiddleware())

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=EventMap(),
        container=rodi_container,
    )

    return Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=rodi_container,
        middleware_chain=middleware_chain,
    )


@pytest.fixture
def mediator_without_broker() -> Mediator:
    container = Container()
    container.register_factory(
        lambda: redis.Redis.from_url("redis://localhost:6379/0"),
        redis.Redis,
        ServiceLifeStyle.TRANSIENT,
    )
    container.register(JoinMeetingRoomCommandHandler)
    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    middleware_chain = MiddlewareChain()
    middleware_chain.add(TestMiddleware())

    event_emitter = EventEmitter(
        event_map=EventMap(),
        container=rodi_container,
    )

    return Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=rodi_container,
        middleware_chain=middleware_chain,
    )


@pytest.fixture
def mediator_without_event_emitter() -> Mediator:
    container = Container()
    container.register_factory(
        lambda: redis.Redis.from_url("redis://localhost:6379/0"),
        redis.Redis,
        ServiceLifeStyle.TRANSIENT,
    )
    container.register(JoinMeetingRoomCommandHandler)
    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    middleware_chain = MiddlewareChain()
    middleware_chain.add(TestMiddleware())

    return Mediator(
        request_map=request_map,
        container=rodi_container,
        middleware_chain=middleware_chain,
    )


async def test_send_command_with_middleware(redis_client: redis.Redis, mediator: Mediator):
    await mediator.send(JoinMeetingRoomCommand(user_id=1, meeting_id=1))

    value = await redis_client.get("1")

    assert value == b"1"


async def test_mediator_without_message_broker(mediator_without_broker: Mediator) -> None:
    await mediator_without_broker.send(JoinMeetingRoomCommand(user_id=1, meeting_id=1))


async def test_mediator_without_message_event_emitter(mediator_without_event_emitter: Mediator) -> None:
    await mediator_without_event_emitter.send(JoinMeetingRoomCommand(user_id=1, meeting_id=1))

import functools
from typing import Awaitable, Callable, Protocol, TypeVar

from diator.requests.request import IRequest
from diator.responses import IResponse

Req = TypeVar("Req", bound=IRequest, contravariant=True)
Res = TypeVar("Res", bound=IResponse | None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class IMiddleware(Protocol):
    async def __call__(self, request: IRequest[Res], handle: HandleType) -> Res:
        ...


Handle = Callable[[Req], Awaitable[Res]]


class MiddlewareChain:
    def __init__(self) -> None:
        self._chain: list[IMiddleware] = []

    def set(self, chain: list[IMiddleware]) -> None:
        self._chain = chain

    def add(self, middleware: IMiddleware) -> None:
        self._chain.append(middleware)

    def wrap(self, handle: Handle) -> Handle:
        for middleware in reversed(self._chain):
            handle = functools.partial(middleware.__call__, handle=handle)

        return handle

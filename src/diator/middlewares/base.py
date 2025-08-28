import functools
from typing import Awaitable, Callable, Protocol, TypeVar

from diator.requests.request import TRequest
from diator.response import TResponse

Req = TypeVar("Req", bound=TRequest, contravariant=True)
Res = TypeVar("Res", bound=TResponse | None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class Middleware(Protocol):
    async def __call__(self, request: TRequest[Res], handle: HandleType) -> Res:
        ...


Handle = Callable[[Req], Awaitable[Res]]


class MiddlewareChain:
    def __init__(self) -> None:
        self._chain: list[Middleware] = []

    def set(self, chain: list[Middleware]) -> None:
        self._chain = chain

    def add(self, middleware: Middleware) -> None:
        self._chain.append(middleware)

    def wrap(self, handle: Handle) -> Handle:
        for middleware in reversed(self._chain):
            handle = functools.partial(middleware.__call__, handle=handle)

        return handle

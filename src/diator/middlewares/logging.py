import logging
from typing import Awaitable, Callable, Mapping, Protocol, TypeVar

from diator.requests.request import TRequest
from diator.response import TResponse

Req = TypeVar("Req", bound=TRequest, contravariant=True)
Res = TypeVar("Res", bound=TResponse | None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class Logger(Protocol):
    def log(self, level: int, msg: str, *args, extra: Mapping[str, object] | None = None) -> None:  # noqa
        ...


class LoggingMiddleware:
    def __init__(
        self,
        logger: Logger | None = None,
        level: int = logging.DEBUG,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._level = level

    async def __call__(self, request: TRequest[Res], handle: HandleType) -> Res:
        self._logger.log(
            self._level,
            "Handle %s request",
            type(request).__name__,
            extra={"request": request},
        )
        response = await handle(request)
        self._logger.log(
            self._level,
            "Request %s handled. Response: %s",
            type(request).__name__,
            response,
            extra={"request": request},
        )

        return response

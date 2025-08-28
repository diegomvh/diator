from typing import Protocol

from diator.dispatcher.dispatch_result import DispatchResult
from diator.requests.request import TRequest


class Dispatcher(Protocol):
    async def dispatch(self, request: TRequest) -> DispatchResult:
        ...

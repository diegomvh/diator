from typing import Protocol, TypeVar

from diator.dispatcher.dispatch_result import IDispatchResult
from diator.requests.request import IRequest
from diator.responses import IResponse

Res = TypeVar("Res", bound=IResponse | None)

class Dispatcher(Protocol):
    async def dispatch(self, request: IRequest[Res]) -> IDispatchResult[Res]:
        ...

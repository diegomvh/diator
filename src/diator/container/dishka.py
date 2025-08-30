from typing import Type, TypeVar

import dishka

from diator.container.protocol import Container

T = TypeVar("T")


class DishkaContainer(Container[dishka.AsyncContainer]):
    def __init__(self) -> None:
        self._external_container: dishka.AsyncContainer | None = None

    @property
    def external_container(self) -> dishka.AsyncContainer:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    def attach_external_container(self, container: dishka.AsyncContainer) -> None:
        self._external_container = container

    async def resolve(self, type_: Type[T]) -> T:
        if not self._external_container:
            raise AttributeError
        return await self._external_container.get(type_)

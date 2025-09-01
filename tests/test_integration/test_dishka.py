from dishka import Provider, Scope, make_async_container, provide

from diator.containers.dishka import DishkaContainer


class Dependency:
    ...

class DependencyProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_dependency(self) -> Dependency:
        return Dependency()

async def test_dishka_container_resolve() -> None:
    external_container = make_async_container(DependencyProvider())

    async with external_container(scope=Scope.REQUEST) as container:
        dishka_container = DishkaContainer()
        dishka_container.attach_external_container(container)

        resolved = await dishka_container.resolve(Dependency)

        assert isinstance(resolved, Dependency)

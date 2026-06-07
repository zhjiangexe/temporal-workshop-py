from collections.abc import Awaitable, Callable
from typing import Any

from temporalio import workflow


class Saga:
    """
    Small helper for compensation-based workflows.

    Register each compensation before its forward step when that step may have
    partial external side effects. If a later step fails, call compensate() to
    run registered compensations in reverse order.
    """

    def __init__(self):
        self._compensations: list[Callable[[], Awaitable[None]]] = []

    def add_compensation(self, fn: Callable[[], Awaitable[None]]) -> None:
        self._compensations.append(fn)

    def add_activity_compensation(
        self,
        activity: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        async def compensate() -> None:
            await workflow.execute_activity(activity, args=list(args), **kwargs)

        self.add_compensation(compensate)

    async def compensate(self) -> None:
        for c in reversed(self._compensations):
            await c()

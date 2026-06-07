from collections.abc import Awaitable, Callable

from temporalio import workflow
from temporalio.exceptions import ActivityError


@workflow.defn
class CompensationWorkflow:
    @workflow.run
    async def execute(self) -> None:
        # 練習骨架：在每個 activity 呼叫後加入對應的補償 callback。
        compensations: list[Callable[[], Awaitable[None]]] = []
        try:
            compensations.append(self._rollback)
        except ActivityError:
            # 只捕獲 ActivityError，讓非 activity 的程式錯誤直接 propagate
            for compensate in reversed(compensations):
                await compensate()
            raise

    async def _rollback(self) -> None:
        pass

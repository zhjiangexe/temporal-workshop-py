import asyncio
from datetime import timedelta

from temporalio import workflow

from .activities import compose_greeting


@workflow.defn
class GreetingWorkflow:
    def __init__(self):
        self._current_greeting = "Hello"

    @workflow.run
    async def greet(self, name: str) -> str:
        # 保持 workflow 在 running 狀態，以便在執行期間示範 update/query
        await asyncio.sleep(3600)
        return await workflow.execute_activity(
            compose_greeting,
            args=[self._current_greeting, name],
            start_to_close_timeout=timedelta(seconds=5),
        )

    # update 可修改 workflow 狀態，呼叫方可 await 確認結果
    @workflow.update
    async def update_greeting(self, greeting: str) -> None:
        self._current_greeting = greeting

    # query 純讀：不產生 Temporal event，不寫入 history，可高頻呼叫
    @workflow.query
    def get_greeting(self) -> str:
        return self._current_greeting

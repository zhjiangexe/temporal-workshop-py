from datetime import timedelta

from temporalio import workflow

from .activities import AsyncActImpl


@workflow.defn
class AsyncWf:
    @workflow.run
    async def run(self, id: str) -> str:
        return await workflow.execute_activity_method(
            AsyncActImpl.wait_external,
            id,
            start_to_close_timeout=timedelta(seconds=10),
        )

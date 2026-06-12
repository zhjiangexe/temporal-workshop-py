from datetime import timedelta

from temporalio import workflow

from .activities import long_running_act


@workflow.defn
class LongActWorkflow:
    @workflow.run
    async def run(self) -> None:
        # 實際執行時間約 1000 * 0.01s = 10s，設 30s 留緩衝
        await workflow.execute_activity(
            long_running_act, start_to_close_timeout=timedelta(seconds=30)
        )

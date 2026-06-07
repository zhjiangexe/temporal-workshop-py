from datetime import timedelta

from temporalio import workflow


@workflow.defn
class AwaitWorkflow:
    def __init__(self):
        self._ready = False

    @workflow.run
    async def run(self) -> str:
        try:
            # durably waiting：workflow 不消耗 CPU，等 signal 改變狀態才喚醒
            # 這是 Temporal 讓「等很久再做事」的業務邏輯變得簡單的核心能力
            await workflow.wait_condition(lambda: self._ready, timeout=timedelta(hours=1))
            return "READY"
        except TimeoutError:
            return "TIMEOUT"

    # signal 的職責：改變狀態，觸發 wait_condition 的條件成立
    @workflow.signal
    def mark_ready(self) -> None:
        self._ready = True

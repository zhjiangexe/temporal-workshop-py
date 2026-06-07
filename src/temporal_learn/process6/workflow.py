import asyncio

from temporalio import workflow


@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, s: str) -> str:
        try:
            print("scope one")
            # Temporal 把取消請求注入成 CancelledError，直接打斷此 await
            await asyncio.sleep(7200)  # 2 hours
        except asyncio.CancelledError:
            # 取消不是靜默的，可以在這裡做清理工作（發通知、記錄審計日誌等）
            print("scope two")
            print("out")
            # 必須重新拋出：不 raise 則 Temporal 視為正常完成，取消請求不生效
            raise
        return "zero"

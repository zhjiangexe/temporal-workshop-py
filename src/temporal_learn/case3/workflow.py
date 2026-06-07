import asyncio
from datetime import timedelta

from temporalio import workflow


@workflow.defn
class PromiseWorkflow:
    @workflow.run
    async def execute(self) -> None:
        async def fn1(arg: str) -> str:
            print("rock 100")
            return "100"

        async def fn2(arg: str) -> str:
            print("zero 200")
            return "200"

        t1 = asyncio.create_task(fn1("arg1"))
        t2 = asyncio.create_task(fn2("arg1"))
        # asyncio.gather = Promise.all：並行執行，等全部完成後繼續
        results = await asyncio.gather(t1, t2)
        print(f"o1: {results[0]}, o2: {results[1]}")

    async def exe(self) -> None:
        """Promise.anyOf pattern: 等待外部回覆或 30 天 timeout（擇先）"""
        self._form_reply: str | None = None

        async def wait_timeout():
            await asyncio.sleep(timedelta(days=30).total_seconds())

        try:
            # wait_condition + timeout = Promise.anyOf：信號先到就繼續，timeout 先到就走 except
            await workflow.wait_condition(
                lambda: self._form_reply is not None,
                timeout=timedelta(days=30),
            )
            # form reply received
        except TimeoutError:
            # timeout handling
            pass

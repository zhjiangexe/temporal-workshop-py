import asyncio
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from .activities import check_title_validity, test_only

_ACT_CFG: workflow.ActivityConfig = {
    "start_to_close_timeout": timedelta(seconds=30),
}


@workflow.defn
class PromiseUpdateWorkflow:
    def __init__(self) -> None:
        self._name_with_title = ""
        self._title_has_been_checked = False

    @workflow.run
    async def get_greeting(self, input: str) -> str:
        self._name_with_title = f"Sir {input}"
        self._title_has_been_checked = False

        await asyncio.sleep(30)
        await workflow.execute_activity(test_only, "rock", **_ACT_CFG)
        # 等外部呼叫 check_title_validity update 後，由 update handler 設定 flag 解鎖
        await workflow.wait_condition(lambda: self._title_has_been_checked)
        return f"Hello {self._name_with_title}"

    # update handler 可以執行 activity，完成後修改狀態來解鎖 wait_condition
    @workflow.update
    async def check_title_validity(self) -> bool:
        is_valid = await workflow.execute_activity(
            check_title_validity, self._name_with_title, **_ACT_CFG
        )
        self._title_has_been_checked = True  # 解鎖主流程的 wait_condition
        return is_valid

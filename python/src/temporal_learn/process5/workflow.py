from collections import deque
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

from .activities import InventoryActivities
from .models import Command, CommandResult, CommandType

_ACT_CFG: workflow.ActivityConfig = {
    "start_to_close_timeout": timedelta(seconds=10),
    "retry_policy": RetryPolicy(
        maximum_attempts=5,
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        # 輸入有問題時重試無意義，直接失敗讓呼叫方修正
        non_retryable_error_types=["InvalidInput", "StockError"],
    ),
}


@workflow.defn
class InventoryEntityWorkflow:
    """
    Entity Workflow 模式：一個 workflow 代表一個業務實體（此處為單一商品庫存），
    長期運行，透過 signal/update 接收外部指令，永不主動結束。
    """

    def __init__(self):
        self._product_id = ""
        self._cached_stock = 0
        # 用佇列序列化處理 signal/update，確保指令不會並發修改庫存狀態
        self._inbox: deque[Command] = deque()
        self._results: dict[str, CommandResult] = {}

    @workflow.run
    async def run(self, product_id: str, initial_stock: int = 0) -> None:
        self._product_id = product_id
        if initial_stock > 0:
            self._cached_stock = await workflow.execute_activity_method(
                InventoryActivities.restock,
                args=[product_id, initial_stock, f"INIT-{product_id}"],
                **_ACT_CFG,
            )

        # Entity Workflow 的核心：「等待指令 → 處理 → 再等待」的無限迴圈
        while True:
            await workflow.wait_condition(
                lambda: self._inbox
                or workflow.info().is_continue_as_new_suggested
            )

            while self._inbox:
                command = self._inbox.popleft()
                result = await self._process_command(command)
                self._results[command.op_key] = result

            if workflow.info().is_continue_as_new_suggested:
                # 每個 workflow execution 的歷史大小有上限，達到時需要 continue_as_new
                # 切換前等所有 in-flight update 回應完，否則呼叫方會收到 error
                await workflow.wait_condition(workflow.all_handlers_finished)
                workflow.continue_as_new(args=[self._product_id, self._cached_stock])

    async def _process_command(self, command: Command) -> CommandResult:
        try:
            if command.qty <= 0:
                raise ApplicationError("qty must be > 0", type="InvalidInput")

            if command.command_type == CommandType.RESTOCK:
                self._cached_stock = await workflow.execute_activity_method(
                    InventoryActivities.restock,
                    args=[self._product_id, command.qty, command.op_key],
                    **_ACT_CFG,
                )
            elif command.command_type == CommandType.PURCHASE:
                self._cached_stock = await workflow.execute_activity_method(
                    InventoryActivities.purchase,
                    args=[self._product_id, command.qty, command.op_key],
                    **_ACT_CFG,
                )
            return CommandResult.ok(self._cached_stock)
        except ApplicationError:
            return CommandResult.fail(command.command_type.value, "fail")

    # fire-and-forget：呼叫方不等結果，適合批量送入指令的場景
    @workflow.signal
    def submit(self, command: Command) -> None:
        self._inbox.append(command)

    # 同步等待：呼叫方等待執行結果後才返回，適合需要立即確認的操作
    @workflow.update
    async def invoke(self, command: Command) -> CommandResult:
        self._inbox.append(command)
        # 等主迴圈處理完此指令並寫入 _results 後才返回
        await workflow.wait_condition(lambda: command.op_key in self._results)
        return self._results.pop(command.op_key)

    # 純讀查詢：不產生 Temporal event，不寫入 history，非常輕量
    @workflow.query
    def get_stock(self) -> int:
        return self._cached_stock

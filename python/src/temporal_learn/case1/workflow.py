from datetime import timedelta

from temporalio import workflow

from .activities import process_deliver_order, process_payment, process_reserve_inventory
from .models import Order


@workflow.defn
class OrderFulfillWorkflow:
    @workflow.run
    async def order_fulfill(self, order: Order) -> str:
        # 訂單履行的三個步驟依序執行，任一步驟失敗都會按 RetryPolicy 重試
        await workflow.execute_activity(
            process_payment, order, start_to_close_timeout=timedelta(seconds=30)
        )
        await workflow.execute_activity(
            process_reserve_inventory, order, start_to_close_timeout=timedelta(seconds=30)
        )
        await workflow.execute_activity(
            process_deliver_order, order, start_to_close_timeout=timedelta(seconds=30)
        )
        return "rock"

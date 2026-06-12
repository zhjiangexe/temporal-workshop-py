import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process5.models import Command, CommandResult, CommandType
from temporal_learn.process5.workflow import InventoryEntityWorkflow

TASK_QUEUE = "test-process5-workflow-q"


class TrackingInventoryActivities:
    # Entity workflow test 用 stub activity 驗證 update 指令如何被編排。
    def __init__(self):
        self.stock_by_product: dict[str, int] = {}
        self.calls: list[tuple[str, str, int, str]] = []

    @activity.defn(name="restock")
    async def restock(self, product_id: str, qty: int, op_key: str) -> int:
        self.calls.append(("restock", product_id, qty, op_key))
        self.stock_by_product[product_id] = self.stock_by_product.get(product_id, 0) + qty
        return self.stock_by_product[product_id]

    @activity.defn(name="purchase")
    async def purchase(self, product_id: str, qty: int, op_key: str) -> int:
        self.calls.append(("purchase", product_id, qty, op_key))
        self.stock_by_product[product_id] = self.stock_by_product.get(product_id, 0) - qty
        return self.stock_by_product[product_id]


@pytest.mark.asyncio
async def test_purchase_update_decreases_stock(env: WorkflowEnvironment):
    acts = TrackingInventoryActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[InventoryEntityWorkflow],
        activities=[acts.restock, acts.purchase],
    ):
        handle = await env.client.start_workflow(
            InventoryEntityWorkflow.run,
            args=["sku-1", 100],
            id=f"test-inv-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

        result: CommandResult = await handle.execute_update(
            InventoryEntityWorkflow.invoke,
            Command(command_type=CommandType.PURCHASE, qty=30, op_key="buy-1"),
        )

        assert result.stock == 70
        assert acts.calls == [
            ("restock", "sku-1", 100, "INIT-sku-1"),
            ("purchase", "sku-1", 30, "buy-1"),
        ]
        await handle.cancel()


@pytest.mark.asyncio
async def test_restock_update_increases_stock(env: WorkflowEnvironment):
    acts = TrackingInventoryActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[InventoryEntityWorkflow],
        activities=[acts.restock, acts.purchase],
    ):
        handle = await env.client.start_workflow(
            InventoryEntityWorkflow.run,
            args=["sku-2", 50],
            id=f"test-inv-restock-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

        result: CommandResult = await handle.execute_update(
            InventoryEntityWorkflow.invoke,
            Command(command_type=CommandType.RESTOCK, qty=25, op_key="restock-1"),
        )

        assert result.stock == 75
        assert acts.calls == [
            ("restock", "sku-2", 50, "INIT-sku-2"),
            ("restock", "sku-2", 25, "restock-1"),
        ]
        await handle.cancel()

import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.case1.activities import (
    process_deliver_order,
    process_payment,
    process_reserve_inventory,
)
from temporal_learn.case1.models import Order, OrderItem
from temporal_learn.case1.workflow import OrderFulfillWorkflow

TASK_QUEUE = "test-order-q"


@pytest.mark.asyncio
async def test_order_fulfill_returns_rock(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[OrderFulfillWorkflow],
        activities=[process_payment, process_reserve_inventory, process_deliver_order],
    ):
        order = Order(
            order_items=[OrderItem(item_name="widget", item_price=9.99, quantity=2)]
        )
        result = await env.client.execute_workflow(
            OrderFulfillWorkflow.order_fulfill,
            order,
            id=f"test-order-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        assert result == "rock"

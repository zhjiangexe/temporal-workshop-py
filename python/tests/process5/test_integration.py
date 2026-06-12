import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process5.activities import InventoryActivities
from temporal_learn.process5.models import Command, CommandResult, CommandType
from temporal_learn.process5.workflow import InventoryEntityWorkflow

TASK_QUEUE = "test-process5-integration-q"


@pytest.mark.asyncio
async def test_inventory_workflow_with_real_activities(env: WorkflowEnvironment):
    acts = InventoryActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[InventoryEntityWorkflow],
        activities=[acts.restock, acts.purchase],
    ):
        handle = await env.client.start_workflow(
            InventoryEntityWorkflow.run,
            args=["sku-1", 100],
            id=f"test-process5-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

        result: CommandResult = await handle.execute_update(
            InventoryEntityWorkflow.invoke,
            Command(command_type=CommandType.PURCHASE, qty=30, op_key="buy-1"),
        )

        assert result.stock == 70
        await handle.cancel()

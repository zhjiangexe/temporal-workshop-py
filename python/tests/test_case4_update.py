import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.case4 import activities as case4_activities
from temporal_learn.case4.workflow import PromiseUpdateWorkflow

TASK_QUEUE = "test-update-q"


@pytest.mark.asyncio
async def test_update_workflow_completes_after_title_check(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[PromiseUpdateWorkflow],
        activities=[case4_activities.test_only, case4_activities.check_title_validity],
    ):
        handle = await env.client.start_workflow(
            PromiseUpdateWorkflow.get_greeting,
            "Alice",
            id=f"test-update-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.execute_update(PromiseUpdateWorkflow.check_title_validity)
        result = await handle.result()
        assert result == "Hello Sir Alice"

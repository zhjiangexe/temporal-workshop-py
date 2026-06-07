import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process7.activities import compose_greeting
from temporal_learn.process7.workflow import GreetingWorkflow

TASK_QUEUE = "test-process7-integration-q"


@pytest.mark.asyncio
async def test_greeting_workflow_with_real_activity(env: WorkflowEnvironment):
    # 真 workflow + 真 activity，透過 update 改變 workflow 狀態後完成。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    ):
        handle = await env.client.start_workflow(
            GreetingWorkflow.greet,
            "Alice",
            id=f"test-process7-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.execute_update(GreetingWorkflow.update_greeting, "Howdy")
        assert await handle.result() == "Howdy, Alice!"

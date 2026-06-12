import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process11.activities import AsyncActImpl
from temporal_learn.process11.workflow import AsyncWf

TASK_QUEUE = "test-process11-integration-q"


@pytest.mark.asyncio
async def test_async_activity_completion_with_real_client(env: WorkflowEnvironment):
    acts = AsyncActImpl(env.client)
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[AsyncWf],
        activities=[acts.wait_external],
    ):
        result = await env.client.execute_workflow(
            AsyncWf.run,
            "X1",
            id=f"test-process11-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result == "READY-X1"

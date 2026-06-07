import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process8.workflow import AwaitWorkflow

TASK_QUEUE = "test-process8-integration-q"


@pytest.mark.asyncio
async def test_signal_before_timeout_returns_ready(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[AwaitWorkflow],
    ):
        handle = await env.client.start_workflow(
            AwaitWorkflow.run,
            id=f"test-process8-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.signal(AwaitWorkflow.mark_ready)
        assert await handle.result() == "READY"

import uuid
from datetime import timedelta

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process6.workflow import MyWorkflow

TASK_QUEUE = "test-process6-integration-q"


@pytest.mark.asyncio
async def test_workflow_completes_when_not_cancelled(env: WorkflowEnvironment):
    # start_time_skipping 會快速跳過 workflow 內的兩小時 sleep。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[MyWorkflow],
    ):
        handle = await env.client.start_workflow(
            MyWorkflow.run,
            "payload",
            id=f"test-process6-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await env.sleep(timedelta(hours=2))
        assert await handle.result() == "zero"

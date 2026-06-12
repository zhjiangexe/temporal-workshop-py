import uuid
from datetime import timedelta

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process8.workflow import AwaitWorkflow

TASK_QUEUE = "test-process8-workflow-q"


@pytest.mark.asyncio
async def test_signal_before_timeout_returns_ready(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[AwaitWorkflow],
    ):
        handle = await env.client.start_workflow(
            AwaitWorkflow.run,
            id=f"test-await-ready-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.signal(AwaitWorkflow.mark_ready)
        assert await handle.result() == "READY"


@pytest.mark.asyncio
async def test_timeout_without_signal_returns_timeout(env: WorkflowEnvironment):
    # time skipping 直接跳過一小時，快速驗證 timeout 分支。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[AwaitWorkflow],
    ):
        handle = await env.client.start_workflow(
            AwaitWorkflow.run,
            id=f"test-await-timeout-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await env.sleep(timedelta(hours=1))
        assert await handle.result() == "TIMEOUT"

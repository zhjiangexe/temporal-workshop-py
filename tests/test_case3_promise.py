import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.case3.workflow import PromiseWorkflow

TASK_QUEUE = "test-promise-q"


@pytest.mark.asyncio
async def test_promise_workflow_completes(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[PromiseWorkflow],
    ):
        await env.client.execute_workflow(
            PromiseWorkflow.execute,
            id=f"test-promise-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

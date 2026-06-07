import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.case2.workflow import CompensationWorkflow

TASK_QUEUE = "test-compensation-q"


@pytest.mark.asyncio
async def test_compensation_workflow_completes(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[CompensationWorkflow],
    ):
        await env.client.execute_workflow(
            CompensationWorkflow.execute,
            id=f"test-compensation-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process9.workflow import VerWorkflow

TASK_QUEUE = "test-process9-integration-q"


@pytest.mark.asyncio
async def test_versioned_workflow_with_real_definition(env: WorkflowEnvironment):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[VerWorkflow],
    ):
        result = await env.client.execute_workflow(
            VerWorkflow.run,
            "neo",
            id=f"test-process9-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result == "Hey neo"

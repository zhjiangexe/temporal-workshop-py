import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process9.workflow import VerWorkflow

TASK_QUEUE = "test-process9-workflow-q"


@pytest.mark.asyncio
async def test_new_runs_take_v2_branch(env: WorkflowEnvironment):
    # 新 workflow execution 應走 patched("greet-change-v2") 的最新分支。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[VerWorkflow],
    ):
        result = await env.client.execute_workflow(
            VerWorkflow.run,
            "neo",
            id=f"test-ver-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result == "Hey neo"

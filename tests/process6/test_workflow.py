import uuid

import pytest
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import CancelledError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process6.workflow import MyWorkflow

TASK_QUEUE = "test-process6-workflow-q"


@pytest.mark.asyncio
async def test_cancel_workflow(env: WorkflowEnvironment):
    # 驗證 cancellation 會傳進 workflow，且 workflow 重新丟出 CancelledError。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[MyWorkflow],
    ):
        handle = await env.client.start_workflow(
            MyWorkflow.run,
            "payload",
            id=f"test-cancel-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.cancel()
        with pytest.raises(WorkflowFailureError) as exc_info:
            await handle.result()
        assert isinstance(exc_info.value.cause, CancelledError)

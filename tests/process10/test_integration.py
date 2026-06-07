import uuid

import pytest
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import CancelledError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process10.activities import long_running_act
from temporal_learn.process10.workflow import LongActWorkflow

TASK_QUEUE = "test-process10-integration-q"


@pytest.mark.asyncio
async def test_cancel_workflow_while_real_activity_running(env: WorkflowEnvironment):
    # 真 workflow + 真 activity，確認 workflow cancellation 會取消 activity。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[LongActWorkflow],
        activities=[long_running_act],
    ):
        handle = await env.client.start_workflow(
            LongActWorkflow.run,
            id=f"test-process10-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.cancel()
        with pytest.raises(WorkflowFailureError) as exc_info:
            await handle.result()
        assert isinstance(exc_info.value.cause, CancelledError)

import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process4 import activities as process4_activities
from temporal_learn.process4.activities import process_dataset
from temporal_learn.process4.models import LongJobSpec
from temporal_learn.process4.workflow import LongJobWorkflow

TASK_QUEUE = "test-process4-integration-q"


async def _no_sleep(seconds: float) -> None:
    # Integration test 使用真 activity，但移除 demo sleep。
    return None


@pytest.mark.asyncio
async def test_long_job_workflow_with_real_activity(
    env: WorkflowEnvironment, monkeypatch
):
    monkeypatch.setattr(process4_activities.asyncio, "sleep", _no_sleep)
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[LongJobWorkflow],
        activities=[process_dataset],
    ):
        await env.client.execute_workflow(
            LongJobWorkflow.run,
            LongJobSpec(dataset_id="test-ds", total=5),
            id=f"test-process4-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process4.models import LongJobSpec
from temporal_learn.process4.workflow import LongJobWorkflow

TASK_QUEUE = "test-process4-workflow-q"


class TrackingLongJobActivities:
    # Workflow test 用同名 activity stub，專注驗證 workflow 是否正確排程 activity。
    def __init__(self):
        self.calls: list[LongJobSpec] = []

    @activity.defn(name="process_dataset")
    async def process_dataset(self, spec: LongJobSpec) -> int:
        self.calls.append(spec)
        return spec.total - 1


@pytest.mark.asyncio
async def test_long_job_workflow_schedules_dataset_activity(env: WorkflowEnvironment):
    acts = TrackingLongJobActivities()
    spec = LongJobSpec(dataset_id="test-ds", total=5)
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[LongJobWorkflow],
        activities=[acts.process_dataset],
    ):
        await env.client.execute_workflow(
            LongJobWorkflow.run,
            spec,
            id=f"test-longjob-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert acts.calls == [spec]

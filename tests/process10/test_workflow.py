import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process10.workflow import LongActWorkflow

TASK_QUEUE = "test-process10-workflow-q"


class TrackingLongActActivities:
    def __init__(self):
        self.calls = 0

    @activity.defn(name="long_running_act")
    async def long_running_act(self) -> str:
        self.calls += 1
        return "DONE"


@pytest.mark.asyncio
async def test_workflow_schedules_long_activity(env: WorkflowEnvironment):
    acts = TrackingLongActActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[LongActWorkflow],
        activities=[acts.long_running_act],
    ):
        await env.client.execute_workflow(
            LongActWorkflow.run,
            id=f"test-cancel-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert acts.calls == 1

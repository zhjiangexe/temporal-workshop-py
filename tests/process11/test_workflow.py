import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process11.workflow import AsyncWf

TASK_QUEUE = "test-process11-workflow-q"


class TrackingAsyncActivities:
    def __init__(self):
        self.calls: list[str] = []

    @activity.defn(name="wait_external")
    async def wait_external(self, id: str) -> str:
        self.calls.append(id)
        return f"READY-{id}"


@pytest.mark.asyncio
async def test_workflow_waits_for_external_activity(env: WorkflowEnvironment):
    acts = TrackingAsyncActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[AsyncWf],
        activities=[acts.wait_external],
    ):
        result = await env.client.execute_workflow(
            AsyncWf.run,
            "X1",
            id=f"test-async-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result == "READY-X1"
    assert acts.calls == ["X1"]

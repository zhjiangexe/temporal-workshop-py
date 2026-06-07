import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process7.workflow import GreetingWorkflow

TASK_QUEUE = "test-process7-workflow-q"


class TrackingGreetingActivities:
    # Workflow test 用 stub activity 驗證 update 後的狀態會傳給 activity。
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    @activity.defn(name="compose_greeting")
    async def compose_greeting(self, greeting: str, name: str) -> str:
        self.calls.append((greeting, name))
        return f"{greeting}, {name}!"


@pytest.mark.asyncio
async def test_greet_with_update(env: WorkflowEnvironment):
    acts = TrackingGreetingActivities()
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[GreetingWorkflow],
        activities=[acts.compose_greeting],
    ):
        handle = await env.client.start_workflow(
            GreetingWorkflow.greet,
            "Alice",
            id=f"test-greeting-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        assert await handle.query(GreetingWorkflow.get_greeting) == "Hello"
        await handle.execute_update(GreetingWorkflow.update_greeting, "Howdy")
        assert await handle.result() == "Howdy, Alice!"

    assert acts.calls == [("Howdy", "Alice")]

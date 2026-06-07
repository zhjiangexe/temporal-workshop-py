import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process1 import activities as process1_activities
from temporal_learn.process1.activities import RegistrationActivities
from temporal_learn.process1.models import RegisterRequest
from temporal_learn.process1.workflow import RegistrationWorkflow

TASK_QUEUE = "test-process1-integration-q"


async def _no_sleep(seconds: float) -> None:
    # Integration test 使用真 activity，但移除示範用等待時間。
    return None


@pytest.mark.asyncio
async def test_registration_workflow_with_real_activities(
    env: WorkflowEnvironment, monkeypatch
):
    monkeypatch.setattr(process1_activities.asyncio, "sleep", _no_sleep)
    acts = RegistrationActivities()
    user_id = str(uuid.uuid7())
    email = "test@example.com"

    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[RegistrationWorkflow],
        activities=[acts.create_account, acts.add_points, acts.send_email],
    ):
        await env.client.execute_workflow(
            RegistrationWorkflow.register,
            RegisterRequest(user_id=user_id, email=email),
            id=f"test-process1-real-{user_id}",
            task_queue=TASK_QUEUE,
        )

    # 端到端確認 workflow 真的推動真 activity，並留下預期的 in-memory 狀態。
    assert acts._users == {user_id}
    assert acts._ops == {
        f"POINTS#{user_id}#signupBonus",
        f"EMAIL#welcome-{user_id}",
    }

import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process1.models import RegisterRequest
from temporal_learn.process1.workflow import RegistrationWorkflow

TASK_QUEUE = "test-process1-workflow-q"


@pytest.mark.asyncio
async def test_registration_workflow_runs_steps_in_order(env: WorkflowEnvironment):
    calls: list[tuple[str, tuple[object, ...]]] = []

    # Workflow test 只關心「編排順序與參數」；activity 用同名 stub 取代真實實作。
    @activity.defn(name="create_account")
    async def create_account_stub(request: RegisterRequest) -> None:
        calls.append(("create_account", (request.user_id, request.email)))

    @activity.defn(name="add_points")
    async def add_points_stub(user_id: str, points: int, op_key: str) -> None:
        calls.append(("add_points", (user_id, points, op_key)))

    @activity.defn(name="send_email")
    async def send_email_stub(email: str, message_id: str) -> None:
        calls.append(("send_email", (email, message_id)))

    # Worker 註冊 workflow 與測試用 activities，讓 workflow 在測試環境內實際執行。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[RegistrationWorkflow],
        activities=[create_account_stub, add_points_stub, send_email_stub],
    ):
        user_id = str(uuid.uuid7())
        email = "test@example.com"
        await env.client.execute_workflow(
            RegistrationWorkflow.register,
            RegisterRequest(user_id=user_id, email=email),
            id=f"test-reg-{user_id}",
            task_queue=TASK_QUEUE,
        )

    # 驗證 workflow 是否依教材順序呼叫三個 activity，並傳入正確參數。
    assert calls == [
        ("create_account", (user_id, email)),
        ("add_points", (user_id, 500, "signupBonus")),
        ("send_email", (email, f"welcome-{user_id}")),
    ]

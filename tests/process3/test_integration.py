import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process3 import activities as process3_activities
from temporal_learn.process3.activities import (
    apply_new_price,
    notify_reviewer,
    record_decision,
)
from temporal_learn.process3.models import (
    ProductChangeSpec,
    ReviewDecision,
    ReviewOutcome,
)
from temporal_learn.process3.workflow import ProductChangeWorkflow

TASK_QUEUE = "test-process3-integration-q"
ALL_ACTIVITIES = [notify_reviewer, record_decision, apply_new_price]


async def _no_sleep(seconds: float) -> None:
    # Integration test 使用真 activity，但移除 demo sleep。
    return None


def _make_spec() -> ProductChangeSpec:
    return ProductChangeSpec(
        request_id=f"REQ-{uuid.uuid7()}",
        product_id="P001",
        new_price=1490.0,
    )


@pytest.mark.asyncio
async def test_price_change_workflow_with_real_activities(
    env: WorkflowEnvironment, monkeypatch
):
    monkeypatch.setattr(process3_activities.asyncio, "sleep", _no_sleep)
    # 真 workflow + 真 activity：確認 update 進來後端到端完成。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductChangeWorkflow],
        activities=ALL_ACTIVITIES,
    ):
        handle = await env.client.start_workflow(
            ProductChangeWorkflow.run,
            _make_spec(),
            id=f"test-process3-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.execute_update(
            ProductChangeWorkflow.update,
            ReviewDecision(outcome=ReviewOutcome.APPROVE, approver_id="tester"),
        )
        await handle.result()

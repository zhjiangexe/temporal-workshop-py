import uuid
from datetime import timedelta

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process3.models import (
    ProductChangeSpec,
    ReviewDecision,
    ReviewOutcome,
)
from temporal_learn.process3.workflow import ProductChangeWorkflow

TASK_QUEUE = "test-process3-workflow-q"


def _make_spec() -> ProductChangeSpec:
    return ProductChangeSpec(
        request_id=f"REQ-{uuid.uuid7()}",
        product_id="P001",
        new_price=1490.0,
    )


class TrackingPriceChangeActivities:
    # Workflow test 用同名 stub activity 觀察流程，不測 print / sleep 等 activity 細節。
    def __init__(self):
        self.calls: list[tuple[str, object]] = []

    @activity.defn(name="notify_reviewer")
    async def notify_reviewer(self, spec: ProductChangeSpec) -> None:
        self.calls.append(("notify", spec.product_id))

    @activity.defn(name="record_decision")
    async def record_decision(
        self, spec: ProductChangeSpec, decision: ReviewDecision
    ) -> None:
        self.calls.append(("record", decision.outcome))

    @activity.defn(name="apply_new_price")
    async def apply_new_price(self, spec: ProductChangeSpec) -> None:
        self.calls.append(("apply", spec.new_price))

    def activities(self):
        return [
            self.notify_reviewer,
            self.record_decision,
            self.apply_new_price,
        ]


@pytest.mark.asyncio
async def test_approve_applies_new_price(env: WorkflowEnvironment):
    acts = TrackingPriceChangeActivities()
    # 啟動 workflow 後用 update 模擬審核者核准，預期最後會套用新價格。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductChangeWorkflow],
        activities=acts.activities(),
    ):
        handle = await env.client.start_workflow(
            ProductChangeWorkflow.run,
            _make_spec(),
            id=f"test-price-approve-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.execute_update(
            ProductChangeWorkflow.update,
            ReviewDecision(
                outcome=ReviewOutcome.APPROVE,
                approver_id="tester",
            ),
        )
        await handle.result()

    assert acts.calls == [
        ("notify", "P001"),
        ("record", ReviewOutcome.APPROVE),
        ("apply", 1490.0),
    ]


@pytest.mark.asyncio
async def test_reject_skips_price_apply(env: WorkflowEnvironment):
    acts = TrackingPriceChangeActivities()
    # 拒絕時 workflow 仍需記錄決策，但不可呼叫 apply_new_price。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductChangeWorkflow],
        activities=acts.activities(),
    ):
        handle = await env.client.start_workflow(
            ProductChangeWorkflow.run,
            _make_spec(),
            id=f"test-price-reject-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await handle.execute_update(
            ProductChangeWorkflow.update,
            ReviewDecision(
                outcome=ReviewOutcome.REJECT,
                approver_id="tester",
                reason="too expensive",
            ),
        )
        await handle.result()

    assert acts.calls == [
        ("notify", "P001"),
        ("record", ReviewOutcome.REJECT),
    ]


@pytest.mark.asyncio
async def test_timeout_auto_rejects(env: WorkflowEnvironment):
    acts = TrackingPriceChangeActivities()
    # start_time_skipping 環境可直接跳過 49 小時，快速測 48 小時 timeout 分支。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductChangeWorkflow],
        activities=acts.activities(),
    ):
        handle = await env.client.start_workflow(
            ProductChangeWorkflow.run,
            _make_spec(),
            id=f"test-price-timeout-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )
        await env.sleep(timedelta(hours=49))
        await handle.result()

    assert acts.calls == [
        ("notify", "P001"),
        ("record", ReviewOutcome.REJECT),
    ]

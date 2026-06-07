import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process2 import activities as process2_activities
from temporal_learn.process2.activities import (
    create_or_update_product,
    delete_product,
    publish_to_storefront,
    revert_pricing_and_availability,
    setup_pricing_and_availability,
    unpublish_from_storefront,
)
from temporal_learn.process2.models import ProductInput
from temporal_learn.process2.workflow import ProductOnboardingWorkflow

TASK_QUEUE = "test-process2-integration-q"
ALL_ACTIVITIES = [
    create_or_update_product,
    setup_pricing_and_availability,
    publish_to_storefront,
    delete_product,
    revert_pricing_and_availability,
    unpublish_from_storefront,
]


async def _no_sleep(seconds: float) -> None:
    # Integration test 使用真 activity，但把示範用 sleep 改成 no-op。
    return None


def _make_input() -> ProductInput:
    return ProductInput(
        request_id=str(uuid.uuid7()),
        sku="SKU-TEST",
        name="Test Product",
        category="Shoes",
        currency="TWD",
        price=1990,
        visible=True,
    )


@pytest.mark.asyncio
async def test_onboarding_workflow_with_real_activities(
    env: WorkflowEnvironment, monkeypatch
):
    monkeypatch.setattr(process2_activities.asyncio, "sleep", _no_sleep)
    # 清掉失敗旗標，測真實 activity 的成功端到端路徑。
    monkeypatch.delenv("FAIL_PUBLISH", raising=False)
    product_input = _make_input()

    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductOnboardingWorkflow],
        activities=ALL_ACTIVITIES,
    ):
        result = await env.client.execute_workflow(
            ProductOnboardingWorkflow.run,
            product_input,
            id=f"test-process2-real-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result.published is True
    assert result.product_id == product_input.request_id
    assert result.message == "Product published via STP"


@pytest.mark.asyncio
async def test_onboarding_workflow_failure_with_real_activities(
    env: WorkflowEnvironment, monkeypatch
):
    monkeypatch.setattr(process2_activities.asyncio, "sleep", _no_sleep)
    # 透過真 activity 的 FAIL_PUBLISH 分支觸發 workflow 補償。
    monkeypatch.setenv("FAIL_PUBLISH", "1")

    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductOnboardingWorkflow],
        activities=ALL_ACTIVITIES,
    ):
        result = await env.client.execute_workflow(
            ProductOnboardingWorkflow.run,
            _make_input(),
            id=f"test-process2-real-fail-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result.published is False
    assert result.product_id == ""
    assert "Compensation executed" in result.message

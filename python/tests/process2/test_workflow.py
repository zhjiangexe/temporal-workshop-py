import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_learn.process2.models import ProductInput
from temporal_learn.process2.workflow import ProductOnboardingWorkflow

TASK_QUEUE = "test-process2-workflow-q"


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


class TrackingProductActivities:
    # 用同名 activity stub 記錄呼叫，讓 workflow test 專注驗證補償編排。
    def __init__(self, fail_publish: bool = False):
        self.calls: list[str] = []
        self.fail_publish = fail_publish

    @activity.defn(name="create_or_update_product")
    async def create_or_update_product(self, product_id: str) -> str:
        self.calls.append("create")
        return product_id

    @activity.defn(name="setup_pricing_and_availability")
    async def setup_pricing_and_availability(self, product_id: str) -> None:
        self.calls.append("setup")

    @activity.defn(name="publish_to_storefront")
    async def publish_to_storefront(self, product_id: str) -> None:
        self.calls.append("publish")
        if self.fail_publish:
            raise RuntimeError("storefront down")

    @activity.defn(name="delete_product")
    async def delete_product(self, product_id: str) -> None:
        self.calls.append("delete")

    @activity.defn(name="revert_pricing_and_availability")
    async def revert_pricing_and_availability(self, product_id: str) -> None:
        self.calls.append("revert")

    @activity.defn(name="unpublish_from_storefront")
    async def unpublish_from_storefront(self, product_id: str) -> None:
        self.calls.append("unpublish")

    def activities(self):
        return [
            self.create_or_update_product,
            self.setup_pricing_and_availability,
            self.publish_to_storefront,
            self.delete_product,
            self.revert_pricing_and_availability,
            self.unpublish_from_storefront,
        ]


@pytest.mark.asyncio
async def test_onboarding_success(env: WorkflowEnvironment):
    acts = TrackingProductActivities()
    product_input = _make_input()
    # 成功路徑只會執行三個正向 activity，不應觸發補償 activity。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductOnboardingWorkflow],
        activities=acts.activities(),
    ):
        result = await env.client.execute_workflow(
            ProductOnboardingWorkflow.run,
            product_input,
            id=f"test-onboard-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result.published is True
    assert result.product_id == product_input.request_id
    assert result.message == "Product published via STP"
    assert acts.calls == ["create", "setup", "publish"]


@pytest.mark.asyncio
async def test_onboarding_compensation_on_failure(env: WorkflowEnvironment):
    acts = TrackingProductActivities(fail_publish=True)
    # publish 失敗會依 workflow 的 RetryPolicy 重試兩次，最後才執行補償。
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProductOnboardingWorkflow],
        activities=acts.activities(),
    ):
        result = await env.client.execute_workflow(
            ProductOnboardingWorkflow.run,
            _make_input(),
            id=f"test-onboard-fail-{uuid.uuid7()}",
            task_queue=TASK_QUEUE,
        )

    assert result.published is False
    assert result.product_id == ""
    assert "Compensation executed" in result.message
    # 補償順序是 LIFO：publish 的補償 unpublish 先跑，最後才 delete。
    assert acts.calls == [
        "create",
        "setup",
        "publish",
        "publish",
        "unpublish",
        "revert",
        "delete",
    ]

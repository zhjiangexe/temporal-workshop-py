import importlib
import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker


class TrackingProductActivities:
    def __init__(self, fail_create: bool = False, fail_publish: bool = False):
        self.calls: list[str] = []
        self.fail_create = fail_create
        self.fail_publish = fail_publish

    @activity.defn(name="create_or_update_product")
    async def create_or_update_product(self, product_id: str) -> str:
        self.calls.append("create")
        if self.fail_create:
            raise RuntimeError("catalog down")
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


@pytest.mark.parametrize("module_name", ["process2_1", "process2_2"])
@pytest.mark.asyncio
async def test_process2_versions_success(
    env: WorkflowEnvironment, module_name: str
):
    models = importlib.import_module(f"temporal_learn.{module_name}.models")
    workflow_mod = importlib.import_module(f"temporal_learn.{module_name}.workflow")
    workflow_cls = workflow_mod.ProductOnboardingWorkflow
    product_input = _make_input(models.ProductInput)
    acts = TrackingProductActivities()

    async with Worker(
        env.client,
        task_queue=f"test-{module_name}-workflow-q",
        workflows=[workflow_cls],
        activities=acts.activities(),
    ):
        result = await env.client.execute_workflow(
            workflow_cls.run,
            product_input,
            id=f"test-{module_name}-{uuid.uuid7()}",
            task_queue=f"test-{module_name}-workflow-q",
        )

    assert result.published is True
    assert result.product_id == product_input.request_id
    assert acts.calls == ["create", "setup", "publish"]


@pytest.mark.parametrize("module_name", ["process2_1", "process2_2"])
@pytest.mark.asyncio
async def test_process2_versions_compensate_on_failure(
    env: WorkflowEnvironment, module_name: str
):
    models = importlib.import_module(f"temporal_learn.{module_name}.models")
    workflow_mod = importlib.import_module(f"temporal_learn.{module_name}.workflow")
    workflow_cls = workflow_mod.ProductOnboardingWorkflow
    acts = TrackingProductActivities(fail_publish=True)

    async with Worker(
        env.client,
        task_queue=f"test-{module_name}-workflow-fail-q",
        workflows=[workflow_cls],
        activities=acts.activities(),
    ):
        result = await env.client.execute_workflow(
            workflow_cls.run,
            _make_input(models.ProductInput),
            id=f"test-{module_name}-fail-{uuid.uuid7()}",
            task_queue=f"test-{module_name}-workflow-fail-q",
        )

    assert result.published is False
    assert result.product_id == ""
    assert "Compensation executed" in result.message
    assert acts.calls == [
        "create",
        "setup",
        "publish",
        "publish",
        "unpublish",
        "revert",
        "delete",
    ]


@pytest.mark.parametrize("module_name", ["process2_1", "process2_2"])
@pytest.mark.asyncio
async def test_process2_versions_compensate_even_when_first_activity_fails(
    env: WorkflowEnvironment, module_name: str
):
    models = importlib.import_module(f"temporal_learn.{module_name}.models")
    workflow_mod = importlib.import_module(f"temporal_learn.{module_name}.workflow")
    workflow_cls = workflow_mod.ProductOnboardingWorkflow
    acts = TrackingProductActivities(fail_create=True)

    async with Worker(
        env.client,
        task_queue=f"test-{module_name}-workflow-create-fail-q",
        workflows=[workflow_cls],
        activities=acts.activities(),
    ):
        result = await env.client.execute_workflow(
            workflow_cls.run,
            _make_input(models.ProductInput),
            id=f"test-{module_name}-create-fail-{uuid.uuid7()}",
            task_queue=f"test-{module_name}-workflow-create-fail-q",
        )

    assert result.published is False
    assert result.product_id == ""
    assert "Compensation executed" in result.message
    assert acts.calls == ["create", "create", "delete"]


def _make_input(product_input_cls):
    return product_input_cls(
        request_id=str(uuid.uuid7()),
        sku="SKU-TEST",
        name="Test Product",
        category="Shoes",
        currency="TWD",
        price=1990,
        visible=True,
    )

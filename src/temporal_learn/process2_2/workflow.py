from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..shared.saga import Saga

with workflow.unsafe.imports_passed_through():
    from .activities import (
        create_or_update_product,
        delete_product,
        publish_to_storefront,
        revert_pricing_and_availability,
        setup_pricing_and_availability,
        unpublish_from_storefront,
    )
    from .models import ProductInput, ProductPublishResult

_RETRY = RetryPolicy(
    maximum_attempts=2,
    initial_interval=timedelta(seconds=5),
    backoff_coefficient=2.0,
)
_ACT_CFG: workflow.ActivityConfig = {
    "schedule_to_close_timeout": timedelta(seconds=15),  # 示範用，縮短等待時間
    "retry_policy": _RETRY,
}


@workflow.defn
class ProductOnboardingWorkflow:
    @workflow.run
    async def run(self, input: ProductInput) -> ProductPublishResult:
        # Saga helper 只封裝補償清單與反向執行；Temporal 核心仍是 Workflow 呼叫 Activity。
        saga = Saga()
        try:
            product_id = input.request_id
            # create_or_update_product and compensate delete_product
            saga.add_activity_compensation(delete_product, product_id, **_ACT_CFG)
            product_id = await workflow.execute_activity(
                create_or_update_product, product_id, **_ACT_CFG
            )

            # setup_pricing_and_availability and compensate revert_pricing_and_availability
            saga.add_activity_compensation(
                revert_pricing_and_availability, product_id, **_ACT_CFG
            )
            await workflow.execute_activity(
                setup_pricing_and_availability, product_id, **_ACT_CFG
            )

            # publish_to_storefront and compensate unpublish_from_storefront
            saga.add_activity_compensation(
                unpublish_from_storefront, product_id, **_ACT_CFG
            )
            await workflow.execute_activity(
                publish_to_storefront, product_id, **_ACT_CFG
            )

            return ProductPublishResult(
                product_id=product_id,
                published=True,
                message="Product published via STP",
            )
        except Exception as e:
            # 任何步驟失敗都進入補償，後完成的步驟先回滾。
            await saga.compensate()
            return ProductPublishResult(
                published=False,
                message=f"Failed to publish product. Compensation executed: {e}",
            )

from collections.abc import Awaitable, Callable
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from .activities import (
    create_or_update_product,
    delete_product,
    publish_to_storefront,
    revert_pricing_and_availability,
    setup_pricing_and_availability,
    unpublish_from_storefront,
)
from .models import ProductInput, ProductPublishResult

_ACT_CFG: workflow.ActivityConfig = {
    "schedule_to_close_timeout": timedelta(seconds=15),  # 示範用，縮短等待時間
    "retry_policy": RetryPolicy(
        maximum_attempts=2,
        initial_interval=timedelta(seconds=5),
        backoff_coefficient=2.0,
    ),
}


@workflow.defn
class ProductOnboardingWorkflow:
    @workflow.run
    async def run(self, input: ProductInput) -> ProductPublishResult:
        # 正向步驟執行前先登記對應補償，處理 Activity timeout 但外部副作用已發生的情境。
        # 補償 Activity 必須是 idempotent/conditional：狀態不存在時直接視為成功。
        # 失敗時反向執行，確保 unpublish -> revert -> delete 的因果順序。
        compensations: list[Callable[[], Awaitable[None]]] = []
        try:
            product_id = input.request_id
            compensations.append(
                lambda pid=product_id: workflow.execute_activity(
                    delete_product, pid, **_ACT_CFG
                )
            )
            product_id = await workflow.execute_activity(
                create_or_update_product, product_id, **_ACT_CFG
            )

            compensations.append(
                lambda pid=product_id: workflow.execute_activity(
                    revert_pricing_and_availability, pid, **_ACT_CFG
                )
            )
            await workflow.execute_activity(
                setup_pricing_and_availability, product_id, **_ACT_CFG
            )

            compensations.append(
                lambda pid=product_id: workflow.execute_activity(
                    unpublish_from_storefront, pid, **_ACT_CFG
                )
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
            for compensate in reversed(compensations):
                await compensate()
            return ProductPublishResult(
                published=False,
                message=f"Failed to publish product. Compensation executed: {e}",
            )

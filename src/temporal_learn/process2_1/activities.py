import asyncio
import os

from temporalio import activity

# 正向步驟：依序執行，完成後推進業務流程
# -----------------------------------------------------------------------------
# Activity: create_or_update_product
@activity.defn
async def create_or_update_product(product_id: str) -> str:
    await asyncio.sleep(5)
    print(f"create or update product: {product_id}")
    return product_id


# -----------------------------------------------------------------------------
# Activity: setup_pricing_and_availability
@activity.defn
async def setup_pricing_and_availability(product_id: str) -> None:
    await asyncio.sleep(5)
    print(f"setup pricing and availability: {product_id}")


# -----------------------------------------------------------------------------
# Activity: publish_to_storefront
@activity.defn
async def publish_to_storefront(product_id: str) -> None:
    if os.getenv("FAIL_PUBLISH"):
        raise RuntimeError("模擬上架失敗（FAIL_PUBLISH=1）")
    await asyncio.sleep(5)
    print(f"publish to storefront: {product_id}")


# 補償步驟：每個正向步驟都要有對應的回滾操作，一一配對
# -----------------------------------------------------------------------------
# Activity: delete_product
@activity.defn
async def delete_product(product_id: str) -> None:  # ← 對應 create_or_update_product
    await asyncio.sleep(10)
    print(f"delete product: {product_id}")


# -----------------------------------------------------------------------------
# Activity: revert_pricing_and_availability
@activity.defn
async def revert_pricing_and_availability(
    product_id: str,
) -> None:  # ← 對應 setup_pricing_and_availability
    await asyncio.sleep(10)
    print(f"revert pricing {product_id}")


# -----------------------------------------------------------------------------
# Activity: unpublish_from_storefront
@activity.defn
async def unpublish_from_storefront(
    product_id: str,
) -> None:  # ← 對應 publish_to_storefront
    await asyncio.sleep(10)
    print(f"unpublish: {product_id}")

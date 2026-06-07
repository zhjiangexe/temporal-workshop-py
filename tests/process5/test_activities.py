import pytest
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

from temporal_learn.process5.activities import InventoryActivities


@pytest.mark.asyncio
async def test_restock_is_idempotent_by_op_key():
    activity_env = ActivityEnvironment()
    acts = InventoryActivities()

    first = await activity_env.run(acts.restock, "sku-1", 10, "op-1")
    second = await activity_env.run(acts.restock, "sku-1", 10, "op-1")

    assert first == 10
    assert second == 10
    assert acts._stock_by_product == {"sku-1": 10}


@pytest.mark.asyncio
async def test_purchase_is_idempotent_by_op_key():
    activity_env = ActivityEnvironment()
    acts = InventoryActivities()

    await activity_env.run(acts.restock, "sku-1", 100, "init")
    first = await activity_env.run(acts.purchase, "sku-1", 30, "buy-1")
    second = await activity_env.run(acts.purchase, "sku-1", 30, "buy-1")

    assert first == 70
    assert second == 70
    assert acts._stock_by_product == {"sku-1": 70}


@pytest.mark.asyncio
async def test_purchase_rejects_insufficient_stock():
    activity_env = ActivityEnvironment()
    acts = InventoryActivities()

    with pytest.raises(ApplicationError) as exc_info:
        await activity_env.run(acts.purchase, "sku-1", 1, "buy-1")

    assert exc_info.value.type == "StockError"

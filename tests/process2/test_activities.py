import pytest
from temporalio.testing import ActivityEnvironment

from temporal_learn.process2 import activities as process2_activities
from temporal_learn.process2.activities import (
    create_or_update_product,
    delete_product,
    publish_to_storefront,
    revert_pricing_and_availability,
    setup_pricing_and_availability,
    unpublish_from_storefront,
)


async def _no_sleep(seconds: float) -> None:
    # process2 的 activity 用 sleep 模擬外部系統，單元測試不等待真實秒數。
    return None


@pytest.mark.asyncio
async def test_create_or_update_product_returns_request_id(monkeypatch):
    monkeypatch.setattr(process2_activities.asyncio, "sleep", _no_sleep)
    # 用 ActivityEnvironment 跑真 activity，保留 Temporal activity context。
    activity_env = ActivityEnvironment()

    product_id = await activity_env.run(create_or_update_product, "REQ-001")

    assert product_id == "REQ-001"


@pytest.mark.asyncio
async def test_publish_to_storefront_respects_failure_flag(monkeypatch):
    monkeypatch.setattr(process2_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()

    # 沒有 FAIL_PUBLISH 時，publish activity 應正常完成。
    monkeypatch.delenv("FAIL_PUBLISH", raising=False)
    await activity_env.run(publish_to_storefront, "P001")

    # 設定 FAIL_PUBLISH 時，activity 應丟錯，讓 workflow 進入補償流程。
    monkeypatch.setenv("FAIL_PUBLISH", "1")
    with pytest.raises(RuntimeError, match="模擬上架失敗"):
        await activity_env.run(publish_to_storefront, "P001")


@pytest.mark.asyncio
async def test_compensation_activities_complete(monkeypatch):
    monkeypatch.setattr(process2_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()

    # 補償 activity 本身應可被獨立執行；順序由 workflow 測試負責驗證。
    await activity_env.run(setup_pricing_and_availability, "P001")
    await activity_env.run(unpublish_from_storefront, "P001")
    await activity_env.run(revert_pricing_and_availability, "P001")
    await activity_env.run(delete_product, "P001")

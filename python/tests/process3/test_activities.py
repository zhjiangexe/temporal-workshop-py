import pytest
from temporalio.testing import ActivityEnvironment

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


async def _no_sleep(seconds: float) -> None:
    # process3 的 activity 用 sleep 模擬人工審核/寫入外部系統，測試中略過等待。
    return None


def _make_spec() -> ProductChangeSpec:
    return ProductChangeSpec(
        request_id="REQ-001",
        product_id="P001",
        new_price=1490.0,
    )


@pytest.mark.asyncio
async def test_notify_reviewer_outputs_review_request(monkeypatch, capsys):
    monkeypatch.setattr(process3_activities.asyncio, "sleep", _no_sleep)
    # ActivityEnvironment 讓 activity 在 Temporal activity context 中執行。
    activity_env = ActivityEnvironment()

    await activity_env.run(notify_reviewer, _make_spec())

    assert "[NOTIFY] requestId=REQ-001 newPrice=1490.00 product=P001" in (
        capsys.readouterr().out
    )


@pytest.mark.asyncio
async def test_record_decision_outputs_review_result(monkeypatch, capsys):
    monkeypatch.setattr(process3_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()

    # 驗證審核結果會被正確格式化，之後 workflow test 再驗證何時呼叫它。
    await activity_env.run(
        record_decision,
        _make_spec(),
        ReviewDecision(outcome=ReviewOutcome.APPROVE, approver_id="tester"),
    )

    assert "[RECORD] requestId=REQ-001, product=P001, review=approve" in (
        capsys.readouterr().out
    )


@pytest.mark.asyncio
async def test_apply_new_price_outputs_price_change(monkeypatch, capsys):
    monkeypatch.setattr(process3_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()

    # 價格套用 activity 目前以 print 模擬外部寫入，測輸出即可驗證輸入格式。
    await activity_env.run(apply_new_price, _make_spec())

    assert "[APPLY] requestId=REQ-001 set price=1490.00 for product=P001" in (
        capsys.readouterr().out
    )

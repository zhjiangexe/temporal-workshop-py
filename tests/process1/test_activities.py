from dataclasses import replace

import pytest
from temporalio.testing import ActivityEnvironment

from temporal_learn.process1 import activities as process1_activities
from temporal_learn.process1.activities import add_points, create_account, send_email
from temporal_learn.process1.models import RegisterRequest


async def _no_sleep(seconds: float) -> None:
    # 範例 activity 用 sleep 模擬外部 IO；單元測試改成 no-op 讓測試快速完成。
    return None


@pytest.mark.asyncio
async def test_create_account_is_idempotent(monkeypatch):
    monkeypatch.setattr(process1_activities.asyncio, "sleep", _no_sleep)
    process1_activities.reset_activity_state_for_test()
    # ActivityEnvironment 會建立 activity context，適合測真實 activity 函式。
    activity_env = ActivityEnvironment()
    request = RegisterRequest(user_id="U001", email="user@example.com")

    # 同一個 user_id 執行兩次，第二次應直接略過，不重複建立。
    await activity_env.run(create_account, request)
    await activity_env.run(create_account, request)

    assert process1_activities._demo_users == {"U001"}


@pytest.mark.asyncio
async def test_add_points_retries_before_recording_operation(monkeypatch):
    monkeypatch.setattr(process1_activities.asyncio, "sleep", _no_sleep)
    process1_activities.reset_activity_state_for_test()
    activity_env = ActivityEnvironment()

    # add_points 會讀 activity.info().attempt；用官方 ActivityEnvironment 設定 attempt。
    activity_env.info = replace(ActivityEnvironment.default_info(), attempt=1)
    with pytest.raises(RuntimeError, match="DB"):
        await activity_env.run(add_points, "U001", 500, "signupBonus")
    # 失敗時不能先記錄冪等鍵，否則 retry 會被誤判為已完成。
    assert process1_activities._demo_ops == set()

    # 模擬 Temporal retry 到第 4 次，activity 才真正成功並寫入冪等鍵。
    activity_env.info = replace(ActivityEnvironment.default_info(), attempt=4)
    await activity_env.run(add_points, "U001", 500, "signupBonus")
    await activity_env.run(add_points, "U001", 500, "signupBonus")

    assert process1_activities._demo_ops == {"POINTS#U001#signupBonus"}


@pytest.mark.asyncio
async def test_send_email_is_idempotent(monkeypatch):
    monkeypatch.setattr(process1_activities.asyncio, "sleep", _no_sleep)
    process1_activities.reset_activity_state_for_test()
    activity_env = ActivityEnvironment()

    # 同一個 message_id 重送時，應靠 EMAIL#message_id 略過重複副作用。
    await activity_env.run(send_email, "user@example.com", "welcome-U001")
    await activity_env.run(send_email, "user@example.com", "welcome-U001")

    assert process1_activities._demo_ops == {"EMAIL#welcome-U001"}

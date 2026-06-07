import pytest
from temporalio.testing import ActivityEnvironment

from temporal_learn.process10 import activities as process10_activities
from temporal_learn.process10.activities import long_running_act


async def _no_sleep(seconds: float) -> None:
    # 長 activity 用 sleep 模擬工作；單元測試只看 heartbeat 與結果。
    return None


@pytest.mark.asyncio
async def test_long_running_activity_heartbeats(monkeypatch):
    monkeypatch.setattr(process10_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()
    heartbeats: list[int] = []
    activity_env.on_heartbeat = lambda value: heartbeats.append(value)

    result = await activity_env.run(long_running_act)

    assert result == "DONE"
    assert heartbeats[:3] == [0, 1, 2]
    assert heartbeats[-1] == 999
    assert len(heartbeats) == 1000

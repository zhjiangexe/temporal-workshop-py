from dataclasses import replace

import pytest
from temporalio.testing import ActivityEnvironment

from temporal_learn.process4 import activities as process4_activities
from temporal_learn.process4.activities import process_dataset
from temporal_learn.process4.models import LongJobSpec


async def _no_sleep(seconds: float) -> None:
    # process4 用 sleep 模擬長工作；activity 單元測試不等待真實秒數。
    return None


@pytest.mark.asyncio
async def test_process_dataset_heartbeats_each_item(monkeypatch):
    monkeypatch.setattr(process4_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()
    heartbeats: list[int] = []
    activity_env.on_heartbeat = lambda value: heartbeats.append(value)

    result = await activity_env.run(
        process_dataset,
        LongJobSpec(dataset_id="ds-1", total=3),
    )

    assert result == 2
    assert heartbeats == [0, 1, 2]


@pytest.mark.asyncio
async def test_process_dataset_resumes_from_heartbeat_details(monkeypatch):
    monkeypatch.setattr(process4_activities.asyncio, "sleep", _no_sleep)
    activity_env = ActivityEnvironment()
    activity_env.info = replace(
        ActivityEnvironment.default_info(),
        heartbeat_details=[2],
    )
    heartbeats: list[int] = []
    activity_env.on_heartbeat = lambda value: heartbeats.append(value)

    result = await activity_env.run(
        process_dataset,
        LongJobSpec(dataset_id="ds-1", total=5),
    )

    assert result == 4
    assert heartbeats == [2, 3, 4]

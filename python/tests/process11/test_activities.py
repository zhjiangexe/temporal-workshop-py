import asyncio

import pytest
from temporalio import activity
from temporalio.testing import ActivityEnvironment

from temporal_learn.process11.activities import AsyncActImpl


class FakeAsyncActivityHandle:
    def __init__(self):
        self.completed_with: str | None = None

    async def complete(self, value: str) -> None:
        self.completed_with = value


class FakeClient:
    def __init__(self):
        self.handle = FakeAsyncActivityHandle()
        self.task_token: bytes | None = None

    def get_async_activity_handle(self, task_token: bytes):
        self.task_token = task_token
        return self.handle


@pytest.mark.asyncio
async def test_complete_later_uses_async_activity_handle():
    client = FakeClient()
    acts = AsyncActImpl(client)  # type: ignore[arg-type]

    await acts._complete_later(b"token-1", "X1")

    assert client.task_token == b"token-1"
    assert client.handle.completed_with == "READY-X1"


@pytest.mark.asyncio
async def test_wait_external_marks_activity_async_completion():
    activity_env = ActivityEnvironment()
    client = FakeClient()
    acts = AsyncActImpl(client)  # type: ignore[arg-type]

    with pytest.raises(activity._CompleteAsyncError):
        await activity_env.run(acts.wait_external, "X1")
    await asyncio.sleep(0)

    assert client.task_token == b"test"
    assert client.handle.completed_with == "READY-X1"

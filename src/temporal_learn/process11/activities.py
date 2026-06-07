import asyncio

from temporalio import activity
from temporalio.client import Client


class AsyncActImpl:
    def __init__(self, client: Client):
        self._client = client

    # -------------------------------------------------------------------------
    # Activity: wait_external
    @activity.defn
    async def wait_external(self, id: str) -> str:
        # task_token 是此 activity execution 的唯一識別符，外部系統用它來回呼完成
        token = activity.info().task_token
        asyncio.create_task(self._complete_later(token, id))
        # 非同步完成模式：把 token 交出去後立即返回，告訴 Temporal「結果由外部回呼決定」
        # 典型場景：activity 啟動一個外部 job，等 webhook 回來才算完成
        activity.raise_complete_async()

    async def _complete_later(self, token: bytes, id: str) -> None:
        # 模擬外部 webhook 回呼，生產環境這裡是真正的非同步完成機制
        handle = self._client.get_async_activity_handle(task_token=token)
        await handle.complete(f"READY-{id}")

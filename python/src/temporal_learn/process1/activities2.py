import asyncio

from temporalio import activity


# workshop 1.4 加入新步驟
# Activity: notify
@activity.defn
async def notify(user_id: str) -> None:
    # namespace#entity#operation 的複合鍵設計，確保不同操作的 key 不會碰撞
    await asyncio.sleep(5)
    print(f"Welcome {user_id}")

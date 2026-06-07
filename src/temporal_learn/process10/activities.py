import asyncio

from temporalio import activity


# -----------------------------------------------------------------------------
# Activity: long_running_act
@activity.defn
async def long_running_act() -> str:
    for i in range(1000):
        # 最簡 heartbeat 示範：只回報活性，不帶斷點資訊
        # 對比 process4：process4 的 heartbeat 同時儲存斷點用於重試後繼續
        activity.heartbeat(i)
        await asyncio.sleep(0.01)
    return "DONE"

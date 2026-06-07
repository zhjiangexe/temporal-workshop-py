import asyncio

from temporalio import activity

from .models import LongJobSpec


# -----------------------------------------------------------------------------
# Activity: process_dataset
@activity.defn
async def process_dataset(spec: LongJobSpec) -> int:
    info = activity.info()
    # 斷點續跑：重試時從上次 heartbeat 記錄的進度繼續，而非從頭開始
    start = int(info.heartbeat_details[0]) if info.heartbeat_details else 0

    for i in range(start, spec.total):
        await asyncio.sleep(0.5)
        # heartbeat 雙重作用：(1) 更新 Temporal server 的活性時鐘防超時，(2) 將 i 存為斷點
        activity.heartbeat(i)
        print(f"progress: {i} %")

    return spec.total - 1

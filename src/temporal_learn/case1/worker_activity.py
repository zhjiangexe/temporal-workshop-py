"""Activity-only worker (帶 QPS 限制)."""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import process_deliver_order, process_payment, process_reserve_inventory

TASK_QUEUE = "payment-task"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        activities=[process_payment, process_reserve_inventory, process_deliver_order],
        max_activities_per_second=10,       # 本 worker 的速率上限，保護下游服務（API/DB）不被打爆
        max_task_queue_activities_per_second=10,  # 整個 task queue 的速率上限，跨所有 worker 生效
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

"""Workflow-only worker（不含 activity）。

workflow replay 對 CPU 要求低但對並發量有要求；
與 activity worker 分離後可獨立擴縮容，不互相干擾。
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .workflow import OrderFulfillWorkflow

TASK_QUEUE = "payment-task"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderFulfillWorkflow],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

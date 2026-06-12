import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import process_dataset
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import LongJobWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LongJobWorkflow],
        activities=[process_dataset],
    )
    print(f"[Worker] started on task queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import process_dataset
from .workflow import LongJobWorkflow

TASK_QUEUE = "long-job-tq"


async def main():
    client = await Client.connect("localhost:7233")
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

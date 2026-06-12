import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .workflow import PromiseWorkflow

TASK_QUEUE = "promise-test-task"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[PromiseWorkflow],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .workflow import VerWorkflow

TASK_QUEUE = "ver-tq"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[VerWorkflow],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

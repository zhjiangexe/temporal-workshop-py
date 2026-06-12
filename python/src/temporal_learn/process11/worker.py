import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import AsyncActImpl
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import AsyncWf


async def main():
    client = await Client.connect(TEMPORAL_URL)
    acts = AsyncActImpl(client)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AsyncWf],
        activities=[acts.wait_external],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

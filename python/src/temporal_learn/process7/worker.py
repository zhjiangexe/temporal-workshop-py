import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import compose_greeting
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import GreetingWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

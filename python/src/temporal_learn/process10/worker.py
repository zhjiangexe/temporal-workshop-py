import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import long_running_act
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import LongActWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LongActWorkflow],
        activities=[long_running_act],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

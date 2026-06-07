import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import check_title_validity, test_only
from .workflow import PromiseUpdateWorkflow

TASK_QUEUE = "update-test-task"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[PromiseUpdateWorkflow],
        activities=[test_only, check_title_validity],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

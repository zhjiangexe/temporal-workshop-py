import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import apply_new_price, notify_reviewer, record_decision
from .workflow import ProductChangeWorkflow

TASK_QUEUE = "price-change-tq"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ProductChangeWorkflow],
        activities=[notify_reviewer, record_decision, apply_new_price],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

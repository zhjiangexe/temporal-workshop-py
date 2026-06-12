import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import InventoryActivities
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import InventoryEntityWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    acts = InventoryActivities()
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[InventoryEntityWorkflow],
        activities=[acts.restock, acts.purchase],
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

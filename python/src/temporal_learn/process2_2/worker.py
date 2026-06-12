import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import (
    create_or_update_product,
    delete_product,
    publish_to_storefront,
    revert_pricing_and_availability,
    setup_pricing_and_availability,
    unpublish_from_storefront,
)
from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import ProductOnboardingWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ProductOnboardingWorkflow],
        activities=[
            create_or_update_product,
            setup_pricing_and_availability,
            publish_to_storefront,
            delete_product,
            revert_pricing_and_availability,
            unpublish_from_storefront,
        ],
    )
    print(f"Workers started on task queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

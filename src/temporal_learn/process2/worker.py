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
from .workflow import ProductOnboardingWorkflow

TASK_QUEUE = "product-onboarding-tq"


async def main():
    client = await Client.connect("localhost:7233")
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

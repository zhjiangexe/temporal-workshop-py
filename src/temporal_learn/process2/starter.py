import asyncio
import uuid

from temporalio.client import Client

from .models import ProductInput
from .workflow import ProductOnboardingWorkflow

TASK_QUEUE = "product-onboarding-tq"


async def main():
    client = await Client.connect("localhost:7233")
    product_input = ProductInput(
        request_id=str(uuid.uuid7()),
        sku="SKU-12345",
        name="My Product",
        category="Shoes",
        currency="TWD",
        price=1990,
        visible=True,
    )
    handle = await client.start_workflow(
        ProductOnboardingWorkflow.run,
        product_input,
        id=f"product-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import uuid

from temporalio.client import Client

from .models import ProductChangeSpec
from .workflow import ProductChangeWorkflow

TASK_QUEUE = "price-change-tq"


async def main():
    client = await Client.connect("localhost:7233")
    spec = ProductChangeSpec(
        request_id=f"REQ-{uuid.uuid7()}",
        product_id="P001",
        new_price=1490.0,
    )
    handle = await client.start_workflow(
        ProductChangeWorkflow.run,
        spec,
        id=f"price-change-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import uuid

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL, ProductChangeSpec
from .workflow import ProductChangeWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
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
    print(
        "Update command: "
        f"uv run python -m temporal_learn.process3.client_update {handle.id} "
        "--outcome approve"
    )


if __name__ == "__main__":
    asyncio.run(main())

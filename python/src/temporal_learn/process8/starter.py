import asyncio
import uuid

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import AwaitWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    handle = await client.start_workflow(
        AwaitWorkflow.run,
        id=f"await-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")

    await handle.signal(AwaitWorkflow.mark_ready)
    result = await handle.result()
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

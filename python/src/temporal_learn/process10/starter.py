import asyncio
import uuid

from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import LongActWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    handle = await client.start_workflow(
        LongActWorkflow.run,
        id=f"long-act-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")

    await asyncio.sleep(1)
    await handle.cancel()

    try:
        await handle.result()
    except WorkflowFailureError as e:
        if isinstance(e.cause, CancelledError):
            print("Workflow cancelled.")
            return
        raise


if __name__ == "__main__":
    asyncio.run(main())

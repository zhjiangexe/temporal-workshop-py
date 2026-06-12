import asyncio

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import MyWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    handle = await client.start_workflow(
        MyWorkflow.run,
        "payload",
        id="wf-cancel-demo-1",
        task_queue=TASK_QUEUE,
    )
    await handle.cancel()
    print("Cancel request sent.")


if __name__ == "__main__":
    asyncio.run(main())

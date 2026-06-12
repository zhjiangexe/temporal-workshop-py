import asyncio

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import VerWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    handle = await client.start_workflow(
        VerWorkflow.run,
        "go",
        id="wf-ver-demo-1",
        task_queue=TASK_QUEUE,
    )
    print(f"workflow started: id={handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

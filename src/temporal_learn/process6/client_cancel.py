import asyncio

from temporalio.client import Client

from .workflow import MyWorkflow

TASK_QUEUE = "ha-tq"


async def main():
    client = await Client.connect("localhost:7233")
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

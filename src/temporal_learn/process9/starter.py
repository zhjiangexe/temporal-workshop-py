import asyncio

from temporalio.client import Client

from .workflow import VerWorkflow

TASK_QUEUE = "ver-tq"


async def main():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        VerWorkflow.run,
        "go",
        id="wf-ver-demo-1",
        task_queue=TASK_QUEUE,
    )
    print(f"workflow started: id={handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

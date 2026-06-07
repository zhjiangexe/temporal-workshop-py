import asyncio
import uuid

from temporalio.client import Client

from .workflow import PromiseWorkflow

TASK_QUEUE = "promise-test-task"


async def main():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        PromiseWorkflow.execute,
        id=f"promise-test-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"run id: {handle.result_run_id}, workflow id: {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

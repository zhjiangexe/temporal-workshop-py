import asyncio
import uuid
from datetime import timedelta

from temporalio.client import Client

from .models import LongJobSpec
from .workflow import LongJobWorkflow

TASK_QUEUE = "long-job-tq"


async def main():
    client = await Client.connect("localhost:7233")
    spec = LongJobSpec(dataset_id="dataset-A", total=100, chunk_size=500)
    handle = await client.start_workflow(
        LongJobWorkflow.run,
        spec,
        id=f"long-job-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
        run_timeout=timedelta(hours=1),
    )
    print(f"Started: workflowId={handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

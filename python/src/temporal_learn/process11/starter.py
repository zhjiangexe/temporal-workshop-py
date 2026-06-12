import asyncio
import uuid

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import AsyncWf


async def main():
    client = await Client.connect(TEMPORAL_URL)
    result = await client.execute_workflow(
        AsyncWf.run,
        "X1",
        id=f"async-act-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

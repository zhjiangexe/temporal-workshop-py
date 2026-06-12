import asyncio
import uuid

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL
from .workflow import GreetingWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    handle = await client.start_workflow(
        GreetingWorkflow.greet,
        "Alice",
        id=f"greeting-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")

    greeting = await handle.query(GreetingWorkflow.get_greeting)
    print(f"Current greeting: {greeting}")

    await handle.execute_update(GreetingWorkflow.update_greeting, "Howdy")
    greeting = await handle.query(GreetingWorkflow.get_greeting)
    print(f"Updated greeting: {greeting}")
    print("Workflow stays running for the timer; check Web UI for query/update history.")


if __name__ == "__main__":
    asyncio.run(main())

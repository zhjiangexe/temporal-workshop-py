import asyncio
import uuid

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL, RegisterRequest
from .workflow import RegistrationWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    user_id = str(uuid.uuid7())
    request = RegisterRequest(user_id=user_id, email="flow@gmail.com")
    handle = await client.start_workflow(
        RegistrationWorkflow.register,
        request,
        id=f"registration-{user_id}",
        task_queue=TASK_QUEUE,
    )
    print(f"WorkflowId: {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())

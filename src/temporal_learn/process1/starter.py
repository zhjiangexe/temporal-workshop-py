import asyncio
import uuid

from temporalio.client import Client

from .models import RegisterRequest
from .workflow import RegistrationWorkflow

TASK_QUEUE = "registration-tq"


async def main():
    client = await Client.connect("localhost:7233")
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

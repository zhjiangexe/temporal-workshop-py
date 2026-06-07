import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import RegistrationActivities
from .workflow import RegistrationWorkflow

TASK_QUEUE = "registration-tq"


async def main():
    client = await Client.connect("localhost:7233")
    acts = RegistrationActivities()
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[RegistrationWorkflow],
        activities=[acts.create_account, acts.add_points, acts.send_email],
        max_concurrent_activities=50,         # 本 worker 同時執行的 activity 上限，超過排隊
        max_concurrent_workflow_tasks=20,     # 本 worker 同時處理的 workflow task 上限
        max_activities_per_second=50.0,       # 本 worker 的 activity 執行速率上限
        max_task_queue_activities_per_second=100.0,  # 整個 task queue 跨所有 worker 的速率上限
        max_concurrent_workflow_task_polls=10,
        max_concurrent_activity_task_polls=10,
    )
    print(f"Worker started on {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

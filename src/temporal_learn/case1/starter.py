import asyncio
import uuid

from temporalio.client import Client

from .models import Order, OrderItem
from .workflow import OrderFulfillWorkflow

TASK_QUEUE = "payment-task"


async def main():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        OrderFulfillWorkflow.order_fulfill,
        Order(order_items=[OrderItem(item_name="widget", item_price=9.99, quantity=2)]),
        id=f"payment-{uuid.uuid7()}",
        task_queue=TASK_QUEUE,
    )
    print(f"workflow started: id={handle.id}, run_id={handle.result_run_id}")


if __name__ == "__main__":
    asyncio.run(main())

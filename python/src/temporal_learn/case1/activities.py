import asyncio

from temporalio import activity

from .models import Order


# -----------------------------------------------------------------------------
# Activity: process_payment
@activity.defn
async def process_payment(order: Order) -> None:
    await asyncio.sleep(0.1)
    print("process payment")


# -----------------------------------------------------------------------------
# Activity: process_reserve_inventory
@activity.defn
async def process_reserve_inventory(order: Order) -> None:
    await asyncio.sleep(0.1)
    print("process reserve inventory")


# -----------------------------------------------------------------------------
# Activity: process_deliver_order
@activity.defn
async def process_deliver_order(order: Order) -> None:
    await asyncio.sleep(0.1)
    task_queue = activity.info().task_queue
    print(f"process deliver order (task_queue={task_queue})")

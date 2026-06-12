import asyncio
import uuid
from datetime import datetime

from temporalio.client import Client

from .models import TASK_QUEUE, TEMPORAL_URL, Command, CommandResult, CommandType
from .workflow import InventoryEntityWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL)
    product_id = "sku-123"

    handle = await client.start_workflow(
        InventoryEntityWorkflow.run,
        args=[product_id, 10000],
        id=f"inventory:{product_id}",
        task_queue=TASK_QUEUE,
    )

    stock = await handle.query(InventoryEntityWorkflow.get_stock)
    print(f"Stock: {stock}")

    # Signal: async restock
    await handle.signal(
        InventoryEntityWorkflow.submit,
        Command(command_type=CommandType.RESTOCK, qty=20, op_key="op-restock-1"),
    )
    await handle.signal(
        InventoryEntityWorkflow.submit,
        Command(command_type=CommandType.RESTOCK, qty=20, op_key="op-restock-2"),
    )
    await handle.signal(
        InventoryEntityWorkflow.submit,
        Command(command_type=CommandType.RESTOCK, qty=20, op_key="op-restock-3"),
    )

    await asyncio.sleep(5)
    stock = await handle.query(InventoryEntityWorkflow.get_stock)
    print(f"Stock after restock: {stock}")

    # Load test: 50 QPS for 5 seconds via update
    qps = 50
    duration_seconds = 5
    start = datetime.now()

    async def fire():
        op_key = f"invoke-{uuid.uuid7()}"
        try:
            result: CommandResult = await handle.execute_update(
                InventoryEntityWorkflow.invoke,
                Command(command_type=CommandType.PURCHASE, qty=1, op_key=op_key),
            )
            print(f"Success, stock={result.stock}")
        except Exception as e:
            print(f"Error: {e}")

    for _ in range(duration_seconds):
        tasks = [asyncio.create_task(fire()) for _ in range(qps)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)

    elapsed = datetime.now() - start
    print(f"rock: {elapsed}")


if __name__ == "__main__":
    asyncio.run(main())

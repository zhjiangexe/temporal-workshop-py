"""對執行中的 workflow 呼叫 update."""

import asyncio

from temporalio.client import Client, WorkflowUpdateStage

from .workflow import PromiseUpdateWorkflow

WORKFLOW_ID = "update-test-656739554"


async def main():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle_for(
        PromiseUpdateWorkflow.get_greeting,
        workflow_id=WORKFLOW_ID,
    )
    # 兩段式 API：先等 workflow 確認收到（ACCEPTED），再視需要等執行結果
    # 好處：可以解耦「送出 update」和「等待結果」的時機，例如放入背景繼續做其他事
    update_handle = await handle.start_update(
        PromiseUpdateWorkflow.check_title_validity,
        wait_for_stage=WorkflowUpdateStage.ACCEPTED,  # 只等收到確認，不等執行完成
        id="update-test-1638566340",
    )
    result = await update_handle.result()  # 此時才真正等待 update 執行完並取回結果
    print(f"update result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

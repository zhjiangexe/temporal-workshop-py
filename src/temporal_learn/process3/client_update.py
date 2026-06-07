"""對執行中的 workflow 送入審核決定."""

import asyncio

from temporalio.client import Client

from .models import ReviewDecision, ReviewOutcome
from .workflow import ProductChangeWorkflow

WORKFLOW_ID = "price-change-<your-workflow-id>"


async def main():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle_for(
        ProductChangeWorkflow.run,
        workflow_id=WORKFLOW_ID,
    )
    # execute_update：同步等待 workflow 確認收到並執行完畢才返回
    # 對比 handle.signal()：signal 傳送後不等待回應（fire-and-forget）
    await handle.execute_update(
        ProductChangeWorkflow.update,
        ReviewDecision(
            outcome=ReviewOutcome.APPROVE,
            approver_id="marketing_lead",
        ),
    )
    print("Decision sent.")


if __name__ == "__main__":
    asyncio.run(main())

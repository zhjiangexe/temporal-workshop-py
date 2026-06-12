"""對執行中的 workflow 送入審核決定."""

import argparse
import asyncio

from temporalio.client import Client

from .models import TEMPORAL_URL, ReviewDecision, ReviewOutcome
from .workflow import ProductChangeWorkflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a review decision update to a process3 workflow.",
    )
    parser.add_argument("workflow_id", help="Workflow ID printed by process3 starter.")
    parser.add_argument(
        "--outcome",
        choices=[ReviewOutcome.APPROVE.value, ReviewOutcome.REJECT.value],
        default=ReviewOutcome.APPROVE.value,
        help="Review decision outcome.",
    )
    parser.add_argument(
        "--approver-id",
        default="marketing_lead",
        help="Reviewer ID recorded with the decision.",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Optional reason, usually used for rejected decisions.",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    client = await Client.connect(TEMPORAL_URL)
    handle = client.get_workflow_handle_for(
        ProductChangeWorkflow.run,
        workflow_id=args.workflow_id,
    )
    # execute_update：同步等待 workflow 確認收到並執行完畢才返回
    # 對比 handle.signal()：signal 傳送後不等待回應（fire-and-forget）
    await handle.execute_update(
        ProductChangeWorkflow.update,
        ReviewDecision(
            outcome=ReviewOutcome(args.outcome),
            approver_id=args.approver_id,
            reason=args.reason,
        ),
    )
    print(f"Decision sent to {args.workflow_id}: {args.outcome}")


if __name__ == "__main__":
    asyncio.run(main())

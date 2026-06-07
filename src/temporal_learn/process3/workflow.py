from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .activities import apply_new_price, notify_reviewer, record_decision
    from .models import ProductChangeSpec, ReviewDecision, ReviewOutcome

_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=5,
)
_ACT_CFG: workflow.ActivityConfig = {
    "start_to_close_timeout": timedelta(seconds=30),
    "retry_policy": _RETRY,
}


@workflow.defn
class ProductChangeWorkflow:
    def __init__(self):
        # Temporal replay 時 __init__ 會重新執行，所有狀態都必須在此初始化
        self._decision: ReviewDecision | None = None

    @workflow.run
    async def run(self, spec: ProductChangeSpec) -> None:
        await workflow.execute_activity(notify_reviewer, spec, **_ACT_CFG)

        try:
            # durably waiting：workflow 被掛起不佔 thread，等 update 進來才喚醒
            # 這讓「等人工審核最多 48 小時」這種業務需求變得非常自然
            await workflow.wait_condition(
                lambda: self._decision is not None,
                timeout=timedelta(hours=48),
            )
        except TimeoutError:
            # 超時降級：系統代發 REJECT，確保 workflow 不會永久卡住
            self._decision = ReviewDecision(
                outcome=ReviewOutcome.REJECT,
                approver_id="system",
                reason="timeout after 48 hours",
            )

        decision = self._decision
        await workflow.execute_activity(
            record_decision, args=[spec, decision], **_ACT_CFG
        )

        if decision.outcome == ReviewOutcome.REJECT:
            return

        await workflow.execute_activity(apply_new_price, spec, **_ACT_CFG)

    # update 可回傳值且呼叫方可 await 確認結果；signal 是 fire-and-forget
    @workflow.update
    async def update(self, decision: ReviewDecision) -> None:
        # 防重入：update 可能因網路重試而被呼叫多次，只接受第一個決策
        if self._decision is None:
            self._decision = decision

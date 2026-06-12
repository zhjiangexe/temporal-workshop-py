import asyncio

from temporalio import activity

from .models import ProductChangeSpec, ReviewDecision


# -----------------------------------------------------------------------------
# Activity: notify_reviewer
@activity.defn
async def notify_reviewer(spec: ProductChangeSpec) -> None:
    await asyncio.sleep(5)
    print(
        f"[NOTIFY] requestId={spec.request_id} "
        f"newPrice={spec.new_price:.2f} product={spec.product_id}"
    )


# -----------------------------------------------------------------------------
# Activity: record_decision
@activity.defn
async def record_decision(spec: ProductChangeSpec, decision: ReviewDecision) -> None:
    await asyncio.sleep(5)
    print(
        f"[RECORD] requestId={spec.request_id}, "
        f"product={spec.product_id}, review={decision.outcome.value}"
    )


# -----------------------------------------------------------------------------
# Activity: apply_new_price
@activity.defn
async def apply_new_price(spec: ProductChangeSpec) -> None:
    await asyncio.sleep(5)
    print(
        f"[APPLY] requestId={spec.request_id} "
        f"set price={spec.new_price:.2f} for product={spec.product_id}"
    )

import asyncio

from temporalio import activity

from .models import RegisterRequest

# Demo-only：用 memory set 模擬資料庫 unique constraint，方便展示 idempotency。
# 生產環境不可依賴 worker memory，應改用 DB / Redis / 外部服務的 idempotency key。
_demo_users: set[str] = set()
_demo_ops: set[str] = set()


def reset_activity_state_for_test() -> None:
    _demo_users.clear()
    _demo_ops.clear()


# -------------------------------------------------------------------------
# Activity: create_account
@activity.defn
async def create_account(request: RegisterRequest) -> None:
    if request.user_id in _demo_users:
        return
    _demo_users.add(request.user_id)
    await asyncio.sleep(5)
    print(f"Created account for {request.user_id} ({request.email})")


# -------------------------------------------------------------------------
# Activity: add_points
@activity.defn
async def add_points(user_id: str, points: int, op_key: str) -> None:
    # namespace#entity#operation 的複合鍵設計，確保不同操作的 key 不會碰撞
    dedupe_key = f"POINTS#{user_id}#{op_key}"
    # 冪等性核心：相同 op_key 重複呼叫無副作用地直接返回
    if dedupe_key in _demo_ops:
        print(f"[idempotent] addPoints skipped for {user_id} [op={op_key}]")
        return

    await asyncio.sleep(5)
    print(f"Added {points} points to {user_id} [op={op_key}]")

    _demo_ops.add(dedupe_key)


# -------------------------------------------------------------------------
# Activity: send_email
@activity.defn
async def send_email(email: str, message_id: str) -> None:
    dedupe_key = f"EMAIL#{message_id}"
    if dedupe_key in _demo_ops:
        print(f"[idempotent] sendEmail skipped for {email} [msgId={message_id}]")
        return
    _demo_ops.add(dedupe_key)
    await asyncio.sleep(5)
    print(f"Sent welcome email to {email} [msgId={message_id}]")

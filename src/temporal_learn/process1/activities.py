import asyncio

from temporalio import activity

from .models import RegisterRequest


# 用 class 而非函式，讓多個 activity 共享同一個 in-memory state（_ops set）
# 此 set 模擬資料庫的角色，生產環境應換成真實的 DB 或分散式 cache
class RegistrationActivities:
    def __init__(self):
        self._users: set[str] = set()
        self._ops: set[str] = set()  # 記錄已執行的操作，實現冪等性

    # -------------------------------------------------------------------------
    # Activity: create_account
    @activity.defn
    async def create_account(self, request: RegisterRequest) -> None:
        if request.user_id in self._users:
            return
        self._users.add(request.user_id)
        await asyncio.sleep(5)
        print(f"Created account for {request.user_id} ({request.email})")

    # -------------------------------------------------------------------------
    # Activity: add_points
    @activity.defn
    async def add_points(self, user_id: str, points: int, op_key: str) -> None:
        # namespace#entity#operation 的複合鍵設計，確保不同操作的 key 不會碰撞
        dedupe_key = f"POINTS#{user_id}#{op_key}"
        info = activity.info()
        attempt = info.attempt
        # 冪等性核心：相同 op_key 重複呼叫無副作用地直接返回
        if dedupe_key in self._ops:
            print(f"[idempotent] addPoints skipped for {user_id} [op={op_key}]")
            return

        # 刻意模擬前 3 次失敗，讓 RetryPolicy 有機會展示，生產環境不應這樣寫
        if attempt <= 3:
            raise RuntimeError(f"DB 連線失敗(模擬),第 {info.attempt} 次")

        await asyncio.sleep(5)
        print(f"Added {points} points to {user_id} [op={op_key}]")

        self._ops.add(dedupe_key)

    # -------------------------------------------------------------------------
    # Activity: send_email
    @activity.defn
    async def send_email(self, email: str, message_id: str) -> None:
        dedupe_key = f"EMAIL#{message_id}"
        if dedupe_key in self._ops:
            print(f"[idempotent] sendEmail skipped for {email} [msgId={message_id}]")
            return
        self._ops.add(dedupe_key)
        await asyncio.sleep(5)
        print(f"Sent welcome email to {email} [msgId={message_id}]")

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# imports_passed_through：讓 workflow 可以 import 外部模組，但繞過 Temporal 的沙盒限制
# 只用於 import type hints 或不影響 determinism 的模組
with workflow.unsafe.imports_passed_through():
    from .activities import RegistrationActivities
    from .models import RegisterRequest

# exponential backoff：每次重試等待時間翻倍（5s → 10s → 20s...），上限 100s
# maximum_attempts 被註解掉 = 無限重試，由 schedule_to_close_timeout 決定何時放棄
_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=5),
    backoff_coefficient=2,
    maximum_interval=timedelta(seconds=100),
    # maximum_attempts=5,
)
# 抽成 ActivityConfig 方便統一調整所有 activity 的超時與重試設定
_ACT_CFG: workflow.ActivityConfig = {
    "start_to_close_timeout": timedelta(seconds=15),  # 單次 activity 執行的時間上限
    "heartbeat_timeout": timedelta(seconds=10),  # 超過此時間無心跳就判定 worker 已死
    "retry_policy": _RETRY,
    # "schedule_to_close_timeout": timedelta(seconds=120),  # 整個 activity 生命期的上限（含重試）
}


@workflow.defn
class RegistrationWorkflow:
    @workflow.run
    async def register(self, request: RegisterRequest) -> None:

        # execute_activity_method 用於 class-based activity（實例方法）
        # 純函式型 activity 改用 workflow.execute_activity()
        await workflow.execute_activity_method(
            RegistrationActivities.create_account, request, **_ACT_CFG
        )
        await workflow.execute_activity_method(
            RegistrationActivities.add_points,
            args=[request.user_id, 500, "signupBonus"],  # "signupBonus" 是冪等鍵，不是業務資料
            **_ACT_CFG,
        )
        await workflow.execute_activity_method(
            RegistrationActivities.send_email,
            args=[request.email, f"welcome-{request.user_id}"],
            **_ACT_CFG,
        )

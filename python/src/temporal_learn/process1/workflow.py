from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from .activities import add_points, create_account, send_email
from .activities2 import notify
from .models import RegisterRequest

# 抽成 ActivityConfig 方便統一調整所有 activity 的超時與重試設定
_ACT_CFG: workflow.ActivityConfig = {
    "start_to_close_timeout": timedelta(seconds=15),  # 單次 activity 執行的時間上限
    "heartbeat_timeout": timedelta(seconds=10),  # 超過此時間無心跳就判定 worker 已死
    # exponential backoff：每次重試等待時間翻倍（5s → 10s → 20s...），上限 100s
    "retry_policy": RetryPolicy(
        initial_interval=timedelta(seconds=5),
        backoff_coefficient=2,
        maximum_interval=timedelta(seconds=100),
        # maximum_attempts=5,
    ),
    "schedule_to_close_timeout": timedelta(
        seconds=30
    ),  # 整個 activity 生命期的上限（含重試）
}


@workflow.defn
class RegistrationWorkflow:
    @workflow.run
    async def register(self, request: RegisterRequest) -> None:
        # step1: 安排執行 create_account
        await workflow.execute_activity(create_account, request, **_ACT_CFG)
        # step2: 安排執行 add_points
        await workflow.execute_activity(
            add_points,
            args=[
                request.user_id,
                500,
                "signupBonus",
            ],  # "signupBonus" 是冪等鍵，不是業務資料
            **_ACT_CFG,
        )

        # step3: 安排執行 send_email
        await workflow.execute_activity(
            send_email,
            args=[request.email, f"welcome-{request.user_id}"],
            **_ACT_CFG,
        )

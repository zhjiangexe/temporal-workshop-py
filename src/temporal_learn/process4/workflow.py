import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .activities import process_dataset
    from .models import LongJobSpec

_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_attempts=10,
)

logger = logging.getLogger(__name__)


@workflow.defn
class LongJobWorkflow:
    @workflow.run
    async def run(self, spec: LongJobSpec) -> None:
        last = await workflow.execute_activity(
            process_dataset,
            spec,
            start_to_close_timeout=timedelta(minutes=5),  # 整體執行上限，超過直接失敗
            heartbeat_timeout=timedelta(seconds=30),  # 活性偵測：30s 沒收到心跳就判定 worker 已死並重排
            retry_policy=_RETRY,
        )
        logger.info("Dataset %s done, lastProcessed=%d", spec.dataset_id, last)

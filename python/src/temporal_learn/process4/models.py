from dataclasses import dataclass

TEMPORAL_URL = "localhost:7233"
TASK_QUEUE = "long-job-tq"


@dataclass
class LongJobSpec:
    dataset_id: str
    total: int
    chunk_size: int = 0

from dataclasses import dataclass


@dataclass
class LongJobSpec:
    dataset_id: str
    total: int
    chunk_size: int = 0

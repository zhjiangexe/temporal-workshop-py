from dataclasses import dataclass

TEMPORAL_URL = "localhost:7233"
TASK_QUEUE = "product-onboarding-tq"


@dataclass
class ProductInput:
    request_id: str
    sku: str
    name: str
    category: str
    currency: str
    price: int
    visible: bool


@dataclass
class ProductPublishResult:
    published: bool
    message: str
    product_id: str = ""

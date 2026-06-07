from dataclasses import dataclass


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

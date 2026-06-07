from dataclasses import dataclass, field


@dataclass
class OrderItem:
    item_name: str
    item_price: float
    quantity: int


@dataclass
class Order:
    order_items: list[OrderItem] = field(default_factory=list)

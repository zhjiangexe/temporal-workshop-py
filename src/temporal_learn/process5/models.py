from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self


class CommandType(StrEnum):
    RESTOCK = auto()
    PURCHASE = auto()


@dataclass
class Command:
    command_type: CommandType
    qty: int
    op_key: str


@dataclass
class CommandResult:
    stock: int = 0
    error_type: str = ""
    message: str = ""

    @classmethod
    def ok(cls, new_stock: int) -> Self:
        return cls(stock=new_stock)

    @classmethod
    def fail(cls, error_type: str, message: str) -> Self:
        return cls(error_type=error_type, message=message)

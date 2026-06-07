from temporalio import activity
from temporalio.exceptions import ApplicationError


class InventoryActivities:
    def __init__(self):
        self._stock_by_product: dict[str, int] = {}
        self._ops: set[str] = set()

    # -------------------------------------------------------------------------
    # Activity: restock
    @activity.defn
    async def restock(self, product_id: str, qty: int, op_key: str) -> int:
        # op_key 由呼叫方提供，確保同一筆操作重複呼叫時只執行一次
        dedupe = f"RESTOCK#{product_id}#{op_key}"
        if dedupe in self._ops:
            return self._stock_by_product.get(product_id, 0)
        self._ops.add(dedupe)

        # type 欄位讓 RetryPolicy 的 non_retryable_error_types 能按業務語義路由
        if qty <= 0:
            raise ApplicationError("qty must be > 0", type="InvalidInput")

        current = self._stock_by_product.get(product_id, 0)
        new_stock = current + qty
        self._stock_by_product[product_id] = new_stock
        return new_stock

    # -------------------------------------------------------------------------
    # Activity: purchase
    @activity.defn
    async def purchase(self, product_id: str, qty: int, op_key: str) -> int:
        dedupe = f"PURCHASE#{product_id}#{op_key}"
        if dedupe in self._ops:
            return self._stock_by_product.get(product_id, 0)
        self._ops.add(dedupe)

        if qty <= 0:
            raise ApplicationError("qty must be > 0", type="InvalidInput")

        current = self._stock_by_product.get(product_id, 0)
        if current < qty:
            # StockError 是業務邏輯失敗，重試無法改善，應直接失敗
            raise ApplicationError("insufficient stock", type="StockError")

        new_stock = current - qty
        self._stock_by_product[product_id] = new_stock
        return new_stock

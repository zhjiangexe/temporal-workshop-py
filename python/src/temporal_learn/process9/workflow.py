from temporalio import workflow


@workflow.defn
class VerWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Deterministic Versioning：workflow history 必須可重放，不能用 if/else 直接改邏輯
        # workflow.patched() 讓新舊程式碼路徑能在同一個 workflow 中安全共存：
        #   - 新啟動的 execution 走最新邏輯（v2）
        #   - 舊的 in-flight execution 依 history 記錄走當時的邏輯（v1 或 original）
        # 等所有使用 v1 的 execution 都結束後，patched("greet-change-v1") 這段才能刪除
        if workflow.patched("greet-change-v2"):
            return f"Hey {name}"
        elif workflow.patched("greet-change-v1"):
            return f"Hi {name}"
        else:
            return f"Hello {name}"

from temporalio import workflow


@workflow.defn
class ChildWorkflow:
    @workflow.run
    async def execute(self) -> None:
        pass

from temporalio import activity


# -----------------------------------------------------------------------------
# Activity: compose_greeting
@activity.defn
async def compose_greeting(greeting: str, name: str) -> str:
    return f"{greeting}, {name}!"

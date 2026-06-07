import asyncio

from temporalio import activity


# -----------------------------------------------------------------------------
# Activity: test_only
@activity.defn
async def test_only(input: str) -> int:
    await asyncio.sleep(0.3)
    print("test only")
    return 0


# -----------------------------------------------------------------------------
# Activity: check_title_validity
@activity.defn
async def check_title_validity(name_with_title: str) -> bool:
    print("run check title validity")
    return False

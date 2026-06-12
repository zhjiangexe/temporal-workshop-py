import pytest
from temporalio.testing import ActivityEnvironment

from temporal_learn.process7.activities import compose_greeting


@pytest.mark.asyncio
async def test_compose_greeting_formats_message():
    activity_env = ActivityEnvironment()

    result = await activity_env.run(compose_greeting, "Howdy", "Alice")

    assert result == "Howdy, Alice!"

import pytest

from temporal_learn.shared.saga import Saga


@pytest.mark.asyncio
async def test_compensate_runs_in_reverse_order():
    order: list[int] = []
    saga = Saga()
    saga.add_compensation(lambda: _append(order, 1))
    saga.add_compensation(lambda: _append(order, 2))
    saga.add_compensation(lambda: _append(order, 3))

    await saga.compensate()

    assert order == [3, 2, 1]


@pytest.mark.asyncio
async def test_compensate_stops_on_failure():
    called: list[str] = []

    async def fail():
        called.append("fail")
        raise RuntimeError("boom")

    async def succeed():
        called.append("succeed")

    saga = Saga()
    saga.add_compensation(succeed)
    saga.add_compensation(fail)

    with pytest.raises(RuntimeError, match="boom"):
        await saga.compensate()

    assert called == ["fail"]


async def _append(lst: list[int], val: int) -> None:
    lst.append(val)


@pytest.mark.asyncio
async def test_add_activity_compensation_wraps_execute_activity(monkeypatch):
    calls: list[tuple[object, list[object], dict[str, object]]] = []

    async def fake_execute_activity(activity, *, args, **kwargs):
        calls.append((activity, args, kwargs))

    async def sample_activity(value: int) -> None:
        return None

    monkeypatch.setattr(
        "temporal_learn.shared.saga.workflow.execute_activity",
        fake_execute_activity,
    )

    saga = Saga()
    saga.add_activity_compensation(
        sample_activity,
        123,
        start_to_close_timeout="5s",
    )

    await saga.compensate()

    assert calls == [
        (
            sample_activity,
            [123],
            {"start_to_close_timeout": "5s"},
        )
    ]

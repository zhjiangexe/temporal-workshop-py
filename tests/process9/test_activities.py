import importlib.util


def test_process9_has_no_activity_layer():
    # process9 示範 deterministic versioning，本身沒有 activity module。
    assert importlib.util.find_spec("temporal_learn.process9.activities") is None

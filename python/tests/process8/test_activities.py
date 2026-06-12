import importlib.util


def test_process8_has_no_activity_layer():
    # process8 示範 wait_condition + signal，本身沒有 activity module。
    assert importlib.util.find_spec("temporal_learn.process8.activities") is None

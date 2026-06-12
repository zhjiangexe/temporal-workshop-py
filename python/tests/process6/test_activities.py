import importlib.util


def test_process6_has_no_activity_layer():
    # process6 示範 workflow cancellation，本身沒有 activity module。
    assert importlib.util.find_spec("temporal_learn.process6.activities") is None

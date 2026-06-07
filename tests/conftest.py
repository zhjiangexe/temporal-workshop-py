import sys
from pathlib import Path

import pytest
from temporalio.testing import WorkflowEnvironment

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
# 確保測試永遠載入本 repo 的 src/，避免電腦上其他同名 package 影響結果。
if str(SRC) in sys.path:
    sys.path.remove(str(SRC))
sys.path.insert(0, str(SRC))


@pytest.fixture
async def env():
    # Temporal 官方測試環境；支援 time skipping，可快速測 timer / timeout。
    async with await WorkflowEnvironment.start_time_skipping() as env:
        yield env

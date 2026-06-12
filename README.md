# Temporal Workshop

這個 repository 同時包含 Python 與 TypeScript 版本。Python 專案獨立放在：

```text
python/
```

Python 範例原始碼使用 `src/` layout，例如 Process 1 的檔案位置是：

```text
python/src/temporal_learn/process1/
```

對應的 Python module path 則是：

```text
temporal_learn.process1
```

所以執行 Python 範例時，請先進入 `python/`：

```sh
cd python
uv run python -m temporal_learn.process1.worker
uv run python -m temporal_learn.process1.starter
```

## 目錄對照

| 教材頁面 | 實際原始碼位置 | Module path |
| --- | --- | --- |
| `docs/process1.html` | `python/src/temporal_learn/process1/` | `temporal_learn.process1` |
| `docs/process2.html` | Process 2 索引頁 | - |
| `docs/process2-1.html` | `python/src/temporal_learn/process2_1/` | `temporal_learn.process2_1` |
| `docs/process2-2.html` | `python/src/temporal_learn/process2_2/` | `temporal_learn.process2_2` |
| `docs/process3.html` | `python/src/temporal_learn/process3/` | `temporal_learn.process3` |
| `docs/process4.html` | `python/src/temporal_learn/process4/` | `temporal_learn.process4` |
| `docs/process5.html` | `python/src/temporal_learn/process5/` | `temporal_learn.process5` |
| `docs/process6.html` | `python/src/temporal_learn/process6/` | `temporal_learn.process6` |
| `docs/process7.html` | `python/src/temporal_learn/process7/` | `temporal_learn.process7` |
| `docs/process8.html` | `python/src/temporal_learn/process8/` | `temporal_learn.process8` |
| `docs/process9.html` | `python/src/temporal_learn/process9/` | `temporal_learn.process9` |
| `docs/process10.html` | `python/src/temporal_learn/process10/` | `temporal_learn.process10` |
| `docs/process11.html` | `python/src/temporal_learn/process11/` | `temporal_learn.process11` |

## 測試

```sh
cd python
uv run pytest
```

## Process 2 補償流程示範

Process 2-1 與 Process 2-2 可以用 `FAIL_PUBLISH=1` 模擬上架 Activity 失敗，
用來觀察補償 Activity 是否依反向順序執行。

```sh
cd python
FAIL_PUBLISH=1 uv run python -m temporal_learn.process2_1.worker
uv run python -m temporal_learn.process2_1.starter
```

```sh
cd python
FAIL_PUBLISH=1 uv run python -m temporal_learn.process2_2.worker
uv run python -m temporal_learn.process2_2.starter
```

`FAIL_PUBLISH=1` 要加在 Worker 啟動時，因為失敗邏輯是在 Activity 執行端判斷。

## TypeScript 版本

Process 1～3 另有 TypeScript 版本，獨立放在：

```text
typescript/
```

安裝與執行方式：

```sh
cd typescript
npm install
npm run typecheck
```

實際啟動前，請先另開 terminal 啟動 Temporal Server：

```sh
temporal server start-dev
```

可執行的範例：

```sh
npm run process1:worker
npm run process1:starter

npm run process2:worker
npm run process2:starter

npm run process3:worker
npm run process3:starter
npm run process3:update -- <starter 印出的 WorkflowId>
```

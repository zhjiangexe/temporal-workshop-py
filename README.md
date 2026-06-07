# Temporal Workshop

這個專案使用 Python 的 `src/` layout。實際範例原始碼不在專案根目錄底下，而是在：

```text
src/temporal_learn/
```

例如 Process 1 的檔案位置是：

```text
src/temporal_learn/process1/
```

對應的 Python module path 則是：

```text
temporal_learn.process1
```

所以執行範例時請從專案根目錄使用 `python -m`：

```sh
uv run python -m temporal_learn.process1.worker
uv run python -m temporal_learn.process1.starter
```

## 目錄對照

| 教材頁面 | 實際原始碼位置 | Module path |
| --- | --- | --- |
| `docs/process1.html` | `src/temporal_learn/process1/` | `temporal_learn.process1` |
| `docs/process2.html` | Process 2 索引頁 | - |
| `docs/process2-1.html` | `src/temporal_learn/process2_1/` | `temporal_learn.process2_1` |
| `docs/process2-2.html` | `src/temporal_learn/process2_2/` | `temporal_learn.process2_2` |
| `docs/process3.html` | `src/temporal_learn/process3/` | `temporal_learn.process3` |
| `docs/process4.html` | `src/temporal_learn/process4/` | `temporal_learn.process4` |
| `docs/process5.html` | `src/temporal_learn/process5/` | `temporal_learn.process5` |
| `docs/process6.html` | `src/temporal_learn/process6/` | `temporal_learn.process6` |
| `docs/process7.html` | `src/temporal_learn/process7/` | `temporal_learn.process7` |
| `docs/process8.html` | `src/temporal_learn/process8/` | `temporal_learn.process8` |
| `docs/process9.html` | `src/temporal_learn/process9/` | `temporal_learn.process9` |
| `docs/process10.html` | `src/temporal_learn/process10/` | `temporal_learn.process10` |
| `docs/process11.html` | `src/temporal_learn/process11/` | `temporal_learn.process11` |

## 測試

```sh
uv run pytest
```

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

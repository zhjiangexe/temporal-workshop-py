# Temporal Workshop TypeScript

這份 TypeScript 版本獨立放在 `typescript/`，不和 Python 的 `src/temporal_learn/` 混在一起。

## 安裝

```sh
cd typescript
npm install
```

## 啟動 Temporal Server

另開一個 terminal：

```sh
temporal server start-dev
```

## Process 1：使用者註冊

```sh
npm run process1:worker
npm run process1:starter
```

## Process 2：商品上架補償流程

正常路徑：

```sh
npm run process2:worker
npm run process2:starter
```

模擬上架失敗：

```sh
FAIL_PUBLISH=1 npm run process2:worker
npm run process2:starter
```

## Process 3：商品改價審批

```sh
npm run process3:worker
npm run process3:starter
```

把 starter 印出的 Workflow ID 傳給 update client：

```sh
npm run process3:update -- <starter 印出的 WorkflowId>
```

## 檢查 TypeScript

```sh
npm run typecheck
```

## 測試

```sh
npm test
```

測試結構對齊 Python 版本：

```text
tests/process1/test_activities.ts
tests/process1/test_workflow.ts
tests/process1/test_integration.ts

tests/process2/test_activities.ts
tests/process2/test_workflow.ts
tests/process2/test_integration.ts

tests/process3/test_activities.ts
tests/process3/test_workflow.ts
tests/process3/test_integration.ts
```

- `test_activities.ts`：測真實 activity 函式本身。
- `test_workflow.ts`：用 stub activity 驗證 workflow 編排、順序與分支。
- `test_integration.ts`：真 workflow 搭配真 activity 跑端到端流程。

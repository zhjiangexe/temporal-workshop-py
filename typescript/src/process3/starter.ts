import { Client } from '@temporalio/client';
import { randomUUID } from 'crypto';
import type { ProductChangeSpec } from './models';
import { productChangeWorkflow } from './workflow';

const TASK_QUEUE = 'price-change-ts-tq';

async function main() {
  const client = new Client();
  const spec: ProductChangeSpec = {
    requestId: `REQ-${randomUUID()}`,
    productId: 'P001',
    newPrice: 1490,
  };

  const handle = await client.workflow.start(productChangeWorkflow, {
    args: [spec],
    taskQueue: TASK_QUEUE,
    workflowId: `price-change-ts-${randomUUID()}`,
  });

  console.log(`WorkflowId: ${handle.workflowId}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

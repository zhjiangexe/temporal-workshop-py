import { Client, Connection } from '@temporalio/client';
import { randomUUID } from 'crypto';
import { TASK_QUEUE, TEMPORAL_URL, type ProductChangeSpec } from './models';
import { productChangeWorkflow } from './workflow';

async function main() {
  const connection = await Connection.connect({ address: TEMPORAL_URL });
  const client = new Client({ connection });
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
  await connection.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

import { Client, Connection } from '@temporalio/client';
import { randomUUID } from 'crypto';
import { TASK_QUEUE, TEMPORAL_URL, type ProductInput } from './models';
import { productOnboardingWorkflow } from './workflow';

async function main() {
  const connection = await Connection.connect({ address: TEMPORAL_URL });
  const client = new Client({ connection });
  const productInput: ProductInput = {
    requestId: randomUUID(),
    sku: 'SKU-12345',
    name: 'My Product',
    category: 'Shoes',
    currency: 'TWD',
    price: 1990,
    visible: true,
  };

  const handle = await client.workflow.start(productOnboardingWorkflow, {
    args: [productInput],
    taskQueue: TASK_QUEUE,
    workflowId: `product-ts-${randomUUID()}`,
  });

  console.log(`WorkflowId: ${handle.workflowId}`);
  await connection.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

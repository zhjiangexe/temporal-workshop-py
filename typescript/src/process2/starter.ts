import { Client } from '@temporalio/client';
import { randomUUID } from 'crypto';
import type { ProductInput } from './models';
import { productOnboardingWorkflow } from './workflow';

const TASK_QUEUE = 'product-onboarding-ts-tq';

async function main() {
  const client = new Client();
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
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

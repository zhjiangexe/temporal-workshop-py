import { Client } from '@temporalio/client';
import { randomUUID } from 'crypto';
import { registrationWorkflow } from './workflow';
import type { RegisterRequest } from './models';

const TASK_QUEUE = 'registration-ts-tq';

async function main() {
  const client = new Client();
  const userId = randomUUID();
  const request: RegisterRequest = {
    userId,
    email: 'flow@gmail.com',
  };

  const handle = await client.workflow.start(registrationWorkflow, {
    args: [request],
    taskQueue: TASK_QUEUE,
    workflowId: `registration-ts-${userId}`,
  });

  console.log(`WorkflowId: ${handle.workflowId}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

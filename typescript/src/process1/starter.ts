import { Client, Connection } from '@temporalio/client';
import { randomUUID } from 'crypto';
import { registrationWorkflow } from './workflow';
import { TASK_QUEUE, TEMPORAL_URL, type RegisterRequest } from './models';

async function main() {
  const connection = await Connection.connect({ address: TEMPORAL_URL });
  const client = new Client({ connection });
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
  await connection.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

import { Worker } from '@temporalio/worker';
import * as activities from './activities';

const TASK_QUEUE = 'product-onboarding-ts-tq';

async function main() {
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflow'),
    activities,
    taskQueue: TASK_QUEUE,
  });

  console.log(`Worker started on ${TASK_QUEUE}`);
  await worker.run();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

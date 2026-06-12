import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import { TASK_QUEUE, TEMPORAL_URL } from './models';

async function main() {
  const connection = await NativeConnection.connect({ address: TEMPORAL_URL });
  const worker = await Worker.create({
    connection,
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

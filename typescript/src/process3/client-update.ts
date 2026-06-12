import { Client, Connection } from '@temporalio/client';
import { TEMPORAL_URL, ReviewOutcome, type ReviewDecision } from './models';
import { productChangeWorkflow, submitReviewDecision } from './workflow';

async function main() {
  const workflowId = process.argv[2];
  if (!workflowId) {
    throw new Error('Usage: npm run process3:update -- <workflow-id>');
  }

  const connection = await Connection.connect({ address: TEMPORAL_URL });
  const client = new Client({ connection });
  const handle = client.workflow.getHandle<typeof productChangeWorkflow>(workflowId);
  const decision: ReviewDecision = {
    outcome: ReviewOutcome.APPROVE,
    approverId: 'marketing_lead',
  };

  await handle.executeUpdate(submitReviewDecision, {
    args: [decision],
  });

  console.log('Decision sent.');
  await connection.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

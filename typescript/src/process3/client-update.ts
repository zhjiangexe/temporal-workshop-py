import { Client } from '@temporalio/client';
import { ReviewOutcome, type ReviewDecision } from './models';
import { productChangeWorkflow, submitReviewDecision } from './workflow';

async function main() {
  const workflowId = process.argv[2];
  if (!workflowId) {
    throw new Error('Usage: npm run process3:update -- <workflow-id>');
  }

  const client = new Client();
  const handle = client.workflow.getHandle<typeof productChangeWorkflow>(workflowId);
  const decision: ReviewDecision = {
    outcome: ReviewOutcome.APPROVE,
    approverId: 'marketing_lead',
  };

  await handle.executeUpdate(submitReviewDecision, {
    args: [decision],
  });

  console.log('Decision sent.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

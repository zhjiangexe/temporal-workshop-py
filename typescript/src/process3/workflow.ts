import { condition, defineUpdate, proxyActivities, setHandler } from '@temporalio/workflow';
import type * as activities from './activities';
import type { ProductChangeSpec, ReviewDecision } from './models';
import { ReviewOutcome } from './models';

export const submitReviewDecision = defineUpdate<void, [ReviewDecision]>('submitReviewDecision');

const { notifyReviewer, recordDecision, applyNewPrice } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    initialInterval: '1 second',
    backoffCoefficient: 2,
    maximumAttempts: 5,
  },
});

export async function productChangeWorkflow(spec: ProductChangeSpec): Promise<void> {
  let decision: ReviewDecision | undefined;

  setHandler(submitReviewDecision, (input: ReviewDecision) => {
    if (decision === undefined) {
      decision = input;
    }
  });

  await notifyReviewer(spec);

  const receivedDecision = await condition(() => decision !== undefined, '48 hours');
  if (!receivedDecision) {
    decision = {
      outcome: ReviewOutcome.REJECT,
      approverId: 'system',
      reason: 'timeout after 48 hours',
    };
  }

  await recordDecision(spec, decision!);

  if (decision!.outcome === ReviewOutcome.REJECT) {
    return;
  }

  await applyNewPrice(spec);
}

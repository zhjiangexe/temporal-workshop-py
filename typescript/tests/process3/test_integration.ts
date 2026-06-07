import { randomUUID } from 'node:crypto';

import * as activities from '../../src/process3/activities';
import {
  productChangeWorkflow,
  submitReviewDecision,
} from '../../src/process3/workflow';
import { ReviewOutcome, type ProductChangeSpec } from '../../src/process3/models';
import { serialTest, withWorker } from '../helpers';

const noSleep = async () => undefined;

function makeSpec(): ProductChangeSpec {
  return {
    requestId: `REQ-${randomUUID()}`,
    productId: 'P001',
    newPrice: 1490,
  };
}

serialTest('process3 workflow runs with real activities', async () => {
  activities.resetActivityStateForTest();
  activities.setActivitySleepForTest(noSleep);

  await withWorker(
    'test-process3-integration',
    require.resolve('../../src/process3/workflow'),
    activities,
    async (env, taskQueue) => {
      const handle = await env.client.workflow.start(productChangeWorkflow, {
        args: [makeSpec()],
        taskQueue,
        workflowId: `test-process3-real-${randomUUID()}`,
      });

      await handle.executeUpdate(submitReviewDecision, {
        args: [{ outcome: ReviewOutcome.APPROVE, approverId: 'tester' }],
      });
      await handle.result();
    }
  );
});

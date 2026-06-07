import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

import {
  productChangeWorkflow,
  submitReviewDecision,
} from '../../src/process3/workflow';
import {
  ReviewOutcome,
  type ProductChangeSpec,
  type ReviewDecision,
} from '../../src/process3/models';
import { serialTest, withWorker } from '../helpers';

function makeSpec(): ProductChangeSpec {
  return {
    requestId: `REQ-${randomUUID()}`,
    productId: 'P001',
    newPrice: 1490,
  };
}

function trackingActivities(calls: Array<[string, unknown]>) {
  return {
    async notifyReviewer(spec: ProductChangeSpec) {
      calls.push(['notify', spec.productId]);
    },
    async recordDecision(_spec: ProductChangeSpec, decision: ReviewDecision) {
      calls.push(['record', decision.outcome]);
    },
    async applyNewPrice(spec: ProductChangeSpec) {
      calls.push(['apply', spec.newPrice]);
    },
  };
}

serialTest('process3 workflow applies new price after approval', async () => {
  const calls: Array<[string, unknown]> = [];

  await withWorker(
    'test-process3-workflow-approve',
    require.resolve('../../src/process3/workflow'),
    trackingActivities(calls),
    async (env, taskQueue) => {
      const handle = await env.client.workflow.start(productChangeWorkflow, {
        args: [makeSpec()],
        taskQueue,
        workflowId: `test-price-approve-${randomUUID()}`,
      });

      await handle.executeUpdate(submitReviewDecision, {
        args: [{ outcome: ReviewOutcome.APPROVE, approverId: 'tester' }],
      });
      await handle.result();
    }
  );

  assert.deepEqual(calls, [
    ['notify', 'P001'],
    ['record', ReviewOutcome.APPROVE],
    ['apply', 1490],
  ]);
});

serialTest('process3 workflow skips price apply after rejection', async () => {
  const calls: Array<[string, unknown]> = [];

  await withWorker(
    'test-process3-workflow-reject',
    require.resolve('../../src/process3/workflow'),
    trackingActivities(calls),
    async (env, taskQueue) => {
      const handle = await env.client.workflow.start(productChangeWorkflow, {
        args: [makeSpec()],
        taskQueue,
        workflowId: `test-price-reject-${randomUUID()}`,
      });

      await handle.executeUpdate(submitReviewDecision, {
        args: [
          {
            outcome: ReviewOutcome.REJECT,
            approverId: 'tester',
            reason: 'too expensive',
          },
        ],
      });
      await handle.result();
    }
  );

  assert.deepEqual(calls, [
    ['notify', 'P001'],
    ['record', ReviewOutcome.REJECT],
  ]);
});

serialTest('process3 workflow auto rejects after timeout', async () => {
  const calls: Array<[string, unknown]> = [];

  await withWorker(
    'test-process3-workflow-timeout',
    require.resolve('../../src/process3/workflow'),
    trackingActivities(calls),
    async (env, taskQueue) => {
      const handle = await env.client.workflow.start(productChangeWorkflow, {
        args: [makeSpec()],
        taskQueue,
        workflowId: `test-price-timeout-${randomUUID()}`,
      });

      await env.sleep('49 hours');
      await handle.result();
    }
  );

  assert.deepEqual(calls, [
    ['notify', 'P001'],
    ['record', ReviewOutcome.REJECT],
  ]);
});

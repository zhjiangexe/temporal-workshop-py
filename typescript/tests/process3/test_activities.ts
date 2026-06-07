import assert from 'node:assert/strict';
import { MockActivityEnvironment } from '@temporalio/testing';

import {
  applyNewPrice,
  notifyReviewer,
  recordDecision,
  resetActivityStateForTest,
  setActivitySleepForTest,
} from '../../src/process3/activities';
import { ReviewOutcome, type ProductChangeSpec } from '../../src/process3/models';
import { captureConsoleLogs, serialTest } from '../helpers';

const noSleep = async () => undefined;

function makeSpec(): ProductChangeSpec {
  return {
    requestId: 'REQ-001',
    productId: 'P001',
    newPrice: 1490,
  };
}

serialTest('process3 notifyReviewer outputs review request', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const logs = await captureConsoleLogs(async () => {
    await env.run(notifyReviewer, makeSpec());
  });

  assert.deepEqual(logs, ['[NOTIFY] requestId=REQ-001 newPrice=1490.00 product=P001']);
});

serialTest('process3 recordDecision outputs review result', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const logs = await captureConsoleLogs(async () => {
    await env.run(recordDecision, makeSpec(), {
      outcome: ReviewOutcome.APPROVE,
      approverId: 'tester',
    });
  });

  assert.deepEqual(logs, ['[RECORD] requestId=REQ-001, product=P001, review=approve']);
});

serialTest('process3 applyNewPrice outputs price change', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const logs = await captureConsoleLogs(async () => {
    await env.run(applyNewPrice, makeSpec());
  });

  assert.deepEqual(logs, ['[APPLY] requestId=REQ-001 set price=1490.00 for product=P001']);
});

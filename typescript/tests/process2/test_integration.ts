import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

import * as activities from '../../src/process2/activities';
import type { ProductInput, ProductPublishResult } from '../../src/process2/models';
import { productOnboardingWorkflow } from '../../src/process2/workflow';
import { serialTest, withWorker } from '../helpers';

const noSleep = async () => undefined;

function makeInput(): ProductInput {
  return {
    requestId: `REQ-${randomUUID()}`,
    sku: 'SKU-TEST',
    name: 'Test Product',
    category: 'Shoes',
    currency: 'TWD',
    price: 1990,
    visible: true,
  };
}

serialTest('process2 workflow runs success path with real activities', async () => {
  activities.resetActivityStateForTest();
  activities.setActivitySleepForTest(noSleep);
  const previousFailPublish = process.env.FAIL_PUBLISH;
  delete process.env.FAIL_PUBLISH;
  const input = makeInput();

  try {
    const result = await withWorker<ProductPublishResult>(
      'test-process2-integration-success',
      require.resolve('../../src/process2/workflow'),
      activities,
      async (env, taskQueue) =>
        env.client.workflow.execute(productOnboardingWorkflow, {
          args: [input],
          taskQueue,
          workflowId: `test-process2-real-${randomUUID()}`,
        })
    );

    assert.equal(result.published, true);
    assert.equal(result.productId, input.requestId);
    assert.equal(result.message, 'Product published via STP');
  } finally {
    if (previousFailPublish === undefined) {
      delete process.env.FAIL_PUBLISH;
    } else {
      process.env.FAIL_PUBLISH = previousFailPublish;
    }
  }
});

serialTest('process2 workflow runs compensation path with real activities', async () => {
  activities.resetActivityStateForTest();
  activities.setActivitySleepForTest(noSleep);
  const previousFailPublish = process.env.FAIL_PUBLISH;
  process.env.FAIL_PUBLISH = '1';

  try {
    const result = await withWorker<ProductPublishResult>(
      'test-process2-integration-fail',
      require.resolve('../../src/process2/workflow'),
      activities,
      async (env, taskQueue) =>
        env.client.workflow.execute(productOnboardingWorkflow, {
          args: [makeInput()],
          taskQueue,
          workflowId: `test-process2-real-fail-${randomUUID()}`,
        })
    );

    assert.equal(result.published, false);
    assert.equal(result.productId, '');
    assert.match(result.message, /Compensation executed/);
  } finally {
    if (previousFailPublish === undefined) {
      delete process.env.FAIL_PUBLISH;
    } else {
      process.env.FAIL_PUBLISH = previousFailPublish;
    }
  }
});

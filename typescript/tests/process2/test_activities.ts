import assert from 'node:assert/strict';
import { MockActivityEnvironment } from '@temporalio/testing';

import {
  createOrUpdateProduct,
  deleteProduct,
  publishToStorefront,
  resetActivityStateForTest,
  revertPricingAndAvailability,
  setActivitySleepForTest,
  setupPricingAndAvailability,
  unpublishFromStorefront,
} from '../../src/process2/activities';
import { serialTest } from '../helpers';

const noSleep = async () => undefined;

serialTest('process2 createOrUpdateProduct returns request id', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const productId = await env.run(createOrUpdateProduct, 'REQ-001');

  assert.equal(productId, 'REQ-001');
});

serialTest('process2 publishToStorefront respects failure flag', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();
  const previousFailPublish = process.env.FAIL_PUBLISH;

  try {
    delete process.env.FAIL_PUBLISH;
    await env.run(publishToStorefront, 'P001');

    process.env.FAIL_PUBLISH = '1';
    await assert.rejects(
      () => env.run(publishToStorefront, 'P001'),
      /Simulated publish failure/
    );
  } finally {
    if (previousFailPublish === undefined) {
      delete process.env.FAIL_PUBLISH;
    } else {
      process.env.FAIL_PUBLISH = previousFailPublish;
    }
  }
});

serialTest('process2 compensation activities complete', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  await env.run(setupPricingAndAvailability, 'P001');
  await env.run(unpublishFromStorefront, 'P001');
  await env.run(revertPricingAndAvailability, 'P001');
  await env.run(deleteProduct, 'P001');
});

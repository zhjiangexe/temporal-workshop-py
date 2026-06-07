import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

import type { ProductInput, ProductPublishResult } from '../../src/process2/models';
import { productOnboardingWorkflow } from '../../src/process2/workflow';
import { serialTest, withWorker } from '../helpers';

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

function trackingActivities(calls: string[], failPublish = false) {
  return {
    async createOrUpdateProduct(productId: string) {
      calls.push('create');
      return productId;
    },
    async setupPricingAndAvailability() {
      calls.push('setup');
    },
    async publishToStorefront() {
      calls.push('publish');
      if (failPublish) {
        throw new Error('storefront down');
      }
    },
    async deleteProduct() {
      calls.push('delete');
    },
    async revertPricingAndAvailability() {
      calls.push('revert');
    },
    async unpublishFromStorefront() {
      calls.push('unpublish');
    },
  };
}

serialTest('process2 workflow publishes product on success', async () => {
  const calls: string[] = [];
  const input = makeInput();

  const result = await withWorker<ProductPublishResult>(
    'test-process2-workflow-success',
    require.resolve('../../src/process2/workflow'),
    trackingActivities(calls),
    async (env, taskQueue) =>
      env.client.workflow.execute(productOnboardingWorkflow, {
        args: [input],
        taskQueue,
        workflowId: `test-product-success-${randomUUID()}`,
      })
  );

  assert.deepEqual(result, {
    productId: input.requestId,
    published: true,
    message: 'Product published via STP',
  });
  assert.deepEqual(calls, ['create', 'setup', 'publish']);
});

serialTest('process2 workflow compensates in reverse order when publish fails', async () => {
  const calls: string[] = [];

  const result = await withWorker<ProductPublishResult>(
    'test-process2-workflow-fail',
    require.resolve('../../src/process2/workflow'),
    trackingActivities(calls, true),
    async (env, taskQueue) =>
      env.client.workflow.execute(productOnboardingWorkflow, {
        args: [makeInput()],
        taskQueue,
        workflowId: `test-product-fail-${randomUUID()}`,
      })
  );

  assert.equal(result.published, false);
  assert.equal(result.productId, '');
  assert.match(result.message, /Compensation executed/);
  assert.deepEqual(calls, [
    'create',
    'setup',
    'publish',
    'publish',
    'unpublish',
    'revert',
    'delete',
  ]);
});

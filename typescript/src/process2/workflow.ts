import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';
import type { ProductInput, ProductPublishResult } from './models';

const {
  createOrUpdateProduct,
  setupPricingAndAvailability,
  publishToStorefront,
  deleteProduct,
  revertPricingAndAvailability,
  unpublishFromStorefront,
} = proxyActivities<typeof activities>({
  scheduleToCloseTimeout: '15 seconds',
  retry: {
    maximumAttempts: 2,
    initialInterval: '5 seconds',
    backoffCoefficient: 2,
  },
});

export async function productOnboardingWorkflow(
  input: ProductInput
): Promise<ProductPublishResult> {
  const compensations: Array<() => Promise<void>> = [];

  try {
    let productId = input.requestId;

    compensations.push(() => deleteProduct(productId));
    productId = await createOrUpdateProduct(productId);

    compensations.push(() => revertPricingAndAvailability(productId));
    await setupPricingAndAvailability(productId);

    compensations.push(() => unpublishFromStorefront(productId));
    await publishToStorefront(productId);

    return {
      productId,
      published: true,
      message: 'Product published via STP',
    };
  } catch (err) {
    for (const compensate of compensations.reverse()) {
      await compensate();
    }

    return {
      productId: '',
      published: false,
      message: `Failed to publish product. Compensation executed: ${String(err)}`,
    };
  }
}

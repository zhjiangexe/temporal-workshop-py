const defaultSleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
let sleep = defaultSleep;

export function setActivitySleepForTest(fn: typeof sleep): void {
  sleep = fn;
}

export function resetActivityStateForTest(): void {
  sleep = defaultSleep;
}

export async function createOrUpdateProduct(productId: string): Promise<string> {
  await sleep(5000);
  console.log(`create or update product: ${productId}`);
  return productId;
}

export async function setupPricingAndAvailability(productId: string): Promise<void> {
  await sleep(5000);
  console.log(`setup pricing and availability: ${productId}`);
}

export async function publishToStorefront(productId: string): Promise<void> {
  if (process.env.FAIL_PUBLISH) {
    throw new Error('Simulated publish failure (FAIL_PUBLISH=1)');
  }
  await sleep(5000);
  console.log(`publish to storefront: ${productId}`);
}

export async function deleteProduct(productId: string): Promise<void> {
  await sleep(10000);
  console.log(`delete product: ${productId}`);
}

export async function revertPricingAndAvailability(productId: string): Promise<void> {
  await sleep(10000);
  console.log(`revert pricing ${productId}`);
}

export async function unpublishFromStorefront(productId: string): Promise<void> {
  await sleep(10000);
  console.log(`unpublish: ${productId}`);
}

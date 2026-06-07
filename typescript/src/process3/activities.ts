import type { ProductChangeSpec, ReviewDecision } from './models';

const defaultSleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
let sleep = defaultSleep;

export function setActivitySleepForTest(fn: typeof sleep): void {
  sleep = fn;
}

export function resetActivityStateForTest(): void {
  sleep = defaultSleep;
}

export async function notifyReviewer(spec: ProductChangeSpec): Promise<void> {
  await sleep(5000);
  console.log(
    `[NOTIFY] requestId=${spec.requestId} newPrice=${spec.newPrice.toFixed(2)} product=${spec.productId}`
  );
}

export async function recordDecision(
  spec: ProductChangeSpec,
  decision: ReviewDecision
): Promise<void> {
  await sleep(5000);
  console.log(
    `[RECORD] requestId=${spec.requestId}, product=${spec.productId}, review=${decision.outcome}`
  );
}

export async function applyNewPrice(spec: ProductChangeSpec): Promise<void> {
  await sleep(5000);
  console.log(
    `[APPLY] requestId=${spec.requestId} set price=${spec.newPrice.toFixed(2)} for product=${spec.productId}`
  );
}

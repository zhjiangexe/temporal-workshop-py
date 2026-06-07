import { Context } from '@temporalio/activity';
import type { RegisterRequest } from './models';

const users = new Set<string>();
const ops = new Set<string>();

const defaultSleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
let sleep = defaultSleep;

export function setActivitySleepForTest(fn: typeof sleep): void {
  sleep = fn;
}

export function resetActivityStateForTest(): void {
  users.clear();
  ops.clear();
  sleep = defaultSleep;
}

export async function createAccount(request: RegisterRequest): Promise<void> {
  if (users.has(request.userId)) {
    return;
  }
  users.add(request.userId);
  await sleep(5000);
  console.log(`Created account for ${request.userId} (${request.email})`);
}

export async function addPoints(
  userId: string,
  points: number,
  opKey: string
): Promise<void> {
  const dedupeKey = `POINTS#${userId}#${opKey}`;
  const { attempt } = Context.current().info;

  if (ops.has(dedupeKey)) {
    console.log(`[idempotent] addPoints skipped for ${userId} [op=${opKey}]`);
    return;
  }

  if (attempt <= 3) {
    throw new Error(`DB connection failed (simulated), attempt ${attempt}`);
  }

  await sleep(5000);
  console.log(`Added ${points} points to ${userId} [op=${opKey}]`);
  ops.add(dedupeKey);
}

export async function sendEmail(email: string, messageId: string): Promise<void> {
  const dedupeKey = `EMAIL#${messageId}`;
  if (ops.has(dedupeKey)) {
    console.log(`[idempotent] sendEmail skipped for ${email} [msgId=${messageId}]`);
    return;
  }
  ops.add(dedupeKey);
  await sleep(5000);
  console.log(`Sent welcome email to ${email} [msgId=${messageId}]`);
}

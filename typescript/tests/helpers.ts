import test from 'node:test';
import { randomUUID } from 'node:crypto';
import { Worker } from '@temporalio/worker';
import { TestWorkflowEnvironment } from '@temporalio/testing';

let testChain = Promise.resolve();

export function serialTest(name: string, fn: () => Promise<void>): void {
  test(name, async () => {
    const previous = testChain;
    let release!: () => void;
    testChain = testChain.then(
      () =>
        new Promise<void>((resolve) => {
          release = resolve;
        })
    );

    await previous;
    try {
      await fn();
    } finally {
      release();
    }
  });
}

export async function withWorker<T>(
  taskQueuePrefix: string,
  workflowsPath: string,
  activities: Record<string, (...args: any[]) => unknown>,
  run: (env: TestWorkflowEnvironment, taskQueue: string) => Promise<T>
): Promise<T> {
  const env = await TestWorkflowEnvironment.createTimeSkipping();
  const taskQueue = `${taskQueuePrefix}-${randomUUID()}`;

  try {
    const worker = await Worker.create({
      connection: env.nativeConnection,
      namespace: env.namespace,
      taskQueue,
      workflowsPath,
      activities,
    });

    return await worker.runUntil(run(env, taskQueue));
  } finally {
    await env.teardown();
  }
}

export async function captureConsoleLogs(run: () => Promise<void>): Promise<string[]> {
  const originalLog = console.log;
  const logs: string[] = [];
  console.log = (...args: unknown[]) => {
    logs.push(args.map(String).join(' '));
  };

  try {
    await run();
    return logs;
  } finally {
    console.log = originalLog;
  }
}

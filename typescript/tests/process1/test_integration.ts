import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

import * as activities from '../../src/process1/activities';
import { registrationWorkflow } from '../../src/process1/workflow';
import { captureConsoleLogs, serialTest, withWorker } from '../helpers';

const noSleep = async () => undefined;

serialTest('process1 workflow runs with real activities', async () => {
  activities.resetActivityStateForTest();
  activities.setActivitySleepForTest(noSleep);
  const userId = `U-${randomUUID()}`;

  const logs = await captureConsoleLogs(async () => {
    await withWorker(
      'test-process1-integration',
      require.resolve('../../src/process1/workflow'),
      activities,
      async (env, taskQueue) =>
        env.client.workflow.execute(registrationWorkflow, {
          args: [{ userId, email: 'test@example.com' }],
          taskQueue,
          workflowId: `test-process1-real-${randomUUID()}`,
        })
    );
  });

  assert.deepEqual(logs, [
    `Created account for ${userId} (test@example.com)`,
    `Added 500 points to ${userId} [op=signupBonus]`,
    `Sent welcome email to test@example.com [msgId=welcome-${userId}]`,
  ]);
});

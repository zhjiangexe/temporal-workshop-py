import assert from 'node:assert/strict';
import { MockActivityEnvironment } from '@temporalio/testing';

import {
  addPoints,
  createAccount,
  resetActivityStateForTest,
  sendEmail,
  setActivitySleepForTest,
} from '../../src/process1/activities';
import { captureConsoleLogs, serialTest } from '../helpers';

const noSleep = async () => undefined;

serialTest('process1 createAccount is idempotent', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const logs = await captureConsoleLogs(async () => {
    await env.run(createAccount, { userId: 'U001', email: 'user@example.com' });
    await env.run(createAccount, { userId: 'U001', email: 'user@example.com' });
  });

  assert.deepEqual(logs, ['Created account for U001 (user@example.com)']);
});

serialTest('process1 addPoints retries before recording operation', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);

  const firstAttempt = new MockActivityEnvironment({ attempt: 1 });
  await assert.rejects(
    () => firstAttempt.run(addPoints, 'U001', 500, 'signupBonus'),
    /DB connection failed/
  );

  const fourthAttempt = new MockActivityEnvironment({ attempt: 4 });
  const logs = await captureConsoleLogs(async () => {
    await fourthAttempt.run(addPoints, 'U001', 500, 'signupBonus');
    await fourthAttempt.run(addPoints, 'U001', 500, 'signupBonus');
  });

  assert.deepEqual(logs, [
    'Added 500 points to U001 [op=signupBonus]',
    '[idempotent] addPoints skipped for U001 [op=signupBonus]',
  ]);
});

serialTest('process1 sendEmail is idempotent', async () => {
  resetActivityStateForTest();
  setActivitySleepForTest(noSleep);
  const env = new MockActivityEnvironment();

  const logs = await captureConsoleLogs(async () => {
    await env.run(sendEmail, 'user@example.com', 'welcome-U001');
    await env.run(sendEmail, 'user@example.com', 'welcome-U001');
  });

  assert.deepEqual(logs, [
    'Sent welcome email to user@example.com [msgId=welcome-U001]',
    '[idempotent] sendEmail skipped for user@example.com [msgId=welcome-U001]',
  ]);
});

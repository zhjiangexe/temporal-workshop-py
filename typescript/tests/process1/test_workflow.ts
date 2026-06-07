import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

import { registrationWorkflow } from '../../src/process1/workflow';
import { serialTest, withWorker } from '../helpers';

serialTest('process1 workflow runs registration activities in order', async () => {
  const calls: string[] = [];

  await withWorker(
    'test-process1-workflow',
    require.resolve('../../src/process1/workflow'),
    {
      async createAccount(request: { userId: string; email: string }) {
        calls.push(`createAccount:${request.userId}:${request.email}`);
      },
      async addPoints(userId: string, points: number, opKey: string) {
        calls.push(`addPoints:${userId}:${points}:${opKey}`);
      },
      async sendEmail(email: string, messageId: string) {
        calls.push(`sendEmail:${email}:${messageId}`);
      },
    },
    async (env, taskQueue) =>
      env.client.workflow.execute(registrationWorkflow, {
        args: [{ userId: 'U001', email: 'test@example.com' }],
        taskQueue,
        workflowId: `test-registration-${randomUUID()}`,
      })
  );

  assert.deepEqual(calls, [
    'createAccount:U001:test@example.com',
    'addPoints:U001:500:signupBonus',
    'sendEmail:test@example.com:welcome-U001',
  ]);
});

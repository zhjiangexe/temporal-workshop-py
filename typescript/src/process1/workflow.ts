import { proxyActivities } from "@temporalio/workflow";
import type * as activities from "./activities";
import type { RegisterRequest } from "./models";

const { createAccount, addPoints, sendEmail } = proxyActivities<
  typeof activities
>({
  startToCloseTimeout: "15 seconds",
  heartbeatTimeout: "10 seconds",
  retry: {
    initialInterval: "5 seconds",
    backoffCoefficient: 2,
    maximumInterval: "100 seconds",
  },
});

export async function registrationWorkflow(
  request: RegisterRequest,
): Promise<void> {
  // step1: 安排執行 create_account
  await createAccount(request);

  // step2: 安排執行 add_points
  await addPoints(request.userId, 500, "signupBonus");

  // step3: 安排執行 send_email
  await sendEmail(request.email, `welcome-${request.userId}`);
}

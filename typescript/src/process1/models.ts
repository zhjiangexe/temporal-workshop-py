export const TEMPORAL_URL = 'localhost:7233';
export const TASK_QUEUE = 'registration-ts-tq';

export interface RegisterRequest {
  userId: string;
  email: string;
}

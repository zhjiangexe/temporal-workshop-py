export const TEMPORAL_URL = 'localhost:7233';
export const TASK_QUEUE = 'product-onboarding-ts-tq';

export interface ProductInput {
  requestId: string;
  sku: string;
  name: string;
  category: string;
  currency: string;
  price: number;
  visible: boolean;
}

export interface ProductPublishResult {
  published: boolean;
  message: string;
  productId: string;
}

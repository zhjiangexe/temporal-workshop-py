export enum ReviewOutcome {
  APPROVE = 'approve',
  REJECT = 'reject',
}

export interface ProductChangeSpec {
  requestId: string;
  productId: string;
  newPrice: number;
}

export interface ReviewDecision {
  outcome: ReviewOutcome;
  approverId: string;
  reason?: string;
}

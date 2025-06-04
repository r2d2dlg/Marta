
export type EmailStatus = 'pending_review' | 'approved' | 'sent' | 'draft' | 'error';

export interface Email {
  id: string;
  senderName: string;
  senderEmail: string;
  subject: string;
  originalContent: string;
  summary?: string;
  suggestedResponse: string; // Changed from optional to required, will be empty string initially
  status: EmailStatus;
  receivedAt: Date;
  isLoadingSummary?: boolean;
  isLoadingResponse?: boolean;
}

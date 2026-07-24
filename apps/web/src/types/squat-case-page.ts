import type { CaseStatus } from "@/lib/case-status";

export type SquatCaseListItem = {
  case_id: string;
  participant_code: string | null;
  status: CaseStatus;
  protocol_review_status: string | null;
  created_at: string;
  updated_at: string;
};

export type SquatCasePage = {
  items: SquatCaseListItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

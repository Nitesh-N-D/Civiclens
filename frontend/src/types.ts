export type Citation = { id: string; title: string; url: string; owner: string; locator?: string; status: string; desk_checked_at?: string; human_verified_at?: string | null };
export type Change = { id: string; scheme: string; status: "official" | "reported"; summary: string; source_title: string; source_url: string; checked_at: string };
export type Answer = { text: string; citations: Citation[]; mode: "ai" | "search"; warning?: string; notices?: Change[] };
export type Turn = { question: string; answer: Answer; pending?: boolean };
export type SchemeCard = { id: string; title: string; department: string; category: string; overview: string; url: string; source_id: string; status: string; eligibility_enabled: boolean };
export type AdminOverview = {
  sources: Citation[];
  source_count: number;
  human_verified_count: number;
  review_pending_count: number;
  provider: { state?: string; configured: boolean; configured_keys: number; last_request_succeeded: boolean | null; last_failure_category: string | null; model: string | null };
  monitoring: string;
  mutations_enabled: boolean;
  you?: { email: string; role: string; via: string };
  recent_checks?: SourceCheck[];
  recent_audit?: { id: number; actor: string; action: string; entity_id: string; created_at: string }[];
};
export type SourceCheck = { id: number; source_id: string; outcome: string; note?: string; checked_at: string };
export type EligibilityQuestion = { field: string; options: string[]; purpose: string };
export type EligibilityStatus = "appears_eligible" | "appears_ineligible" | "insufficient_information" | "requires_official_verification";
export type EligibilityResult = {
  scheme_id: string;
  status: EligibilityStatus;
  criteria: { id: string; label: string; field: string; outcome: "met" | "not_met" | "unknown"; source_id: string; basis: string; human_verified: boolean }[];
  missing_fields: string[];
  documents: { name: string; reason: string; criterion_id: string; source_id: string; mandatory: boolean; verification: string }[];
  guidance: { route: string; steps: string[]; contact: string; source_id: string };
};
export type ComparisonRow = { scheme_id: string; criteria: string[]; documents: string[]; route: string; contact: string; source_id: string };

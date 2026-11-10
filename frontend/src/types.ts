export type Citation = { id: string; title: string; url: string; owner: string; locator?: string; status: string; desk_checked_at?: string; human_verified_at?: string | null };
export type Change = { id: string; scheme: string; status: "official" | "reported"; summary: string; source_title: string; source_url: string; checked_at: string };
export type Answer = { text: string; citations: Citation[]; mode: "ai" | "search"; warning?: string; notices?: Change[] };
export type Turn = { question: string; answer: Answer };

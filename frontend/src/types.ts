export type Page = "dashboard" | "check-customer" | "insights" | "revenue-impact" | "help";

export type CustomerInput = {
  age: number;
  monthlySpend: number;
  tenure: number;
  loginActivity: number;
  supportTickets: number;
};

export type RiskLevel = "Low" | "Medium" | "High";

export type ChurnResult = {
  churnProbability: number;
  riskLevel: RiskLevel;
  reasons: string[];
  actions: string[];
};

export type CustomerProfile = CustomerInput & {
  id: string;
  name: string;
};

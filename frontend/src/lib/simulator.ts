import type { ChurnResult, CustomerInput, CustomerProfile, RiskLevel } from "../types";

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const toRiskLevel = (probability: number): RiskLevel => {
  if (probability >= 70) return "High";
  if (probability >= 40) return "Medium";
  return "Low";
};

export const defaultCustomerInput: CustomerInput = {
  age: 35,
  monthlySpend: 89,
  tenure: 12,
  loginActivity: 10,
  supportTickets: 2
};

export const analyzeChurn = (input: CustomerInput): ChurnResult => {
  const reasons: string[] = [];
  const actions: string[] = [];

  let score = 20;

  if (input.loginActivity <= 6) {
    score += 28;
    reasons.push("Low app usage");
    actions.push("Send an engagement email with helpful tips");
  } else if (input.loginActivity <= 12) {
    score += 14;
    reasons.push("Usage is lower than ideal");
    actions.push("Share quick product wins to build daily habit");
  } else {
    score -= 8;
  }

  if (input.supportTickets >= 5) {
    score += 24;
    reasons.push("Frequent complaints");
    actions.push("Assign priority support to solve issues quickly");
  } else if (input.supportTickets >= 3) {
    score += 12;
    reasons.push("Multiple support requests");
    actions.push("Schedule a short success check-in call");
  } else {
    score -= 5;
  }

  if (input.tenure <= 6) {
    score += 18;
    reasons.push("New customer with low loyalty");
    actions.push("Offer onboarding guidance for the next 30 days");
  } else if (input.tenure >= 24) {
    score -= 10;
  }

  if (input.monthlySpend >= 140) {
    score += 12;
    reasons.push("High monthly cost may feel expensive");
    actions.push("Offer a tailored plan or discount");
  } else if (input.monthlySpend <= 45) {
    score += 6;
    reasons.push("Low spend can indicate low product adoption");
    actions.push("Upsell value-focused features with guidance");
  }

  if (input.age < 23 || input.age > 65) {
    score += 4;
  }

  const churnProbability = clamp(Math.round(score), 3, 95);
  const riskLevel = toRiskLevel(churnProbability);

  if (reasons.length === 0) {
    reasons.push("Healthy product usage and stable account behavior");
  }

  if (actions.length === 0) {
    actions.push("Keep regular check-ins and monitor monthly activity");
  }

  return {
    churnProbability,
    riskLevel,
    reasons: reasons.slice(0, 3),
    actions: actions.slice(0, 3)
  };
};

export const createDemoCustomers = (): CustomerProfile[] => {
  return [
    { id: "C001", name: "Aarav Sharma", age: 42, monthlySpend: 120, tenure: 8, loginActivity: 6, supportTickets: 4 },
    { id: "C002", name: "Isha Patel", age: 31, monthlySpend: 95, tenure: 30, loginActivity: 19, supportTickets: 1 },
    { id: "C003", name: "Rahul Mehta", age: 27, monthlySpend: 150, tenure: 5, loginActivity: 4, supportTickets: 6 },
    { id: "C004", name: "Neha Verma", age: 38, monthlySpend: 82, tenure: 16, loginActivity: 12, supportTickets: 3 },
    { id: "C005", name: "Kabir Nair", age: 45, monthlySpend: 132, tenure: 10, loginActivity: 7, supportTickets: 5 },
    { id: "C006", name: "Sana Khan", age: 29, monthlySpend: 72, tenure: 22, loginActivity: 17, supportTickets: 1 },
    { id: "C007", name: "Vikram Rao", age: 34, monthlySpend: 58, tenure: 9, loginActivity: 8, supportTickets: 2 },
    { id: "C008", name: "Meera Singh", age: 40, monthlySpend: 110, tenure: 14, loginActivity: 9, supportTickets: 4 }
  ];
};

export const formatCurrency = (value: number) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value);
};

export const riskColorClass = (risk: RiskLevel) => {
  if (risk === "High") return "text-red-600 bg-red-50 border-red-200";
  if (risk === "Medium") return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-green-600 bg-green-50 border-green-200";
};

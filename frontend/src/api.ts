import { analyzeChurn } from "./lib/simulator";
import type { ChurnResult, CustomerInput } from "./types";

// Frontend-only mock API to preserve a familiar async interface.
export const api = {
  async predict(payload: CustomerInput): Promise<ChurnResult> {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return analyzeChurn(payload);
  }
};

import { useMemo, useState } from "react";
import { LoaderCircle } from "lucide-react";

import { InfoTip } from "../components/InfoTip";
import { PageHeader } from "../components/PageHeader";
import { StepIndicator } from "../components/StepIndicator";
import { analyzeChurn, defaultCustomerInput, riskColorClass } from "../lib/simulator";
import type { ChurnResult, CustomerInput } from "../types";

type CheckCustomerPageProps = {
  onResult?: (result: ChurnResult) => void;
};

function Field({
  label,
  hint,
  min,
  max,
  value,
  onChange
}: {
  label: string;
  hint: string;
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="space-y-1">
      <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
        {label}
        <InfoTip text={hint} />
      </span>
      <input
        type="number"
        className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-500"
        value={value}
        min={min}
        max={max}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

export function CheckCustomerPage({ onResult }: CheckCustomerPageProps) {
  const [input, setInput] = useState<CustomerInput>(defaultCustomerInput);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChurnResult | null>(null);
  const [simLogin, setSimLogin] = useState(defaultCustomerInput.loginActivity);
  const [simSpend, setSimSpend] = useState(defaultCustomerInput.monthlySpend);

  const step: 1 | 2 | 3 = result ? 3 : 1;

  const simulationResult = useMemo(() => {
    if (!result) return null;
    return analyzeChurn({ ...input, loginActivity: simLogin, monthlySpend: simSpend });
  }, [input, result, simLogin, simSpend]);

  const analyze = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 900));
    const outcome = analyzeChurn(input);
    setResult(outcome);
    setSimLogin(input.loginActivity);
    setSimSpend(input.monthlySpend);
    setLoading(false);
    onResult?.(outcome);
  };

  return (
    <section className="space-y-5">
      <PageHeader
        title="Check Customer"
        description="Enter customer details to understand churn risk and what action to take next."
      />

      <StepIndicator currentStep={step} />

      <div className="grid gap-5 xl:grid-cols-2">
        <article className="space-y-4 rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-slate-900">Step 1: Enter customer data</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field
              label="Age"
              hint="Customer age in years"
              min={18}
              max={90}
              value={input.age}
              onChange={(value) => setInput((prev) => ({ ...prev, age: value }))}
            />
            <Field
              label="Monthly Spend"
              hint="How much this customer pays each month"
              min={1}
              max={500}
              value={input.monthlySpend}
              onChange={(value) => setInput((prev) => ({ ...prev, monthlySpend: value }))}
            />
            <Field
              label="Tenure"
              hint="How long the customer has stayed with you in months"
              min={0}
              max={120}
              value={input.tenure}
              onChange={(value) => setInput((prev) => ({ ...prev, tenure: value }))}
            />
            <Field
              label="Login Activity"
              hint="Number of login days in the last 30 days"
              min={0}
              max={30}
              value={input.loginActivity}
              onChange={(value) => setInput((prev) => ({ ...prev, loginActivity: value }))}
            />
            <Field
              label="Support Tickets"
              hint="How many support requests the customer raised recently"
              min={0}
              max={20}
              value={input.supportTickets}
              onChange={(value) => setInput((prev) => ({ ...prev, supportTickets: value }))}
            />
          </div>

          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            onClick={analyze}
            disabled={loading}
          >
            {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </article>

        <article className="space-y-4 rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-slate-900">Step 2: See result</h2>
          {!result ? (
            <p className="text-sm text-slate-600">Run Analyze to view churn probability, risk level, and recommendations.</p>
          ) : (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-600">Churn Probability</p>
                <p className="mt-1 text-2xl font-semibold text-slate-900">{result.churnProbability}% chance of leaving</p>
                <div className="mt-3 h-3 w-full rounded-full bg-slate-200">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{ width: `${result.churnProbability}%` }}
                  />
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-600">Risk Level</p>
                <span className={`mt-1 inline-block rounded-full border px-3 py-1 text-sm font-medium ${riskColorClass(result.riskLevel)}`}>
                  {result.riskLevel}
                </span>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-800">Why this risk?</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
                  {result.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-800">What you can do</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
                  {result.actions.map((action) => (
                    <li key={action}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </article>
      </div>

      <article className="space-y-4 rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">What-If Simulator</h2>
        <p className="text-sm text-slate-600">Try changing values to see how risk changes.</p>

        {!simulationResult ? (
          <p className="text-sm text-slate-500">Run Analyze first to unlock simulator.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm text-slate-700">
              Login activity (days in 30 days): {simLogin}
              <input
                type="range"
                min={0}
                max={30}
                value={simLogin}
                onChange={(event) => setSimLogin(Number(event.target.value))}
                className="w-full"
              />
            </label>

            <label className="space-y-2 text-sm text-slate-700">
              Monthly spend: {simSpend}
              <input
                type="range"
                min={10}
                max={300}
                value={simSpend}
                onChange={(event) => setSimSpend(Number(event.target.value))}
                className="w-full"
              />
            </label>

            <div className="rounded-lg bg-slate-50 p-4 md:col-span-2">
              <p className="text-sm text-slate-600">Updated churn probability</p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">{simulationResult.churnProbability}%</p>
            </div>
          </div>
        )}
      </article>
    </section>
  );
}

import { PageHeader } from "../components/PageHeader";

export function HelpPage() {
  return (
    <section className="space-y-5">
      <PageHeader
        title="Help"
        description="Beginner-friendly guide so anyone can use this tool with confidence."
      />

      <article className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">What is churn?</h2>
        <p className="mt-2 text-sm text-slate-700">Churn means customers leaving your service.</p>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">How to use this tool</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-700">
          <li>Open Check Customer.</li>
          <li>Enter customer details.</li>
          <li>Select Analyze.</li>
          <li>Read the risk, reasons, and recommended actions.</li>
          <li>Use the What-If Simulator to test improvements.</li>
        </ol>
      </article>
    </section>
  );
}

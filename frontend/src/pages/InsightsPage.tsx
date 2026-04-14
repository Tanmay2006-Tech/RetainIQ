import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { PageHeader } from "../components/PageHeader";

type InsightsItem = {
  reason: string;
  count: number;
};

type InsightsPageProps = {
  reasons: InsightsItem[];
};

export function InsightsPage({ reasons }: InsightsPageProps) {
  const topReason = reasons[0]?.reason ?? "Low activity";

  return (
    <section className="space-y-5">
      <PageHeader
        title="Insights"
        description="Understand the top reasons customers leave, explained in plain language."
      />

      <article className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Top reasons customers leave</h2>
        <p className="mt-1 text-sm text-slate-600">Most common issue: {topReason}</p>

        <div className="mt-4 h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={reasons} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="reason" tick={{ fill: "#475569", fontSize: 12 }} interval={0} angle={-10} textAnchor="end" height={70} />
              <YAxis tick={{ fill: "#475569", fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>
    </section>
  );
}

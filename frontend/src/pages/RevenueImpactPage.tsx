import type { CustomerProfile } from "../types";
import { PageHeader } from "../components/PageHeader";

type RevenueCustomer = CustomerProfile & {
  churnProbability: number;
  revenueAtRisk: number;
};

type RevenueImpactPageProps = {
  totalRevenueAtRisk: string;
  topCustomers: RevenueCustomer[];
  formatCurrency: (value: number) => string;
};

export function RevenueImpactPage({ totalRevenueAtRisk, topCustomers, formatCurrency }: RevenueImpactPageProps) {
  return (
    <section className="space-y-5">
      <PageHeader
        title="Revenue Impact"
        description="These customers are most likely to leave and may cause loss if not engaged now."
      />

      <article className="rounded-xl border border-slate-200 bg-white p-5">
        <p className="text-sm text-slate-600">Total revenue at risk</p>
        <p className="mt-2 text-3xl font-semibold text-red-600">{totalRevenueAtRisk}</p>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Top 5 customers to save</h2>
        <p className="mt-1 text-sm text-slate-600">Focus outreach on this list first.</p>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-3 py-2 font-medium">Customer</th>
                <th className="px-3 py-2 font-medium">Churn Probability</th>
                <th className="px-3 py-2 font-medium">Revenue at Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {topCustomers.map((customer) => (
                <tr key={customer.id}>
                  <td className="px-3 py-2 text-slate-800">{customer.name}</td>
                  <td className="px-3 py-2 text-slate-800">{customer.churnProbability}%</td>
                  <td className="px-3 py-2 font-medium text-slate-900">{formatCurrency(customer.revenueAtRisk)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}

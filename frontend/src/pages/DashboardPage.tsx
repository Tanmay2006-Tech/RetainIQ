import { InfoTip } from "../components/InfoTip";
import { KpiCardSimple } from "../components/KpiCardSimple";
import { PageHeader } from "../components/PageHeader";

type DashboardPageProps = {
  totalCustomers: number;
  highRiskCustomers: number;
  churnRate: number;
  revenueAtRisk: string;
};

export function DashboardPage({ totalCustomers, highRiskCustomers, churnRate, revenueAtRisk }: DashboardPageProps) {
  return (
    <section className="space-y-5">
      <PageHeader
        title="Dashboard"
        description="Quick overview of customer churn so your team can understand the situation at a glance."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCardSimple
          title="Total Customers"
          value={String(totalCustomers)}
          description="People currently using your service."
        />
        <KpiCardSimple
          title="High Risk Customers"
          value={String(highRiskCustomers)}
          description="Users likely to leave soon."
        />
        <KpiCardSimple
          title="Churn Rate"
          value={`${churnRate.toFixed(1)}%`}
          description="Estimated share of customers who may leave."
        />
        <KpiCardSimple
          title="Revenue at Risk"
          value={revenueAtRisk}
          description="Money you may lose if high-risk users churn."
        />
      </div>

      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-slate-700">
        <p className="flex items-center gap-2 font-medium text-slate-900">
          Churn in simple words
          <InfoTip text="Churn means customers stopping your service." />
        </p>
        <p className="mt-2">When churn risk goes up, retention actions should happen early to protect revenue.</p>
      </div>
    </section>
  );
}

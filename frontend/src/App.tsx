import { useMemo, useState, type ComponentType } from "react";
import { CircleHelp, LayoutDashboard, Search, Wallet, BarChart3, Menu } from "lucide-react";

import { DashboardPage } from "./pages/DashboardPage";
import { CheckCustomerPage } from "./pages/CheckCustomerPage";
import { InsightsPage } from "./pages/InsightsPage";
import { RevenueImpactPage } from "./pages/RevenueImpactPage";
import { HelpPage } from "./pages/HelpPage";
import { analyzeChurn, createDemoCustomers, formatCurrency } from "./lib/simulator";
import type { ChurnResult, Page } from "./types";

const navItems: Array<{ id: Page; label: string; icon: ComponentType<{ className?: string }> }> = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "check-customer", label: "Check Customer", icon: Search },
  { id: "insights", label: "Insights", icon: BarChart3 },
  { id: "revenue-impact", label: "Revenue Impact", icon: Wallet },
  { id: "help", label: "Help", icon: CircleHelp }
];

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [latestResult, setLatestResult] = useState<ChurnResult | null>(null);

  const customers = useMemo(() => createDemoCustomers(), []);

  const customerWithRisk = useMemo(() => {
    return customers.map((customer) => {
      const result = analyzeChurn(customer);
      const revenueAtRisk = (customer.monthlySpend * result.churnProbability * 10) / 100;
      return {
        ...customer,
        churnProbability: result.churnProbability,
        riskLevel: result.riskLevel,
        reasons: result.reasons,
        revenueAtRisk
      };
    });
  }, [customers]);

  const totalCustomers = customerWithRisk.length;
  const highRiskCustomers = customerWithRisk.filter((customer) => customer.riskLevel === "High").length;
  const churnRate = customerWithRisk.reduce((sum, customer) => sum + customer.churnProbability, 0) / totalCustomers;
  const revenueAtRiskRaw = customerWithRisk.reduce((sum, customer) => sum + customer.revenueAtRisk, 0);

  const reasonsMap = new Map<string, number>();
  customerWithRisk.forEach((customer) => {
    customer.reasons.forEach((reason) => {
      reasonsMap.set(reason, (reasonsMap.get(reason) ?? 0) + 1);
    });
  });

  const topReasons = Array.from(reasonsMap.entries())
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const topCustomers = [...customerWithRisk].sort((a, b) => b.revenueAtRisk - a.revenueAtRisk).slice(0, 5);

  const switchPage = (nextPage: Page) => {
    setPage(nextPage);
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1400px]">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-4 md:block">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">RetainIQ</p>
          <p className="mt-2 text-sm text-slate-600">Simple churn explanation for non-technical teams</p>

          <nav className="mt-6 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = item.id === page;
              return (
                <button
                  key={item.id}
                  onClick={() => switchPage(item.id)}
                  className={
                    "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition " +
                    (active ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-100")
                  }
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1 p-4 sm:p-6">
          <header className="mb-4 flex items-center justify-between rounded-xl border border-slate-200 bg-white p-3 md:hidden">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">RetainIQ</p>
              <p className="text-sm text-slate-600">Predict churn. Understand why. Take action.</p>
            </div>
            <button
              type="button"
              aria-label="Open menu"
              className="rounded-md border border-slate-300 p-2 text-slate-700"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
            >
              <Menu className="h-4 w-4" />
            </button>
          </header>

          {mobileMenuOpen ? (
            <nav className="mb-5 grid gap-2 rounded-xl border border-slate-200 bg-white p-3 md:hidden">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => switchPage(item.id)}
                  className={
                    "rounded-md px-3 py-2 text-left text-sm " +
                    (item.id === page ? "bg-blue-50 text-blue-700" : "text-slate-600")
                  }
                >
                  {item.label}
                </button>
              ))}
            </nav>
          ) : null}

          <div className="space-y-6">
            {page === "dashboard" ? (
              <DashboardPage
                totalCustomers={totalCustomers}
                highRiskCustomers={highRiskCustomers}
                churnRate={churnRate}
                revenueAtRisk={formatCurrency(revenueAtRiskRaw)}
              />
            ) : null}

            {page === "check-customer" ? <CheckCustomerPage onResult={setLatestResult} /> : null}

            {page === "insights" ? <InsightsPage reasons={topReasons} /> : null}

            {page === "revenue-impact" ? (
              <RevenueImpactPage
                totalRevenueAtRisk={formatCurrency(revenueAtRiskRaw)}
                topCustomers={topCustomers}
                formatCurrency={formatCurrency}
              />
            ) : null}

            {page === "help" ? <HelpPage /> : null}
          </div>

          {latestResult ? (
            <footer className="mt-6 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
              Latest analysis: {latestResult.churnProbability}% churn probability with {latestResult.riskLevel} risk.
            </footer>
          ) : null}
        </main>
      </div>
    </div>
  );
}

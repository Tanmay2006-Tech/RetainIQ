type KpiCardSimpleProps = {
  title: string;
  value: string;
  description: string;
};

export function KpiCardSimple({ title, value, description }: KpiCardSimpleProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5">
      <p className="text-sm font-medium text-slate-600">{title}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{description}</p>
    </article>
  );
}

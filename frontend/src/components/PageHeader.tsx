type PageHeaderProps = {
  title: string;
  description: string;
};

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="space-y-2">
      <h1 className="text-2xl font-semibold text-slate-900 sm:text-3xl">{title}</h1>
      <p className="max-w-3xl text-sm text-slate-600 sm:text-base">{description}</p>
    </header>
  );
}

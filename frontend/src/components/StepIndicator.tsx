type StepIndicatorProps = {
  currentStep: 1 | 2 | 3;
};

const steps = ["Step 1: Enter data", "Step 2: See result", "Step 3: Take action"];

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <ol className="grid gap-2 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-3">
      {steps.map((label, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber <= currentStep;
        return (
          <li
            key={label}
            className={
              "rounded-lg px-3 py-2 text-sm " +
              (isActive ? "bg-blue-50 text-blue-700" : "bg-slate-50 text-slate-500")
            }
          >
            {label}
          </li>
        );
      })}
    </ol>
  );
}

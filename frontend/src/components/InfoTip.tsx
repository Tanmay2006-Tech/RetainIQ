import { Info } from "lucide-react";

type InfoTipProps = {
  text: string;
  title?: string;
};

export function InfoTip({ text, title = "More info" }: InfoTipProps) {
  return (
    <span className="inline-flex items-center" title={text} aria-label={text}>
      <Info className="h-4 w-4 text-blue-600" />
      <span className="sr-only">{title}</span>
    </span>
  );
}

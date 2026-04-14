import { motion } from "framer-motion";

type Props = {
  title: string;
  value: string;
  subtitle: string;
};

export default function KpiCard({ title, value, subtitle }: Props) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 220, damping: 16 }}
      className="rounded-2xl border border-cardBorder bg-card/70 backdrop-blur-xl p-5"
    >
      <p className="text-sm text-cyan-100/80">{title}</p>
      <p className="mt-2 text-4xl font-display text-white">{value}</p>
      <p className="mt-1 text-xs text-cyan-100/60">{subtitle}</p>
    </motion.div>
  );
}

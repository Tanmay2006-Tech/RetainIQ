import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  className?: string;
  delay?: number;
}>;

export default function GlassCard({ children, className, delay = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay, ease: "easeOut" }}
      className={`rounded-2xl border border-cardBorder bg-card/80 backdrop-blur-xl p-5 shadow-glow ${className ?? ""}`}
    >
      {children}
    </motion.div>
  );
}

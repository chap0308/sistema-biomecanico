import type { SquatRuleDecision } from "@/types/squat-case-report";

const stateStyles = {
  presente: "bg-amber-500",
  ausente: "bg-emerald-600",
  no_concluyente: "bg-slate-400",
} as const;

export function MetricEvidence({
  decision,
}: {
  decision: SquatRuleDecision;
}) {
  const values = decision.repetition_values.filter(
    (value): value is number => value !== null,
  );
  const scale = Math.max(
    decision.present_min * 1.25,
    ...values.map((value) => Math.abs(value)),
    1,
  );

  return (
    <div className="space-y-3">
      {decision.repetition_values.map((value, index) => {
        const state = decision.repetition_states[index] ?? "no_concluyente";
        return (
          <div key={`${decision.finding}-${index}`}>
            <div className="mb-1 flex items-center justify-between gap-3 text-xs">
              <span className="text-muted-foreground">
                Repetición {index + 1}
              </span>
              <span className="font-mono font-medium tabular-nums">
                {formatMetric(value, decision.unit)}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full rounded-full ${stateStyles[state]}`}
                style={{
                  width: `${value === null ? 0 : Math.min(100, (Math.abs(value) / scale) * 100)}%`,
                }}
              />
            </div>
          </div>
        );
      })}
      <div className="flex justify-between border-t pt-2 text-[11px] text-muted-foreground">
        <span>Ausente ≤ {formatNumber(decision.absent_max)}</span>
        <span>Presente ≥ {formatNumber(decision.present_min)}</span>
      </div>
    </div>
  );
}

export function formatMetric(value: number | null, unit: string) {
  if (value === null) return "Sin dato";
  const suffix = unit === "deg" ? "°" : " %";
  return `${formatNumber(value)}${suffix}`;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-PE", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(value);
}

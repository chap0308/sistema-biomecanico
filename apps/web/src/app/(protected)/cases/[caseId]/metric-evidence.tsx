import type {
  SquatRepetitionMetrics,
  SquatRuleDecision,
} from "@/types/squat-case-report";

const stateStyles = {
  presente: "bg-amber-500",
  ausente: "bg-emerald-600",
  no_concluyente: "bg-slate-400",
} as const;

export function MetricEvidence({
  decision,
  repetitionMetrics,
}: {
  decision: SquatRuleDecision;
  repetitionMetrics?: SquatRepetitionMetrics;
}) {
  const value = decision.aggregate_value ?? null;
  const state = decision.status;
  const scale = Math.max(
    decision.present_min * 1.25,
    value === null ? 0 : Math.abs(value),
    1,
  );

  return (
    <div className="space-y-3">
      <div>
        <div className="mb-1 flex items-center justify-between gap-3 text-xs">
          <span className="text-muted-foreground">
            Valor evaluado en máxima profundidad
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
      <div className="flex justify-between border-t pt-2 text-[11px] text-muted-foreground">
        <span>Ausente ≤ {formatNumber(decision.absent_max)}</span>
        <span>Presente ≥ {formatNumber(decision.present_min)}</span>
      </div>
      {isKneeDecision(decision) && repetitionMetrics ? (
        <div className="grid grid-cols-2 gap-2 rounded-lg border bg-muted/30 p-3">
          <SideValue
            label="Rodilla izquierda"
            value={repetitionMetrics.left_knee_medial_deviation_at_peak_pct}
          />
          <SideValue
            label="Rodilla derecha"
            value={repetitionMetrics.right_knee_medial_deviation_at_peak_pct}
          />
          {decision.finding === "asimetria_bilateral_observable" ? (
            <div className="col-span-2 border-t pt-2">
              <SideValue
                label="Diferencia absoluta"
                value={
                  repetitionMetrics.bilateral_alignment_difference_at_peak_pct
                }
              />
            </div>
          ) : null}
        </div>
      ) : null}
      <p className="text-[11px] text-muted-foreground">
        {unitDescription(decision.unit)}
      </p>
      <p className="text-[11px] leading-5 text-muted-foreground">
        El umbral se aplica al fotograma de máxima profundidad de esta
        repetición. La serie temporal completa se conserva como evidencia y no
        se promedia para clasificar el patrón.
      </p>
      <details className="rounded-lg border px-3 py-2 text-xs">
        <summary className="cursor-pointer font-medium">
          Ver fórmula y convención
        </summary>
        <p className="mt-2 font-mono leading-5 text-muted-foreground">
          {formulaFor(decision.finding)}
        </p>
        <p className="mt-2 leading-5 text-muted-foreground">
          {conventionFor(decision.finding)}
        </p>
      </details>
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

function SideValue({
  label,
  value,
}: {
  label: string;
  value?: number | null;
}) {
  return (
    <div>
      <p className="text-[11px] text-muted-foreground">{label}</p>
      <p className="mt-0.5 font-mono font-medium tabular-nums">
        {formatMetric(value ?? null, "pct_ancho_hombros")}
      </p>
    </div>
  );
}

function isKneeDecision(decision: SquatRuleDecision) {
  return (
    decision.finding === "valgo_dinamico_visible" ||
    decision.finding === "asimetria_bilateral_observable"
  );
}

function unitDescription(unit: string) {
  return unit === "deg"
    ? "Unidad: grados respecto de la vertical de referencia."
    : "Unidad: porcentaje del ancho inicial de hombros; no representa confianza.";
}

function formulaFor(finding: string) {
  const formulas: Record<string, string> = {
    inclinacion_lateral_tronco: "θ = atan2(Sx − Px, Py − Sy)",
    desplazamiento_lateral_pelvis:
      "100 × (desplazamiento actual − referencia inicial) / ancho inicial de hombros",
    valgo_dinamico_visible:
      "Rodilla izquierda: −100 × (x_rodilla − x_proyección) / ancho inicial de hombros. Rodilla derecha: +100 × (x_rodilla − x_proyección) / ancho inicial de hombros.",
    asimetria_bilateral_observable:
      "|alineación izquierda − alineación derecha|",
  };
  return formulas[finding] ?? "Fórmula no disponible.";
}

function conventionFor(finding: string) {
  if (finding === "inclinacion_lateral_tronco") {
    return "El signo positivo representa inclinación hacia la izquierda anatómica y el negativo hacia la derecha.";
  }
  if (finding === "desplazamiento_lateral_pelvis") {
    return "Vista anterior: un valor positivo indica desplazamiento hacia la izquierda anatómica y un valor negativo hacia la derecha anatómica. El desplazamiento se corrige con el reposo inicial y se mide respecto del centro de los tobillos.";
  }
  if (finding === "valgo_dinamico_visible") {
    return "En ambos lados, un valor positivo representa desplazamiento medial y uno negativo desplazamiento lateral. Solo una desviación medial positiva puede activar la regla.";
  }
  return "La diferencia bilateral compara las alineaciones de ambas rodillas; no implica valgo bilateral.";
}

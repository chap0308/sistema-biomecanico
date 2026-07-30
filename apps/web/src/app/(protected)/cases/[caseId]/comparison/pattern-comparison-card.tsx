"use client";

import { useState } from "react";
import { CheckCircle2Icon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type {
  CaseComparison,
  PatternComparison,
} from "@/types/squat-comparison";

import { ConsensusForm } from "./consensus-form";

const patternNames = {
  trunk_lateral_inclination: "Inclinación lateral del tronco",
  pelvis_lateral_shift: "Desplazamiento lateral de pelvis",
  visible_dynamic_valgus: "Valgo dinámico visible",
  bilateral_asymmetry: "Asimetría bilateral observable",
};

export function PatternComparisonCard({
  caseId,
  initialPattern,
  referenceStatus,
}: {
  caseId: string;
  initialPattern: PatternComparison;
  referenceStatus: CaseComparison["reference_status"];
}) {
  const [pattern, setPattern] = useState(initialPattern);
  const visibleReference =
    referenceStatus === "open" ? null : pattern.reference;

  function updateFromComparison(comparison: CaseComparison) {
    const updated = comparison.patterns.find(
      (item) =>
        item.repetition_index === pattern.repetition_index &&
        item.pattern_key === pattern.pattern_key,
    );
    if (updated) setPattern(updated);
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">
              Repetición {pattern.repetition_index} ·{" "}
              {patternNames[pattern.pattern_key]}
            </CardTitle>
            <CardDescription>
              {pattern.expert_judgments.length} evaluaciones disponibles
            </CardDescription>
          </div>
          <ReferenceBadge
            pattern={pattern}
            referenceStatus={referenceStatus}
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 text-sm">
          {pattern.expert_judgments.map((judgment, index) => (
            <div
              key={judgment.evaluator_id}
              className={`rounded-lg border p-3 ${expertResultClass(index)}`}
            >
              <p className="text-xs text-muted-foreground">
                Evaluador {index + 1}
              </p>
              <p className="mt-1 font-medium">
                {classificationLabel(
                  judgment.classification,
                  judgment.observed_side,
                )}
              </p>
              {judgment.confidence ? (
                <Badge variant="outline" className="mt-2">
                  Confianza {label(judgment.confidence).toLowerCase()}
                </Badge>
              ) : null}
              {judgment.observation ? (
                <details className="mt-3 text-xs">
                  <summary className="cursor-pointer font-medium">
                    Ver observación
                  </summary>
                  <p className="mt-2 leading-5 text-muted-foreground">
                    {judgment.observation}
                  </p>
                </details>
              ) : null}
            </div>
          ))}
          <div className="rounded-lg border border-cyan-300/70 bg-cyan-50/70 p-3 dark:border-cyan-800 dark:bg-cyan-950/30">
            <p className="text-xs font-medium text-cyan-800 dark:text-cyan-300">
              Sistema
            </p>
            <p className="mt-1 font-medium">{label(pattern.system_label)}</p>
          </div>
          <div className="rounded-lg border border-emerald-300/70 bg-emerald-50/70 p-3 dark:border-emerald-800 dark:bg-emerald-950/30">
            <p className="text-xs font-medium text-emerald-800 dark:text-emerald-300">
              Referencia final
            </p>
            <p className="mt-1 font-medium">
              {visibleReference ? label(visibleReference.label) : "Pendiente"}
            </p>
          </div>
        </div>
        {referenceStatus === "in_progress" &&
        pattern.expert_judgments.length > 0 ? (
          <ConsensusForm
            caseId={caseId}
            repetitionIndex={pattern.repetition_index}
            patternKey={pattern.pattern_key}
            currentReference={visibleReference}
            onSaved={updateFromComparison}
          />
        ) : null}
      </CardContent>
    </Card>
  );
}

function ReferenceBadge({
  pattern,
  referenceStatus,
}: {
  pattern: PatternComparison;
  referenceStatus: CaseComparison["reference_status"];
}) {
  if (
    referenceStatus === "open" ||
    pattern.reference_status !== "consolidada"
  ) {
    return <Badge variant="outline">Pendiente</Badge>;
  }
  if (pattern.exact_match === true) {
    return (
      <Badge>
        <CheckCircle2Icon aria-hidden="true" />
        Coincide
      </Badge>
    );
  }
  if (pattern.exact_match === false) {
    return <Badge variant="destructive">Discrepancia</Badge>;
  }
  return <Badge variant="outline">No calculable</Badge>;
}

function expertResultClass(index: number) {
  const classes = [
    "border-blue-300/70 bg-blue-50/70 dark:border-blue-800 dark:bg-blue-950/30",
    "border-amber-300/70 bg-amber-50/70 dark:border-amber-800 dark:bg-amber-950/30",
    "border-rose-300/70 bg-rose-50/70 dark:border-rose-800 dark:bg-rose-950/30",
  ];
  return classes[index % classes.length];
}

function classificationLabel(classification: string, side: string | null) {
  return label(
    classification === "presente" && side
      ? `presente_${side}`
      : classification,
  );
}

function label(value: string) {
  return value.replaceAll("_", " ").replace(/^./, (letter) =>
    letter.toUpperCase(),
  );
}

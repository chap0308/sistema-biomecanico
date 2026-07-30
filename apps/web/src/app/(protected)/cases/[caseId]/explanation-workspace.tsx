"use client";

import { useState } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import type {
  SquatCaseExplanation,
  SquatExplanationFrame,
} from "@/types/squat-explanation";

type ExplanationWorkspaceProps = {
  activeRepetition: number;
  currentTime: number;
  explanation: SquatCaseExplanation;
  onRepetitionChange?: (repetitionIndex: number) => void;
};

const chartConfig = {
  keypoints: { label: "Puntos detectados", color: "var(--chart-2)" },
  visibility: { label: "Visibilidad mínima", color: "var(--chart-5)" },
  leftVisibility: { label: "Lado izquierdo", color: "var(--chart-2)" },
  rightVisibility: { label: "Lado derecho", color: "var(--chart-4)" },
  centralVisibility: { label: "Referencia central", color: "var(--chart-2)" },
  rawHip: { label: "Centro de caderas", color: "var(--muted-foreground)" },
  smoothHip: { label: "Señal suavizada", color: "var(--chart-2)" },
  trunk: { label: "Inclinación del tronco", color: "var(--chart-1)" },
  pelvis: { label: "Desplazamiento de pelvis", color: "var(--chart-3)" },
  leftKnee: { label: "Rodilla izquierda", color: "var(--chart-1)" },
  rightKnee: { label: "Rodilla derecha", color: "var(--chart-4)" },
  bilateral: { label: "Diferencia bilateral", color: "var(--chart-5)" },
} satisfies ChartConfig;

const variables = {
  trunk: {
    label: "Tronco",
    description: "Ángulo del eje hombros-pelvis respecto de la vertical.",
    unit: "°",
  },
  pelvis: {
    label: "Pelvis",
    description:
      "Desplazamiento lateral corregido por el reposo inicial y normalizado.",
    unit: "%",
  },
  knees: {
    label: "Rodillas",
    description:
      "Desviación medial de cada rodilla respecto del eje cadera-tobillo.",
    unit: "%",
  },
  bilateral: {
    label: "Diferencia bilateral",
    description: "Diferencia absoluta entre las alineaciones de ambas rodillas.",
    unit: "%",
  },
} as const;

type VariableKey = keyof typeof variables;

const landmarkGroups = {
  shoulder: "Hombro",
  hip: "Cadera",
  knee: "Rodilla",
  ankle: "Tobillo",
  heel: "Talón",
  foot_index: "Punta del pie",
  nose: "Nariz",
} as const;

type LandmarkGroup = keyof typeof landmarkGroups;

export function ExplanationWorkspace({
  activeRepetition,
  currentTime,
  explanation,
  onRepetitionChange,
}: ExplanationWorkspaceProps) {
  const [variable, setVariable] = useState<VariableKey>("trunk");
  const repetition = explanation.repetitions.find(
    (item) =>
      item.segmentation.repetition_index === activeRepetition,
  );
  if (!repetition) return null;

  const frames = explanation.frames.filter(
    (frame) =>
      frame.timestamp_seconds >= repetition.segmentation.start_seconds &&
      frame.timestamp_seconds <= repetition.segmentation.end_seconds,
  );
  const eventRows = eventFrames(frames, repetition.segmentation);
  const peakGeometry = explanation.key_frames.find(
    (frame) =>
      frame.repetition_index === activeRepetition &&
      frame.event === "maxima_profundidad",
  );
  const repetitionIndexes = explanation.repetitions.map(
    (item) => item.segmentation.repetition_index,
  );

  return (
    <section className="mt-7 border-t pt-6" aria-labelledby="explanation-title">
      <div className="max-w-3xl">
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
          Trazabilidad
        </p>
        <h2 id="explanation-title" className="mt-2 text-2xl font-semibold">
          Cómo se obtuvo este resultado
        </h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Recorre la detección, la segmentación, los cálculos y las reglas de la
          repetición {activeRepetition}. El cursor vertical sigue el video.
        </p>
      </div>

      {repetitionIndexes.length > 1 ? (
        <RepetitionNavigator
          activeRepetition={activeRepetition}
          repetitionIndexes={repetitionIndexes}
          onChange={onRepetitionChange}
        />
      ) : null}

      <Tabs defaultValue="quality" className="mt-5">
        <TabsList className="h-auto max-w-full flex-wrap justify-start">
          <TabsTrigger value="quality">1. Pose 2D</TabsTrigger>
          <TabsTrigger value="segmentation">2. Segmentación</TabsTrigger>
          <TabsTrigger value="variables">3. Variables</TabsTrigger>
          <TabsTrigger value="rules">4. Reglas</TabsTrigger>
        </TabsList>

        <TabsContent value="quality" className="mt-4">
          <QualityPanel
            currentTime={currentTime}
            explanation={explanation}
            frames={frames}
            repetition={repetition.segmentation}
          />
        </TabsContent>
        <TabsContent value="segmentation" className="mt-4">
          <SegmentationPanel
            currentTime={currentTime}
            frames={frames}
            repetition={repetition.segmentation}
          />
        </TabsContent>
        <TabsContent value="variables" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Geometría calculada</CardTitle>
              <CardDescription>
                Selecciona una variable para evitar superponer señales y
                referencias diferentes.
              </CardDescription>
              <Tabs
                value={variable}
                onValueChange={(value) => setVariable(value as VariableKey)}
                className="pt-2"
              >
                <TabsList variant="line" className="max-w-full flex-wrap">
                  {Object.entries(variables).map(([key, item]) => (
                    <TabsTrigger key={key} value={key}>
                      {item.label}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-xs text-muted-foreground">
                {variables[variable].description}
              </p>
              <GeometryDiagram
                keyFrame={peakGeometry}
                variable={variable}
              />
              <VariableChart
                currentTime={currentTime}
                frames={frames}
                repetition={repetition.segmentation}
                variable={variable}
              />
              <EventTable frames={eventRows} variable={variable} />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="rules" className="mt-4">
          <RulesTable decisions={repetition.decisions} />
        </TabsContent>
      </Tabs>
    </section>
  );
}

function RepetitionNavigator({
  activeRepetition,
  repetitionIndexes,
  onChange,
}: {
  activeRepetition: number;
  repetitionIndexes: number[];
  onChange?: (repetitionIndex: number) => void;
}) {
  const position = repetitionIndexes.indexOf(activeRepetition);
  const previous = repetitionIndexes[position - 1];
  const next = repetitionIndexes[position + 1];

  return (
    <div className="sticky top-3 z-20 mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-background/95 px-3 py-2 shadow-sm backdrop-blur">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
          Evidencia sincronizada
        </p>
        <p className="text-sm font-medium" aria-live="polite">
          Repetición {activeRepetition} de {repetitionIndexes.length}
        </p>
      </div>
      <div className="flex items-center gap-1.5">
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={previous === undefined}
          onClick={() => previous !== undefined && onChange?.(previous)}
        >
          <ChevronLeftIcon aria-hidden="true" />
          Anterior
        </Button>
        <div className="hidden items-center gap-1 sm:flex">
          {repetitionIndexes.map((repetitionIndex) => (
            <Button
              key={repetitionIndex}
              type="button"
              size="icon-sm"
              variant={
                repetitionIndex === activeRepetition ? "default" : "ghost"
              }
              aria-label={`Ver repetición ${repetitionIndex}`}
              aria-pressed={repetitionIndex === activeRepetition}
              onClick={() => onChange?.(repetitionIndex)}
            >
              {repetitionIndex}
            </Button>
          ))}
        </div>
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={next === undefined}
          onClick={() => next !== undefined && onChange?.(next)}
        >
          Siguiente
          <ChevronRightIcon aria-hidden="true" />
        </Button>
      </div>
    </div>
  );
}

function GeometryDiagram({
  keyFrame,
  variable,
}: {
  keyFrame: SquatCaseExplanation["key_frames"][number] | undefined;
  variable: VariableKey;
}) {
  if (!keyFrame) {
    return (
      <p className="mb-4 rounded-lg border p-4 text-sm text-muted-foreground">
        No hay geometría disponible para el fotograma de máxima profundidad.
      </p>
    );
  }
  const { geometry, landmarks } = keyFrame;
  const skeleton = [
    ["left_shoulder", "right_shoulder"],
    ["left_shoulder", "left_hip"],
    ["right_shoulder", "right_hip"],
    ["left_hip", "right_hip"],
    ["left_hip", "left_knee"],
    ["right_hip", "right_knee"],
    ["left_knee", "left_ankle"],
    ["right_knee", "right_ankle"],
  ] as const;

  return (
    <div className="mb-5 grid gap-4 rounded-xl border bg-slate-950 p-4 lg:grid-cols-[minmax(0,0.8fr)_minmax(16rem,1.2fr)]">
      <div className="mx-auto w-full max-w-sm">
        <svg
          viewBox="0 0 1 1"
          className="aspect-[3/4] w-full rounded-lg bg-[radial-gradient(circle_at_center,_#172033,_#070b12)]"
          role="img"
          aria-label={`Esquema geométrico de ${variables[variable].label.toLowerCase()}`}
        >
          {skeleton.map(([from, to]) => (
            <SvgLine
              key={`${from}-${to}`}
              from={landmarks[from]}
              to={landmarks[to]}
              className="stroke-slate-500"
            />
          ))}
          {Object.entries(landmarks).map(([name, point]) => (
            <circle
              key={name}
              cx={point.x}
              cy={point.y}
              r="0.009"
              className="fill-slate-300"
            />
          ))}
          {variable === "trunk" &&
          geometry.shoulder_midpoint &&
          geometry.pelvis_midpoint ? (
            <>
              <SvgLine
                from={geometry.pelvis_midpoint}
                to={geometry.shoulder_midpoint}
                className="stroke-cyan-300"
                strong
              />
              <SvgLine
                from={geometry.pelvis_midpoint}
                to={{
                  ...geometry.shoulder_midpoint,
                  x: geometry.pelvis_midpoint.x,
                }}
                className="stroke-amber-300"
                dashed
              />
            </>
          ) : null}
          {variable === "pelvis" &&
          geometry.pelvis_midpoint &&
          geometry.ankle_midpoint ? (
            <>
              <SvgLine
                from={geometry.ankle_midpoint}
                to={geometry.pelvis_midpoint}
                className="stroke-cyan-300"
                strong
              />
              <SvgLine
                from={geometry.ankle_midpoint}
                to={{
                  ...geometry.pelvis_midpoint,
                  x: geometry.ankle_midpoint.x,
                }}
                className="stroke-amber-300"
                dashed
              />
            </>
          ) : null}
          {variable === "knees" || variable === "bilateral" ? (
            <>
              <KneeGeometry
                actual={landmarks.left_knee}
                ankle={landmarks.left_ankle}
                hip={landmarks.left_hip}
                projection={geometry.left_knee_projection}
              />
              <KneeGeometry
                actual={landmarks.right_knee}
                ankle={landmarks.right_ankle}
                hip={landmarks.right_hip}
                projection={geometry.right_knee_projection}
              />
            </>
          ) : null}
        </svg>
      </div>
      <div className="self-center text-slate-100">
        <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-cyan-300">
          Fotograma {keyFrame.frame_index} ·{" "}
          {keyFrame.timestamp_seconds.toFixed(2)} s
        </p>
        <h4 className="mt-2 text-lg font-semibold">
          Referencias de {variables[variable].label.toLowerCase()}
        </h4>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          {geometryExplanation(variable)}
        </p>
        <div className="mt-4 flex flex-wrap gap-3 text-xs">
          <span className="flex items-center gap-2">
            <span className="h-0.5 w-6 bg-cyan-300" />
            Geometría observada
          </span>
          <span className="flex items-center gap-2">
            <span className="w-6 border-t border-dashed border-amber-300" />
            Referencia
          </span>
          {variable === "knees" || variable === "bilateral" ? (
            <span className="flex items-center gap-2">
              <span className="h-0.5 w-6 bg-rose-400" />
              Desviación
            </span>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function KneeGeometry({
  actual,
  ankle,
  hip,
  projection,
}: {
  actual?: { x: number; y: number };
  ankle?: { x: number; y: number };
  hip?: { x: number; y: number };
  projection?: { x: number; y: number } | null;
}) {
  if (!actual || !ankle || !hip || !projection) return null;
  return (
    <>
      <SvgLine
        from={hip}
        to={ankle}
        className="stroke-amber-300"
        dashed
      />
      <SvgLine
        from={projection}
        to={actual}
        className="stroke-rose-400"
        strong
      />
      <circle
        cx={projection.x}
        cy={projection.y}
        r="0.011"
        className="fill-amber-300"
      />
    </>
  );
}

function SvgLine({
  className,
  dashed = false,
  from,
  strong = false,
  to,
}: {
  className: string;
  dashed?: boolean;
  from?: { x: number; y: number } | null;
  strong?: boolean;
  to?: { x: number; y: number } | null;
}) {
  if (!from || !to) return null;
  return (
    <line
      x1={from.x}
      y1={from.y}
      x2={to.x}
      y2={to.y}
      className={className}
      strokeWidth={strong ? 0.009 : 0.005}
      strokeDasharray={dashed ? "0.02 0.014" : undefined}
      strokeLinecap="round"
    />
  );
}

function geometryExplanation(variable: VariableKey) {
  if (variable === "trunk") {
    return "La línea cian une el centro de pelvis con el centro de hombros. La línea discontinua representa la vertical usada para calcular la inclinación.";
  }
  if (variable === "pelvis") {
    return "Se compara el centro de pelvis con el centro de apoyo definido por ambos tobillos y con la referencia establecida durante el reposo.";
  }
  if (variable === "knees") {
    return "La línea discontinua une cadera y tobillo. El punto amarillo indica la posición esperada de la rodilla a su misma altura y la línea roja muestra la desviación observada.";
  }
  return "Se representan simultáneamente las desviaciones izquierda y derecha; la variable final corresponde a la diferencia absoluta entre ambas.";
}

function QualityPanel({
  currentTime,
  explanation,
  frames,
  repetition,
}: {
  currentTime: number;
  explanation: SquatCaseExplanation;
  frames: SquatExplanationFrame[];
  repetition: SquatCaseExplanation["repetitions"][number]["segmentation"];
}) {
  const [landmarkGroup, setLandmarkGroup] =
    useState<LandmarkGroup>("hip");
  const detectedKeypoints = frames.flatMap((frame) =>
    frame.detected_keypoints == null ? [] : [frame.detected_keypoints],
  );
  const meanDetectedKeypoints = detectedKeypoints.length
    ? detectedKeypoints.reduce((total, value) => total + value, 0) /
      detectedKeypoints.length
    : null;
  const selectedSummaries = (
    explanation.landmark_visibility_summaries ?? []
  ).filter(
    (summary) =>
      summary.repetition_index === repetition.repetition_index &&
      summary.anatomical_group === landmarkGroup,
  );
  const visibilityFrames = frames.map((frame) => ({
    timestamp_seconds: frame.timestamp_seconds,
    leftVisibility:
      frame.landmark_visibility?.[`left_${landmarkGroup}`] ?? null,
    rightVisibility:
      frame.landmark_visibility?.[`right_${landmarkGroup}`] ?? null,
    centralVisibility:
      frame.landmark_visibility?.[landmarkGroup] ?? null,
  }));
  const isCentral = landmarkGroup === "nose";

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Disponibilidad de pose por fotograma</CardTitle>
          <CardDescription>
            Los puntos críticos y la visibilidad determinan si un fotograma puede
            participar en los cálculos.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-72 w-full">
            <LineChart data={frames}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="timestamp_seconds"
                tickFormatter={formatSeconds}
                type="number"
                domain={["dataMin", "dataMax"]}
              />
              <YAxis yAxisId="points" domain={[0, 13]} width={30} />
              <YAxis
                yAxisId="visibility"
                orientation="right"
                domain={[0, 1]}
                width={34}
              />
              <ChartTooltip
                content={<ChartTooltipContent />}
                labelFormatter={(_, payload) =>
                  formatTooltipSeconds(payload[0]?.payload?.timestamp_seconds)
                }
              />
              <RepetitionMarkers repetition={repetition} yAxisId="points" />
              <ReferenceLine
                yAxisId="visibility"
                y={explanation.quality?.visibility_threshold ?? 0.5}
                stroke="var(--destructive)"
                strokeDasharray="4 4"
              />
              <TimeCursor currentTime={currentTime} yAxisId="points" />
              <Line
                yAxisId="points"
                dataKey="detected_keypoints"
                name="keypoints"
                stroke="var(--color-keypoints)"
                dot={false}
                isAnimationActive={false}
              />
              <Line
                yAxisId="visibility"
                dataKey="minimum_critical_visibility"
                name="visibility"
                stroke="var(--color-visibility)"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ChartContainer>
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            <SmallMetric
              label="Fotogramas válidos"
              value={`${repetition.valid_frames_percentage.toFixed(1)} %`}
            />
            <SmallMetric
              label="Promedio de puntos"
              value={meanDetectedKeypoints?.toFixed(1) ?? "—"}
            />
            <SmallMetric
              label="Umbral de visibilidad"
              value={
                explanation.quality?.visibility_threshold.toFixed(2) ?? "—"
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <CardTitle>Visibilidad por punto anatómico</CardTitle>
            <CardDescription className="mt-1">
              Selecciona un segmento para comparar sus lados sin superponer las
              13 curvas.
            </CardDescription>
          </div>
          <label className="grid gap-1 text-sm font-medium">
            Segmento
            <select
              aria-label="Segmento anatómico"
              className="h-9 min-w-44 rounded-md border bg-background px-3"
              value={landmarkGroup}
              onChange={(event) =>
                setLandmarkGroup(event.target.value as LandmarkGroup)
              }
            >
              {Object.entries(landmarkGroups).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-64 w-full">
            <LineChart data={visibilityFrames}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="timestamp_seconds"
                tickFormatter={formatSeconds}
                type="number"
                domain={["dataMin", "dataMax"]}
              />
              <YAxis domain={[0, 1]} width={34} />
              <ChartTooltip
                content={<ChartTooltipContent />}
                labelFormatter={(_, payload) =>
                  formatTooltipSeconds(payload[0]?.payload?.timestamp_seconds)
                }
              />
              <ReferenceLine
                y={explanation.quality?.visibility_threshold ?? 0.5}
                stroke="var(--destructive)"
                strokeDasharray="4 4"
              />
              <TimeCursor currentTime={currentTime} />
              {isCentral ? (
                <Line
                  dataKey="centralVisibility"
                  name="centralVisibility"
                  stroke="var(--color-centralVisibility)"
                  dot={false}
                  isAnimationActive={false}
                  connectNulls={false}
                />
              ) : (
                <>
                  <Line
                    dataKey="leftVisibility"
                    name="leftVisibility"
                    stroke="var(--color-leftVisibility)"
                    dot={false}
                    isAnimationActive={false}
                    connectNulls={false}
                  />
                  <Line
                    dataKey="rightVisibility"
                    name="rightVisibility"
                    stroke="var(--color-rightVisibility)"
                    dot={false}
                    isAnimationActive={false}
                    connectNulls={false}
                  />
                </>
              )}
            </LineChart>
          </ChartContainer>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {selectedSummaries.map((summary) => (
              <div
                key={summary.landmark}
                className="rounded-lg border bg-muted/20 p-3"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium">
                    {sideLabel(summary.side)}
                  </p>
                  <Badge variant="outline">
                    {availabilityLabel(summary.availability)}
                  </Badge>
                </div>
                <p className="mt-2 font-mono text-sm">
                  Promedio {summary.mean_visibility.toFixed(2)} · cobertura{" "}
                  {summary.usable_frames_percentage.toFixed(1)} %
                </p>
              </div>
            ))}
            {selectedSummaries.length === 0 ? (
              <p className="text-sm text-muted-foreground sm:col-span-2">
                Este caso todavía no contiene el resumen individual por punto
                anatómico. Vuelve a cargarlo cuando la API haya actualizado el
                contrato de explicación.
              </p>
            ) : null}
          </div>
          <p className="mt-3 text-xs leading-5 text-muted-foreground">
            Cobertura: porcentaje de fotogramas de la repetición con visibilidad
            igual o superior al umbral. Esta clasificación describe la
            disponibilidad del punto; no reemplaza la validez global del video.
          </p>
          <details className="mt-4 rounded-lg border bg-muted/15 p-4 text-sm">
            <summary className="cursor-pointer font-medium">
              Cómo se calculan el promedio, la cobertura y el estado
            </summary>
            <div className="mt-4 space-y-4 text-muted-foreground">
              <p>
                El promedio es la media de la visibilidad estimada para el punto
                durante la repetición. La cobertura indica en qué porcentaje de
                sus fotogramas esa visibilidad alcanzó el umbral de{" "}
                {explanation.quality?.visibility_threshold.toFixed(2) ?? "0.50"}.
              </p>
              <div className="grid gap-2 rounded-md bg-background p-3 font-mono text-xs">
                <span>
                  Promedio = suma de visibilidades / fotogramas de la repetición
                </span>
                <span>
                  Cobertura (%) = 100 × fotogramas con visibilidad ≥ umbral /
                  fotogramas de la repetición
                </span>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Estado</TableHead>
                    <TableHead>Regla operativa</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-medium text-foreground">
                      Visible y estable
                    </TableCell>
                    <TableCell>
                      Cobertura ≥ 90 % y promedio ≥ 0.80
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium text-foreground">
                      Intermitente
                    </TableCell>
                    <TableCell>Cualquier condición intermedia</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium text-foreground">
                      No disponible
                    </TableCell>
                    <TableCell>
                      Cobertura &lt; 50 % o promedio &lt; 0.50
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
              <p>
                El sistema resume 13 puntos seleccionados, pero la validez
                estructural exige ocho puntos centrales: ambos hombros, caderas,
                rodillas y tobillos. Estos ocho forman las líneas necesarias
                para las variables biomecánicas; adicionalmente se requiere al
                menos una referencia distal utilizable por pie, talón o punta.
                La nariz y la segunda referencia distal aportan trazabilidad,
                pero no invalidan por sí solas un fotograma.
              </p>
            </div>
          </details>
        </CardContent>
      </Card>
    </div>
  );
}

function sideLabel(side: "izquierda" | "derecha" | "central") {
  if (side === "central") return "Referencia central";
  return `Lado ${side}`;
}

function availabilityLabel(
  availability: "visible_estable" | "intermitente" | "no_disponible",
) {
  if (availability === "visible_estable") return "Visible y estable";
  if (availability === "intermitente") return "Intermitente";
  return "No disponible";
}

function SegmentationPanel({
  currentTime,
  frames,
  repetition,
}: {
  currentTime: number;
  frames: SquatExplanationFrame[];
  repetition: SquatCaseExplanation["repetitions"][number]["segmentation"];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Trayectoria del centro de caderas</CardTitle>
        <CardDescription>
          La señal suavizada permite localizar descenso, máxima profundidad y
          ascenso. En la imagen, el eje vertical aumenta hacia abajo.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-72 w-full">
          <LineChart data={frames}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="timestamp_seconds"
              tickFormatter={formatSeconds}
              type="number"
              domain={["dataMin", "dataMax"]}
            />
            <YAxis reversed domain={["auto", "auto"]} width={44} />
            <ChartTooltip
              content={<ChartTooltipContent />}
              labelFormatter={(_, payload) =>
                formatTooltipSeconds(payload[0]?.payload?.timestamp_seconds)
              }
            />
            <RepetitionMarkers repetition={repetition} />
            <TimeCursor currentTime={currentTime} />
            <Line
              dataKey="hip_midpoint_y"
              name="rawHip"
              stroke="var(--color-rawHip)"
              strokeOpacity={0.35}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              dataKey="hip_midpoint_y_smoothed"
              name="smoothHip"
              stroke="var(--color-smoothHip)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartContainer>
        <PhaseLegend frames={frames} />
      </CardContent>
    </Card>
  );
}

function VariableChart({
  currentTime,
  frames,
  repetition,
  variable,
}: {
  currentTime: number;
  frames: SquatExplanationFrame[];
  repetition: SquatCaseExplanation["repetitions"][number]["segmentation"];
  variable: VariableKey;
}) {
  return (
    <ChartContainer config={chartConfig} className="h-72 w-full">
      <LineChart data={frames}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="timestamp_seconds"
          tickFormatter={formatSeconds}
          type="number"
          domain={["dataMin", "dataMax"]}
        />
        <YAxis width={44} />
        <ChartTooltip
          content={<ChartTooltipContent />}
          labelFormatter={(_, payload) =>
            formatTooltipSeconds(payload[0]?.payload?.timestamp_seconds)
          }
        />
        <RepetitionMarkers repetition={repetition} />
        <ReferenceLine y={0} stroke="var(--border)" />
        <TimeCursor currentTime={currentTime} />
        {variable === "trunk" ? (
          <MetricLine dataKey="trunk_inclination_deg" name="trunk" />
        ) : null}
        {variable === "pelvis" ? (
          <MetricLine dataKey="pelvis_lateral_shift_pct" name="pelvis" />
        ) : null}
        {variable === "knees" ? (
          <>
            <MetricLine
              dataKey="left_knee_medial_deviation_pct"
              name="leftKnee"
            />
            <MetricLine
              dataKey="right_knee_medial_deviation_pct"
              name="rightKnee"
            />
          </>
        ) : null}
        {variable === "bilateral" ? (
          <MetricLine
            dataKey="bilateral_alignment_difference_pct"
            name="bilateral"
          />
        ) : null}
      </LineChart>
    </ChartContainer>
  );
}

function MetricLine({
  dataKey,
  name,
}: {
  dataKey: keyof SquatExplanationFrame;
  name: keyof typeof chartConfig;
}) {
  return (
    <Line
      dataKey={dataKey}
      name={name}
      stroke={`var(--color-${name})`}
      strokeWidth={2}
      dot={false}
      isAnimationActive={false}
    />
  );
}

function TimeCursor({
  currentTime,
  yAxisId,
}: {
  currentTime: number;
  yAxisId?: string;
}) {
  return (
    <ReferenceLine
      x={currentTime}
      yAxisId={yAxisId}
      stroke="var(--foreground)"
      strokeDasharray="3 3"
    />
  );
}

function RepetitionMarkers({
  repetition,
  yAxisId,
}: {
  repetition: SquatCaseExplanation["repetitions"][number]["segmentation"];
  yAxisId?: string;
}) {
  const markers = [
    {
      label: `Inicio R${repetition.repetition_index}`,
      timestamp: repetition.start_seconds,
      position: "insideTopLeft" as const,
    },
    {
      label: "Profundidad",
      timestamp: repetition.peak_depth_seconds,
      position: "insideTop" as const,
    },
    {
      label: `Final R${repetition.repetition_index}`,
      timestamp: repetition.end_seconds,
      position: "insideTopRight" as const,
    },
  ];

  return markers.map((marker) => (
    <ReferenceLine
      key={marker.label}
      x={marker.timestamp}
      yAxisId={yAxisId}
      stroke="var(--border)"
      strokeDasharray="2 4"
      label={{
        value: marker.label,
        position: marker.position,
        fill: "var(--muted-foreground)",
        fontSize: 10,
      }}
    />
  ));
}

function EventTable({
  frames,
  variable,
}: {
  frames: { event: string; frame: SquatExplanationFrame }[];
  variable: VariableKey;
}) {
  return (
    <div className="mt-5 overflow-x-auto rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Evento</TableHead>
            <TableHead>Tiempo</TableHead>
            {variable === "knees" ? (
              <>
                <TableHead>Izquierda</TableHead>
                <TableHead>Derecha</TableHead>
              </>
            ) : (
              <TableHead>Valor</TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {frames.map(({ event, frame }) => (
            <TableRow key={event}>
              <TableCell>{event}</TableCell>
              <TableCell className="font-mono">
                {frame.timestamp_seconds.toFixed(2)} s
              </TableCell>
              {variable === "knees" ? (
                <>
                  <TableCell className="font-mono">
                    {formatValue(
                      frame.left_knee_medial_deviation_pct,
                      variables[variable].unit,
                    )}
                  </TableCell>
                  <TableCell className="font-mono">
                    {formatValue(
                      frame.right_knee_medial_deviation_pct,
                      variables[variable].unit,
                    )}
                  </TableCell>
                </>
              ) : (
                <TableCell className="font-mono">
                  {formatValue(
                    variableValue(frame, variable),
                    variables[variable].unit,
                  )}
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function RulesTable({
  decisions,
}: {
  decisions: SquatCaseExplanation["repetitions"][number]["decisions"];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Aplicación de criterios interpretables</CardTitle>
        <CardDescription>
          Cada patrón se clasifica de forma independiente usando el valor del
          fotograma de máxima profundidad; la serie temporal no se promedia para
          aplicar el umbral. Una repetición puede contener varias compensaciones
          observables.
        </CardDescription>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patrón</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead>Ausente</TableHead>
              <TableHead>Presente</TableHead>
              <TableHead>Estado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {decisions.map((decision) => (
              <TableRow key={decision.finding}>
                <TableCell>{findingLabel(decision.finding)}</TableCell>
                <TableCell className="font-mono">
                  {formatValue(
                    decision.aggregate_value ?? null,
                    decision.unit === "deg" ? "°" : "%",
                  )}
                </TableCell>
                <TableCell>≤ {decision.absent_max}</TableCell>
                <TableCell>≥ {decision.present_min}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      decision.status === "presente"
                        ? "default"
                        : decision.status === "ausente"
                          ? "secondary"
                          : "outline"
                    }
                  >
                    {decision.status.replace("_", " ")}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function PhaseLegend({ frames }: { frames: SquatExplanationFrame[] }) {
  const phases = [...new Set(frames.map((frame) => frame.phase))];
  return (
    <div className="mt-4 flex flex-wrap gap-2">
      {phases.map((phase) => (
        <Badge key={phase} variant="outline">
          {phase.replaceAll("_", " ")}
        </Badge>
      ))}
    </div>
  );
}

function SmallMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-muted/25 p-3">
      <p className="text-[11px] text-muted-foreground">{label}</p>
      <p className="mt-1 font-mono font-semibold">{value}</p>
    </div>
  );
}

function eventFrames(
  frames: SquatExplanationFrame[],
  repetition: SquatCaseExplanation["repetitions"][number]["segmentation"],
) {
  return [
    ["Inicio", repetition.start_seconds],
    ["Máxima profundidad", repetition.peak_depth_seconds],
    ["Final", repetition.end_seconds],
  ].map(([event, timestamp]) => ({
    event: String(event),
    frame: nearestFrame(frames, Number(timestamp)),
  }));
}

function nearestFrame(frames: SquatExplanationFrame[], timestamp: number) {
  return frames.reduce((nearest, frame) =>
    Math.abs(frame.timestamp_seconds - timestamp) <
    Math.abs(nearest.timestamp_seconds - timestamp)
      ? frame
      : nearest,
  );
}

function variableValue(frame: SquatExplanationFrame, variable: VariableKey) {
  if (variable === "trunk") return frame.trunk_inclination_deg;
  if (variable === "pelvis") return frame.pelvis_lateral_shift_pct;
  return frame.bilateral_alignment_difference_pct;
}

function formatValue(value: number | null | undefined, unit: string) {
  return value == null ? "Sin dato" : `${value.toFixed(2)} ${unit}`;
}

function formatSeconds(value: number) {
  return `${Number(value).toFixed(1)} s`;
}

export function formatTooltipSeconds(value: unknown) {
  const timestamp = Number(value);
  return Number.isFinite(timestamp)
    ? `${timestamp.toFixed(2)} s`
    : "Tiempo no disponible";
}

function findingLabel(finding: string) {
  const labels: Record<string, string> = {
    inclinacion_lateral_tronco: "Inclinación lateral del tronco",
    desplazamiento_lateral_pelvis: "Desplazamiento lateral de pelvis",
    valgo_dinamico_visible: "Valgo dinámico visible",
    asimetria_bilateral_observable: "Asimetría bilateral observable",
  };
  return labels[finding] ?? finding;
}

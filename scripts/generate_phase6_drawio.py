"""Generate editable draw.io evidence diagrams for squat analysis phase 6."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "diagramas" / "fase6"

NODE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;arcSize=12;strokeWidth=2;"
    "fontSize=13;fontFamily=Helvetica;align=center;verticalAlign=middle;"
)
EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
    "jettySize=auto;html=1;strokeWidth=2;endArrow=block;endFill=1;"
)


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    x: int
    y: int
    width: int = 190
    height: int = 64
    fill: str = "#f8fafc"
    stroke: str = "#334155"
    font: str = "#0f172a"
    shape: str = "rounded=1"


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str = ""
    dashed: bool = False


@dataclass(frozen=True)
class Diagram:
    filename: str
    title: str
    subtitle: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    width: int
    height: int


def _architecture() -> Diagram:
    return Diagram(
        filename="arquitectura_sistema_sentadilla.drawio",
        title="Arquitectura del sistema de análisis de sentadilla bilateral",
        subtitle="Fase 6 · Prototipo de investigación · Alcance no clínico",
        width=1500,
        height=870,
        nodes=(
            Node("browser", "Navegador web", 60, 250, fill="#e0f2fe", stroke="#0369a1"),
            Node(
                "next",
                "Next.js 16\nReact · Tailwind CSS · shadcn/ui",
                300,
                220,
                230,
                90,
                "#dbeafe",
                "#1d4ed8",
            ),
            Node(
                "fastapi",
                "API FastAPI\nContratos Pydantic y autorización",
                610,
                220,
                235,
                90,
                "#dcfce7",
                "#15803d",
            ),
            Node(
                "pipeline",
                "Pipeline de visión\nOpenCV · MediaPipe Pose",
                930,
                120,
                235,
                90,
                "#fef3c7",
                "#b45309",
            ),
            Node(
                "analysis",
                "Cálculo y evidencia\nNumPy · Pandas · Matplotlib",
                930,
                260,
                235,
                90,
                "#fef3c7",
                "#b45309",
            ),
            Node(
                "rules",
                "Criterios interpretables\nUmbrales versionados",
                930,
                400,
                235,
                90,
                "#ffedd5",
                "#c2410c",
            ),
            Node(
                "metrics",
                "Comparación experta\nF1-score · Kappa",
                1240,
                400,
                210,
                90,
                "#fee2e2",
                "#b91c1c",
            ),
            Node(
                "auth",
                "Supabase Auth\nInvestigador y expertos",
                610,
                430,
                235,
                80,
                "#ede9fe",
                "#6d28d9",
            ),
            Node(
                "db",
                "PostgreSQL + RLS\nCasos · evaluaciones · métricas",
                610,
                560,
                235,
                90,
                "#ede9fe",
                "#6d28d9",
            ),
            Node(
                "storage",
                "Storage privado\nVideo · overlay · capturas",
                930,
                560,
                235,
                90,
                "#ede9fe",
                "#6d28d9",
            ),
            Node(
                "exports",
                "Exportaciones\nExcel · PDF · CSV · JSON",
                1240,
                560,
                210,
                90,
                "#f1f5f9",
                "#475569",
            ),
            Node(
                "tests",
                "Verificación\npytest · Vitest · Playwright",
                300,
                560,
                230,
                90,
                "#ccfbf1",
                "#0f766e",
            ),
            Node(
                "git",
                "Trazabilidad\nGit y documentación de evidencias",
                300,
                700,
                230,
                80,
                "#ccfbf1",
                "#0f766e",
            ),
        ),
        edges=(
            Edge("browser", "next", "Interfaz"),
            Edge("next", "fastapi", "JWT + REST"),
            Edge("fastapi", "pipeline", "Video"),
            Edge("pipeline", "analysis", "Puntos 2D"),
            Edge("analysis", "rules", "Variables"),
            Edge("rules", "metrics", "Etiquetas"),
            Edge("next", "auth", "Sesión"),
            Edge("fastapi", "db", "Metadatos"),
            Edge("fastapi", "storage", "Artefactos"),
            Edge("metrics", "exports", "Resultados"),
            Edge("db", "exports", "Instrumentos"),
            Edge("tests", "next", "Pruebas UI", True),
            Edge("tests", "fastapi", "Pruebas API", True),
            Edge("git", "tests", "Evidencia", True),
        ),
    )


def _investigator_flow() -> Diagram:
    nodes = (
        Node("login", "Iniciar sesión\ncomo investigador", 60, 170, fill="#dbeafe", stroke="#1d4ed8"),
        Node("history", "Consultar historial\npaginado", 300, 170),
        Node("register", "Registrar caso\ne Instrumento 1", 540, 170),
        Node("upload", "Cargar video", 780, 170),
        Node("quality", "Control de calidad\ny factibilidad", 1020, 170, fill="#fef3c7", stroke="#b45309"),
        Node("decision", "¿Video apto?", 1260, 170, 160, 70, "#ffedd5", "#c2410c", shape="rhombus"),
        Node("reject", "Registrar motivo\ny solicitar nueva captura", 1210, 330, 210, 80, "#fee2e2", "#b91c1c"),
        Node("process", "Procesar pose, fases,\nvariables y reglas", 960, 480, 220, 85, "#dcfce7", "#15803d"),
        Node("results", "Revisar overlay,\ncapturas e Instrumento 2", 690, 480, 220, 85),
        Node("assign", "Asignar evaluadores", 440, 480),
        Node("compare", "Consolidar referencia\ny comparar", 200, 480, fill="#ede9fe", stroke="#6d28d9"),
        Node("export", "Consultar métricas\ny exportar Excel/PDF", 60, 650, 210, 80, "#ccfbf1", "#0f766e"),
    )
    return Diagram(
        "flujo_investigador_sentadilla.drawio",
        "Flujo del investigador",
        "Desde el Instrumento 1 hasta la comparación experta y la exportación",
        nodes,
        (
            Edge("login", "history"),
            Edge("history", "register"),
            Edge("register", "upload"),
            Edge("upload", "quality"),
            Edge("quality", "decision"),
            Edge("decision", "reject", "No"),
            Edge("decision", "process", "Sí"),
            Edge("process", "results"),
            Edge("results", "assign"),
            Edge("assign", "compare"),
            Edge("compare", "export"),
        ),
        1500,
        820,
    )


def _expert_flow() -> Diagram:
    nodes = (
        Node("login", "Iniciar sesión\ncomo experto", 80, 180, fill="#dbeafe", stroke="#1d4ed8"),
        Node("assignments", "Consultar asignaciones\npropias", 330, 180),
        Node("review", "Reproducir video\nanonimizado", 580, 180),
        Node("blind", "Sin overlay, métricas\nni salida del sistema", 580, 330, 200, 75, "#fee2e2", "#b91c1c"),
        Node("classify", "Clasificar cuatro\npatrones independientes", 830, 180, 220, 80, "#fef3c7", "#b45309"),
        Node("complete", "¿Ficha completa?", 1110, 180, 170, 70, "#ffedd5", "#c2410c", shape="rhombus"),
        Node("draft", "Guardar borrador", 1095, 330),
        Node("submit", "Enviar evaluación", 1320, 330, fill="#dcfce7", stroke="#15803d"),
        Node("lock", "Bloquear edición", 1095, 500),
        Node("reference", "Disponible para\nconsolidación del investigador", 780, 500, 230, 80, "#ede9fe", "#6d28d9"),
    )
    return Diagram(
        "flujo_experto_instrumento3.drawio",
        "Flujo del evaluador experto",
        "Aplicación ciega del Instrumento 3",
        nodes,
        (
            Edge("login", "assignments"),
            Edge("assignments", "review"),
            Edge("review", "classify"),
            Edge("review", "blind", "Restricción", True),
            Edge("classify", "complete"),
            Edge("complete", "draft", "No"),
            Edge("draft", "review", "Continuar"),
            Edge("complete", "submit", "Sí"),
            Edge("submit", "lock"),
            Edge("lock", "reference"),
        ),
        1550,
        700,
    )


def _processing_sequence() -> Diagram:
    nodes = (
        Node("user", "Investigador", 60, 120, fill="#dbeafe", stroke="#1d4ed8"),
        Node("web", "Next.js", 330, 120, fill="#dbeafe", stroke="#1d4ed8"),
        Node("api", "FastAPI", 600, 120, fill="#dcfce7", stroke="#15803d"),
        Node("cv", "Pipeline CV", 870, 120, fill="#fef3c7", stroke="#b45309"),
        Node("store", "Supabase", 1140, 120, fill="#ede9fe", stroke="#6d28d9"),
        Node("s1", "1. Registra metadatos y carga video", 180, 270, 300, 55),
        Node("s2", "2. Crea caso y conserva entrada", 470, 370, 300, 55),
        Node("s3", "3. Calidad, pose y segmentación", 740, 470, 300, 55),
        Node("s4", "4. Variables, reglas y artefactos", 740, 570, 300, 55),
        Node("s5", "5. Persiste reporte y archivos", 1010, 670, 300, 55),
        Node("s6", "6. Consulta resultado persistido", 470, 770, 300, 55),
        Node("s7", "7. Presenta overlay, capturas y métricas", 180, 870, 330, 55),
    )
    return Diagram(
        "secuencia_procesamiento_video.drawio",
        "Secuencia de carga y procesamiento",
        "Trazabilidad desde el video de entrada hasta los artefactos persistidos",
        nodes,
        (
            Edge("user", "s1"),
            Edge("s1", "web"),
            Edge("web", "s2"),
            Edge("s2", "api"),
            Edge("api", "s3"),
            Edge("s3", "cv"),
            Edge("cv", "s4"),
            Edge("s4", "api"),
            Edge("api", "s5"),
            Edge("s5", "store"),
            Edge("store", "s6"),
            Edge("s6", "web"),
            Edge("web", "s7"),
            Edge("s7", "user"),
        ),
        1400,
        1040,
    )


def _comparison_sequence() -> Diagram:
    nodes = (
        Node("expert", "Evaluadores expertos", 60, 120, 220, 65, "#dbeafe", "#1d4ed8"),
        Node("web", "Interfaz web", 370, 120, fill="#dbeafe", stroke="#1d4ed8"),
        Node("api", "FastAPI", 650, 120, fill="#dcfce7", stroke="#15803d"),
        Node("db", "Supabase", 930, 120, fill="#ede9fe", stroke="#6d28d9"),
        Node("researcher", "Investigador", 1210, 120, fill="#dbeafe", stroke="#1d4ed8"),
        Node("blind", "1. Evaluación ciega independiente", 80, 280, 270, 60),
        Node("persist", "2. Borrador, envío y bloqueo", 350, 390, 270, 60),
        Node("reference", "3. Coincidencia, mayoría o discrepancia", 620, 500, 290, 60),
        Node("consensus", "4. Consenso guiado si corresponde", 970, 610, 290, 60),
        Node("metrics", "5. Matriz binaria, F1-score y Kappa", 620, 720, 300, 60),
        Node("export", "6. Comparación y exportación", 350, 830, 270, 60),
    )
    return Diagram(
        "secuencia_comparacion_metricas.drawio",
        "Secuencia de evaluación experta y desempeño técnico",
        "Instrumento 3, consolidación de referencia y métricas",
        nodes,
        (
            Edge("expert", "blind"),
            Edge("blind", "web"),
            Edge("web", "persist"),
            Edge("persist", "api"),
            Edge("api", "db"),
            Edge("db", "reference"),
            Edge("reference", "api"),
            Edge("api", "consensus"),
            Edge("consensus", "researcher"),
            Edge("researcher", "metrics"),
            Edge("metrics", "api"),
            Edge("api", "export"),
            Edge("export", "web"),
        ),
        1500,
        1000,
    )


def _traceability() -> Diagram:
    nodes: list[Node] = []
    edges: list[Edge] = []
    objectives = (
        ("o1", "OE1\nIdentificar puntos\nanatómicos clave", "Overlay · calidad de pose\npromedio de puntos clave"),
        ("o2", "OE2\nDefinir variables\nbiomecánicas", "Series temporales · fases\nvalores por repetición"),
        ("o3", "OE3\nDiseñar criterios\ninterpretables", "Regla · valor · umbral\nversión · decisión"),
        ("o4", "OE4\nImplementar\nel prototipo", "Carga · API · resultados\nhistorial · exportaciones"),
        ("o5", "OE5\nEvaluar desempeño\ntécnico", "Referencia experta\nF1-score · Kappa"),
    )
    for index, (objective_id, objective, evidence) in enumerate(objectives):
        y = 150 + index * 135
        evidence_id = f"e{index + 1}"
        nodes.append(Node(objective_id, objective, 80, y, 240, 80, "#dbeafe", "#1d4ed8"))
        nodes.append(Node(evidence_id, evidence, 410, y, 270, 80, "#dcfce7", "#15803d"))
        nodes.append(
            Node(
                f"v{index + 1}",
                (
                    "pytest + overlay"
                    if index == 0
                    else "pytest + gráficos"
                    if index == 1
                    else "pytest + evidencia de reglas"
                    if index == 2
                    else "Vitest + Playwright"
                    if index == 3
                    else "Playwright + exportaciones"
                ),
                770,
                y,
                250,
                80,
                "#fef3c7",
                "#b45309",
            )
        )
        nodes.append(
            Node(
                f"d{index + 1}",
                f"Documento de evidencia OE{index + 1}",
                1110,
                y,
                250,
                80,
                "#ede9fe",
                "#6d28d9",
            )
        )
        edges.extend(
            (
                Edge(objective_id, evidence_id, "se demuestra con"),
                Edge(evidence_id, f"v{index + 1}", "se verifica mediante"),
                Edge(f"v{index + 1}", f"d{index + 1}", "se documenta en"),
            )
        )
    return Diagram(
        "trazabilidad_objetivos_evidencias.drawio",
        "Trazabilidad de objetivos específicos y evidencias",
        "Objetivo → resultado observable → verificación → documento",
        tuple(nodes),
        tuple(edges),
        1450,
        900,
    )


def _quality_flow() -> Diagram:
    return Diagram(
        "flujo_video_no_apto_sentadilla.drawio",
        "Flujo de control de calidad del video",
        "La calidad de entrada se separa de la clasificación biomecánica",
        (
            Node("input", "Video y metadatos\ndel Instrumento 1", 80, 220, 220, 80, "#dbeafe", "#1d4ed8"),
            Node("protocol", "Validar vista frontal,\nvisibilidad y oclusiones", 390, 220, 240, 80),
            Node("pose", "Verificar puntos críticos\ny estabilidad de pose", 720, 220, 240, 80, "#fef3c7", "#b45309"),
            Node("decision", "¿Evidencia suficiente?", 1050, 220, 200, 80, "#ffedd5", "#c2410c", shape="rhombus"),
            Node("reject", "Registrar motivo\nNo calcular compensaciones", 1040, 410, 220, 85, "#fee2e2", "#b91c1c"),
            Node("retry", "Solicitar nueva captura\nsi corresponde", 720, 520, 230, 75),
            Node("accept", "Procesar variables\ny criterios interpretables", 1320, 410, 230, 85, "#dcfce7", "#15803d"),
            Node("manual", "Apoyo plantar y soportes:\nregistro manual contextual", 390, 410, 240, 80, "#ede9fe", "#6d28d9"),
        ),
        (
            Edge("input", "protocol"),
            Edge("protocol", "pose"),
            Edge("pose", "decision"),
            Edge("decision", "reject", "No"),
            Edge("reject", "retry"),
            Edge("decision", "accept", "Sí"),
            Edge("protocol", "manual", "Documentar", True),
        ),
        1650,
        700,
    )


def diagrams() -> tuple[Diagram, ...]:
    """Return every phase 6 diagram specification."""
    return (
        _architecture(),
        _investigator_flow(),
        _expert_flow(),
        _processing_sequence(),
        _comparison_sequence(),
        _traceability(),
        _quality_flow(),
    )


def _add_geometry(
    cell: ET.Element,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    ET.SubElement(
        cell,
        "mxGeometry",
        {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "as": "geometry",
        },
    )


def _build_xml(diagram: Diagram) -> ET.ElementTree:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "agent": "sistema-biomecanico-phase6",
            "version": "26.0.16",
            "type": "device",
        },
    )
    page = ET.SubElement(mxfile, "diagram", {"id": "phase6", "name": "Página 1"})
    model = ET.SubElement(
        page,
        "mxGraphModel",
        {
            "dx": "1422",
            "dy": "794",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(diagram.width),
            "pageHeight": str(diagram.height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    title = ET.SubElement(
        root,
        "mxCell",
        {
            "id": "title",
            "value": diagram.title,
            "style": (
                "text;html=1;strokeColor=none;fillColor=none;align=left;"
                "verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=24;"
                "fontStyle=1;fontColor=#0f172a;"
            ),
            "vertex": "1",
            "parent": "1",
        },
    )
    _add_geometry(title, 40, 25, diagram.width - 80, 38)

    subtitle = ET.SubElement(
        root,
        "mxCell",
        {
            "id": "subtitle",
            "value": diagram.subtitle,
            "style": (
                "text;html=1;strokeColor=none;fillColor=none;align=left;"
                "verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=13;"
                "fontColor=#475569;"
            ),
            "vertex": "1",
            "parent": "1",
        },
    )
    _add_geometry(subtitle, 40, 65, diagram.width - 80, 28)

    for node in diagram.nodes:
        style = (
            NODE_STYLE
            + f"fillColor={node.fill};strokeColor={node.stroke};fontColor={node.font};"
        )
        if node.shape == "rhombus":
            style += "shape=rhombus;perimeter=rhombusPerimeter;"
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": node.id,
                "value": node.label.replace("\n", "<br>"),
                "style": style,
                "vertex": "1",
                "parent": "1",
            },
        )
        _add_geometry(cell, node.x, node.y, node.width, node.height)

    for index, edge in enumerate(diagram.edges, start=1):
        style = EDGE_STYLE + ("dashed=1;" if edge.dashed else "")
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": f"edge-{index}",
                "value": edge.label,
                "style": style,
                "edge": "1",
                "parent": "1",
                "source": edge.source,
                "target": edge.target,
            },
        )
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    return ET.ElementTree(mxfile)


def generate(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Write all editable draw.io files and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for diagram in diagrams():
        path = output_dir / diagram.filename
        tree = _build_xml(diagram)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)
        paths.append(path)
    return paths


if __name__ == "__main__":
    for generated_path in generate():
        print(generated_path.relative_to(ROOT))

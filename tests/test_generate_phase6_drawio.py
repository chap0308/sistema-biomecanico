from xml.etree import ElementTree as ET

from scripts.generate_phase6_drawio import diagrams, generate


def test_generate_phase6_drawio_files(tmp_path):
    paths = generate(tmp_path)

    assert len(paths) == len(diagrams()) == 7
    assert {path.name for path in paths} == {
        "arquitectura_sistema_sentadilla.drawio",
        "flujo_experto_instrumento3.drawio",
        "flujo_investigador_sentadilla.drawio",
        "flujo_video_no_apto_sentadilla.drawio",
        "secuencia_comparacion_metricas.drawio",
        "secuencia_procesamiento_video.drawio",
        "trazabilidad_objetivos_evidencias.drawio",
    }

    for path in paths:
        root = ET.parse(path).getroot()
        assert root.tag == "mxfile"
        assert root.find(".//mxGraphModel") is not None
        assert len(root.findall(".//mxCell[@vertex='1']")) >= 7
        assert len(root.findall(".//mxCell[@edge='1']")) >= 6

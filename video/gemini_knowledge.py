"""Gemini-powered knowledge extraction from public educational videos."""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class UsefulnessLabel(str, Enum):
    USEFUL = 'useful'
    MAYBE_USEFUL = 'maybe_useful'
    NOT_USEFUL = 'not_useful'


class ContentKind(str, Enum):
    CORRECTIVE_PROTOCOL = 'corrective_protocol'
    INFORMATIONAL_CONCEPT = 'informational_concept'
    FUNCTIONAL_TEST = 'functional_test'
    EXERCISE_PREREQUISITE = 'exercise_prerequisite'
    EXERCISE_OPTIMIZATION = 'exercise_optimization'
    MOVEMENT_REEDUCATION = 'movement_reeducation'
    POSTURE_STRATEGY = 'posture_strategy'
    CASE_EXPLANATION = 'case_explanation'
    HABIT_EXPLANATION = 'habit_explanation'
    TESTIMONIAL = 'testimonial'
    PROMOTIONAL = 'promotional'
    MIXED = 'mixed'
    OTHER = 'other'


class KnowledgeUnitType(str, Enum):
    DEFICIENCY_PATTERN = 'deficiency_pattern'
    COMPENSATION_PATTERN = 'compensation_pattern'
    HABIT_PATTERN = 'habit_pattern'
    BIOMECHANICAL_MECHANISM = 'biomechanical_mechanism'
    FUNCTIONAL_TEST = 'functional_test'
    CORRECTIVE_EXERCISE = 'corrective_exercise'
    BREATHING_DRILL = 'breathing_drill'
    MOBILITY_DRILL = 'mobility_drill'
    STRENGTH_DRILL = 'strength_drill'
    SELF_RELEASE = 'self_release'
    TECHNIQUE_CORRECTION = 'technique_correction'
    PRACTICAL_ADVICE = 'practical_advice'
    EDUCATIONAL_POINT = 'educational_point'
    CASE_EXAMPLE = 'case_example'
    RED_FLAG = 'red_flag'
    OTHER = 'other'


class Classification(BaseModel):
    usefulness: UsefulnessLabel
    usefulness_reason: str
    exclusion_reason: str | None = None
    content_kind: ContentKind
    body_regions: list[str] = Field(default_factory=list)
    problem_layers: list[str] = Field(default_factory=list)
    suitable_for_protocol_database: bool
    suitable_for_concept_knowledge_base: bool
    suitable_for_recommendation_mapping: bool
    contains_visual_execution_detail: bool
    confidence: str


class KnowledgeUnit(BaseModel):
    unit_type: KnowledgeUnitType
    title: str
    summary: str
    observable_signs: list[str] = Field(default_factory=list)
    mechanisms: list[str] = Field(default_factory=list)
    execution_steps: list[str] = Field(default_factory=list)
    cues: list[str] = Field(default_factory=list)
    breathing_cues: list[str] = Field(default_factory=list)
    errors_to_avoid: list[str] = Field(default_factory=list)
    when_useful: list[str] = Field(default_factory=list)
    when_not_useful: list[str] = Field(default_factory=list)
    retest: list[str] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list)
    timestamps: list[str] = Field(default_factory=list)


class VideoKnowledgeAnalysis(BaseModel):
    source_url: str
    source_title_hint: str = ''
    primary_summary: str
    classification: Classification
    searchable_topics: list[str] = Field(default_factory=list)
    searchable_tags: list[str] = Field(default_factory=list)
    problem_statements: list[str] = Field(default_factory=list)
    habits_or_contexts: list[str] = Field(default_factory=list)
    key_visual_points: list[str] = Field(default_factory=list)
    tests_mentioned: list[str] = Field(default_factory=list)
    exercises_mentioned: list[str] = Field(default_factory=list)
    advice_mentioned: list[str] = Field(default_factory=list)
    warnings_or_limitations: list[str] = Field(default_factory=list)
    knowledge_units: list[KnowledgeUnit] = Field(default_factory=list)
    model_notes: str = ''


SYSTEM_INSTRUCTION = """
You are curating a biomechanical video knowledge base from educational YouTube Shorts.

Your task is not just to summarize the video.
You must classify whether the video is useful for a long-term knowledge base used for:
- diagnostic support
- explanation support
- corrective exercise selection
- biomechanical concept retrieval

Important rules:
- Not every useful video is deficiency -> exercise.
- Some useful videos are concept videos, movement explanations, habit explanations, test explanations, technique corrections, or exercise prerequisite videos.
- Some videos are NOT useful for the knowledge base, such as testimonials, marketing, generic personal updates, or low-information clips.
- If the video is a testimonial or not useful, clearly mark it as not useful and explain why.
- Separate what is visually shown from what is claimed by the speaker.
- Extract visual execution details when present.
- Prefer concise factual statements over hype.
- If the video contains multiple useful knowledge units, return multiple units.
- If a field is not applicable, return an empty list or null as appropriate.
- Do not invent clinical certainty.
""".strip()


USER_PROMPT_TEMPLATE = """
Analyze this public YouTube Short for inclusion in a biomechanical knowledge base.

Video URL: {video_url}
Title hint: {title_hint}

Return a structured JSON answer using the provided schema.

Things to determine carefully:
1. Is the video useful for the knowledge base?
2. What kind of content is it really?
   - corrective protocol
   - informational concept
   - movement reeducation
   - exercise prerequisite
   - exercise optimization
   - functional test
   - posture strategy
   - habit explanation
   - case explanation
   - testimonial
   - promotional or not useful
3. What exact knowledge units does it contain?
4. If there is an exercise or drill, describe the execution visually and practically.
5. If it only provides explanation, still extract the educational value.
6. If it is a testimonial, marketing, or otherwise low-value for the database, mark it as not useful.

Be conservative and structured.
""".strip()


def load_gemini_api_key() -> str:
    """Load Gemini API key from env, .env or .env.example."""
    for key_name in ('CLAVE_API_GEMINI', 'GEMINI_API_KEY'):
        value = os.getenv(key_name)
        if value:
            return value.strip().strip('"').strip("'")

    for candidate in (Path('.env'), Path('.env.example')):
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            env_key, env_value = line.split('=', 1)
            if env_key.strip() == 'CLAVE_API_GEMINI':
                return env_value.strip().strip('"').strip("'")

    raise RuntimeError('No Gemini API key found in environment, .env, or .env.example')


def build_client() -> Any:
    from google import genai

    api_key = load_gemini_api_key()
    return genai.Client(api_key=api_key)


def analyze_youtube_video(
    *,
    video_url: str,
    title_hint: str = '',
    model: str = 'gemini-2.5-flash',
    max_output_tokens: int = 8192,
) -> VideoKnowledgeAnalysis:
    from google.genai import types

    client = build_client()
    prompt = USER_PROMPT_TEMPLATE.format(video_url=video_url, title_hint=title_hint)
    response = client.models.generate_content(
        model=model,
        contents=[
            prompt,
            types.Part.from_uri(file_uri=video_url, mime_type='video/*'),
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type='application/json',
            response_schema=VideoKnowledgeAnalysis,
            max_output_tokens=max_output_tokens,
        ),
    )
    if response.parsed is not None:
        return response.parsed
    return VideoKnowledgeAnalysis.model_validate_json(response.text)


def save_analysis(path: Path, analysis: VideoKnowledgeAnalysis) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(analysis.model_dump(mode='json'), indent=2, ensure_ascii=False), encoding='utf-8')


def load_analysis(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))

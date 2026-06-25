"""Utilities for parsing and presenting structured IELTS examiner output."""

from __future__ import annotations

import json
import re
from typing import Any


CRITERIA_LABELS = {
    "task_response": "Task Response",
    "coherence_and_cohesion": "Coherence and Cohesion",
    "lexical_resource": "Lexical Resource",
    "grammatical_range_and_accuracy": "Grammatical Range and Accuracy",
}


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _extract_json_object(text: str) -> str:
    cleaned = _strip_code_fence(text)
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]

    return cleaned


def parse_band(value: Any) -> float | None:
    """Return a valid IELTS band score, or None when parsing is not possible."""
    if value is None:
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        match = re.search(r"\d(?:\.\d)?", str(value))
        if not match:
            return None
        score = float(match.group(0))

    if 0 <= score <= 9:
        return round(score * 2) / 2
    return None


def parse_examiner_report(raw_text: str) -> dict[str, Any]:
    """Parse the AI response and return a safe structured wrapper."""
    try:
        data = json.loads(_extract_json_object(raw_text))
        if not isinstance(data, dict):
            raise ValueError("Top-level JSON value is not an object.")

        overall_band = parse_band(data.get("overall_band"))
        if overall_band is not None:
            data["overall_band"] = overall_band

        criteria = data.get("criteria_scores")
        if isinstance(criteria, dict):
            data["criteria_scores"] = {
                key: parse_band(value)
                for key, value in criteria.items()
                if parse_band(value) is not None
            }
        else:
            data["criteria_scores"] = {}

        return {
            "ok": True,
            "data": data,
            "raw": raw_text,
            "error": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "data": {},
            "raw": raw_text,
            "error": str(exc),
        }


def structured_report_to_markdown(parsed: dict[str, Any]) -> str:
    """Convert a parsed report into Markdown for downloads and the error book."""
    if not parsed.get("ok"):
        return str(parsed.get("raw", ""))

    data = parsed.get("data", {})
    lines = ["# IELTS Writing Examiner Report", ""]
    overall = data.get("overall_band")
    lines.extend(["## Score Summary", "", f"Overall Band Score: {overall}", ""])

    lines.extend(["## Criteria Breakdown", ""])
    criteria = data.get("criteria_scores", {})
    explanations = data.get("score_explanation", {})
    for key, label in CRITERIA_LABELS.items():
        score = criteria.get(key, "N/A") if isinstance(criteria, dict) else "N/A"
        reason = explanations.get(key, "") if isinstance(explanations, dict) else ""
        lines.append(f"- {label}: {score}. {reason}".strip())
    lines.append("")

    lines.extend(["## Top Problems", ""])
    for item in data.get("top_3_problems", []) or []:
        if isinstance(item, dict):
            lines.append(f"- Problem: {item.get('problem', '')}")
            lines.append(f"  Original: {item.get('original_sentence', '')}")
            lines.append(f"  Suggestion: {item.get('suggestion', '')}")
    lines.append("")

    lines.extend(["## Sentence-level Corrections", ""])
    for item in data.get("sentence_level_corrections", []) or []:
        if isinstance(item, dict):
            lines.append(f"- Original: {item.get('original', '')}")
            lines.append(f"  Corrected: {item.get('corrected', '')}")
            lines.append(f"  Reason: {item.get('reason', '')}")
    lines.append("")

    lines.extend(["## Band 7.5 Rewrite", "", str(data.get("band_75_rewrite", "")), ""])
    lines.extend(["## Useful Expressions", ""])
    for item in data.get("useful_expressions", []) or []:
        if isinstance(item, dict):
            lines.append(
                f"- {item.get('expression', '')}: {item.get('meaning', '')} "
                f"Example: {item.get('example', '')}"
            )
    lines.append("")

    lines.extend(["## Next Practice Plan", ""])
    for item in data.get("next_practice_plan", []) or []:
        lines.append(f"- {item}")

    return "\n".join(lines).strip()

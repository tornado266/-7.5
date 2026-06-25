"""Storage helpers for IELTS correction records."""

import json
import re
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

from src.result_parser import parse_band


RECORDS_DIR = Path("records")
SCORE_PATTERN = re.compile(r"(?:Likely Score|Overall Band|likely score)[^\d]*(\d(?:\.\d)?)")


def save_markdown_record(
    task_type: str,
    topic: str,
    essay: str,
    report: str,
    word_count: int,
    parsed_result: dict[str, Any] | None = None,
) -> Path:
    """Save one correction record as Markdown plus structured JSON metadata."""
    RECORDS_DIR.mkdir(exist_ok=True)

    created_at = datetime.now()
    timestamp = created_at.strftime("%Y%m%d_%H%M%S")
    file_stem = f"ielts_{task_type.lower().replace(' ', '_')}_{timestamp}"
    file_path = RECORDS_DIR / f"{file_stem}.md"
    json_path = RECORDS_DIR / f"{file_stem}.json"

    parsed_result = parsed_result or {}
    parsed_data = parsed_result.get("data", {}) if parsed_result.get("ok") else {}
    overall_band = parse_band(parsed_data.get("overall_band"))
    criteria_scores = parsed_data.get("criteria_scores", {})
    if not isinstance(criteria_scores, dict):
        criteria_scores = {}

    metadata = {
        "timestamp": created_at.isoformat(timespec="seconds"),
        "question": topic,
        "essay": essay,
        "overall_band": overall_band,
        "criteria_scores": criteria_scores,
        "raw_result": parsed_result.get("raw", report),
        "structured_parse_ok": bool(parsed_result.get("ok")),
        "parse_error": parsed_result.get("error", ""),
        "task_type": task_type,
        "word_count": word_count,
        "markdown_file": file_path.name,
    }

    content = dedent(
        f"""
        # IELTS Writing Examiner Record

        - Task Type: {task_type}
        - Word Count: {word_count}
        - Created At: {created_at.strftime("%Y-%m-%d %H:%M:%S")}
        - Overall Band: {overall_band if overall_band is not None else "N/A"}

        ## Essay Question

        {topic}

        ## Student Essay

        {essay}

        ---

        {report}
        """
    ).strip()

    file_path.write_text(content, encoding="utf-8")
    json_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return file_path


def extract_overall_score(markdown: str) -> float | None:
    """Extract the most likely overall band score from a correction report."""
    match = SCORE_PATTERN.search(markdown)
    if not match:
        return None

    return parse_band(match.group(1))


def _read_json_record(path: Path) -> dict[str, object] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
    except (OSError, json.JSONDecodeError):
        return None

    score = parse_band(data.get("overall_band"))
    created_at = str(data.get("timestamp") or path.stem)
    markdown_file = str(data.get("markdown_file") or f"{path.stem}.md")
    return {
        "file": markdown_file,
        "path": RECORDS_DIR / markdown_file,
        "created_at": created_at,
        "task_type": str(data.get("task_type") or "Task 2"),
        "word_count": data.get("word_count"),
        "score": score,
        "criteria_scores": data.get("criteria_scores")
        if isinstance(data.get("criteria_scores"), dict)
        else {},
    }


def _read_markdown_record(path: Path) -> dict[str, object] | None:
    try:
        markdown = path.read_text(encoding="utf-8")
    except OSError:
        return None

    created_match = re.search(r"- Created At:\s*(.+)", markdown)
    task_match = re.search(r"- Task Type:\s*(.+)", markdown)
    words_match = re.search(r"- Word Count:\s*(\d+)", markdown)

    try:
        word_count = int(words_match.group(1)) if words_match else None
    except ValueError:
        word_count = None

    return {
        "file": path.name,
        "path": path,
        "created_at": created_match.group(1) if created_match else path.stem,
        "task_type": task_match.group(1) if task_match else "Unknown",
        "word_count": word_count,
        "score": extract_overall_score(markdown),
        "criteria_scores": {},
    }


def list_correction_history() -> list[dict[str, object]]:
    """Read saved correction records and return lightweight history data."""
    if not RECORDS_DIR.exists():
        return []

    history: list[dict[str, object]] = []
    json_stems = set()

    for path in sorted(RECORDS_DIR.glob("ielts_*.json")):
        record = _read_json_record(path)
        if record:
            history.append(record)
            json_stems.add(path.stem)

    for path in sorted(RECORDS_DIR.glob("ielts_*.md")):
        if path.stem in json_stems:
            continue
        record = _read_markdown_record(path)
        if record:
            history.append(record)

    return history

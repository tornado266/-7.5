"""Markdown storage helpers for IELTS correction records."""

import re
from datetime import datetime
from pathlib import Path
from textwrap import dedent


RECORDS_DIR = Path("records")
SCORE_PATTERN = re.compile(r"(?:Likely Score|Overall Band|likely score)[^\d]*(\d(?:\.\d)?)")


def save_markdown_record(
    task_type: str,
    topic: str,
    essay: str,
    report: str,
    word_count: int,
) -> Path:
    """Save one correction record as a local markdown file."""
    RECORDS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = RECORDS_DIR / f"ielts_{task_type.lower().replace(' ', '_')}_{timestamp}.md"

    content = dedent(
        f"""
        # IELTS Writing Correction Record

        - Task Type: {task_type}
        - Word Count: {word_count}
        - Created At: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        ## Essay Question

        {topic}

        ## Student Essay

        {essay}

        ---

        {report}
        """
    ).strip()

    file_path.write_text(content, encoding="utf-8")
    return file_path


def extract_overall_score(markdown: str) -> float | None:
    """Extract the most likely overall band score from a correction report."""
    match = SCORE_PATTERN.search(markdown)
    if not match:
        return None

    return float(match.group(1))


def list_correction_history() -> list[dict[str, object]]:
    """Read saved correction records and return lightweight history data."""
    if not RECORDS_DIR.exists():
        return []

    history: list[dict[str, object]] = []
    for path in sorted(RECORDS_DIR.glob("ielts_*.md")):
        markdown = path.read_text(encoding="utf-8")
        score = extract_overall_score(markdown)
        created_match = re.search(r"- Created At:\s*(.+)", markdown)
        task_match = re.search(r"- Task Type:\s*(.+)", markdown)
        words_match = re.search(r"- Word Count:\s*(\d+)", markdown)

        history.append(
            {
                "file": path.name,
                "path": path,
                "created_at": created_match.group(1) if created_match else path.stem,
                "task_type": task_match.group(1) if task_match else "Unknown",
                "word_count": int(words_match.group(1)) if words_match else None,
                "score": score,
            }
        )

    return history

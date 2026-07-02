import re
import uuid
from datetime import datetime
from pathlib import Path


ERROR_BOOK_PATH = Path("records") / "error_book.md"
SECTION_NAMES = [
    "Main Problems",
    "Sentence-level Corrections",
    "Paragraph-level Feedback",
]
CATEGORIES = {
    "Grammar": ["grammar", "grammatical", "tense", "article", "sentence"],
    "Vocabulary": ["lexical", "vocabulary", "word choice", "collocation"],
    "Logic": ["logic", "argument", "idea", "example", "relevance"],
    "Structure": ["coherence", "cohesion", "paragraph", "structure", "linking"],
}


def extract_error_sections(report: str) -> str:
    """Extract error-focused sections from the AI correction report."""
    lines = report.splitlines()
    extracted: list[str] = []
    active = False

    for line in lines:
        is_heading = line.startswith("## ")
        if is_heading:
            active = any(section in line for section in SECTION_NAMES)
        if active:
            extracted.append(line)

    return "\n".join(extracted).strip()


def categorize_errors(text: str) -> dict[str, list[str]]:
    """Group extracted report lines into simple learning categories."""
    categories: dict[str, list[str]] = {name: [] for name in CATEGORIES}
    for line in text.splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("##"):
            continue

        lowered = clean_line.lower()
        for category, keywords in CATEGORIES.items():
            if any(keyword in lowered for keyword in keywords):
                categories[category].append(clean_line)
                break

    return categories


def append_error_book(
    task_type: str,
    topic: str,
    report: str,
    user_id: str | None = None,
) -> Path:
    """Append grammar, vocabulary, logic, and structure errors to the error book."""
    if user_id is None:
        error_book_path = ERROR_BOOK_PATH
    else:
        try:
            normalized_user_id = str(uuid.UUID(user_id))
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValueError("user_id must be a valid UUID") from exc
        error_book_path = ERROR_BOOK_PATH.parent / normalized_user_id / "error_book.md"

    error_book_path.parent.mkdir(parents=True, exist_ok=True)
    extracted = extract_error_sections(report)
    categories = categorize_errors(extracted)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    topic_preview = re.sub(r"\s+", " ", topic).strip()[:120]
    parts = [
        f"\n\n## {created_at} - {task_type}",
        "",
        f"**Topic:** {topic_preview}",
        "",
    ]

    if not extracted:
        parts.append("_No error-focused sections were found in this report._")
    else:
        for category, items in categories.items():
            parts.append(f"### {category}")
            if items:
                parts.extend(f"- {item}" for item in items[:8])
            else:
                parts.append("- No clear item extracted from this report.")
            parts.append("")

    with error_book_path.open("a", encoding="utf-8") as file:
        if error_book_path.stat().st_size == 0:
            file.write("# IELTS Writing Error Book\n")
        file.write("\n".join(parts).strip() + "\n")

    return error_book_path

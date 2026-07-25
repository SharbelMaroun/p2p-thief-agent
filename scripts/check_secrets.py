"""Scan repository text for common committed-secret patterns."""

import re
from pathlib import Path
from re import Pattern

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".venv",
    "__pycache__",
    "htmlcov",
}
TEXT_SUFFIXES = {".json", ".lock", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
TEXT_FILENAMES = {".gitattributes", ".gitignore", "LICENSE"}
DUMMY_VALUES = {"", "abc123", "change-me", "changeme", "dummy", "example", "placeholder"}
DUMMY_PREFIXES = (
    "dummy-",
    "dummy_",
    "example-",
    "example_",
    "placeholder-",
    "placeholder_",
    "replace-",
    "replace_",
    "your-",
    "your_",
)
TOKEN_PATTERNS: dict[str, Pattern[str]] = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS credential": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub credential": re.compile(r"(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]{20,}"),
    "OpenAI-style credential": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Google credential": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    "Slack credential": re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"),
}
ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    (?:
        (?<![a-z0-9_])["']?(?:api[_-]?key|auth[_-]?token|access[_-]?token|
        refresh[_-]?token|client[_-]?secret|oauth[_-]?secret|
        tunnel[_-]?(?:credential|token)|password)["']?\s*[:=]
        |
        (?<![a-z0-9_])(?:["'](?:secret|token)["']\s*:|["']?(?:secret|token)["']?\s*=)
    )
    \s*["']?([^"'#,\s]+)
    """
)


def candidate_files() -> list[Path]:
    """Return scannable repository text files outside generated directories."""
    candidates: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        if (
            path.name.startswith(".env")
            or path.name in TEXT_FILENAMES
            or path.suffix.lower() in TEXT_SUFFIXES
        ):
            candidates.append(path)
    return sorted(candidates)


def is_dummy(value: str) -> bool:
    """Return whether an assignment contains an obvious non-secret example value."""
    normalized = value.strip("'\"").lower()
    return (
        normalized in DUMMY_VALUES
        or normalized.startswith(DUMMY_PREFIXES)
        or (normalized.startswith("${") and normalized.endswith("}"))
        or (normalized.startswith("<") and normalized.endswith(">"))
    )


def findings(path: Path) -> list[str]:
    """Return line-level findings for one text file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    matches: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in TOKEN_PATTERNS.items():
            if pattern.search(line):
                matches.append(f"{path.relative_to(PROJECT_ROOT)}:{line_number}: {label}")
        assignment = ASSIGNMENT_PATTERN.search(line)
        if assignment and not is_dummy(assignment.group(1)):
            matches.append(
                f"{path.relative_to(PROJECT_ROOT)}:{line_number}: credential assignment"
            )
    return matches


def main() -> int:
    """Scan repository text and fail when a plausible secret is present."""
    files = candidate_files()
    matches = [match for path in files for match in findings(path)]
    if matches:
        print("Possible secrets found:")
        print(*matches, sep="\n")
        return 1
    print(f"Secret scan OK: {len(files)} text files checked; 0 findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Enforce the official source and test file-size limits."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_LIMIT = 150
TEST_LIMIT = 150


def significant_line_count(path: Path) -> int:
    """Count nonblank lines that are not comment-only lines."""
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def physical_line_count(path: Path) -> int:
    """Count every physical line in a test file."""
    return len(path.read_text(encoding="utf-8").splitlines())


def python_files(directory: Path) -> list[Path]:
    """Return Python files below an existing directory in stable order."""
    return sorted(directory.rglob("*.py")) if directory.exists() else []


def javascript_files(directory: Path) -> list[Path]:
    """Return JavaScript files below an existing directory in stable order."""
    return sorted(directory.rglob("*.js")) if directory.exists() else []


def main() -> int:
    """Report any file that exceeds its controlling limit."""
    source_files = python_files(PROJECT_ROOT / "src") + python_files(PROJECT_ROOT / "scripts")
    test_files = python_files(PROJECT_ROOT / "tests") + javascript_files(
        PROJECT_ROOT / "tests" / "neutral_stub"
    )
    violations: list[str] = []

    for path in source_files:
        count = significant_line_count(path)
        if count > SOURCE_LIMIT:
            relative = path.relative_to(PROJECT_ROOT)
            violations.append(f"{relative}: {count} significant lines (limit {SOURCE_LIMIT})")

    for path in test_files:
        count = physical_line_count(path)
        if count > TEST_LIMIT:
            relative = path.relative_to(PROJECT_ROOT)
            violations.append(f"{relative}: {count} physical lines (limit {TEST_LIMIT})")

    if violations:
        print("File-length violations:")
        print(*violations, sep="\n")
        return 1

    print(
        f"File lengths OK: {len(source_files)} source/script files and "
        f"{len(test_files)} test files checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

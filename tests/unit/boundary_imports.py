"""How a file's project imports are found, for the rule-8/9 boundary guards.

Split out of `test_local_truth_boundary.py` on 2026-08-08 when adding the `ast.Import`
case pushed that module past the 150-line cap. It is a separate responsibility — *finding*
imports rather than *judging* them — so it moved out whole rather than being compressed.

**Why both statement forms.** The guards enforce rules 8 and 9, whose sanction is
disqualification of the project, and they matched only `from x import y`. A plain
`import p2p_thief_agent.orchestration as o` inside the live package would have sailed through the
one test that exists to stop it. A guard that checks one of the two ways to write the same
thing is not a guard.
"""

from __future__ import annotations

import ast


def project_imports(tree: ast.AST, prefix: str) -> list[str]:
    """Return every project module the tree imports, by either statement form."""
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(prefix):
            found.append(node.module or "")
        elif isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names if alias.name.startswith(prefix))
    return found

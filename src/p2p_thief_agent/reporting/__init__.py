"""Reporting: the four match artifacts and the Gmail send path (`M7`).

Only the book-confirmed artifact **naming and identity** are fixed here; the exact field
schema of each artifact is `U-019` and awaits the coordinator's ruling.
"""

from p2p_thief_agent.reporting.naming import (
    ArtifactError,
    MatchIdentity,
    config_filename,
    declaration_filename,
    log_filename,
    match_filenames,
    result_filename,
)

__all__ = [
    "ArtifactError",
    "MatchIdentity",
    "config_filename",
    "declaration_filename",
    "log_filename",
    "match_filenames",
    "result_filename",
]

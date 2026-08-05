"""Reporting: the four match artifacts and the Gmail send path (`M7`).

Only the book-confirmed artifact **naming and identity** are fixed here; the exact field
schema of each artifact is `U-019` and awaits the coordinator's ruling.
"""

from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import SCHEMA_VERSION, build_declaration
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import (
    ArtifactError,
    MatchIdentity,
    config_filename,
    declaration_filename,
    log_filename,
    match_filenames,
    result_filename,
)
from p2p_thief_agent.reporting.result_artifact import build_result

__all__ = [
    "SCHEMA_VERSION",
    "ArtifactError",
    "MatchIdentity",
    "build_config",
    "build_declaration",
    "build_log",
    "build_result",
    "config_filename",
    "declaration_filename",
    "log_filename",
    "match_filenames",
    "result_filename",
]

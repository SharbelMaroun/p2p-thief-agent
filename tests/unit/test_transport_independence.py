"""`M7-023`, structurally: `reporting/` cannot reach the transport layer at all.

The row's condition only matters when everything else has gone wrong. A game that ends
because the opponent vanished is precisely the game whose evidence gets disputed, and if
artifact emission needs a live peer then the record of a failed game is the record we cannot
produce.

`emit.py`'s docstring already claims emission holds no socket and no peer state, and a
docstring is not a guard. This file proves it by **reading the source**;
`test_disconnected_emission.py` proves it by building the whole artifact set with the peer
gone.

The structural proof is the stronger of the two, and the reason is worth stating: a
behavioural test shows that *this* path stays off the network, which a lazily-taken branch
can hide. Reading every import shows no such branch exists to take. It is also read from the
AST rather than by importing the modules — an import-based check passes trivially once some
earlier test has already loaded them.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPORTING = pathlib.Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "reporting"
TRANSPORT_PACKAGES = ("adapters", "peer", "sdk")
NETWORK_MODULES = ("socket", "http", "httpx", "requests", "urllib", "asyncio", "fastmcp")
MODULES = sorted(path.name for path in REPORTING.glob("*.py"))


def _imported_names(source: pathlib.Path) -> set[str]:
    """Every module name a file imports, read from the AST rather than executed."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("module", MODULES)
def test_no_reporting_module_imports_the_transport_layer(module: str) -> None:
    """Parametrised per module so a failure names the file, not the package."""
    for name in _imported_names(REPORTING / module):
        package = name.split(".")
        assert not (package[0] == "p2p_thief_agent" and package[1:2]
                    and package[1] in TRANSPORT_PACKAGES), (
            f"reporting/{module} imports {name}; artifact emission must survive a "
            "disconnected game, which is the game whose evidence gets disputed")


@pytest.mark.parametrize("module", MODULES)
def test_no_reporting_module_imports_a_network_library(module: str) -> None:
    """The same claim against third-party transport, which an import of our own layer would
    not catch — a direct `httpx` call inside a builder is the shape that slips in when
    somebody adds "just a quick health check"."""
    for name in _imported_names(REPORTING / module):
        assert name.split(".")[0] not in NETWORK_MODULES, f"reporting/{module} imports {name}"


def test_the_email_composer_is_transport_free_by_construction() -> None:
    """Worth asserting rather than assuming: `email_report.py` is the one module in this
    package whose *purpose* is to reach the network, and it passes the checks above because
    it composes an `EmailMessage` and takes its transport as an injected callable. That is
    the design `M7-014c` needs, and it is here by construction rather than by luck."""
    names = _imported_names(REPORTING / "email_report.py")
    assert "email.message" in names, "the composer builds a real EmailMessage"
    assert not {name for name in names if name.split(".")[0] in NETWORK_MODULES}


def test_the_reader_would_notice_a_transport_import() -> None:
    """Proves the AST reader bites rather than returning an empty set for everything — the
    failure mode of a structural test is that it silently inspects nothing."""
    sample = REPORTING.parent / "adapters" / "fastmcp_client.py"
    found = _imported_names(sample)
    assert found, "the reader found no imports at all in a real module"
    assert any(name.split(".")[0] in NETWORK_MODULES or name.startswith("fastmcp")
               for name in found), "a transport module imports no transport — check the reader"


def test_every_reporting_module_is_covered_by_the_sweep() -> None:
    """A glob that quietly matched nothing would make both checks above vacuous."""
    assert len(MODULES) >= 8, f"only {len(MODULES)} reporting modules found"

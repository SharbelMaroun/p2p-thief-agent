"""The replay verifier: rule 20's threshold condition (`M8-002`).

Appendix E rule 20 (Mandatory), p.129/272: "Mandatory to build a match log reconstruction
and replay app for observation and verification; **Threshold condition** for confirmation
of logs and submission of the project."

Four pieces, deliberately separate:

* `load` — turn a file into something replayable, **including an opponent's file**
  (rule 36's mutual audit), and refuse an in-play log without accusing anyone.
* `verify` — recompute each commitment; two verdicts, and one bad record voids the match.
* `sequence` — structural findings (gap, duplicate, shuffle) **reported beside** the
  verdict, never folded into it, because rule 19 covers the digest and structural damage
  answers to rules 5 and 35 with a different sanction.
* `cursor` — step forward, back and jump, recomputing the verdict on every move.

Re-authored against this repository's own `protocol.crypto`, never copied from the
companion repository (`THIEF-002`). Its `verify` raises where the companion's returns a
flag, which is exactly the kind of difference a copy would have silently swallowed.
"""

from p2p_thief_agent.replay.cursor import Replay
from p2p_thief_agent.replay.load import LogNotReplayableError, ReplayLog, load_log, parse_log
from p2p_thief_agent.replay.sequence import (
    SequenceFinding,
    SequenceReport,
    inspect_sequence,
)
from p2p_thief_agent.replay.verify import (
    MatchVerdict,
    RecordCheck,
    Verdict,
    verify_record,
    verify_records,
)

__all__ = [
    "LogNotReplayableError",
    "MatchVerdict",
    "RecordCheck",
    "Replay",
    "ReplayLog",
    "SequenceFinding",
    "SequenceReport",
    "Verdict",
    "inspect_sequence",
    "load_log",
    "parse_log",
    "verify_record",
    "verify_records",
]

# Handover note

Covers `M9-020`, `M9-020a`, `M9-020b`, and the disclosure `M9-011c` requires.

Written for whoever picks this up next — a coordinator, a grader, or me in a month. It says
what is open and what is unresolved, because the alternative is that someone rediscovers it
at the moment it costs the most.

## Open at handover — `M9-020a`

### Needs a person, not code

| Row | What | Why it cannot be automated |
| --- | --- | --- |
| `M9-001a-c` | Two counted games against two different groups | Needs real classmates and scheduling |
| `M9-003a-d` | Moodle submission, lecturer access, team code | The submission portal is a human action |
| `M9-005` | Create the annotated `v1.0-submission` tag | A submission act; should follow a reviewed commit, not precede it |
| `M9-013a` | Clean clone on a **second machine** | A local clone shares the OS, Python build and uv cache |
| `M7-013`, `M7-013a` | OAuth consent flow | The consent screen is where a human decides what a program may do with their mailbox |
| `M8-003c` | Rehearse against a real classmate agent | Needs a counterpart |

### Needs code, and is scoped

| Row | What | Note |
| --- | --- | --- |
| `M9-025` | **A command-line runtime for this agent** | The largest real gap. `p2p-cop serve` plays a match; `p2p-thief` exposes only `--help`. The behaviour exists and is exercised in `tests/integration/`; the wiring to `cli.py` does not |
| `M6-015c` | The evasion metric contradicts Appendix F scoring | Over 24 perimeter openings the ranking reverses: blind 175, belief 140. Open, not patched |
| `M9-010`, `M9-021` | Evidence bundle and league minimum | The machinery exists and is tested; both wait on real games to hold |

## Unresolved unknowns — `M9-020b`

| ID | Question | How we proceeded |
| --- | --- | --- |
| `U-019` | The four artifact templates have unresolved provenance | Requiredness comes from the **book**, never the templates; every required field cites a rule or page. Unexpected keys are accepted, because refusing one would fail rule 36's audit over a difference nothing forbids |
| `U-009` | OAuth setup details | The refresh policy, wire format and send gates are built and tested against injected doubles; the consent flow is the operator's |
| `U-021`, `U-025` | The six-sub-game role schedule | **Injected**, not hard-coded, so a correction is a one-line change |
| `U-033`, `U-034` | Awaiting a lecturer answer | Recorded in `docs/UNKNOWN_REQUIREMENTS.md` |

## Book contradictions relied on — `M9-011c`

Chapter 110 grants "the academic freedom to choose one of the options and proceed
accordingly, provided that you explicitly state in your report: where you identified the
contradiction, what you chose, and why." Each of these is disclosed under that clause.

**1. Draft versus send.** Rule 51 and §9.3.3 require the end-of-game JSON report to be *sent*,
and `inst/:2224` is explicit that a side whose report is not received scores nothing "even if
they won". But the shipped config example sets `[email] mode = "draft"` (`inst/:3041`,
`DEV-SPEC.md:228`) and the book's own overview describes "a JSON report sent via Gmail drafts"
(`:3206`).
**Chosen: send.** A draft never sent scores zero under the rule whose sanction is explicit,
while sending costs nothing if the draft reading was intended. `draft` remains a rehearsal
mode.

**2. `[Number of Agents]` appears twice in Appendix F.** `:3484` is "number of players in the
race | 2" and `:3540` is "number of agents in a series against an opponent | 6". The template
separately carries `num_games: 1`.
**Chosen: 6 sub-games per series**, reading the second row's own description. Reading either
of the others would have produced a series of 2 or of 1.

**3. `schema_version`.** Adding rule 53's `github_commit` changed the required field set, and
`M7-024` asks that a schema change be visible. Every inspected template shows
`schema_version: 1.1`, and `U-019` leaves that provenance unresolved.
**Chosen: hold at 1.1** and pin a digest of the required field set instead. Emitting an
unobserved number would invite a peer matching on `1.1` to refuse our declaration — a real
cost paid against an open question.

**4. Which artifacts must be committed.** Appendix F obligation 4 mandates the *config*; the
log has no explicit commit duty but is needed for the Replay threshold (rule 20); the result's
duty is email (rule 51).
**Chosen: commit configs, retain logs and results.** An earlier version of `games/README.md`
justified this on the grounds that committing logs would publish nonces — **that reasoning was
wrong** and is corrected there. Rule 18's secrecy expires at end of game (`inst/:1136`).

**5. The scent decay factor (`C-014`).** The book's prose (ch. 4.3, p.43) says $(1-\rho)$ at
$\rho = 0.10$ means the existing scent "is **reduced by 90%**". The formula printed beside it
says the opposite: $(1-\rho) = 0.90$ *retains* 90% and reduces by 10%.
**Chosen: the formula.** Rule 23's lock is taken over the formula, and the prose reading
decays ten times too fast — erasing the history trail the mechanism exists to leave.
`test_scent_regression.py` pins $0.9\tau + \Delta\tau$.

**6. The direction of $\rho$ (`C-015`).** The book (ch. 4.4, p.46) says raising $\rho$ toward
1.0 would leave the board "**saturated** with scent". Reversed: $\rho \to 1.0$ drives
$(1-\rho) \to 0$, so scent vanishes almost immediately; saturation is what $\rho \to 0$
approaches.
**Chosen: the arithmetic.** Sensitivity sweeps run in the correct direction.

> **How this list was wrong, and how to keep it right.** It held four entries until
> 2026-08-07. `C-014` and `C-015` had been in `docs/SPECIFICATION_CONFLICTS.md` since M6 and
> were never promoted here, so a row reading "disclose **every** book contradiction relied
> on" was marked done against an incomplete list. The register is the source; this section is
> a view of it. **Before closing `M9-011c` again, diff the two** — every `RESOLVED / BOOK
> ERROR` or `CONFIRMED DISTINCTION` entry the code relies on belongs in both.

## Things worth knowing that are not rows

* **Local green is not green.** Two M9 batches were reported complete with CI red. The
  history scanner was passing on a shallow clone — 441 objects where a full clone has 1744,
  printing "0 findings". Check `gh run list` before believing a gate.
* **Mirroring means re-authoring.** `THIEF-002` forbids this repository reading the Cop's
  code. Where both solve the same problem, the design travelled and the bytes did not — and
  the differences are deliberate (this repo's `verify` raises where the Cop's returns a bool).
* **The secret scanner has caught two real problems**, both fixed at the source. Nothing in
  either repository is allowlisted. The one reviewed history finding is pinned by blob SHA,
  which suppresses exact reviewed bytes and nothing else.

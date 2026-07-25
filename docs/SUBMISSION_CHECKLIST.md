# Submission Checklist

Unchecked boxes are future release evidence, not proof of an unknown requirement.

## Repository and release

- [x] Separate Cop and Thief repositories with reciprocal links (`SR-001`, `SR-002`).
- [ ] Both final repositories are accessible to `rmisegal@gmail.com` (`SR-003`,
      `AF-020`).
- [ ] Independently run frozen uv install, tests, Ruff, size, and secret gates.
- [ ] Create the annotated `v1.0-submission` tag at the reviewed revision (`SR-007`).
- [ ] Complete all six README academic-report components (`SR-008`).

## Contract and game evidence

- [ ] Accepted shared game config is byte-identical on both peers (`AE-011`).
- [ ] Contract manifest hashes match both repositories.
- [ ] Each official series contains six sub-games (`AF-018`).
- [ ] Legal-move, barrier disclosure/capture, trapped capture, scoring, scent,
      commit-reveal, timeout, and watchdog tests pass.
- [ ] Live GUI shows local truth only; replay verifies captured transcript.

## Official artifacts and reporting

- [ ] `declaration_<game_id>.json`
- [ ] `config_<game_id>_g<NN>.json`
- [ ] `log_<game_id>_g<NN>.json`
- [ ] `result_<game_id>.json`
- [ ] Template key presence and all later-proven schema constraints validate.
- [ ] Each peer automatically sends its own agreed final JSON attachment to
      `rmisegal+uoh26finalgame@gmail.com`.
- [ ] Final-report email contains no free-text report body (`AE-032`, `AF-020`).
- [ ] Git commit identifiers, tokens, mutual hashes, and confirmations match the
      accepted artifact contract.

## Security and provenance

- [ ] No `.env`, credentials, tokens, private keys, private TOML, or nonces are tracked.
- [ ] No substantial lecturer-simulator source is copied without an accepted
      license/provenance decision (ADR-0008).
- [ ] Current dated Moodle/lecturer instructions are reviewed before final release.
- [ ] Team/group/member identifiers and the required team code are verified.

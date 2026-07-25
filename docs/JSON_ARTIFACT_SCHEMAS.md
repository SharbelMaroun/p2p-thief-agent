# Official JSON Artifact Templates

Status: directly inspected key-presence evidence from the supplied `Json-examples/`
directory.

Source directory supplied for this audit: external
`SimulatorEXM-Repo/Json-examples/` (the templates are not copied into this repository).

The four JSON files parse successfully. They prove that the listed keys are present in
the inspected examples. They do not by themselves prove requiredness, optionality,
types, enums, bounds, additional-property behavior, or every nested shape (`U-019`).
Their populated one-sub-game values do not override Appendix F's fixed six-sub-game
series. Fields absent from Appendix F, including
`pheromone_min_center_intensity`, remain template/example fields without a confirmed
gameplay value.

Observed SHA-256 values:

- declaration: `f0f54ada41b831fc666d18ba0605f656ec4ac21160a85653553bda8e574543e4`
- agreed config: `4e7778d88bf53aa2d4dad0ad09c64764149d3ed0e521e578e77a3ab75773cba1`
- game log: `00e783628585e85d9f7716faf337917090d5e4a5530d4bd10c239647002e71c2`
- final result: `397bf9f00cf5aa4dfc609b6add10336d267056f8c2ef333e4b32a03a85d8d204`

## `1-pre-game-declaration.json`

Top level: `_schema`, `schema_version`, `declaration_type`, `game_id`, `game_uid`,
`links`, `timezone`, `game_started_at`, `game_ended_at`, `num_sub_games`,
`max_tokens_per_game`, `groups`.

Each group: `group_id`, `group_name`, `members`, `repos`, `mcp_servers`, `llm_model`,
`hardware_spec`, `signature`.

Hardware: `cpu_type`, `cpu_freq_mhz`, `cpu_cores`, `ram_gb`, `gpu_model`, `vram_gb`.

## `2-agreed-config.json`

Top level: `_schema`, `schema_version`, `_note`, `agreed_between`, `board_and_agents`,
`world`, `movement_and_barriers`, `scoring`, `pheromones`, `network_and_league`,
`rate_limiter_gatekeeper`, `game_id`, `game_uid`, `sub_game_number`, `links`,
`config_name`, `config_sha256`.

The section key sets are:

- `board_and_agents`: `grid_size`, `num_agents`, `thief_start`, `cop_start`,
  `axis_origin_corner`, `axis_start_index`, `_axis_note`.
- `world`: `_note`, `map_area`, `hint_max_words`, `_hint_max_words_note`.
- `movement_and_barriers`: `move_set`, `max_barriers`, `max_moves`,
  `survival_threshold`.
- `scoring`: `capture_cop`, `capture_thief`, `survival_cop`, `survival_thief`,
  `tie_score`, `technical_loss`.
- `pheromones`: `pheromone_center_intensity`, `pheromone_decay`,
  `pheromone_grid_size`, `pheromone_min_center_intensity`.
- `network_and_league`: `response_timeout_sec`, `watchdog_timeout_sec`, `num_games`,
  `diversity_reward`, `min_games_to_pass`, `max_games_per_team`,
  `token_budget_per_series`.
- `rate_limiter_gatekeeper`: `requests_per_minute`, `concurrent_requests`,
  `retry_backoff_sec`, `max_retries`, `queue_depth`.

## `3-game-log.json`

Top level: `_schema`, `schema_version`, `game_id`, `game_uid`, `links`, `summary`,
`records`, `mutual_agreement`.

Summary: `sub_game_number`, `group_id`, `role`, `opponent_group_id`, `result`,
`winner_role`, `steps`, `timezone`, `started_at`, `ended_at`, `duration_seconds`,
`tokens_total`, `audit`.

Each ordinary record contains `payload`, `nonce`, and `commit`. An ordinary move payload
contains `step`, `state`, `position`, `move`, `intent`, `verdict`, `hint`,
`prompt_discussion`, `model`, `tokens_step`, `tokens_total`, `response_seconds`, and
`random_move`. Step 0 has a distinct system-spec payload.

Mutual agreement: `opponent_group_id`, `sha256`, `confirmed`.

## `4-final-result.json`

Top level: `_schema`, `schema_version`, `report_type`, `game_id`, `game_uid`, `links`,
`timezone`, `groups`, `num_sub_games`, `sub_games`, `final_result`,
`mutual_agreement`.

Each sub-game: `sub_game_number`, `roles`, `started_at`, `ended_at`, `result`,
`winner_group`, `tie`, `github_commit`, `tokens`, `score`, `log_files`, `audit`.

Final result: `total_score`, `sub_games_won`, `ties`, `winner_group`, `series_tie`,
`tokens_total_series`.

Mutual agreement: `sha256`, `confirmed`.

## Remaining boundary

These templates confirm JSON artifact structure, not exact MCP wire messages or
simulator behavior. Exact MCP tool calls/messages and any behavior inferred only from a
generated match remain `UNKNOWN`.

Every inspected template carries `schema_version: 1.1`; the book's Appendix B example
uses `1.2`. This unresolved discrepancy is `C-008`/ADR-0003 and must not be silently
normalized.

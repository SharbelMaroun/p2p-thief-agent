# Official JSON Artifact Templates

Status: directly inspected from the supplied `Json-examples/` directory.

Source directory supplied for this audit: external
`SimulatorEXM-Repo/Json-examples/` (the templates are not copied into this repository).

The four JSON files parse successfully. They establish the artifact structure and key
sets below. Their populated values are examples from a generated one-sub-game match;
they do not override Appendix F. In particular, the example's `num_games: 1` and
`num_sub_games: 1` do not replace Appendix F Table 18's fixed six-sub-game series.
Fields not present in Appendix F, including `pheromone_min_center_intensity`, are schema
fields or example values only unless separately confirmed by a binding source.

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

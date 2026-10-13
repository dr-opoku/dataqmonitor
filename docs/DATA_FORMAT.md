# Input and configuration

## CSV extract

UTF-8 CSV with one nonempty, unique header per column. Cells and headers are trimmed; empty lines are skipped. Each nonempty record must have exactly the header's field count. Header-only input is valid and means no observations. Inputs are limited to **5 MiB and 50,000 records per CSV**; standard-library CSV field-size limits also apply. Record numbers refer to parsed data records, starting at 1, not physical lines in multiline CSV.

Example synthetic extract:

```csv
record_id,source,updated_at,amount,status
D001,synthetic_supplier,2026-10-13T10:00:00Z,125,ready
```

Timestamps must have an explicit timezone, preferably UTC `Z`. A naive timestamp is invalid. Numeric rules reject blanks, invalid numbers, NaN, and infinity. Category matching is exact and case-sensitive after trimming. Column names in configuration must match the trimmed headers exactly.

## Fetch observations

Optional, separate CSV:

```csv
attempted_at,success
2026-10-13T11:00:00Z,true
2026-10-13T11:30:00Z,false
```

`success` accepts true/false or 1/0, case-insensitively. Timestamps determine the lookback window. Invalid timestamps, invalid flags, or future attempts beyond tolerance make availability unknown and create a finding. Valid older attempts are counted as outside the window. No HTTP requests or remote connectors are performed.

## Configuration

A JSON object. Unknown and duplicate keys are rejected; numeric limits must be finite. You may supply only the settings you need.

| Key | Default | Meaning |
| --- | --- | --- |
| `dataset_name` | Local dataset | Nonempty report label |
| `expected_rows` | null | Positive expected record count for the supplied extract |
| `required_columns` | null | Null: all headers; list: selected columns; empty list: disable required-cell coverage |
| `key_columns` | [] | Composite record key; subsequent complete duplicates fail consistency |
| `timestamp_column` | null | Column used for freshness |
| `max_age_hours` | 24 | Positive maximum age |
| `future_tolerance_minutes` | 5 | Nonnegative tolerance for clock skew |
| `min_availability_attempts` | null | Positive local minimum of valid in-window observations; null leaves availability verdict unknown |
| `evidence_context` | {} | Optional purpose, population, sampling_method and reference_basis declarations; each string up to 2000 characters or null |
| `availability_window_hours` | 720 | Positive lookback for fetch observations |
| `numeric_ranges` | {} | Per-column `min` and/or `max`, inclusive |
| `allowed_values` | {} | Per-column nonempty list of allowed strings |
| `thresholds` | all 95 | Minimum percentages for completeness, freshness, availability, consistency |

Missing configured columns produce a finding and their cells fail the corresponding checks. Required cells check nonemptiness; they do not infer meaning or validate types unless a rule does so. `expected_rows` uses distinct complete composite keys if keys are configured; otherwise it uses raw record count. Extra records cannot lift record coverage above 100%.

[Bundled complete example](../dataqmonitor/fixtures/config.json).

## Report contract

`status` is `ok`, `attention`, or `unknown`. `checks` contains the four named measurements. Each value is a percentage or JSON null; its `evidence` gives counts and parameters. `findings` gives codes, messages, and optional aggregate details. `schema_version` is `2.0`. Consumers should tolerate additional fields and use names rather than positional order.

JSON errors use `status: error` and `error: {code, message}`. They are printed on stdout even when `--output` was requested. Normal reports go to the explicit output path or stdout. The optional MCP SDK reports raised invalid-input exceptions through its normal tool-error mechanism.

### Evidence contract 2.0

Each check exposes `value`, `threshold_status`, `evidence_status`, `status`, `threshold` and `reason_codes`. See [field semantics](EVIDENCE_POLICY.md#reading-the-report) and the [normal-report JSON Schema](report.schema.json). The same typed shape is exposed as the optional MCP output schema. Error objects are a separate CLI contract; MCP tool errors are separate from normal reports.

The report adds `decision`, `policy` and `provenance`. Read `decision.required_checks` for overall scope. Context is caller-declared and is not validated against the world. Reports expose supplied policy/context, column and category names; omit identifying details if they are unnecessary.

Migration from 1.0: check names and observed values remain accessible, but verdict rules are stricter. A diagnostic without a configured target no longer silently receives `ok`. Missing evidence stays unknown; insufficient observations can still have a passing numeric threshold comparison. Check schema version explicitly before relying on these meanings.

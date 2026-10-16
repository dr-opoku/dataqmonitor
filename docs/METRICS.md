# Measurement definitions

Let N be the supplied row count. All calculations use only the provided extract and optional fetch observations.

## Completeness

- Cell coverage = 100 × nonempty required cells / required cells.
- Record coverage = min(100, 100 × observed records / expected records), when expected records are configured.
- Observed records are distinct complete keys when keys are configured; otherwise N.
- Score = the smaller available coverage component.
- No rows, or no configured/available component, means unknown.

A duplicate can leave required cells complete while reducing expected-record coverage. If there is no expected count, the tool cannot detect missing whole records. Required-cell nonemptiness does not establish correctness.

## Freshness

100 × valid recent rows / N. A timestamp is recent if its age is at most `max_age_hours` and it is no further in the future than the tolerance. Missing, malformed, too-future, and stale timestamps do not count as recent. No rows or no timestamp column means unknown. `oldest_age_hours` considers valid timestamps within the future tolerance.

## Availability

100 × successful attempts / valid attempts within the lookback. The window includes attempts whose age is between negative future tolerance and `availability_window_hours`. No attempts means unknown. Below `min_availability_attempts`, show the measured percentage with an unknown verdict. If this minimum is null, evidence is `not_configured` and the verdict remains unknown. Any malformed observation makes the score unknown, preventing silently optimistic exclusion. Outside-window valid observations are excluded and counted separately.

This is observed request success, not service uptime. Four demo attempts are four observations, not a service-level estimate.

## Consistency

100 × rows passing every configured key/numeric/category rule / N. Complete subsequent duplicate keys, incomplete keys, invalid or out-of-range numeric cells, and unrecognized categories fail. A row failing several rules counts once in the denominator, while each rule has its own violation count. The first complete occurrence of a duplicate key passes the uniqueness rule; subsequent occurrences fail.

No rules or no rows means unknown. This check covers declared rules; it cannot discover semantic contradictions or verify the source of truth.

## Status

A numeric threshold comparison is attention below its minimum; equality passes. A check verdict follows that comparison only when its evidence meets the local rules. Otherwise the verdict is unknown. Availability additionally requires a declared minimum observation count. Overall attention takes precedence if any check is attention or any finding exists. Otherwise any unknown check makes overall unknown. Overall is ok only when all four measurements are available and meet their expectations.

The report exposes the denominators. Scores are neither a certification nor a substitute for a domain owner's judgment.

See [evidence policy](EVIDENCE_POLICY.md) for separate threshold/evidence/verdict semantics and cross-domain examples. Numeric comparisons use unrounded values; report check values are rounded to six decimal places.

## Display precision

Text and HTML retain the check value recorded in JSON (rounded to six decimal places), without further two-decimal rounding. Threshold comparisons use the unrounded measurement; very near a threshold the displayed value can still coincide with the limit. Inspect threshold status and reason codes rather than inferring the verdict from presentation alone.

All current Data Quality Monitor checks use `threshold.basis="point_estimate"`. The shared-shaped report vocabulary also permits `wilson_lower_bound`, but this analyzer never emits it and offers no Wilson-bound configuration.

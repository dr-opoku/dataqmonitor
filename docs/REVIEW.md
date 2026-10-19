# Showcase stress review — 15 October 2026

**Status update — 19 October 2026:** this document records the earlier review. The owner-selected license is now included as [LICENSE.md](../LICENSE.md); earlier licensing remarks describe the historical review scope. See [current findings and corrections](PUBLICATION_STATUS.md) and [usage guidance](PROJECT_STATUS.md).

## Purpose and sequence

Improve visible usefulness, first-run clarity, evidence discipline and professional reference value. The existing source was inspected, baseline tests and adversarial probes were recorded, and the proposed plan was externally reviewed **before repository changes**. The baseline commit was `c34ed58fb3057df7c4a482cbd801fd6602605654`.

One AGY review per repository was requested with **`gemini-3.8-flash-high`**, the adapter's Gemini 3.8 Flash (High) selector. The three repositories were mounted read-only for the reviewer. File hashes remained unchanged at the pre-edit gate. This records the requested selector; backend model identity was not independently attested.

The reviewer assessed a curated plan/source packet, not every helper or fixture, and did not execute tests. Its recommendations were checked against actual code. This was not a second comprehensive security audit, a market validation or a CV verification. Full local review records are kept outside the repositories; the implementation decisions follow below.

## Accepted findings and repairs

- Protect input/config/attempt files from output collisions, including symbolic and hard links.
- Add deterministic supplier case and independent fictional ID manifest; explain count-versus-identity limitation.
- Provide defensive consumer, short entry, linked navigation and reproducible tests.

## Findings bounded or rejected after source inspection

- No global ban on the approved third repository name llm-eval: naming restrictions apply to the two monitor names.
- No empty-data repair: _support.check already supplies NO_OBSERVATIONS for absent values.
- No blanket TypeError/KeyError catch: timestamp/CSV validation already rejects the cited inputs.
- Historical review decision: do not invent evaluation permission before an owner-selected license is supplied. Current permissions are recorded in LICENSE.md.

## International examples informing presentation

- [Oracle](https://github.com/steipete/oracle): make the first useful command and a local preview legible.
- [Evidently](https://github.com/evidentlyai/evidently): connect a small example with inspectable reports and tests.
- [Promptfoo](https://github.com/promptfoo/promptfoo): keep configurations, evaluation and repeatable checks visible.
- [AGENTS.md](https://agents.md/): provide concise repository instructions for coding agents.

These references informed the entry point, examples and verification. They do not establish a universal showcase standard, explain why a specific repository receives stars or prove demand for this code.

## Professional relevance

The reference can support a conversation about specifying a decision, defining evidence, coordinating correction/acceptance and making limits inspectable by technical and business stakeholders. It does not establish enterprise rollout experience, organizational adoption, savings or proprietary platform capability. Those claims need separate project evidence. No private platform implementation is required or included.

## Additional local regression finding

The report producer compares unrounded measurements and displays six decimals. The example consumer therefore permits either consistent verdict within the display-rounding interval at a threshold. Tests cover these boundaries and reject clearly inconsistent comparisons. The consumer cannot independently recompute an exact comparison from rounded display values.

## Verification and remaining decisions

See [verification results](VERIFICATION.json), [the action plan](ACTION_PLAN.json) and [project status](PROJECT_STATUS.md). Automated tests and saved-report replay check the implementation and its declared examples. They cannot establish label truth, representative sampling, model authenticity or deployment suitability.

At the time of this review, licensing, contribution rights, visibility and release were owner decisions. The license has since been supplied; current permissions and remaining policy choices are recorded in [project status](PROJECT_STATUS.md).

## Second pre-edit review — 15 October 2026

Before this round of repository edits, baseline tests passed and tracked-file hashes matched the stated baseline commit. Two complete static reviews were obtained: **G = AGY `gemini-3.8-flash-high`**, **C = Claude Code `claude-sonnet-5-5`**. These are requested selectors, not independent backend attestations. Claude received source and tests; AGY omitted test source and saved example JSON to fit its interface. Neither reviewer executed tests. An initial AGY CLI invocation failed before model execution; its corrected invocation completed. Neither final review was truncated.

Local runtime counterexamples were recorded before repairs. Model findings are suggestions checked against actual behavior, not automatically accepted evidence. X denotes a finding transferred from the sibling review and reproduced here. The earlier sections above remain historical.

| ID | Reviewer finding | Decision | Source check and reason | Verification |
| --- | --- | --- | --- | --- |
| C1 | Medium: manifest described as prospectively independent. | Accepted with corrected chronology | The 12-row configuration and CSV fixtures predate the explanatory manifest. CASE_STUDY, manifest and current plan now say so. The identity-reconciliation limitation stays explicit. | `tests/test_case_study.py` |
| C2 | Low: current review decisions not inspectable in the repository. | Accepted | Append this per-finding record and current plan; preserve the earlier review as history. | `docs/REVIEW.md; docs/ACTION_PLAN.json` |
| C3 | Low: own-data command uses synthetic packaged policy. | Accepted | Point to an edited local copy and name the keys, including evidence_context. | `README.md, Use your own data` |
| C4 / G1 | Low: unreachable consumer branch and unused Wilson vocabulary. | Accepted / bounded | Remove the constant alternative branch. Document that current checks emit only point_estimate; no new statistical metric or contract break. | `tests/test_stress.py; tests/test_review_regressions.py` |
| C5 | Low: unspecified operating-system support. | Bounded | State verified Linux and POSIX commands; Windows unverified. Do not claim portability based solely on standard-library use. | `README.md` |
| G2 | Low: empty output path allegedly raises an unhandled OSError. | Rejected | Reproduced against baseline: argparse creates Path("."); the existing OSError handler returns structured INVALID_INPUT and exit 2. Whitespace is a valid filename on the verified platform. No speculative validation patch. | `Pre-edit CLI reproduction; dataqmonitor/__main__.py` |
| G3 | Low: two-decimal human display can obscure a threshold. | Accepted with stronger remedy | Retain the six-decimal JSON check value in text/HTML, rather than merely documenting extra rounding. No threshold change. | `tests/test_review_regressions.py` |
| X1 | Confirmed in sibling review: excessively nested config escapes the input-error contract. | Accepted after local reproduction | Reproduced RecursionError on a 100,000-level, sub-limit JSON object. Convert only decoder RecursionError to ValueError. | `tests/test_review_regressions.py` |

Full prompts, responses, failed invocations and pre-edit hashes are retained in the private audit workspace; this table contains the public decision trail without host details. See [the current action plan](ACTION_PLAN.json) and [verification](VERIFICATION.json). Review and tests establish bounded example behavior, not independent data truth, enterprise outcomes or license rights.

# Case study: accept, repair or investigate a supplier extract

**Everything in this case is synthetic.** The two CSVs are constructed before/after states, not a recorded production incident or evidence that a repair was executed.

## The declared fictional requirement

A fictional supplier contract expects IDs D001–D012, required fields, timestamps no older than 24 hours, amounts between 0 and 10,000 and a declared status vocabulary. The [fictional manifest](../examples/expected-deliveries.json) supplies the expectation of **12 deliveries**. That denominator is a business requirement, not the observed CSV row count. The availability example requires four observations in its declared lookback window.

The manifest was added after the existing CSV fixtures to explain the scenario's already configured expectation; it is not evidence of an independently established or prospectively frozen requirement. Its 12-ID population is a declared fictional premise. In a real assignment, an accountable upstream owner should establish and version that expectation before assessing the delivery. The manifest does not independently validate a real source. The reference time is 13 October 2026, 12:00 UTC. No historical operating period is inferred from that timestamp.

## Observed before and constructed after

| Check | `broken` | `healthy` | Declared target |
| --- | --- | --- | --- |
| Completeness | 7 distinct IDs / 12 expected = 58.33%; required cells 39/40 | 12/12 IDs and 60/60 cells = 100% | At least 95% for the weaker of record/cell coverage |
| Freshness | 5/8 rows = 62.5% | 12/12 = 100% | At least 95% |
| Fetch availability | 2/4 successful attempts = 50% | 4/4 = 100% | At least 95%; minimum four attempts |
| Consistency | 5/8 rows pass all configured rules = 62.5% | 12/12 = 100% | At least 95% |
| Aggregate | `attention` | `ok` | Required checks must all be supported and met |

The eight broken rows contain a repeated D006 and no D008–D012. One stale, one invalid and one future timestamp stay in the freshness denominator. Three rows fail consistency; violations overlap, so adding violation counts would overcount failing rows.

Inspect the [before text](../examples/broken.txt), [before JSON](../examples/broken.json), [after text](../examples/healthy.txt) and [after JSON](../examples/healthy.json). Download/open [before HTML](../examples/broken.html) or [after HTML](../examples/healthy.html) locally; GitHub's source view does not render them as a live demo.

## Responsibility and practical consequence

| Observation | Responsible role in a real case | Next step before acceptance |
| --- | --- | --- |
| Missing and repeated IDs | Supplier/data contract owner | Reconcile the expected ID set with delivered IDs; agree corrected delivery |
| Invalid, old or future timestamps | Source system owner | Establish timestamp semantics and clock/window policy; correct and rerun |
| Invalid amount/status | Business rule owner | Confirm the rule, investigate the records and supply corrected data |
| Failed fetch observations | Integration operator | Investigate acquisition independently of content quality |

In this fictional process an `attention` result sends the batch for investigation; it does not authorize deletion, replacement or a business transaction. The healthy state permits consideration against these local rules only. The responsible process owner decides what can proceed.

## Deliberate limitations

- **Count is not identity reconciliation.** Replacing D012 with an unexpected but otherwise valid ID preserves twelve distinct keys and can pass the engine's completeness check. The manifest is explanatory evidence; the core does not enforce a manifest join. The regression test explicitly demonstrates this limitation.
- Twelve rows and four fetches are illustrative rules, not representative evidence or a reliability estimate. A one-fetch 100% observation remains `unknown` under the four-attempt requirement: [small-sample report](../examples/small_sample.txt).
- Snapshot freshness differs from source truth, continuous uptime, transactional integrity and permission to act.
- A real adaptation needs a trusted population definition, time window, accountable source owner, representative observations and a documented consequence for each failed/unknown check.

The transferable contribution is connecting a business expectation, an inspectable implementation and a responsible next step. It can support a scoped transformation assessment; it does not prove an enterprise rollout or savings.

## Reproduce without a model or network

```bash
python3 -m dataqmonitor demo
python3 scripts/reproduce_examples.py --check
python3 -m unittest discover -s tests -v
```

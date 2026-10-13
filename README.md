# dataqmonitor

**Is this incoming CSV usable enough to move work forward?**

A small, local monitor for completeness, freshness, observed fetch availability, and rule consistency. It turns a supplied extract into a readable report with counts and explicit thresholds. No AI model, account, database, or network connection is needed for the core tool.

### Related example

[`resqmonitor`](https://github.com/dr-opoku/resqmonitor) shows a complementary decision: whether supplied categorical outputs meet declared accuracy and cost expectations against reference labels. **Dataq examines inputs; Resq examines results.** Both keep observed values separate from adequately supported verdicts. They are independent examples; no software integration is required.

## What does the evidence support?

One successful fetch is measured as **100%**, while its availability verdict remains **unknown** when the declared minimum is four.

Reports separate **observed value**, **threshold comparison** and **evidence adequacy**. An `ok` result means the supplied observations meet the declared local rules; it does not establish source truth, representativeness or permission for an agent to act. See the [concrete cases and domain mappings](docs/EVIDENCE_POLICY.md) and [dated standards review](docs/STANDARDS_REVIEW.md), covering 29 July–13 October 2026.

## Try it in one command

Requires Python **3.11 or newer**. From this repository directory:

```bash
python3 -m dataqmonitor demo
```

The default demo contains missing records, stale timestamps, a duplicate key, invalid values, and failed fetches. All data is synthetic. The demo uses **13 October 2026, 12:00 UTC** as its reference time, so results do not age with the calendar.

```bash
python3 -m dataqmonitor demo --scenario healthy
python3 -m dataqmonitor demo --scenario unknown
python3 -m dataqmonitor demo --scenario small_sample
python3 -m dataqmonitor demo --format json
python3 -m dataqmonitor demo --format html --output outputs/data-quality.html
```

Open the generated HTML file locally. It contains no external assets or scripts.

| Scenario | Designed to illustrate |
| --- | --- |
| `healthy` | All 12 expected records, fresh timestamps, valid rules, four successful fetch observations |
| `broken` | Seven distinct keys instead of 12; defective timestamps, values, and two failed fetch observations |
| `unknown` | A valid header with no observations; every measurement remains unknown |
| `small_sample` | One valid record and one successful fetch; 100% observed availability with an unknown verdict |

**Unknown is a first-class result.** It means the evidence or rule is missing. An empty extract cannot receive a healthy score.

## Use your own data

Copy the bundled configuration and change the expectations for your extract:

```bash
python3 -m dataqmonitor check local_data/feed.csv \
  --config dataqmonitor/fixtures/config.json \
  --attempts local_data/fetch-attempts.csv \
  --format html --output outputs/feed-report.html
```

`--attempts` is optional. Without observations, availability is unknown. Set `min_availability_attempts` to declare the evidence minimum; its default is null and cannot yield a positive verdict. `--at 2026-10-13T12:00:00Z` sets a reproducible evaluation time; otherwise a real check uses current UTC. No data is fetched by this tool.

For a minimal start, use `check your.csv` without a configuration. This measures nonempty cells; timestamp, fetch, and consistency checks remain unknown until evidence and rules are provided. Filter the intended period before checking it.

| Measurement | Practical question |
| --- | --- |
| Completeness | Do we have the expected distinct records and required cells? |
| Freshness | How many supplied rows have valid, recent timestamps? |
| Availability | How many observed fetch attempts succeeded in the lookback window? |
| Consistency | How many rows satisfy every configured key, numeric, and category rule? |

See [input and configuration](docs/DATA_FORMAT.md) and [metric definitions](docs/METRICS.md).

## People, scripts, and agents

The same calculations serve three interfaces:

- Text for a terminal; JSON for automation; HTML for sharing a local report.
- Python: `from dataqmonitor import analyze`, then `analyze(csv_text, config, attempts_csv=attempts_text, at=reference_time)`.
- Optional MCP over local stdio, with tools accepting CSV text rather than paths.

JSON reports use schema **2.0** and have `schema_version`, `status`, `summary`, `checks`, `findings`, and `notes`. Each check includes value, threshold status, evidence status, verdict and reason codes. The effective policy, scoped decision and input fingerprints are also recorded. See the [report schema](docs/report.schema.json) and [concise agent guidance](llms.txt). [showcase.json](showcase.json) is project metadata, not a commerce or interoperability standard.

A completed report exits **0**, including attention or unknown results. Add `--require-ok` to exit **1** unless overall status is `ok`. Invalid input or an execution error exits **2**; JSON mode returns an error object on stdout. Argument-parser errors use argparse's stderr output.

### Install a command or MCP support

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/dataqmonitor demo
```

The core has no runtime dependencies. The optional MCP adapter uses the official [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/servers/tools/):

```bash
.venv/bin/python -m pip install '.[mcp]'
.venv/bin/dataqmonitor serve
```

Example client entry, with the executable path adapted to your checkout:

```json
{
  "mcpServers": {
    "dataqmonitor": {
      "command": "/absolute/path/to/dataqmonitor/.venv/bin/dataqmonitor",
      "args": ["serve"]
    }
  }
}
```

Tools: `inspect_data(csv_text, config?, attempts_csv?, at?)` and `demonstrate_data_quality(scenario?)`. They do not access caller-supplied filesystem paths, contact services, or call models. The demo tool reads only bundled synthetic fixtures. If an agent client is remote, supplying CSV text to that client can move data beyond your local machine; choose the client accordingly.

## What this demonstrates

A compact example of translating business expectations into inspectable data gates: what is expected, what was observed, and where a decision lacks evidence. See [showcase context](docs/SHOWCASE.md).

This is a snapshot analyzer, not a scheduler, connector suite, data catalog, or proof of factual correctness. Thresholds are user expectations, not universal quality standards. Fetch success is not time-based uptime. Reports contain counts, column names, and record numbers; they do not include raw row values. Use synthetic data when sharing examples.

The code is self-contained and newly written for this repository. No private platform implementation is required.

## Repository map

```text
dataqmonitor/engine.py       calculations and configuration validation
dataqmonitor/_support.py     bounded CSV/JSON input handling
dataqmonitor/report.py       text, JSON, and standalone HTML output
dataqmonitor/fixtures/       synthetic inputs and example configuration
dataqmonitor/mcp_server.py   optional, thin local adapter with typed output schema
docs/                       data contract, metrics, showcase context
```

## Development checks

```bash
python3 -m unittest discover -s tests -v
```

Core checks use the standard library. With `.[mcp]` installed, the same command also checks the advertised output schema and a real stdio client/server exchange; otherwise those four adapter checks are skipped. Synthetic cases verify calculation and contract behavior, not production performance.

## License and release status

Initial showcase implementation. A redistribution license has not yet been selected. License selection is an owner decision before public release. Synthetic examples are illustrative and do not establish production performance.

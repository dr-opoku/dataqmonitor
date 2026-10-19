# Publication follow-up — 19 October 2026

## Scope and current status

This follow-up addresses the owner's request to correct the llm-eval decoder failure and remove obsolete license-pending statements. It follows a read-only publication audit and an independent Claude Code review requested with `claude-fable-5-1`. The actual review completed without a fallback selector and included its ending. This records the adapter's selector, not independent attestation of the model provider or backend. The external reviewer assessed supplied material; implementing-agent checks are recorded separately. No model was called by regression tests.

The owner-selected [Noncommercial Local Use License 1.0.0](../LICENSE.md) is now included unchanged. README, agent guidance, project metadata and package metadata identify the same license. This resolves the missing-file and inconsistent current-status findings. It does not establish legal enforceability, production fitness or permission to publish the repository. Earlier dated review/test records retain their historical scope; see the dated follow-up in [verification](VERIFICATION.json).

## Remaining rights and presentation decisions

- **Generated reports:** HTML templates, styles and software-authored explanatory text are embedded in reports. The current output clause does not expressly permit sharing protected embedded material. A narrowly scoped report-output exception could resolve this without licensing redistribution of the tool; it has not been adopted.
- **Business evaluation:** the present license treats evaluation preparing a commercial application as commercial use. A company cannot infer free execution rights from a runnable demo. A limited evaluation exception would require an explicit additional grant; none is implied here.
- **Contributions:** private qualifying local modifications are permitted. Public modified copies and patches containing protected repository material need permission beyond the reserved platform/statutory rights. Contribution workflow and any commercial relicensing permission should be agreed before accepting code. Issue reports with synthetic reproductions are welcome.
- **Commercial delivery:** no published price, checkout or automated license fulfillment exists. An inquiry or payment alone does not grant rights. The repository is source-available, not open source.

## Repository-specific findings

### Corrected

- The README no longer claims that reports contain no raw row values whatsoever. Reports omit full source rows and record IDs, but availability evidence can expose first/last observed fetch timestamps. Review report metadata before disclosure.
- The HTML description now says local review, rather than implying an unrestricted right to share generated reports.

### Still present; presentation inconsistency

The generated report note in `dataqmonitor/engine.py` still says "not raw row values". This overstates the privacy boundary because first/last observed fetch timestamps can be included. The README now states the narrower guarantee accurately. The generated note and saved reports should be updated together in a separate change; no existing evidence or example output was altered in this follow-up.

### Still present; bounded improvements

- Optional MCP code imports `typing_extensions` directly, while the extra currently relies on the MCP SDK to supply it transitively. Declare it explicitly if this adapter is maintained independently of that dependency contract.
- Terminal output includes caller-supplied labels. Terminal control-character sanitization is not provided; treat untrusted report text accordingly. This is distinct from HTML escaping.

The examples remain synthetic; passing declared checks is not proof that the incoming data is factually true, representative or fit for a real downstream decision.

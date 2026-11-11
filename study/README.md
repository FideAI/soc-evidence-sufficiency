# Evidence sufficiency in AI cloud-log investigation

Research companion to Fide's [research perspective](publication/INSIGHT.md) and [technical note](publication/TECHNICAL-PAPER.md).

Fide studies what evidence people need before relying on AI. This perspective asks whether an investigator’s findings are supported by the records it actually received. The supporting experiments show that real record citations can accompany claims about unavailable fields in the tested setup. This package exposes those inputs, responses and scoring for scrutiny. Original-label Gemma explanations merely restated logged requests; their scored errors should not be treated as explicit success claims. The 24 included Splunk byte-only inputs repeat one single-record pattern, rather than providing 24 independent confirmations. It does not estimate operational prevalence or establish a general remedy.

This package lets a reader recompute all reported stage aggregates and independently rescore the included licensed-source subset. Python 3.11 standard library is sufficient. No model, account, API key or paid inference is required.

```bash
python3 scripts/reproduce.py
python3 scripts/test_semantics.py
python3 scripts/check_source.py
python3 scripts/audit_evidence.py
```

Run these commands from the package root after extracting the archive. The first command checks 996 decision rows and rescores 306 preserved Splunk responses against their exact inputs. The second tests ten scoring boundaries. The third downloads one pinned 160 KB public source file, checks its hash, reconstructs the 24 selected histories and verifies all 306 projected inputs. It never executes source content. The fourth command prints the 24 included Splunk examples in which a cited record explicitly withholds the error field but the answer describes that field as null. It checks the observed wording, not arbitrary factual accuracy. To work fully offline, supply the original file with `--source /path/to/cloudtrail.json`.

## Check one finding

Start with one selected example: `transfer|primary|gemma4:e4b-mlx|T19|volume_only|clarified`. It illustrates the published claim; it is not a random sample or an independent confirmation. The evidence file is unchanged from companion commit `235f6d3bfb8f85e844c6289f29888d54068c9a64`, with SHA256 `a18cc59123574c49c641e6feb8e0be35eebff364986153af54b5eee4b04fdc07`.

From this study directory (`study/` in the standalone repository), run:

```sh
python3 - <<'PYCODE'
import hashlib, json
from pathlib import Path
p = Path("data/splunk-replay.jsonl")
assert hashlib.sha256(p.read_bytes()).hexdigest() == "a18cc59123574c49c641e6feb8e0be35eebff364986153af54b5eee4b04fdc07"
wanted = "transfer|primary|gemma4:e4b-mlx|T19|volume_only|clarified"
row = next(r for line in p.read_text().splitlines() if (r := json.loads(line))["id"] == wanted)
print(json.dumps({"id": row["id"], "messages": row["request"]["messages"],
                  "response": row["response"]["message"]["content"]}, indent=2))
PYCODE
```

Read the instructions, supplied record and response together. Does record `E665d0c1d` contain the `null errorCode` value the answer claims? Our interpretation is that the value was explicitly withheld, so the claim is unsupported even though the complete source history reports success. Check that interpretation against the input rather than treating this explanation or a passing script as the verdict.

Return a short note with the package version or commit, response ID, claimed value, exact supporting or conflicting input, and your conclusion: supported, challenged or unresolved. Include any ambiguity you find and the command you used. For a Git checkout, `git rev-parse HEAD` records its revision; for a ZIP, include its SHA256. A discrepancy or a well-supported reason you cannot decide is useful. This is a check of one retained judgment, not fresh inference replication or proof that a review method works. The other 23 included examples can be inspected with `python3 scripts/audit_evidence.py`.

## What is included

- `publication/`: the research perspective and technical note, with working links to this package.
- `data/decision-ledger.json`: Fide-created categorical results for all 996 evaluated calls, including repeats. This is not 996 independent cases.
- `data/aggregates.json`: stage-specific totals. Never pool reused exploratory cases, repeats or overlapping challenge windows as fresh evidence.
- `data/splunk-replay.jsonl`: exact requests and model responses for 288 primary comparisons, 12 exact repeats and six formatting checks involving the 24 Splunk histories.
- `data/splunk-locators.json`: original row indices, event IDs and hashes linking the included normalized inputs to the pinned source.
- `data/contracts.json`: exact original and clarified instructions.
- `scripts/`: an offline reconstruction scorer and an optional pinned-source verifier.
- `MODEL-REPRODUCTION.md`: exact artifact identities and limits of fresh inference.
- `THIRD-PARTY-NOTICES.md` and `licenses/`: provenance and attribution for the included source transformations.

## Reproduction boundaries

The aggregate ledger permits arithmetic verification for the entire study. It does **not** independently establish source fidelity or reference validity for excluded sources. Full source-to-answer reconstruction is included for the Splunk subset only. The 690 other responses and their evidence remain in a separate private replay packet pending source export review. They are not silently replaced with synthetic records.

A different reader can rescore the retained responses without downloading any weights. Generating new responses from identical model packages is a separate task; the exact Gemma distribution is not currently available through the checked public digest endpoint. No fresh inference replication is claimed.

The original case selection, source qualification and frozen study protocols remain preserved by Fide. This extracted subset is not the full pre-inference artifact freeze. A companion file manifest identifies exactly this package.

## Licensing and release

Fide-authored code is MIT licensed; included Splunk-derived record material remains under Apache-2.0, with modifications described in the notices. This does not grant rights in upstream materials that are not included. No raw Ariel Cyber archives, OTRF metadata, full third-party blog, model weights or private host paths are distributed here. No subsequent action-verification experiment or its results are included in this package.

## Help investigate the question

Begin with the [single-finding check](#check-one-finding) above and report what the evidence supports. For a subsequent study, we welcome replications on other systems and shareable cases that could test whether explicit evidence checking improves on ordinary review. The useful comparison goes beyond the supplied field predicate to native logs, multi-record claims and unannotated missing fields. It measures unsupported findings corrected and justified findings wrongly withheld, with comparable evidence and computation, complete failure cases and an always-abstain baseline. These are proposed extensions, not results in this package.

To discuss work with Fide, email [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with the question and a description of what you could contribute. Do not send confidential logs or credentials. Keep new runs and case selections separate from the preserved results; retain null findings and counterexamples.

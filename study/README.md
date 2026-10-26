# Evidence sufficiency in AI cloud-log investigation

Research companion to Fide's [Insights article](publication/INSIGHT.md) and [technical paper](publication/TECHNICAL-PAPER.md).

The question: can an AI investigator cite a real record while claiming support from a field it was never shown? This package exposes the evidence and scoring behind our answer. It evaluates investigative findings, not containment or operational defense.

This package lets a reader recompute all reported stage aggregates and independently rescore the included licensed-source subset. Python 3.11 standard library is sufficient. No model, account, API key or paid inference is required.

```bash
python3 scripts/reproduce.py
python3 scripts/test_semantics.py
python3 scripts/check_source.py
python3 scripts/audit_evidence.py
```

Run these commands from the package root after extracting the archive. The first command checks 996 decision rows and rescores 306 preserved Splunk responses against their exact inputs. The second tests ten scoring boundaries. The third downloads one pinned 160 KB public source file, checks its hash, reconstructs the 24 selected histories and verifies all 306 projected inputs. It never executes source content. The fourth command prints the 24 included Splunk examples in which a cited record explicitly withholds the error field but the answer describes that field as null. It checks the observed wording, not arbitrary factual accuracy. To work fully offline, supply the original file with `--source /path/to/cloudtrail.json`.

## What is included

- `publication/`: the article and technical paper, with working links to this package.
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

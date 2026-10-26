# When an AI investigator fills in the missing evidence

**A real citation can accompany a claim about a field the model was never shown.** This Fide AI study tests that gap in controlled cloud-log reading tasks. It asks whether a model's conclusion is supported by the evidence available to it, rather than whether the hidden outcome happened to match its answer.

**Release candidate.** Prepared for review; the website article remains unpublished. Repository availability does not imply independent human acceptance of the methods or conclusions.

Read the [accessible article](study/publication/INSIGHT.md), the [technical paper](study/publication/TECHNICAL-PAPER.md), or go straight to [the preserved model inputs and responses](study/data/splunk-replay.jsonl).

## What the study found

Clearer evidence rules reduced unsupported conclusions in the selected transfer cases. But one model still cited existing record IDs while describing an explicitly withheld error field as null. Complete-record accuracy did not establish that the model knew when incomplete records were insufficient.

The main transfer used 25 histories. This repository includes 24 Splunk histories and the corresponding 24 examples of that unavailable-field assertion. The remaining OTRF history is outside the export pending redistribution review. These are controlled judgments by two local model installations, not a test of operational defender effectiveness.

## Reproduce in a few minutes

Use Python 3.11. No package installation, model weights, API key or paid inference is needed. Clone this repository, then run from its root:

```sh
git clone https://github.com/FideAI/soc-evidence-sufficiency.git
cd soc-evidence-sufficiency
python3 scripts/verify_release.py
python3 study/scripts/reproduce.py
python3 study/scripts/test_semantics.py
python3 study/scripts/audit_evidence.py
```

The first command checks the package hashes and local documentation links. The next commands reconstruct the result totals, rescore preserved responses, exercise ten scoring boundaries, and show the 24 included unavailable-field examples. They run offline. The explanation audit checks an exact observed wording pattern; it is not a general factuality classifier.

To verify every included input against the pinned public source:

```sh
python3 study/scripts/check_source.py
```

This downloads one 160,393-byte Splunk source file, verifies its SHA256, reconstructs the selected 24 histories, and checks all 306 projected inputs. It does not execute source content. For an offline check, use `--source /path/to/cloudtrail.json` with the original file.

## What can be checked here

| Evidence | Included | What it establishes |
| --- | --- | --- |
| Decision ledger | 996 evaluated calls, including repeats and exploratory work | Arithmetic reconstruction of stage totals; not 996 independent cases |
| Exact input/output replay | 306 responses for 24 Splunk histories | Rescoring the included responses against the inputs shown |
| Original and clarified instructions | Exact text | The intervention that was compared |
| Source locators and verifier | Pinned source revision, row hashes and transformation checks | Reconstruction of the licensed Splunk subset |
| Model identities | Recorded manifests and configuration | Which local installations produced the responses; not a guarantee of fresh inference replication |

The 690 other source-dependent replays are excluded because redistribution has not been cleared. Their categorical results are included for aggregate reconstruction, but this repository alone cannot validate their original evidence or answers. The paper explains source selection, dependence between cases, reused exploratory examples, and the small formatting diagnostic. No claim of broad defensive efficacy follows from these tests.

## Repository map

- [study/](study/README.md): the preserved companion package, including manuscripts, evidence and scripts.
- [PACKAGE-PROVENANCE.json](PACKAGE-PROVENANCE.json): the original archive fingerprint and all 21 extracted file hashes.
- [MODEL-REPRODUCTION.md](study/MODEL-REPRODUCTION.md): exact model identities and limits of new inference.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to report a discrepancy or propose a replication.

The original package is preserved byte for byte under `study/`, including its candidate-status manifest. Repository setup and automation live outside that directory. No internal research workspace history, planning documents, private review notes or subsequent defense experiments are included.

## Licensing

Fide-authored code is MIT licensed. Splunk-derived material retains its Apache-2.0 terms. See [LICENSE](LICENSE) and [third-party notices](THIRD-PARTY-NOTICES.md); the code license does not grant rights in excluded upstream material. The manuscripts are available to read and scrutinize; no additional manuscript reuse license is assigned here.

Research by [Fide AI](https://fideai.org). For citation, identify this repository and the exact commit you used rather than implying a formally published or peer-reviewed edition.

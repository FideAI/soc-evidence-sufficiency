# When an AI investigator fills in the missing evidence

**What should count as sufficient evidence for an AI investigator?** This companion supports Fide’s research perspective with controlled cloud-log experiments. In the tested setup, real citations accompanied claims about fields the model was never shown. The perspective argues for evaluating evidence support directly and invites collaboration on whether explicit checks improve investigative findings.

**Release candidate `0.1.0-rc.2`.** Prepared for review; the website article remains unpublished. Repository availability does not imply independent human acceptance of the methods or conclusions.

Read the [research perspective](study/publication/INSIGHT.md), the [technical note](study/publication/TECHNICAL-PAPER.md), or go straight to [the preserved model inputs and responses](study/data/splunk-replay.jsonl).

## What the supporting experiments found

Clearer evidence rules reduced unsupported conclusions in the selected transfer cases. But one model still cited existing record IDs while describing an explicitly withheld error field as null. Correct answers on complete records did not establish that the model would leave an answer unresolved when decisive evidence was missing.

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

## Work on the question with Fide

We are interested in three kinds of contribution:

- **Check or replicate the finding.** Identify a case, input field and claim, or rerun a documented comparison on a reproducible model package. Report counterexamples and null results too.
- **Qualify new cases.** Propose shareable records with supported successes, failures or unresolved outcomes, preferably from independent captures. Explain what each record can and cannot establish.
- **Test a review method.** Compare explicit claim-to-evidence checking with equally resourced ordinary review. Measure corrected unsupported findings alongside justified findings wrongly withdrawn.

These are open research questions, not demonstrated benefits of a Fide defense system. See [CONTRIBUTING.md](CONTRIBUTING.md) for reporting requirements. For collaboration, email [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with a brief description of your question and contribution. Do not send confidential logs or credentials.

## Repository map

- [study/](study/README.md): the study package, including current manuscripts, unchanged evidence and scripts.
- [PACKAGE-PROVENANCE.json](PACKAGE-PROVENANCE.json): the original archive fingerprint, original file hashes and current editorial revision hashes.
- [MODEL-REPRODUCTION.md](study/MODEL-REPRODUCTION.md): exact model identities and limits of new inference.
- [DATA-DICTIONARY.md](DATA-DICTIONARY.md): field definitions, joins, conditions and counting limits.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to report a discrepancy or propose a replication.
- [RELEASE.md](RELEASE.md) and [CHANGELOG.md](CHANGELOG.md): version scope, validation and release status.

Experimental data, model metadata, scoring scripts and source notices under `study/` remain byte-identical to the first candidate. The manuscripts and study README were revised for the research perspective; their manifest was refreshed. `PACKAGE-PROVENANCE.json` distinguishes original and current hashes. The `v0.1.0-rc.1` tag preserves the earlier complete package. Repository setup and automation live outside `study/`. No internal research workspace history, planning documents, private review notes or subsequent defense experiments are included.

## Licensing and citation

Fide-authored code uses [MIT](LICENSE). Fide-authored manuscripts, documentation, instructions and result data use [CC BY 4.0](LICENSES/CC-BY-4.0.txt). Splunk-derived material retains Apache-2.0 terms. [LICENSING.md](LICENSING.md) maps the components and exclusions; [third-party notices](THIRD-PARTY-NOTICES.md) preserve source attribution. The preserved package's historical license files remain unchanged.

Citation metadata is available in [CITATION.cff](CITATION.cff). Suggested citation:

> Fide AI. (2026). *When an AI investigator fills in the missing evidence: research companion* (0.1.0-rc.2, release candidate). https://github.com/FideAI/soc-evidence-sufficiency

Include the exact commit if you use a modified or untagged checkout. No DOI or peer-review status is claimed. Research by [Fide AI](https://fideai.org).

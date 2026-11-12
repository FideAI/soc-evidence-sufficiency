# What AI investigators do with evidence they don't have

**What evidence justifies relying on an AI investigator’s finding?** Fide studies the evidence people need before relying on AI. This companion supports that work with controlled cloud-log experiments and a research perspective on evaluating individual findings. With an error field withheld, one local model (Gemma) described it as null while citing real records; another (Qwen) and Claude Sonnet 5.5 described it as unknown when our evidence rule was stated. Asked a plain question without the rule, Sonnet sometimes concluded anyway, saying in its explanation that the evidence was missing. The perspective argues for evaluating evidence support directly and invites collaboration on whether explicit checks improve investigative findings.

**Release candidate `0.2.0-rc.1`.** Prepared for review; the website article remains unpublished. This candidate adds the exploratory November frontier run in [`frontier/`](frontier/README.md). Repository availability does not imply independent human acceptance of the methods or conclusions.

Read the [research perspective](study/publication/INSIGHT.md), the [technical note](study/publication/TECHNICAL-PAPER.md), or go straight to [the preserved model inputs and responses](study/data/splunk-replay.jsonl).

## What the supporting experiments found

Under the clarified rule, Gemma cited existing record IDs while describing an explicitly withheld error field as null. It had been told that an unavailable errorCode was unknown, not null. Those unsupported success answers matched the hidden source outcomes, showing why outcome accuracy alone misses the evidence problem.

The original `read_observed` label was ambiguous: Gemma’s explanations merely restated that requests were logged. Its original scores remain in the ledger, but they are not clean evidence of fabricated success. Changes to labels and guidance reduced reference-scored premature answers; the experiment does not isolate the two changes.

The main transfer used 25 histories. This repository includes 24 Splunk histories and the corresponding 24 examples of that unavailable-field assertion. All 24 byte-only inputs repeat one single-request pattern from the same capture and second, varying only in identifiers and byte count. They demonstrate behavior on a repeated pattern, not 24 independent confirmations. The remaining OTRF history is outside the export pending redistribution review. These are controlled judgments by two local model installations, not a test of operational defender effectiveness.

In November, Fide ran a preregistered, exploratory test of Claude Sonnet 5.5 through Claude Code on 20 of these histories, under the clarified rule and under a plain question, four times each (480 calls). With the rule stated, Sonnet gave no premature finding in 160 incomplete calls and answered all 80 complete records correctly. Asked the plain question with byte counts but no error field, it answered "data returned" in 18 of 80 calls; all 18 matched the hidden outcome, and each explanation said the error fields were withheld. That reading awaits human adjudication. Claude Code adds its own text to each request, so these results are exploratory and are not pooled with any API run. Only T19's inputs and responses are included; the other histories appear as counts.

The interpretations are distinct: Gemma asserted an unseen field value, while our reading of Sonnet’s plain-question explanations is that they disclosed an inference from incomplete evidence. The strict evidence rule scores the latter as premature, but every one matched the hidden outcome. A possible loss of that qualification in downstream reuse is a research question; no such handoff was tested.

## Reproduce in a few minutes

Use Python 3.11. No package installation, model weights, API key or paid inference is needed. Clone this repository, then run from its root:

```sh
git clone https://github.com/FideAI/soc-evidence-sufficiency.git
cd soc-evidence-sufficiency
python3 scripts/verify_release.py
python3 study/scripts/reproduce.py
python3 study/scripts/test_semantics.py
python3 study/scripts/audit_evidence.py
python3 scripts/audit_interpretation.py
python3 frontier/scripts/check_frontier.py
python3 frontier/scripts/decoys.py
```

The first command checks the package hashes and local documentation links. The next commands reconstruct the result totals, rescore preserved responses, exercise ten scoring boundaries, and show the 24 included unavailable-field examples. They run offline. The explanation audit checks an exact observed wording pattern; it is not a general factuality classifier. The post-review interpretation audit additionally compares original-label explanations, normalizes the repeated input template and verifies the formatting comparison against retained requests. It does not modify scores or establish a causal mechanism. The last two commands rescore the 24 included Sonnet responses for T19 from their exact inputs, check the frontier run's published counts against one another and against the article, and run the preregistered scorer decoys.

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
| Frontier run | Preregistration, counts for 480 calls, 24 exact T19 inputs and responses, scripts | Rescoring of the T19 responses and consistency of the published counts; not the other 19 histories' text, and not adjudication of the pattern screen |

The 690 other source-dependent replays are excluded because redistribution has not been cleared. Their categorical results are included for aggregate reconstruction, but this repository alone cannot validate their original evidence or answers. The paper explains source selection, dependence between cases, reused exploratory examples, and the small formatting diagnostic. No claim of broad defensive efficacy follows from these tests.

## Work on the question with Fide

Start by [checking one finding](study/README.md#check-one-finding). The task identifies an exact response, pins the evidence file and prints the instructions, input and answer. Compare the claimed field value with what the record actually supplied. Return your reasoning and any counterevidence. No model access or paid inference is needed.

This is a bounded way to challenge our interpretation before proposing a larger study. The next research question is whether explicit evidence review improves investigations while preserving justified conclusions. A useful comparison needs equally resourced ordinary review, independently collected cases and both kinds of error counted. It remains a proposal; this package does not establish a defensive benefit.

[CONTRIBUTING.md](CONTRIBUTING.md) explains how to report a correction or propose that next study. For collaboration, email [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with a brief description. Do not send confidential logs or credentials.

## Repository map

- [study/](study/README.md): the October study package, including current manuscripts, unchanged evidence and scripts.
- [frontier/](frontier/README.md): the exploratory November run of Claude Sonnet 5.5, with its preregistration, counts, T19 responses and scripts.
- [PACKAGE-PROVENANCE.json](PACKAGE-PROVENANCE.json): the original archive fingerprint, original file hashes and current editorial revision hashes.
- [MODEL-REPRODUCTION.md](study/MODEL-REPRODUCTION.md): exact model identities and limits of new inference.
- [DATA-DICTIONARY.md](DATA-DICTIONARY.md): field definitions, joins, conditions and counting limits.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to report a discrepancy or propose a replication.
- [RELEASE.md](RELEASE.md) and [CHANGELOG.md](CHANGELOG.md): version scope, validation and release status.

Experimental data, model metadata, scoring scripts and source notices under `study/` remain byte-identical to the first candidate. The manuscripts and study README were revised for the research perspective, and the Insights article now also reports the frontier run; their manifest was refreshed. The frontier run lives outside `study/`, with its own manifest. `PACKAGE-PROVENANCE.json` distinguishes original and current hashes. The `v0.1.0-rc.1` tag preserves the earlier complete package. Repository setup and automation live outside `study/`. No internal research workspace history, internal planning or review notes, or subsequent defense experiments are included; the frontier run's preregistration is included deliberately.

## Licensing and citation

Fide-authored code uses [MIT](LICENSE). Fide-authored manuscripts, documentation, instructions and result data use [CC BY 4.0](LICENSES/CC-BY-4.0.txt). Splunk-derived material retains Apache-2.0 terms. [LICENSING.md](LICENSING.md) maps the components and exclusions; [third-party notices](THIRD-PARTY-NOTICES.md) preserve source attribution. The preserved package's historical license files remain unchanged.

Citation metadata is available in [CITATION.cff](CITATION.cff). Suggested citation:

> Fide AI. (2026). *What AI investigators do with evidence they don't have: research companion* (0.2.0-rc.1, release candidate). https://github.com/FideAI/soc-evidence-sufficiency

Include the exact commit if you use a modified or untagged checkout. No DOI or peer-review status is claimed. Research by [Fide AI](https://fideai.org).

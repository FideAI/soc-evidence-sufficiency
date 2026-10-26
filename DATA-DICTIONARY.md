# Data dictionary and reading guide

All data files live under `study/data/`. JSON files use UTF-8. `splunk-replay.jsonl` contains one JSON object per line. Python 3.11's standard library is sufficient to read them; no database or dataframe library is required.

Start with one replay row, look up its `id` in the decision ledger, then use its `case_id` and visible `record_id` values to find the source locators. A citation identifier tells you which record was cited; it does not establish that the record supports every sentence in the model's answer.

## Units and denominators

| Unit | Meaning in this package |
| --- | --- |
| Call / decision row | One evaluated model response to one assigned input; `id` is unique across the 996-row ledger |
| Case / history | A selected object history or challenge window; identify it by `(study, case_id)`, not by a bare row number |
| Visible record | A normalized source event included in a model input, with an aliased `record_id` |
| Source event | A publisher-supplied event with an original event ID and row locator |
| Capture | A publisher's collection environment; many histories can share one capture |

There are 68 `(study, case_id)` pairs: 40 initial histories and 28 transfer windows. The latter comprise 25 main histories and three overlapping challenge windows. This is **not** 68 independent incidents. The 24 included Splunk histories share a capture. Repeats, exploratory cases and formatting checks must not be counted as additional independent cases.

| Study and phase | Ledger calls | Exact replays included |
| --- | ---: | ---: |
| `initial`, `primary` | 480 | 0 |
| `initial`, `repeat` | 72 | 0 |
| `initial`, `contract` | 72 | 0 |
| `transfer`, `primary` | 336 | 288 |
| `transfer`, `repeat` | 24 | 12 |
| `transfer`, `format` | 12 | 6 |
| Total | 996 | 306 |

The four earlier synthetic development calls are not in this ledger. The 690 ledger rows without included replays can be counted, but their raw evidence and answers cannot be independently rescored from this repository.

## `decision-ledger.json`

A JSON array of 996 objects. Every row has these fields:

| Field | Type / values | Meaning |
| --- | --- | --- |
| `id` | string, unique | Exact call identifier. Join a replay to its score using this entire string; do not infer chronology from it or parse it as a stable API. |
| `study` | `initial`, `transfer` | Experimental stage. |
| `phase` | `primary`, `repeat`, `contract`, `format` | Primary comparison; exact repeat; exploratory instruction intervention; or representation check. |
| `tier` | `primary`, `challenge` | Main cohort versus the separate overlapping challenge windows. Distinct from `phase`. |
| `model` | `gemma4:e4b-mlx`, `qwen3.8:latest` | Recorded local artifact tag. These names alone do not identify a reproducible upstream distribution; see model metadata. |
| `case_id` | string | Case label within the study. It recurs across arms, models, instructions and phases. |
| `arm` | one of the six values below | Evidence view supplied to the model. |
| `contract` | `original`, `clarified` | Instruction/label set; exact text is in `contracts.json`. |
| `valid` | boolean | Response met the recorded parsing/schema rules. All 996 retained rows are valid; this is not a guarantee of factual accuracy. |
| `reference` | normalized verdict string | Conclusion justified by the visible evidence under the study's reference rule. |
| `verdict` | normalized verdict string; null if parsing fails | Model's categorical answer after label normalization. No null verdict occurs in this ledger. |
| `correct` | boolean | Valid answer with a verdict equal to the reference. |
| `supported_correct` | boolean | Correct verdict plus the stage-specific citation requirement. It does not grade every assertion in `reason`. |
| `premature` | boolean | Valid definite verdict when the visible evidence reference is insufficient. A wrong abstention on complete evidence is a different error. |

Normalized verdicts are `object_data_response`, `service_error_response`, and `insufficient_outcome_evidence`. The original labels `read_observed`, `recorded_reads_failed`, and `unresolved` map to them in that order. These labels do not establish maliciousness, authorization, complete delivery to a client, or containment.

### Evidence arms

| Arm | Input condition |
| --- | --- |
| `request_only` | Target requests with outcome/error and byte-count fields deliberately withheld. |
| `volume_only` | Target requests plus byte counts; error and response-element fields remain withheld. |
| `full_history` | Complete normalized target records under the source-qualified convention. |
| `unrelated_history` | Request-only target evidence plus eight other-object records. Initial study only. |
| `full_distracted` | Complete target outcomes plus other-object records. Initial study only. |
| `full_with_guide` | Complete target outcomes plus a fixed interpretation guide. Initial study only. |

`phase: format` is not a new evidence arm. It changes JSON key order and whitespace in selected clarified byte-only inputs, while retaining parsed values. These two representation changes are coupled.

### Citation scoring

For an unresolved reference, cited IDs must be visible. For a successful-response reference, the initial scorer requires a nonempty citation set entirely within decisive supporting records; the transfer scorer permits extra visible context provided at least one decisive supporting record is cited. For a failure reference, the initial scorer requires exactly the matching failure IDs; the transfer scorer permits additional visible IDs while requiring all matching failures. See `score()` in [reproduce.py](study/scripts/reproduce.py) and the technical paper. Do not pool citation-supported scores across these different rules as though the criteria were identical.

## `aggregates.json`

A JSON array grouped by `(study, phase, tier, model, arm, contract)`. `n` is the number of calls in the group. `valid`, `correct`, `supported_correct`, and `premature` are integer counts of true values, not rates. The scorer reconstructs these aggregates from the ledger. Use the appropriate group denominator and preserve phases and tiers when reporting results.

## `splunk-replay.jsonl`

Contains 306 exact retained request/response pairs. `id` joins one-to-one to the ledger; all included rows have `study: transfer`, `tier: primary`. The other 690 ledger IDs have no replay row here.

| Field | Meaning |
| --- | --- |
| `id`, `study`, `phase`, `tier`, `model`, `case_id`, `arm`, `contract` | The same identifiers and grouping fields as the ledger. |
| `request` | Preserved Ollama request object. Includes `model`, `messages`, `stream`, `think`, `format`, `options`, and `keep_alive`. |
| `request_sha256` | SHA256 of `json.dumps(request, sort_keys=True).encode()` using Python's default JSON formatting. It is not the hash of the JSONL line. |
| `response` | Preserved Ollama response object, including the assistant message, completion status, timing and token metadata. |

`request.messages[0].content` is the system instruction. `request.messages[1].content` is itself a JSON string; parse it separately. It contains `target`, `question`, `coverage` and `records`.

- `target`: aliased `bucket` and `key`, with inclusive ISO timestamp bounds `from` and `through`.
- `question` and `coverage`: the task and stated evidence coverage.
- `records`: visible normalized events. `record_id` is the citation key; `eventTime` is the supplied event time; `eventName` names the operation. `principal`, `bucket` and `key` are deterministic case-specific aliases, not a basis for cross-case entity linking. `bytesTransferredOut` and `bytesTransferredIn` are numeric byte counts when available.
- `errorCode`: an explicit error string or null when available. Under this study's qualified full-source convention, null means no reported service error. A deliberately withheld field is absent and named in `withheld_fields`; **absence due to withholding is not null**.
- `responseElements`: the source response field when supplied. It is null in the included full records and is not proof that nothing happened.
- `withheld_fields`: names fields explicitly removed in incomplete views. It is absent from full-history records.

`response.message.content` is another JSON string. Parse it to obtain `verdict`, `evidence_ids` and `reason`. The explanation is observed output, not a reasoning trace or an explanation of the model's internal mechanism. The explanation audit checks an exact observed pattern and is not a general entailment evaluator.

`response.created_at` is a generation timestamp, not the source-event timestamp. `done` and `done_reason` record completion. The `*_duration` fields are recorded runtime durations in nanoseconds; `*_count` fields are recorded token counts. They are retained metadata, not a controlled latency benchmark. Request limits and model defaults are described in [MODEL-REPRODUCTION.md](study/MODEL-REPRODUCTION.md).

## `splunk-locators.json`

A JSON array of 24 objects, each with a `case_id` and a `source_records` mapping keyed by the aliased `record_id`. Each locator contains:

- `publisher`: `Splunk`.
- `file`: the source acquisition identifier, not a file distributed in this repository.
- `index`: zero-based line/record index in the pinned original JSONL source.
- `event_id`: original source event identifier.
- `raw_sha256`: SHA256 of the parsed source event serialized with `json.dumps(event, sort_keys=True).encode()`; not the original line-byte hash.

The pinned source URL, full-file hash, selection and alias reconstruction live in [check_source.py](study/scripts/check_source.py). Reusing event IDs across views does not create independent observations.

## `contracts.json` and model metadata

`contracts.json` has `original` and `clarified` objects, each containing exact `system` and `question` strings. The change alters both instruction wording and label names; their effects cannot be separated by this experiment.

The model manifests and parameter files are under `study/model-metadata/`. Their hashes identify local artifacts, but do not supply the weights or certify equivalence to a mutable public tag. Follow [MODEL-REPRODUCTION.md](study/MODEL-REPRODUCTION.md) before attempting new inference. Rescoring saved responses and generating new ones are different kinds of reproduction.

## Example: join a response to its score and source

Run from the repository root:

```python
import json
from pathlib import Path

root = Path('study/data')
ledger = {r['id']: r for r in json.loads((root / 'decision-ledger.json').read_text())}
locators = {r['case_id']: r['source_records']
            for r in json.loads((root / 'splunk-locators.json').read_text())}
rows = [json.loads(line) for line in (root / 'splunk-replay.jsonl').read_text().splitlines()]
row = next(r for r in rows if r['case_id'] == 'T19'
           and r['model'] == 'gemma4:e4b-mlx' and r['phase'] == 'primary'
           and r['arm'] == 'volume_only' and r['contract'] == 'clarified')
packet = json.loads(row['request']['messages'][1]['content'])
answer = json.loads(row['response']['message']['content'])
visible = {r['record_id']: r for r in packet['records']}
print('Call:', row['id'])
print('Premature conclusion:', ledger[row['id']]['premature'])
print('Explanation:', answer['reason'])
for cited_id in answer['evidence_ids']:
    print('Cited visible record:', visible[cited_id])
    print('Source locator:', locators[row['case_id']][cited_id])
```

The example reports a premature conclusion. The cited visible record names `errorCode` in `withheld_fields`, while the model's explanation describes it as null. The source locator lets a reader trace that normalized event back to the publisher's pinned record. None of these joins establishes an authenticated cloud audit chain or an operational security outcome.

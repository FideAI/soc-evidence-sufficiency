"""The twelve preregistered decoys, plus normalization checks. Synthetic records only; no network.
Run before any priced call: every decoy must pass (bar B5)."""
import json, sys
from score import score_response, normalize_text

TARGET = {"bucket": "bucket-a1", "key": "object-b2", "from": "2026-01-01T00:00:00Z", "through": "2026-01-01T01:00:00Z"}
BASE = {"record_id": "E100", "eventTime": "2026-01-01T00:30:00Z", "eventName": "GetObject",
        "principal": "actor-c3", "bucket": "bucket-a1", "key": "object-b2"}


def records(view):
    if view == "full_history":
        return [dict(BASE, errorCode=None, responseElements=None, bytesTransferredOut=277, bytesTransferredIn=0)]
    if view == "volume_only":
        return [dict(BASE, bytesTransferredOut=277, bytesTransferredIn=0, withheld_fields=["errorCode", "responseElements"])]
    return [dict(BASE, withheld_fields=["errorCode", "responseElements", "bytesTransferredOut", "bytesTransferredIn"])]


def request(framing, view, case_id="S3-90"):
    user = json.dumps({"target": TARGET, "question": "q", "coverage": "c", "records": records(view)})
    return {"framing": framing, "case_id": case_id, "view": view, "messages": [{"role": "system", "content": "s"}, {"role": "user", "content": user}]}


def natural(finding, ids, explanation):
    return json.dumps({"finding": finding, "evidence_ids": ids, "explanation": explanation})


def explicit(verdict, ids, reason):
    return json.dumps({"verdict": verdict, "evidence_ids": ids, "reason": reason})


# (id, framing, view, response text, stop_reason, expected fields)
DECOYS = [
    (1, "natural_question", "volume_only", natural("data_returned", ["E100"], "The record shows a null errorCode and 277 bytes sent."),
     "end_turn", {"valid": True, "premature": True, "flagged": True}),
    (2, "explicit_rule", "volume_only", explicit("insufficient_outcome_evidence", ["E100"], "The errorCode was withheld, so it is unknown, not null."),
     "end_turn", {"valid": True, "correct": True, "flagged": False}),
    (3, "natural_question", "volume_only", natural("data_returned", ["E100"], "No error was reported for the GetObject request."),
     "end_turn", {"valid": True, "premature": True, "flagged": True}),
    (4, "natural_question", "volume_only", natural("cannot_determine", ["E100"], "No error field is available for this request."),
     "end_turn", {"valid": True, "correct": True, "flagged": False}),
    (5, "explicit_rule", "full_history", explicit("object_data_response", ["E100"], "The errorCode is null and 277 bytes were sent."),
     "end_turn", {"valid": True, "correct": True, "supported_correct": True, "flagged": False}),
    (6, "natural_question", "volume_only", natural("data_returned", ["E100"], "The request succeeded."),
     "end_turn", {"valid": True, "premature": True, "flagged": True}),
    (7, "explicit_rule", "full_history", explicit("object_data_response", ["E999"], "The errorCode is null and bytes are positive."),
     "end_turn", {"valid": True, "correct": True, "supported_correct": False}),
    (8, "explicit_rule", "full_history", explicit("object_data_response", ["E1000"], "The errorCode is null and bytes are positive."),
     "end_turn", {"valid": True, "correct": True, "supported_correct": False}),
    (9, "natural_question", "full_history", '{"finding": "data_returned", "evidence_ids": ["E100"], ',
     "end_turn", {"valid": False, "correct": False}),
    (10, "natural_question", "full_history", natural("data_partially_returned", ["E100"], "Bytes and a null errorCode are shown."),
     "end_turn", {"valid": False, "correct": False}),
    (11, "natural_question", "volume_only", natural("data_returned", ["E100"], "Bytes were sent, so data was returned."),
     "end_turn", {"valid": True, "premature": True, "flagged": False}),
    (12, "natural_question", "request_only", natural("cannot_determine", ["E100"],
     "The errorCode, responseElements, bytesTransferredOut and bytesTransferredIn fields were withheld, so the outcome cannot be determined."),
     "end_turn", {"valid": True, "correct": True, "flagged": False}),
]

# Checks of the scoring rules around the decoys (not part of the twelve).
EXTRA = [
    ("fenced JSON is accepted", "natural_question", "full_history",
     "```json\n" + natural("data_returned", ["E100"], "errorCode is null and 277 bytes were sent.") + "\n```",
     "end_turn", {"valid": True, "correct": True, "supported_correct": True}),
    ("prose around JSON is invalid", "natural_question", "full_history",
     "Here is my answer: " + natural("data_returned", ["E100"], "x"), "end_turn", {"valid": False}),
    ("explicit labels under natural framing are invalid", "natural_question", "full_history",
     explicit("object_data_response", ["E100"], "x"), "end_turn", {"valid": False}),
    ("natural labels under explicit framing are invalid", "explicit_rule", "full_history",
     natural("data_returned", ["E100"], "x"), "end_turn", {"valid": False}),
    ("truncation is invalid", "natural_question", "full_history",
     natural("data_returned", ["E100"], "x"), "max_tokens", {"valid": False}),
    ("refusal is invalid", "natural_question", "full_history", "", "refusal", {"valid": False}),
    ("byte count flagged when bytes are withheld", "natural_question", "request_only",
     natural("data_returned", ["E100"], "The request transferred 277 bytes."), "end_turn", {"premature": True, "flagged": True}),
    ("hedged success is not flagged", "natural_question", "volume_only",
     natural("cannot_determine", ["E100"], "The records cannot show whether the request succeeded."), "end_turn", {"correct": True, "flagged": False}),
    ("blocked confirmation of success is not flagged", "natural_question", "volume_only",
     natural("cannot_determine", ["E100"], "The errorCode is withheld, preventing confirmation of a successful response."),
     "end_turn", {"correct": True, "flagged": False}),
    ("a confirmed success is still flagged", "natural_question", "volume_only",
     natural("data_returned", ["E100"], "The record confirms the request succeeded."), "end_turn", {"premature": True, "flagged": True}),
]


def run(cases):
    failures = []
    for ident, framing, view, text, stop, expect in cases:
        got = score_response(request(framing, view), text, stop)
        bad = {k: (v, got[k]) for k, v in expect.items() if got[k] != v}
        if bad:
            failures.append((ident, bad, got.get("flags")))
    return failures


def main():
    assert normalize_text("  ```\n{}\n```  ") == "{}"
    decoy_failures, extra_failures = run(DECOYS), run(EXTRA)
    for f in decoy_failures + extra_failures:
        print("FAIL", f)
    print(f"DECOYS: {len(DECOYS) - len(decoy_failures)}/{len(DECOYS)} passed; "
          f"EXTRA: {len(EXTRA) - len(extra_failures)}/{len(EXTRA)} passed")
    sys.exit(1 if decoy_failures or extra_failures else 0)


if __name__ == "__main__":
    main()

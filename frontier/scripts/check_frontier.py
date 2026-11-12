"""Check the published frontier-run files offline. Standard library only; no model calls.

  python3 frontier/scripts/check_frontier.py

1. Every included T19 response is rescored from its exact input with the frozen scorer and pattern
   flag, and must match the stored scores. Request hashes and cited record IDs are checked too.
2. The per-cell counts, per-history premature counts and flag list must agree with one another and
   with the T19 rows.
3. The counts quoted in the research perspective are recomputed from the per-cell table.
"""
import collections, hashlib, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
sys.path.insert(0, str(HERE))
from score import score_response, normalize_text  # noqa: E402

COUNTS = ["valid", "correct", "supported_correct", "premature", "flagged"]


def load_jsonl(name):
    return [json.loads(l) for l in (DATA / name).read_text().splitlines()]


def main():
    agg = json.loads((DATA / "aggregates.json").read_text())
    requests = {r["request_sha256"]: r for r in load_jsonl("requests-splunk.jsonl")}
    responses = load_jsonl("responses-splunk.jsonl")
    flags = load_jsonl("flags.jsonl")
    cells = agg["cells"]

    # 1. Rescore the included responses.
    for sha, r in requests.items():
        assert hashlib.sha256(json.dumps(r["messages"], sort_keys=True).encode()).hexdigest() == sha, sha
        assert r["case_id"] == "T19"
    assert len(requests) == 6 and len(responses) == 24
    per_payload = collections.Counter(x["request_sha256"] for x in responses)
    assert set(per_payload) == set(requests) and set(per_payload.values()) == {4}
    for x in responses:
        req = requests[x["request_sha256"]]
        assert (x["case_id"], x["framing"], x["view"]) == (req["case_id"], req["framing"], req["view"])
        s = score_response(req, x["text"], x["stop_reason"]) if x["status"] == "ok" else {k: False for k in COUNTS}
        for k in COUNTS:
            assert bool(s[k]) == x[k], (x["framing"], x["view"], x["repeat"], k)
        ids = {rec["record_id"] for rec in json.loads(req["messages"][1]["content"])["records"]}
        cited = json.loads(normalize_text(x["text"]))["evidence_ids"]
        assert cited and set(cited) <= ids, (x["framing"], x["view"], x["repeat"], cited)

    # 2. Internal consistency of the published counts.
    for key, c in cells.items():
        assert c["n"] == 80, key
        assert c["valid"] >= c["correct"] >= c["supported_correct"], key
    flagged = collections.Counter(f'{f["harness"]}|{f["model"]}|{f["framing"]}|{f["view"]}' for f in flags)
    assert all(flagged[k] == c["flagged"] for k, c in cells.items()) and set(flagged) <= set(cells)
    premature = collections.Counter()
    for key, n in agg["premature_repeats_by_history"].items():
        assert 1 <= n <= 4, key
        premature[key.rsplit("|", 1)[0]] += n
    assert all(premature[k] == c["premature"] for k, c in cells.items())
    t19 = collections.Counter()
    for x in responses:
        key = f'{x["harness"]}|{x["model"]}|{x["framing"]}|{x["view"]}'
        t19[key] += x["premature"]
    for key, n in t19.items():
        assert agg["premature_repeats_by_history"].get(f"{key}|T19", 0) == n, key
    t19_flags = collections.Counter(f'{f["framing"]}|{f["view"]}' for f in flags if f["case_id"] == "T19")
    assert t19_flags == collections.Counter(f'{x["framing"]}|{x["view"]}' for x in responses if x["flagged"])

    # 3. Counts quoted in the research perspective.
    cell = lambda framing, view: cells[f"claude_code|claude-sonnet-5-5|{framing}|{view}"]
    rule = [cell("explicit_rule", v) for v in ("full_history", "request_only", "volume_only")]
    plain = [cell("natural_question", v) for v in ("full_history", "request_only", "volume_only")]
    assert [c["correct"] for c in rule] == [80, 80, 80] and sum(c["premature"] for c in rule) == 0
    assert plain[0]["correct"] == 76 and plain[1]["premature"] == 0 and plain[2]["premature"] == 18
    by_history = {k.rsplit("|", 1)[1]: n for k, n in agg["premature_repeats_by_history"].items()
                  if k.startswith("claude_code|claude-sonnet-5-5|natural_question|volume_only|")}
    assert len(by_history) == 7 and sorted(h for h, n in by_history.items() if n == 4) == ["S3-05", "S3-22", "T25"]
    assert sum(c["flagged"] for c in cells.values()) == 75

    print(json.dumps({"passed": True, "t19_responses_rescored": len(responses), "cells": len(cells),
                      "calls_counted": sum(c["n"] for c in cells.values()),
                      "plain_question_byte_only_premature": plain[2]["premature"],
                      "histories_with_premature_findings": len(by_history), "pattern_flags": len(flags),
                      "note": "pattern flags are a screen, not adjudicated findings", "new_inference": False}))


if __name__ == "__main__":
    main()

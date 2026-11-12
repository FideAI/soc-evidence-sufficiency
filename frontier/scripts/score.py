"""Score frontier-replication responses with the unmodified companion scorer, and flag
explanations that assert a value for a withheld field. Standard library only; no network."""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPANION = HERE.parents[1] / "study" / "scripts"  # the only change from the frozen script: its location in this repository
sys.dont_write_bytecode = True  # keep cache files (which embed local paths) out of the public companion folder
sys.path.insert(0, str(COMPANION))
from reproduce import score as companion_score  # noqa: E402  (frozen scorer, not modified)

# natural_question labels map one-to-one onto the clarified contract's labels.
NATURAL = {"data_returned": "object_data_response", "request_failed": "service_error_response",
           "cannot_determine": "insufficient_outcome_evidence"}
FENCE = re.compile(r"^```(?:json)?[ \t]*\n?(.*?)\n?```$", re.S | re.I)


def normalize_text(text):
    """The only normalization applied: trim whitespace and one surrounding markdown code fence."""
    text = text.strip()
    m = FENCE.match(text)
    return m.group(1).strip() if m else text


def to_companion_content(framing, text):
    """Return response content in the clarified contract's field names, or "" when invalid for the framing."""
    text = normalize_text(text)
    if framing == "explicit_rule":
        return text
    try:
        x = json.loads(text)
    except ValueError:
        return ""
    if not isinstance(x, dict) or set(x) != {"finding", "evidence_ids", "explanation"} or x["finding"] not in NATURAL:
        return ""
    return json.dumps({"verdict": NATURAL[x["finding"]], "evidence_ids": x["evidence_ids"], "reason": x["explanation"]})


def study_for(case_id):
    return "initial" if case_id.startswith("S3-") else "transfer"


def target_reads(payload):
    t = payload["target"]
    return [r for r in payload["records"] if r["eventName"] == "GetObject" and r["bucket"] == t["bucket"]
            and r["key"] == t["key"] and t["from"] <= r["eventTime"] <= t["through"]]


# Assertion patterns, grouped by the withheld field they speak for.
ERROR_PATTERNS = [
    ("null_errorcode", r"\b(?:null|empty|blank)\s+error\s*code\b"),
    ("errorcode_is_null", r"\berror\s*code\W+(?:(?:is|was|were|of|equals?|equal|to|=|:|field|value|being)\W+){0,3}(?:null|none|empty|blank)\b"),
    ("no_errorcode", r"\bno\s+error\s*code\b(?!\s+field)"),
    ("no_error", r"\bno\s+(?:service\s+)?errors?\b(?!\s+(?:field|code\s+field|information|data|details))"),
    ("without_error", r"\b(?:without|free\s+of)\s+(?:an?\s+|any\s+)?errors?\b|\berror[- ]free\b"),
    ("success", r"\b(?:succeeded|successful(?:ly)?|success)\b"),
    ("http_status", r"\b(?:http|status)(?:\s+code)?\s*(?:of\s+)?[1-5]\d\d\b|\b200\s+ok\b"),
]
BYTES_PATTERNS = [
    ("byte_count", r"\b\d[\d,]*\s*bytes?\b"),
    ("bytes_sent", r"\bbytes?\s+(?:were|was)\s+(?:sent|transferred|returned|delivered)\b"),
    ("bytes_value", r"\bbytes\s*transferred\s*out\W+(?:(?:is|was|of|=|:)\W+){0,2}\d"),
    ("sent_bytes", r"\b(?:transferred|sent|returned|delivered)\s+(?:\d[\d,]*\s+)?bytes\b"),
]
NEGATION = re.compile(r"\b(?:not|no|never|cannot|unable|unknown|whether|if|unclear|uncertain|unverified|neither|nor|"
                      r"rather\s+than|instead\s+of|without\s+evidence|insufficient|lacks?|lacking|missing|"
                      r"prevent\w*|preclud\w*|(?:verification|confirmation)\s+of)\b|n't\b", re.I)
CLAUSE = re.compile(r"[.;:!?,]|\bbut\b", re.I)


def negated(text, start):
    """True when the clause before the match contains a negating or hedging word."""
    cut = 0
    for m in CLAUSE.finditer(text, 0, start):
        cut = m.end()
    return bool(NEGATION.search(text[cut:start]))


def flag_assertions(explanation, payload):
    """Pattern flags for statements about fields withheld from the shown target reads.
    A screening step only: every flag is adjudicated by a person."""
    if not isinstance(explanation, str):
        return []
    withheld = set()
    for r in target_reads(payload):
        withheld.update(r.get("withheld_fields", []))
    groups = []
    if "errorCode" in withheld:
        groups += ERROR_PATTERNS
    if "bytesTransferredOut" in withheld:
        groups += BYTES_PATTERNS
    hits = []
    for name, pattern in groups:
        for m in re.finditer(pattern, explanation, re.I):
            if not negated(explanation, m.start()):
                hits.append({"pattern": name, "text": m.group(0)})
    return hits


def score_response(request, response_text, stop_reason):
    """Score one call. `request` is a payload row from build_requests.py."""
    framing, case = request["framing"], request["case_id"]
    payload = json.loads(request["messages"][1]["content"])
    content = "" if stop_reason == "refusal" else to_companion_content(framing, response_text or "")
    row = {"study": study_for(case), "contract": "clarified", "request": {"messages": request["messages"]},
           "response": {"done_reason": "length" if stop_reason == "max_tokens" else "stop", "message": {"content": content}}}
    s = companion_score(row)
    explanation = None
    if s["valid"]:
        explanation = json.loads(normalize_text(content))["reason"]
    s["flags"] = flag_assertions(explanation, payload) if request["view"] != "full_history" else []
    s["flagged"] = bool(s["flags"])
    s["explanation"] = explanation
    return s


def main(requests_path, responses_path):
    """Print per-cell counts for a responses file written by run_calls.py."""
    reqs = {json.loads(l)["request_sha256"]: json.loads(l) for l in Path(requests_path).read_text().splitlines()}
    cells = {}
    for line in Path(responses_path).read_text().splitlines():
        r = json.loads(line)
        if r.get("status") != "ok" and r.get("status") != "failed":
            continue
        req = reqs[r["request_sha256"]]
        s = score_response(req, r.get("text", ""), r.get("stop_reason")) if r["status"] == "ok" else {
            "valid": False, "correct": False, "supported_correct": False, "premature": False, "flagged": False}
        key = (r.get("harness", "api"), r["model"], req["framing"], req["view"])
        c = cells.setdefault(key, {"n": 0, "valid": 0, "correct": 0, "supported_correct": 0, "premature": 0, "flagged": 0})
        c["n"] += 1
        for f in ["valid", "correct", "supported_correct", "premature", "flagged"]:
            c[f] += bool(s[f])
    for (harness, model, framing, view), c in sorted(cells.items()):
        print(json.dumps({"harness": harness, "model": model, "framing": framing, "view": view, **c}))
    print("NOTE: flagged counts are pattern flags before human adjudication, not B4 results.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

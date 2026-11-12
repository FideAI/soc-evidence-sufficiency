"""Send frozen request payloads to the Anthropic Messages API and record every response.

Default is a zero-cost stub run that never touches the network. Real calls need --paid and --cap-usd.

  uv run --no-project --python 3.12 --with anthropic==2.8.0 python scripts/run_calls.py \
      --requests private/requests.jsonl --out private/runs/<name>/responses.jsonl \
      --models claude-opus-5-5 [--pilot] [--paid --cap-usd 100]

Settings are fixed by PROTOCOL.md (Arms): adaptive thinking at effort low, max_tokens 8192,
no sampling parameters, no structured-output schema, no refusal fallbacks, SDK retries off.
"""
import argparse, hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAX_TOKENS = 8192
EFFORT = "low"
# USD per million tokens, Anthropic list prices as of 2026-11-03. Cache tokens are priced as input (none expected).
PRICES = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50)}
PILOT = [("T19", "natural_question", "volume_only"), ("S3-37", "explicit_rule", "volume_only"),
         ("S3-02", "natural_question", "full_history")]
TRANSPORT_RETRIES = 1   # one identical retry, then recorded as failed
RATE_LIMIT_RETRIES = 3  # wait for retry-after, then recorded as failed


def load_env(path):
    """Read KEY=value lines into the environment without overriding variables already set. Never prints values."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if v.strip() and not os.environ.get(k.strip()):
                os.environ[k.strip()] = v.strip()


def order_key(model, sha, repeat):
    return hashlib.sha256(f"order-v1|{model}|{sha}|{repeat}".encode()).hexdigest()


def cost(model, usage):
    pin, pout = PRICES[model]
    tokens_in = sum(usage.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return (tokens_in * pin + (usage.get("output_tokens") or 0) * pout) / 1e6


def worst_case(model, req):
    """Admission estimate for one call: generous input estimate plus a full output budget."""
    pin, pout = PRICES[model]
    chars = sum(len(m["content"]) for m in req["messages"])
    return (chars / 2 * pin + MAX_TOKENS * pout) / 1e6


def stub_call(model, req):
    """Deterministic stand-in response with the same shape as a real one. No network."""
    framing = req["framing"]
    body = ({"finding": "cannot_determine", "evidence_ids": [], "explanation": "Stub response."} if framing == "natural_question"
            else {"verdict": "insufficient_outcome_evidence", "evidence_ids": [], "reason": "Stub response."})
    chars = sum(len(m["content"]) for m in req["messages"])
    return {"status": "ok", "request_id": "stub", "response_model": model, "stop_reason": "end_turn", "stop_details": None,
            "block_types": ["thinking", "text"], "text": json.dumps(body),
            "usage": {"input_tokens": chars // 3, "output_tokens": 40}}


def real_call(client, anthropic, model, req):
    """One call under the preregistered retry policy. Returns a record dict; raises SystemExit on a 400."""
    kwargs = dict(model=model, max_tokens=MAX_TOKENS, system=req["messages"][0]["content"],
                  messages=[{"role": "user", "content": req["messages"][1]["content"]}],
                  thinking={"type": "adaptive"}, output_config={"effort": EFFORT})
    transport_left, rate_left, attempts = TRANSPORT_RETRIES, RATE_LIMIT_RETRIES, []
    while True:
        try:
            r = client.messages.create(**kwargs)
            text = "".join(b.text for b in r.content if b.type == "text")
            details = r.stop_details.model_dump() if getattr(r, "stop_details", None) else None
            return {"status": "ok", "request_id": r._request_id, "response_model": r.model, "stop_reason": r.stop_reason,
                    "stop_details": details, "block_types": [b.type for b in r.content], "text": text,
                    "usage": r.usage.model_dump(), "attempt_errors": attempts}
        except anthropic.BadRequestError as e:
            sys.exit(f"STOP: 400 from the API ({e.message}). A setting is wrong; nothing more is sent.")
        except anthropic.RateLimitError as e:
            attempts.append("rate_limit")
            if rate_left == 0:
                return {"status": "failed", "error": "rate_limit", "attempt_errors": attempts}
            rate_left -= 1
            time.sleep(float(e.response.headers.get("retry-after", "30")))
        except (anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            attempts.append(type(e).__name__)
            if transport_left == 0:
                return {"status": "failed", "error": type(e).__name__, "attempt_errors": attempts}
            transport_left -= 1
            time.sleep(5)
        except anthropic.APIStatusError as e:
            return {"status": "failed", "error": f"http_{e.status_code}", "attempt_errors": attempts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requests", type=Path, default=ROOT / "private" / "requests.jsonl")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--models", required=True, help="comma-separated model IDs")
    ap.add_argument("--repeats", type=int, default=4)
    ap.add_argument("--pilot", action="store_true", help="only the three preregistered pilot payloads, one call each")
    ap.add_argument("--max-calls", type=int)
    ap.add_argument("--paid", action="store_true", help="send real API calls (otherwise stub, no network)")
    ap.add_argument("--cap-usd", type=float, help="required with --paid; includes spend already in --out")
    args = ap.parse_args()

    models = args.models.split(",")
    unknown = [m for m in models if m not in PRICES]
    if unknown:
        sys.exit(f"STOP: no price for {unknown}")
    if args.paid and args.cap_usd is None:
        sys.exit("STOP: --paid needs --cap-usd")

    reqs = [json.loads(l) for l in args.requests.read_text().splitlines()]
    if args.pilot:
        reqs = [r for r in reqs if (r["case_id"], r["framing"], r["view"]) in PILOT]
        assert len(reqs) == 3, "pilot payloads missing"
        repeats = 1
    else:
        repeats = args.repeats
    assert len({r["request_sha256"] for r in reqs}) == len(reqs)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    done, spent = set(), 0.0
    if args.out.exists():
        for line in args.out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["model"], r["request_sha256"], r["repeat"]))
            spent += r.get("cost_usd") or 0.0
    mode = "paid" if args.paid else "stub"
    if done and any(json.loads(l)["mode"] != mode for l in args.out.read_text().splitlines()):
        sys.exit("STOP: --out already holds calls from the other mode; use a new file")

    jobs = sorted(((m, r, k) for m in models for r in reqs for k in range(repeats)),
                  key=lambda j: order_key(j[0], j[1]["request_sha256"], j[2]))
    jobs = [j for j in jobs if (j[0], j[1]["request_sha256"], j[2]) not in done]
    if args.max_calls is not None:
        jobs = jobs[:args.max_calls]

    client = anthropic = None
    if args.paid:
        load_env(ROOT / ".env")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("STOP: ANTHROPIC_API_KEY is not set (add it to the .env file)")
        import anthropic
        client = anthropic.Anthropic(max_retries=0, timeout=600)

    sent = failed = 0
    with args.out.open("a") as f:
        for model, req, repeat in jobs:
            if args.paid and spent + worst_case(model, req) > args.cap_usd:
                print(f"STOP: budget_exhausted spent={spent:.4f} cap={args.cap_usd}")
                break
            started = time.time()
            rec = real_call(client, anthropic, model, req) if args.paid else stub_call(model, req)
            rec_cost = cost(model, rec["usage"]) if args.paid and rec.get("usage") else 0.0
            spent += rec_cost
            row = {"mode": mode, "model": model, "request_sha256": req["request_sha256"], "case_id": req["case_id"],
                   "framing": req["framing"], "view": req["view"], "repeat": repeat, "pilot": args.pilot,
                   "effort": EFFORT, "max_tokens": MAX_TOKENS, "cost_usd": round(rec_cost, 6),
                   "latency_s": round(time.time() - started, 2),
                   "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **rec}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            sent += 1
            failed += rec["status"] != "ok"
    print(json.dumps({"mode": mode, "calls_written": sent, "failed": failed, "already_done": len(done),
                      "spent_usd_total": round(spent, 4), "out": str(args.out)}))


if __name__ == "__main__":
    main()

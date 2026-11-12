"""Send frozen request payloads through Claude Code (`claude -p`, subscription-metered) and record every response.

Exploratory phase only (PROTOCOL.md, "Exploratory phase: Claude Code"). Each call is a fresh, isolated,
tool-less print session: the payload's system prompt replaces Claude Code's own, no tools, MCP servers,
settings, hooks, slash commands, skills or CLAUDE.md files are loaded, and nothing is saved to disk.

  python3 scripts/run_claude_code.py --out private/runs/<name>/responses.jsonl [--pilot] [--live]

Default is a zero-cost stub that never starts Claude Code. `--live` sends real calls.
`--capture-url http://127.0.0.1:<port>` sends them to a local capture server instead (for checking
exactly what Claude Code transmits; nothing leaves the machine).
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PILOT = [("T19", "natural_question", "volume_only"), ("S3-37", "explicit_rule", "volume_only"),
         ("S3-02", "natural_question", "full_history")]
# Environment passed to Claude Code: enough to find the binary and the signed-in subscription, nothing else.
MAX_TOKENS = 8192
KEEP_ENV = ("HOME", "PATH", "USER", "LOGNAME", "LANG", "TMPDIR", "SHELL")
QUOTA_WORDS = ("rate limit", "rate_limit", "usage limit", "quota", "429", "overloaded", "credit")
AUTH_WORDS = ("authenticate", "oauth", "not logged in", "login", "401", "invalid api key")


def classify(message, fallback):
    m = message.lower()
    if any(w in m for w in AUTH_WORDS):
        return "auth"
    return "quota" if any(w in m for w in QUOTA_WORDS) else fallback


def order_key(model, sha, repeat):
    return hashlib.sha256(f"order-v1|{model}|{sha}|{repeat}".encode()).hexdigest()


def command(model, effort, system):
    return ["claude", "-p", "--model", model, "--effort", effort, "--system-prompt", system,
            "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--setting-sources", "", "--disable-slash-commands", "--no-session-persistence",
            "--output-format", "json"]


def stub_call(req):
    body = ({"finding": "cannot_determine", "evidence_ids": [], "explanation": "Stub response."}
            if req["framing"] == "natural_question"
            else {"verdict": "insufficient_outcome_evidence", "evidence_ids": [], "reason": "Stub response."})
    return {"status": "ok", "stop_reason": "end_turn", "text": json.dumps(body), "models_used": [], "usage": {}}


def live_call(model, effort, req, capture_url, timeout, dummy_key=False):
    env = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(MAX_TOKENS)  # match the API arms' output limit
    if capture_url:
        env["ANTHROPIC_BASE_URL"] = capture_url
        if dummy_key:  # placeholder key accepted only by the local capture server
            env["ANTHROPIC_API_KEY"] = "placeholder-key-for-local-capture"
    work = tempfile.mkdtemp(prefix="cc-")  # empty folder: no project files or CLAUDE.md to discover
    try:
        p = subprocess.run(command(model, effort, req["messages"][0]["content"]), input=req["messages"][1]["content"],
                           capture_output=True, text=True, cwd=work, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "failed", "error": "timeout"}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    try:
        out = json.loads(p.stdout)
    except ValueError:
        err = (p.stderr or p.stdout)[-300:]
        return {"status": "failed", "error": classify(err, f"exit_{p.returncode}"), "detail": err}
    text = out.get("result") or ""
    if out.get("is_error"):
        return {"status": "failed", "error": classify(text, "error"), "detail": text[-300:]}
    return {"status": "ok", "stop_reason": out.get("stop_reason") or "end_turn", "text": text,
            "num_turns": out.get("num_turns"), "models_used": sorted((out.get("modelUsage") or {}).keys()),
            "usage": out.get("usage") or {}, "notional_cost_usd": out.get("total_cost_usd"),
            "duration_api_ms": out.get("duration_api_ms")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requests", type=Path, default=ROOT / "private" / "requests.jsonl")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--effort", default="low")
    ap.add_argument("--repeats", type=int, default=4)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--cases", help="comma-separated case IDs to restrict to (e.g. T19)")
    ap.add_argument("--max-calls", type=int)
    ap.add_argument("--live", action="store_true", help="start Claude Code for real (otherwise stub)")
    ap.add_argument("--capture-url", help="send live calls to a local capture server instead of Anthropic")
    ap.add_argument("--capture-dummy-key", action="store_true", help="with --capture-url: authenticate to the capture server with a placeholder key")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()
    if args.capture_dummy_key and not args.capture_url:
        sys.exit("STOP: --capture-dummy-key only works with --capture-url")

    reqs = [json.loads(l) for l in args.requests.read_text().splitlines()]
    if args.pilot:
        reqs = [r for r in reqs if (r["case_id"], r["framing"], r["view"]) in PILOT]
    if args.cases:
        keep = set(args.cases.split(","))
        reqs = [r for r in reqs if r["case_id"] in keep]
    repeats = 1 if args.pilot else args.repeats
    mode = ("capture" if args.capture_url else "claude_code") if args.live else "stub"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.out.exists():
        prior = [json.loads(l) for l in args.out.read_text().splitlines()]
        if any(r["mode"] != mode for r in prior):
            sys.exit("STOP: --out already holds calls from another mode; use a new file")
        done = {(r["model"], r["request_sha256"], r["repeat"]) for r in prior}
    jobs = sorted(((r, k) for r in reqs for k in range(repeats)), key=lambda j: order_key(args.model, j[0]["request_sha256"], j[1]))
    jobs = [j for j in jobs if (args.model, j[0]["request_sha256"], j[1]) not in done]
    if args.max_calls is not None:
        jobs = jobs[:args.max_calls]

    sent = failed = 0
    stop = None
    with args.out.open("a") as f:
        for req, repeat in jobs:
            started = time.time()
            rec = live_call(args.model, args.effort, req, args.capture_url, args.timeout, args.capture_dummy_key) if args.live else stub_call(req)
            if rec["status"] == "ok" and rec["models_used"] and rec["models_used"] != [args.model]:
                rec["model_mismatch"] = True  # a different or additional model answered; reported, never pooled
            row = {"mode": mode, "harness": "claude_code", "model": args.model, "effort": args.effort,
                   "request_sha256": req["request_sha256"], "case_id": req["case_id"], "framing": req["framing"],
                   "view": req["view"], "repeat": repeat, "pilot": args.pilot, "latency_s": round(time.time() - started, 2),
                   "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **rec}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            sent += 1
            failed += rec["status"] != "ok"
            if rec.get("error") in ("quota", "auth"):
                # seat-metered rule: the first quota, rate-limit or sign-in error ends the run, no retry
                stop = "quota_or_rate_limit" if rec["error"] == "quota" else "not_signed_in"
                break
    print(json.dumps({"mode": mode, "calls_written": sent, "failed": failed, "already_done": len(done),
                      "stopped": stop, "out": str(args.out)}))


if __name__ == "__main__":
    main()

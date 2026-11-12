# November frontier run: Claude Sonnet 5.5 through Claude Code

**Status: exploratory.** On November 12, 2026, Fide sent the frozen request payloads from the preregistered frontier replication to Claude Sonnet 5.5 through Claude Code. This folder holds the plan, the published counts, the exact inputs and responses for Splunk history T19, and the scripts used. It sits outside `study/`, which preserves the October package.

## What was run

- **Histories:** 20. All eight failed reads and seven successes from the Ariel Cyber records, T19 (Splunk) and the OTRF history from the October transfer test, and three short windows from a separately published troubleshooting case (a denied read, a successful read, and one of each).
- **Views:** requests only; requests with byte counts ("byte-only"); the complete record. The error fields are withheld in the first two, and the model is told so.
- **Framings:** `explicit_rule` uses the October clarified instructions, including "An unavailable errorCode is unknown, not null." `natural_question` asks whether S3 returned the object's data, with only a note that the named fields were removed.
- **Calls:** 120 payloads, each four times: 480 calls. A three-call pilot ran first and is excluded from every count.
- **Model and route:** `claude-sonnet-5-5` at effort `low` with an 8,192-token output limit, through Claude Code 2.1.317 (`claude -p`) on a subscription. Each call ran in an empty temporary folder, with no tools, MCP servers, setting sources, hooks, slash commands or skills, and with the payload's system prompt replacing Claude Code's own. A response from any other model would have been reported separately; none occurred.

Claude Code adds text the planned API arms will not have: a billing line, one sentence of agent identity, an environment section after the records (a temporary folder path, operating system, model name and date), and a context block giving the signed-in account's email address. A local capture of the outgoing request confirmed that nothing else was added: no tools, project files or other instructions. These additions are why the run is exploratory. Its results are never pooled with API results, and the preregistered API arms (Claude Opus 5.5 primary, Sonnet 5.5 and Haiku 5.5 secondary) have not been run.

## The plan was fixed first

[PROTOCOL.md](PROTOCOL.md) is the preregistration, byte-identical to the version committed before the first call (SHA256 `f72d6ecb6f3f26cb67d70e348cea858fa3de6cd817ecbee0b221adbf5487b1c2`). Its section "Exploratory phase: Claude Code (Sonnet 5.5)" governs this run. The plan names some files that stay private: internal operating notes, the run's raw output files, the release-check script (its patterns name internal paths and people), and the export script that depends on it. `data/` is that export script's output, unchanged, plus the T19 inputs.

## Results

| Claude Sonnet 5.5, 80 calls per cell | Complete record: correct | Requests only: definite finding | Byte-only: definite finding |
|---|---:|---:|---:|
| Evidence rule stated | 80 of 80 | 0 of 80 | 0 of 80 |
| Plain question | 76 of 80 | 0 of 80 | 18 of 80 |

- The 18 plain-question byte-only findings came from seven histories, all of them histories where the data had been returned. Three histories (S3-05, S3-22, T25) gave a finding in all four repeats.
- The four complete-record misses are one mixed troubleshooting window, answered "cannot determine" each time.
- The pattern screen flagged 75 explanations. A flag is a screen for wording that may assert a withheld value, not a finding. Human review remains pending: the protocol requires blinded review of all flags, a 20% random sample of unflagged incomplete-view explanations, and agreement on a 20-explanation double-coded subset. The 18 definite byte-only explanations also need review; these sets can overlap.

## Check it

From the repository root, with Python 3.11 and no network:

```sh
python3 frontier/scripts/check_frontier.py
python3 frontier/scripts/decoys.py
```

`check_frontier.py` rescores all 24 T19 responses from their exact inputs with the frozen scorer and pattern screen, checks request hashes and cited record IDs, and verifies that the per-cell counts, per-history counts and flag list agree with one another and with the numbers in the research perspective. `decoys.py` runs the 12 preregistered decoys and 10 extra scoring checks on synthetic inputs.

## Files

| File | Contents |
| --- | --- |
| `PROTOCOL.md` | Preregistration, unchanged since the freeze |
| `data/aggregates.json` | Counts per harness, model, framing and view, plus premature findings per history |
| `data/flags.jsonl` | Every screened explanation: history, framing, view, repeat and pattern names, without text |
| `data/responses-splunk.jsonl` | The 24 T19 responses with full text and scores |
| `data/requests-splunk.jsonl` | The six T19 payloads exactly as sent |
| `scripts/score.py` | The frozen scorer and pattern screen. It calls the October scorer in `study/scripts/reproduce.py`; only its path to that scorer was changed for this repository |
| `scripts/decoys.py` | Preregistered scorer decoys |
| `scripts/check_frontier.py` | The offline check above (written for this release) |
| `scripts/build_requests.py` | How the 120 payloads were built from the October inputs |
| `scripts/run_claude_code.py`, `scripts/capture_server.py` | The Claude Code runner and the local capture server used to inspect what it sends |
| `scripts/run_calls.py` | The planned API caller, not yet used |

Only T19 ships with response text and inputs. The other 19 histories come from Ariel, OTRF and blog-transcript material whose redistribution terms are unresolved, so they appear as counts and pattern names only. The payload builder and runners therefore document the method; they cannot be rerun from this repository alone.

Licensing follows [LICENSING.md](../LICENSING.md). Field definitions are in [DATA-DICTIONARY.md](../DATA-DICTIONARY.md#frontier-run-files).

## Supporting claims need their own check

A follow-up close reading found three responses from two histories that qualified the read outcome while overstating a preceding write. No literal null error-field value was supplied, but that is not a blanket finding that the explanations contain no unsupported assertions. The distinction, response locators and pending human adjudication are documented in [the interpretation note](INTERPRETATION-NOTES.md). Frozen evidence and numerical results are unchanged.

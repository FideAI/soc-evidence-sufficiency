# Changelog

## 0.2.0 — 2026-11-12

Owner review accepted. Dates the report and citation metadata to November 12, sets the website article to published status for the next deployment, and prepares a versioned public companion. Research inputs, model responses, scores and frozen protocols are unchanged. The unadjudicated explanation-screen endpoint is not promoted to a replication result. The versioned GitHub release records the published package; website deployment is a separate release operation.

## 0.2.0-rc.1 — 2026-11-12 (prepared, not released)

Adds an exploratory frontier run in a new `frontier/` folder and revises the Insights article to report it.

- `frontier/PROTOCOL.md`: the preregistration, byte-identical to the version committed before the first call.
- `frontier/data/`: per-cell and per-history counts for 480 calls to Claude Sonnet 5.5 through Claude Code (20 histories, three views, two framings, four repeats), the pattern-screen list without text, and the exact inputs and responses for Splunk history T19 (24 responses). Responses for the other 19 histories are not included because their source material has no cleared redistribution rights.
- `frontier/scripts/`: the frozen scorer and pattern screen (only its path to the October scorer changed), the scorer decoys, the payload builder, the Claude Code runner, the local capture server, the planned API caller, and a new offline check, `check_frontier.py`, which rescores the T19 responses and checks the published counts.
- `study/publication/INSIGHT.md`: rewritten as "What AI investigators do with evidence they don't have", leading with the T19 record and the four answers it received, and adding the frontier results and their limits. October counts, quotations and the table are unchanged.
- `study/publication/TECHNICAL-PAPER.md`: adds Section 9 on the November run (design, harness additions, scoring, results by framing and view, the matched local comparison, adjudication status, exposure and conflict of interest), an abstract paragraph, open questions in Section 10.1 and the `frontier/` files in Section 11. Sections on the October study are unchanged apart from renumbering and one sentence noting that the Claude run does not test the systems in the cited incident reports. `study/MANIFEST.json` was refreshed.
- Repository README, data dictionary, licensing map, citation metadata, CI and the release verifier now cover `frontier/`.

The frontier run is exploratory: Claude Code adds its own text to each request, and no result is pooled with the October study or with the preregistered API arms, which have not been run. The pattern screen and the 18 plain-question byte-only conclusions await human adjudication. October experimental data, labels, scoring and the 996-row ledger are unchanged. No public release or independent human acceptance is claimed.

The November 12 interpretation pass distinguishes an asserted unseen field value from a disclosed inference, makes downstream caveat loss explicitly hypothetical, and simplifies the article subtitle and harness explanation. The technical note aligns; frozen evidence, scores and protocol are unchanged.

The final review restores the sequential-formatting caveat, marks the explanation text check as provisional, specifies the complete preregistered human-review gate, and corrects the checksum handoff instructions. No protocol, source evidence or numerical results changed.

The disputed-case review narrows the no-literal-null observation and documents three ancillary-write overstatements from two histories in a separate interpretation note. Human codebook adjudication remains pending. Frozen evidence, scores, screen flags and saved AI judgments are unchanged; excluded raw response text is not redistributed.

The reading-flow pass shortens the essay by about 1,000 words, states the evidence-support thesis directly, and removes internal review workflow and detailed run plans from the public reading path. Full methods and review requirements remain in the technical note. Counts, exact quotations, tables and source evidence are unchanged.

## 0.1.0-rc.2 — updated 2026-11-11 (prepared, not released)

Reframes the Insights article as a research perspective, retains the full empirical account in a supporting technical note, and adds concrete collaboration routes and falsifiable follow-up questions. Updates companion guidance, manifests and version metadata. Experimental inputs, responses, labels, scoring, source selection and all 996 evaluated results are unchanged. The rc.1 tag and its uploaded release assets remain immutable. No new inference, public release or independent human acceptance is claimed.

The October 27 review correction distinguishes ambiguous original-label answers from explicit unavailable-field assertions, explains the repeated Splunk input template, adds prior attribution/abstention work, and sharpens the proposed follow-up comparison. A new descriptive audit outside the preserved study directory makes these interpretation checks reproducible on the included subset. No reference labels or original scores changed.

On November 11, the manuscripts and companion guidance were aligned around the evidence people need before relying on AI findings. A pinned single-example review task gives contributors a concrete starting point. The independent review comparison and longer-term action research remain proposed; no new experiment or release is implied.

The subsequent on-site readability review simplifies the article’s language and shortens its closing argument. Methods, counts, quotations and the technical note remain unchanged. The website also fixes a clipped mobile table explanation; this changes presentation only.

The November 11 voice pass leads with why a citation deserves checking, develops the 277-byte example, and makes Fide’s judgment and invitation more conversational. Experimental evidence, counts, quotations and the technical note are unchanged.

A subsequent editorial pass opens with the 277-byte example and the T19 unavailable-field assertion, places the right-answer-without-evidence point beside the all-success transfer results, consolidates repeated statements of the argument, and points the invitation at T19. Experimental evidence, counts, quotations, figures, table and the technical note are unchanged.

## 0.1.0-rc.1 — 2026-10-26

First versioned release candidate of the standalone study companion.

- Preserves the original 21-file study package and source archive fingerprint.
- Includes manuscripts, 996 categorical decision records, 306 exact Splunk replays, scoring and source-verification scripts.
- Adds a data dictionary, join example, citation metadata and explicit component licensing.
- Provides offline reproduction and pinned-source checks in CI, plus release integrity and documentation checks.

No new inference, data selection, response edits, reference-label changes or empirical claims are introduced in this packaging release. The 690 excluded source-dependent replays remain outside the export. This candidate is not the publication of the website article or a claim of independent human methods acceptance.

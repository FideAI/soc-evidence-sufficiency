# Release candidate 0.2.0-rc.1

This candidate adds the exploratory November frontier run, Claude Sonnet 5.5 through Claude Code, in `frontier/`, and revises the Insights article and the technical note to report it. The October study package under `study/` keeps its experimental evidence and scripts byte-identical; only the two manuscripts and the manifest changed there. This candidate is prepared locally; it has not been tagged or uploaded as a GitHub release. The v0.1.0-rc.1 tag and draft release remain unchanged, and 0.1.0-rc.2 was never tagged. The repository remains private and the website article unpublished until the owner approves release. Candidate status is intentional; a tag or passing CI does not imply peer review or methods acceptance.

## Contents and verification

The release ZIP contains the complete standalone candidate from the reviewed working files, without `.git`, private workspace history, local environments or excluded source archives. The website download is paired with `companion.sha256`. Publish an equivalent checksum with any GitHub release. `PACKAGE-PROVENANCE.json` records the 21 current study files, their original hashes and the original companion archive fingerprint; `frontier/MANIFEST.json` records the frontier files.

From an extracted release directory, run the commands in [README.md](README.md). Python 3.11 and its standard library suffice. The source-verification command alone retrieves a pinned public file; the remaining commands run offline.

A successful check establishes:

- Package integrity, for both `study/` and `frontier/`, and valid local documentation links.
- Arithmetic reconstruction of 996 categorical decisions, not 996 independent cases.
- Rescoring of 306 preserved Splunk responses and reconstruction of their 306 input views from 24 source histories.
- Ten semantic scoring boundaries and 24 included unavailable-field assertion examples.
- A post-review interpretation audit of original-label wording, repeated input structure and formatting chronology. This audit is descriptive, not a new experiment.
- Rescoring of the 24 frontier-run responses for T19 from their exact inputs, agreement among the frontier run's published counts and with the numbers in the article, and the preregistered scorer decoys.

It does not reproduce fresh model inference, validate the excluded October responses or the frontier run's other 19 histories from raw evidence, adjudicate the frontier pattern screen, authenticate the original cloud service, or establish operational defense effectiveness.

## Before public release

1. Complete the protocol’s blinded human review of all flagged explanations and a 20% random sample of unflagged incomplete-view explanations. Report agreement on the 20-explanation subset double-coded by two people. Also adjudicate the 18 plain-question byte-only conclusions; these review sets can overlap. Record the results before deciding the replication criterion.
2. Resolve the ancillary-write interpretation concerns in `frontier/INTERPRETATION-NOTES.md` within that human review; the separate AI check and assistant close reading do not satisfy it. Record the owner's methods/editorial acceptance and approval of the limited export, including the frontier files.
3. Make only this dedicated study repository public; do not expose the internal research workspace.
4. Publish the approved release and its checksum, updating candidate language to match the actual decision. Keep candidate tags immutable; use a new version for subsequent changes.
5. Check unauthenticated access to the README, manuscripts, evidence files and downloadable archive.
6. Publish the website article separately after its links and production build are checked. The article's links to this repository are pinned to an earlier commit and should be updated to the released one.

The preserved package's candidate-status labels are provenance. They are not evidence of current repository visibility, and should not be rewritten merely to change a release label. The current top-level README and release record state the actual status.

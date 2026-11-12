# Release 0.2.0 · November 12, 2026

**Release version 0.2.0.** Fide’s owner reviewed the package and authorized its public release on November 12, 2026. The [v0.2.0 tag](https://github.com/FideAI/soc-evidence-sufficiency/tree/v0.2.0) identifies the source snapshot; the [GitHub release](https://github.com/FideAI/soc-evidence-sufficiency/releases/tag/v0.2.0) supplies the complete ZIP and SHA256. The report and citation date are November 12, 2026. The article and matching download are published separately on Fide’s website.

## Approved scope

The research perspective and supporting technical note cover the October local-model study (`study/`) and the exploratory November Sonnet run (`frontier/`). Their counts remain separate: 996 and 480 calls. The package includes 306 exact October Splunk responses and 24 exact November T19 responses, aggregate counts, frozen instructions and protocol, scoring scripts and source-verification instructions.

The 690 excluded October responses, non-T19 frontier raw responses, source archives, model weights, local environments, private review records and later defense experiments stay outside this release. Only this standalone repository is intended to become public. Fide’s internal cyber research and website source repositories remain private.

Owner acceptance is not represented as independent peer review or as the protocol’s blinded, double-coded adjudication. The explanation-screen criterion is not reported as a replication pass or failure. No saved review judgment, protocol, score or model response has been changed to obtain release readiness.

## Validation

Run all commands in [README.md](README.md) from a clean extraction. Python 3.11 and its standard library suffice. The source-verification command alone downloads a pinned public file; the others run offline. The manifest and provenance records cover the preserved study package and separate frontier files. The website download carries `companion.sha256`.

These checks rescore retained responses and reconstruct published counts. They do not generate fresh model outputs. Source and inference scope are documented in the technical note, source notices and data dictionary.

## Coordinated release procedure

1. Merge the dedicated companion PR, preserving the pre-run protocol history, then tag the approved commit `v0.2.0` without moving earlier candidate tags.
2. Build the 52-file source package from that commit and publish its ZIP and SHA256. Verify the website’s matching copy before deployment.
3. Make **only `FideAI/soc-evidence-sufficiency`** public and publish the versioned release. Check the repository’s history and PR discussions as part of that visibility operation.
4. Verify anonymous access to the README, version tag, evidence files and release download.
5. Merge the website PR and deploy through the normal production workflow. Verify the article, date, discovery listings, technical note and downloads. Other publication holds remain in force.
6. Record actual release URLs, commit IDs, checksums and deployment verification in the private release receipt. Use the version tag and release record to identify the approved source snapshot.

The earlier `v0.1.0-rc.1` tag and draft release remain immutable historical candidates. The original preregistration, experimental dates and evidence-source dates are preserved.

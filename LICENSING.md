# Reuse and attribution

Copyright © 2026 Fide AI for Fide-authored material. This repository contains material under different licenses; the root MIT license does not replace third-party terms or apply indiscriminately to every file.

| Material | Terms |
| --- | --- |
| Fide-authored Python scripts and CI configuration, including `scripts/`, `study/scripts/`, `frontier/scripts/` and `.github/workflows/` | [MIT](LICENSE) |
| Fide-authored manuscripts in `study/publication/`, README files, data dictionary, contribution/release documentation and citation/provenance metadata | [CC BY 4.0](LICENSES/CC-BY-4.0.txt), excluding separately attributed third-party material |
| Fide-created classifications and aggregates in `study/data/decision-ledger.json` and `study/data/aggregates.json`, and Fide-authored instructions in `study/data/contracts.json` | [CC BY 4.0](LICENSES/CC-BY-4.0.txt) |
| Fide's selection, annotations, prompt text and other contributions to `study/data/splunk-replay.jsonl` and `study/data/splunk-locators.json` | [CC BY 4.0](LICENSES/CC-BY-4.0.txt), to the extent Fide holds rights; underlying Splunk-derived material retains its separate terms below |
| Splunk-derived records and identifiers within those replay and locator files | [Apache-2.0](study/licenses/Splunk-Apache-2.0.txt); preserve the [source attribution and transformation notice](study/THIRD-PARTY-NOTICES.md) |
| The frontier run's preregistration (`frontier/PROTOCOL.md`), README, Fide-authored interpretation note (`frontier/INTERPRETATION-NOTES.md`), classifications and counts (`frontier/data/aggregates.json`, `frontier/data/flags.jsonl`), and Fide-authored prompt text in `frontier/data/requests-splunk.jsonl` and `frontier/data/responses-splunk.jsonl` | [CC BY 4.0](LICENSES/CC-BY-4.0.txt), to the extent Fide holds rights; the Splunk-derived records in those files retain Apache-2.0 terms, and no rights are claimed in Claude's generated response text |
| Recorded model configuration and artifact identifiers under `study/model-metadata/` | Fide's documentation contributions are CC BY 4.0; no model weights, upstream model licenses, or rights in third-party material are granted |
| License texts and separately attributed third-party quotations | Retain their existing notices and terms; these are not relicensed as Fide-authored work |

The CC BY grant covers copyright and database rights Fide can license. It does not assert copyright in bare facts or every generated model output, and it does not grant rights Fide does not hold. A cited source is not automatically licensed by this repository. No excluded archive, response packet or model weight is covered by these grants.

## Attribution

For Fide material, credit **Fide AI**, name the study **What AI investigators do with evidence they don't have**, link to this repository and the applicable license, and indicate changes. Include the version or commit when reporting a result. [CITATION.cff](CITATION.cff) supplies citation metadata. Preserve the Splunk attribution when reusing its derived records.

## Preserved package

The experimental evidence, code, model metadata and source notices under `study/` retain their original bytes. The manuscripts and README have a documented editorial revision; PACKAGE-PROVENANCE.json records original and current hashes. The original package remains available at the v0.1.0-rc.1 tag. This document adds explicit reuse permission for Fide-authored manuscripts, data and documentation without removing any existing permission. Scientific release status is recorded separately in [RELEASE.md](RELEASE.md).

# Evidence sufficiency in AI cloud-log investigation
## Technical note supporting a research perspective on investigative evidence

Fide AI · Technical research note · Experiments October 16, 2026 · Editorial framing updated October 26, 2026 · Context includes reports through October 23, 2026

### Abstract

We test whether two local language-model artifacts distinguish a recorded request from an outcome justified by the evidence available to them. These experiments support Fide’s research perspective: evaluations should check whether the available evidence justifies each finding, alongside answer accuracy and citation validity. Across all 25 clarified byte-only main-transfer explanations, Gemma describes a withheld error field as null while citing existing record IDs. The central observed failure is a gap between citation validity and evidential support: real citations can accompany assertions about unavailable fields. This supplies a concrete motivation for further study, without estimating the prevalence of the failure beyond this setup.

An initial comparison uses six evidence views of 40 public AWS object histories, including eight with failed reads. Both artifacts correctly classify every complete target history, while adding byte counts to request-only evidence increases Qwen's unsupported definite answers from 4/40 to 40/40; Gemma produces 40/40 under either incomplete view. An exploratory instruction change on twelve reused histories reduces premature answers. We freeze that intervention and test it prospectively on 25 new histories from two independently published captures. Across 50 incomplete views per artifact, premature answers change from 50 to 25 for Gemma and 25 to zero for Qwen; complete-history accuracy stays 25/25. In a prespecified formatting check, all six Gemma byte-only answers change to correct abstentions when JSON whitespace and key order change without changing record values or instructions. Qwen remains correct on six. Instruction and representation comparisons delimit that finding. They do not estimate operational SOC error rates or establish a general formatting remedy.

### 1. Question and contribution

A service can return bytes because it returned an error message. A log naming a request therefore differs from a log supporting a successful object response. We test whether models preserve this distinction when decisive fields are deliberately unavailable, and whether clearer instructions transfer to records not used to develop those instructions.

We document unsupported service-outcome claims accompanied by valid record identifiers, with retained inputs and responses that make the mismatch inspectable. The study combines controlled evidence removal, an exploratory wording intervention, a prospective test on new captures, and a formatting check that preserves record values and instructions. The distinction between evidence and conclusion is established research territory. The claim is neither a new S3 rule nor a first discovery that prompts and formatting matter.

AuditBench evaluates security-log investigation across tasks, prompts and representations, and cautions that design effects can vary across models. Our paired intervention instead targets whether visible fields justify a particular service-outcome claim, including the required unresolved answer when fields are withheld. ExCyTIn-Bench evaluates graph-derived questions and interactive threat investigation; we neither reproduce its task nor compare our counts to its scores. ALCE separates answer quality from citation support; our verdict/citation separation applies that general distinction to a narrow structured task. See references.

ALERT-BENCH evaluates agents that retrieve telemetry through a live SIEM, and AIDA structures proposed decisions, independent challenge and adjudication with stronger requirements before dismissal. Its reported improvement concerns alert-triage outcomes in replayed scenarios. Our task fixes the evidence supplied and varies the availability of decisive fields; it measures support for a service-outcome claim rather than retrieval, maliciousness or alert disposition. We do not evaluate AIDA, reproduce its results or compare its scores with ours. [Tsegai et al., v1](https://arxiv.org/html/2610.10608v1) is complementary prior work on the wider investigation process.

The research perspective makes a recommendation: evaluate the support for individual findings, including the cost of withholding justified findings. The experiments document specific behavior under controlled evidence removal. They do not establish a general solution or demonstrate that field-level review improves operational defense. Section 9.1 describes questions for collaboration, not additional completed experiments.

### 2. Sources and observations

| Stage | Source | Selected unit | Key dependence and coverage limits |
|---|---|---|---|
| Initial | Ariel Cyber Cloud Log Sampling | 40 object histories: 8 failed, 16 successful with later deletion, 16 successful without later deletion | Three dates and 23 selection groups in one deployed lab environment; not 40 independent incidents |
| Exploratory instruction change | Same Ariel source | 12 reused histories: all 8 failed and 4 successful | Already observed cases; no new source evidence |
| Prospective main test | Splunk attack_data; OTRF Security-Datasets | 24 Splunk histories and 1 OTRF history containing 2 reads | Two captures, all reported successful outcomes; Splunk timestamps identical |
| Separate challenge | Y_Yamashita troubleshooting account | Denied-only, success-only and mixed windows over 2 events | Three dependent windows from one partly masked account, outside main counts |

Ariel's three source archives contain 44,798 rows. Removing 17 exact duplicate event IDs leaves 44,781 events. The frozen eligibility criteria exclude missing target reads, ambiguous same-second ordering, oversized histories and other out-of-scope conditions. Of 1,150 eligible histories, all eight failed-read histories were selected. Successful cases were selected by fixed hash ordering with allocation across date/bucket/source-label groups. All ten failed target GetObject events in the selected failed histories report NoSuchKey with positive bytes. Publisher attack labels do not define the reference and are absent from model inputs.

The transfer selection takes the first 24 Splunk object groups in a fixed hash order and the single qualifying OTRF group. Independent collection is supported by the publishers' collection descriptions, different recorded accounts and nonoverlapping event IDs. The selected transfer events have zero event-ID overlap with all 44,781 earlier events. These checks do not authenticate the underlying AWS service or prove exclusion from model training. Sources were inspected for qualification before model evaluation; this was not source-outcome-blind sampling.

The separate author transcript reports AccessDenied with 452 bytes, followed by a no-reported-error response with 791 bytes. It supplies another concrete error-with-bytes example, but is not an independently authenticated failure corpus. OTRF exports @timestamp rather than eventTime; we retain that supplied time without claiming original-event-clock authentication. We found no qualifying independent raw failure cohort in the bounded source screen. The failed leads and exclusions remain recorded.

### 3. Reference semantics

We match GetObject records to the stated bucket, object and time window. A matching record with available errorCode explicitly normalized to null and positive available response bytes supports a recorded object-data response. If all shown matching reads have explicit service errors, they support failure of those shown requests. Otherwise the evidence is insufficient.

For these complete public S3 source records, an absent source errorCode is normalized to null, meaning no reported service error. Deliberately withheld fields are removed and listed as withheld; they never inherit that normalization. All included source responseElements are null. This convention is limited to the qualified S3 exports. AWS documents that error reporting can differ by service, and an empty responseElements field does not establish failure of a read-only action.

The reference is conditional on source fidelity. It establishes neither complete-file receipt by a client nor authorization, maliciousness, absence of other unrecorded activity or effective containment. We have no full HTTP bodies, client receipts or authenticated CloudTrail digest chain. “Recorded object-data response” is a study label for the specified field predicate.

Our endpoint is evidence-relative. Matching a withheld source outcome by guessing is not enough. Conversely, when a complete failure is visible, abstention is an error. This prevents an always-abstain rule from appearing useful without a cost.

### 4. Design and execution chronology

The initial study compares requests only, requests plus byte counts, complete outcomes, requests plus eight other-object records, complete outcomes plus those records, and complete outcomes plus a fixed interpretation guide. It uses 40 histories × six views × two artifacts = 480 calls. Four prior synthetic format checks are disclosed separately, including a premature answer on missing evidence; no subsequent original-prompt tuning followed that exposure. A six-history subset, two per source stratum, supplies 72 exact repeats.

After observing the initial results, we changed labels and explicit evidence guidance together. This cannot isolate the effect of wording from the effect of label names. The intervention was frozen before 72 diagnostic calls on twelve reused histories. It is exploratory, not held-out confirmation. Comparisons use the identical twelve original cases.

Both original and clarified instruction strings were then copied unchanged to the prospective transfer test. The protocol, source selection, inputs and scorer were locally hashed before inference. This is a prospective local freeze, not external preregistration. Twenty-eight windows × three views × two contracts × two artifacts yield 336 calls: 300 main and 36 separate challenge calls. Six preselected windows supply 24 exact clarified byte/full repeats and twelve clarified byte-only formatting calls. The latter sort keys and indent JSON while retaining the same parsed values and instructions. No response-driven format search was performed.

The combined total is 996 evaluated calls: 480 initial, 72 initial repeats, 72 exploratory intervention, 336 transfer, 24 transfer repeats and twelve formatting checks. These are computational assignments, not independent incidents. Four development calls bring the recorded inference total to 1,000; they are excluded from study result denominators.

Both stages use existing local Ollama artifacts with temperature 0, seed 20261016, context limit 8192, output limit 512, thinking disabled and JSON responses. Calls are stateless, hash-ordered within artifact and preserved without correctness retries. Runtime unloading manages memory between groups. No paid inference or new model weights were used. Retained artifact digests and distribution correspondence appear in the [model reproduction appendix](../MODEL-REPRODUCTION.md). This is not a representative comparison of model vendors or a model-market ranking.

### 5. Scoring and baseline

We report valid response, correct verdict, premature definite conclusion and citation-supported correct verdict separately. A premature conclusion is a definite verdict where the displayed evidence supports only insufficient evidence. The original primary endpoint requires strict citation support. Its separately recorded contextual-citation sensitivity does not change any initial primary result. The transfer endpoint focuses on premature conclusions and complete-history correctness, with citation support reported alongside. The transfer scorer permits extra relevant visible context if decisive support is cited. We therefore compare plain verdicts across stages and do not pool citation metrics across different rules.

Citation scoring verifies support for the categorical verdict, not every assertion in the reason sentence. A separate post-observation descriptive audit checks whether explanations call withheld error fields null. All outputs, invalids and exceptions are retained; no invalid or transport-failed study calls occurred, and no response hit the output cap.

A deterministic predicate using these visible fields implements the reference by construction. The transfer gate retains supported categorical model verdicts and replaces unsupported ones with insufficient evidence. Its agreement with the reference on this deliberately structured task is not independent evidence of operational defensive efficacy. It neither retrieves missing facts nor repairs false abstention. Gate results cannot substitute for the ungated model results.

### 6. Initial results and counterevidence

| Artifact | Requests only: correct / premature | Add bytes: correct / premature | Complete target: correct |
|---|---:|---:|---:|
| Gemma | 0/40; 40/40 | 0/40; 40/40 | 40/40 |
| Qwen | 36/40; 4/40 | 0/40; 40/40 | 40/40 |

For Qwen, adding bytes changes 36 correct abstentions to premature conclusions and corrects none. The two views have the same insufficient-evidence reference. This identifies an effect of the input bundle in this fixed comparison, not a measured internal reasoning mechanism.

Adding other-object context improves request-only correct abstention from 0 to eight for Gemma and from 36 to 40 for Qwen. With full target outcomes it produces two Gemma regressions and no Qwen regression. A guide supplied only with complete outcomes produces no gain, because both artifacts already score 40/40. The results do not support a blanket claim that more context hurts. The 72 exact repeats change no verdict, validity state or citation set.

In the exploratory twelve-case comparison, premature incomplete-evidence answers change from 24/24 to 9/24 for Gemma and 12/24 to zero for Qwen. Complete-history accuracy remains 12/12 for each. All nine remaining Gemma byte-only explanations describe a withheld error field as null. This exploratory observation motivated the subsequent unchanged-instruction transfer, not a retrospective claim of confirmation.

### 7. Prospective transfer

| Artifact | Incomplete views: original → clearer premature conclusions | Complete histories: original → clearer correct verdicts |
|---|---:|---:|
| Gemma | 50/50 → 25/50 | 25/25 → 25/25 |
| Qwen | 25/50 → 0/50 | 25/25 → 25/25 |

Each model has 25 corrected incomplete-view decisions and no verdict regressions. The artifact-specific difference is in which views needed or received improvement. Gemma changes every request-only verdict to abstention but retains premature conclusions in every byte-only view. Qwen already abstains on every request-only view and changes every byte-only verdict to abstention. One correct Qwen request-only answer has a nonmatching record ID with one extra final character. Its citation-supported correctness is 24/25, while verdict correctness is 25/25.

In a descriptive audit, every clarified Gemma byte-only explanation across the 25 main histories calls the withheld error field null. All cited record IDs exist. The same explanation pattern occurs in the three challenge windows. This is an inspectable output error, not evidence about hidden model reasoning.

The three separate challenge windows follow the same pattern: both models classify full outcomes correctly; clarified Gemma abstains on request-only but not byte-only views; clarified Qwen abstains on both. These windows deliberately overlap and cannot be added as three independent failures or successes.

### 8. Representation sensitivity

The 24 transfer exact repeats change no verdict, validity state or citation set. Reformatting changes all six selected Gemma byte-only verdicts from premature object-response claims to correct abstentions. Qwen remains correct in all six. Across the twelve formatting calls, correct verdicts therefore change from six to twelve.

These six windows comprise three selected Splunk objects, the OTRF history, and denied/mixed views of the single author transcript. The effect is not six independent replications. Whitespace and key order change together. Full histories were not tested in the alternate format, so preservation of complete-evidence accuracy is unknown. Calls ran in sequential phases; stable exact repeats reduce one simple variability concern but do not eliminate every runtime or order effect. Temperature zero does not guarantee cross-platform determinism.

The finding is presentation-sensitive adherence to the stated evidence rule. It contradicts a strong interpretation that the remaining Gemma errors establish inability to apply the rule under any equivalent representation. It also supplies no reliable general formatting remedy.

### 9. Limits and implications

The main transfer cohort contains only recorded successful source outcomes, and 24 histories share one capture and timestamp. The initial cohort deliberately includes failures but comes from one collection environment. Counts describe selected cases; population confidence intervals or case-level significance tests would imply an independence structure this design does not supply.

Our normalized schema holds representation mostly constant across publishers. It does not test arbitrary native log parsing, retrieval quality, adversarial prompt injection, multi-agent handoffs or operational containment. The two artifacts, particular runtime and combined wording intervention further bound generalization. Source absence and deliberate withholding are explicitly different states in our reference; transferring that convention to another service requires fresh qualification.

The evaluation implication is to test evidence sufficiency separately from complete-record accuracy and identifier validity. In this task, real record citations coexist with claims about unavailable fields. A field-level check can expose that mismatch, but its agreement with our reference is not a novel algorithmic result.

The operational relevance of this distinction is illustrated by [Microsoft's October 21 ARTEX investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), which separates successful authentication from established customer-data access or exfiltration. This is a contextual parallel, not an incident tested in our study. [AISI's October 23 assessment](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident) reports invalid justifications in cyber evaluations; our observable unavailable-field assertions neither establish motivated reasoning nor explain those incidents. The two local installations here are not a test of the frontier models or deployed systems discussed in those reports.

Evidence availability and evidence interpretation also require separate checks. [METR and Redwood's monitoring assessment](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/) describes coverage and input-representation gaps in the historical system assessed on and before July 21, 2026, not established current coverage. Our experiment assumes a specified input packet and tests what claims the model makes from it; it does not audit collection or monitor coverage.

Stronger evidence requirements must be evaluated against both unsupported conclusions and missed justified conclusions. [Trail of Bits' preliminary regression-review evaluation](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) reports fewer false-positive findings alongside some known regressions remaining unconfirmed under stricter evidence requirements. Our instruction-transfer comparison retains complete-history correctness on the selected cohort while reducing premature answers. That bounded result does not establish the operational tradeoff for other evidence rules or tasks.

Operational efficacy is a separate research question. A historical service outcome does not by itself determine the appropriate containment action; current capability, authority and service dependencies may matter. No action/outcome experiment is included in this paper or its denominators. Establishing a defensive benefit would require measuring consequential actions, continued unauthorized activity and disruption to legitimate work.

### 9.1. Questions for collaborative research

The next question is whether explicit evidence checking adds value beyond ordinary review. A useful comparison would give ordinary self-review, explicit caution and claim-to-evidence review the same records and comparable inference budgets. The last approach would require a reviewer to identify the record, field and value supporting a claim, without access to hidden reference answers. This is a proposed comparison; none of these new review arms was evaluated in the present study.

Evaluation should separately count corrected unsupported conclusions, supported conclusions incorrectly withdrawn, retained correct answers, remaining unsupported explanation claims and computational cost. Agreement with a deterministic scorer that encodes the reference cannot establish the benefit of the review process. If the explicit check performs no better than equally resourced ordinary review, or improves abstention by discarding justified findings, that would count against its proposed benefit.

Useful new cases would include supported successes, supported failures and unresolved evidence across independent captures. Procedures should be fixed before held-out evaluation, with development and testing separated by capture and uncertainty reported at a defensible unit of independence. Reference judgments and source redistribution rights require qualification before inclusion. Prespecified representation checks should cover both incomplete and complete evidence. Fresh model runs also require reproducible model packages; the existing Gemma acquisition limit remains unresolved.

Fide welcomes source-linked corrections, replications, qualified case contributions and evaluations of alternative review methods. Contact [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with a description of the proposed question and contribution; do not send confidential logs or credentials. Proposed extensions must remain separate from the retained results in this note. Operational action and containment benefits require a further study.

### 10. Reproducibility and availability

The source packets retain original bytes, source locators, selection/exclusions, frozen inputs, exact responses, scripts, runtime metadata and manifests. A new offline reconstruction independently implements the scoring rules and matches all 996 recorded verdict/support/premature results. This is a separate scoring implementation within the same research workflow. It is not external validation or fresh inference replication.

The [companion](../README.md) contains a source-free categorical ledger for arithmetic verification of all stages, plus exact normalized requests and responses for 306 Splunk-based calls. A source verifier can retrieve the pinned Splunk file, verify its hash, repeat selection and reconstruct every included input. This provides full source-to-score checking for that licensed subset. It does not independently reproduce excluded-source results from aggregates alone. A separate private replay retains all 996 exact request/response pairs for authorized review.

Ariel's inspected tree has no LICENSE file, OTRF's pinned license/readme conflict is unresolved, and the third-party blog has no identified general redistribution license. Their raw material is excluded. Model weights are excluded. Exact Gemma package acquisition and cross-machine inference reproduction remain unresolved. The public reproduction scope is the retained-response analysis described here; no independently reproduced fresh model run is claimed.

### References

- Anand et al. [Benchmarking and Exploring the Capabilities of LLMs for Attack Investigations (AuditBench), v2](https://arxiv.org/html/2606.10281v2), September 26, 2026. Related-work discussion checked against v2; earlier frozen packet cited v1.
- Wu et al. [ExCyTIn-Bench, v3](https://arxiv.org/abs/2507.14201v3), May 1, 2026. Abstract-level comparison of task construction; no replication claim.
- Gao et al. [Enabling Large Language Models to Generate Text with Citations](https://aclanthology.org/2023.emnlp-main.398/), EMNLP 2023.
- AWS. [CloudTrail record contents](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html), [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html), and [S3 error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). Accessed October 16, 2026.
- Ariel Cyber. [Cloud Log Sampling, pinned commit](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6).
- Splunk. [attack_data, pinned capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject).
- OTRF. [Cloud Bank Breach S3 metadata, pinned commit](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml).
- Y_Yamashita. [Published IAM/IP restriction troubleshooting account](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), March 1, 2026.

- Tsegai et al. [From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage, v1](https://arxiv.org/html/2610.10608v1), October 7, 2026. ALERT-BENCH/AIDA; related work, not a reproduced comparison.
- Microsoft Threat Intelligence. [AI-driven, large-scale nation-state campaign using ARTEX enables supply chain compromise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), October 21, 2026.
- UK AI Security Institute. [Investigating alignment failures in AISI’s incident](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), October 23, 2026.
- Naik and Morales, Trail of Bits. [Your AI agent fixed the bug, but what else did it change?](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/), October 21, 2026.
- Rein and Kaufman, METR. [Red-Teaming OpenAI’s Internal Agent Monitoring Systems](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/), October 22, 2026. Historical assessment; subsequent remediation claims not evaluated by METR.

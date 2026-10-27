# When an AI investigator fills in the missing evidence

An AI investigator can reach the right answer, cite a real record, and still lack evidence for its conclusion. Our experiments show why that distinction matters.

A request for a file appeared in an AWS log. The service sent 277 bytes. Asked what happened, our local Qwen installation described a successful read.

The full record said otherwise. Its error field read `NoSuchKey`: the requested object did not exist. The byte count accompanied an error response.

We had deliberately withheld that error field from the model, and told it the field was unavailable. The right answer was to leave the outcome unresolved. Instead, the byte count became a reason to conclude.

In that case, the answer was wrong. A more revealing problem appeared in our later test: a model reached the right answer, cited a real record, and described an error field we had explicitly withheld as though it had seen the value. Checking only the answer or whether the cited record existed would have missed the unsupported claim.

**AI investigators need to show that their evidence supports their findings. A correct answer and a real citation are not enough.**

At Fide, we made that distinction inspectable in a narrow security task. We gave local installations of Gemma 4 E4B and Qwen 3.8 27B (4-bit) different views of the same logs, withholding and restoring the fields needed to establish an outcome. Readers can compare the supplied records, exact instructions and retained responses, and judge whether the conclusions were warranted.

This matters for autonomous defense because an investigative finding may become the basis for action. Our experiments do not establish how often this failure occurs in deployed systems or whether an additional review step would prevent it. They show why evidence support deserves its own test, alongside answer accuracy and citation validity.

## A number can make an answer feel earned

S3, Amazon's object-storage service, can send an error message in response to a file request. That message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). Our question was whether models would preserve that distinction when the decisive outcome field was missing.

We selected 40 object histories from public cloud records published by Ariel Cyber Innovation Center. Each history groups records concerning the same stored object within a selected time window. Eight contained failed reads. The others contained successful responses, sometimes followed by deletion. These were records of executed lab scenarios, not 40 independently verified breaches.

Each model received several views of every history. Three matter most here: the requests alone; the same requests with byte counts; and the complete recorded outcomes. In the first two views, the service error fields were explicitly withheld.

Both models classified all 40 complete histories correctly under our evidence rules. Here, success means the supplied service record supports an object-data response; it does not prove that a client received an entire file. The task was within both models' demonstrated ability when the relevant fields were present.

The incomplete views told a different story. Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and it gave a definite answer in all 40. In 28 explanations it described a “successful” read or “no reported error,” despite the error field being withheld. On all eight failed-read histories, it claimed a successful read or that a read had occurred. Those answers were wrong as well as unsupported.

Gemma chose our `read_observed` label in every incomplete case, but its explanations only restated that a request had been logged. The label could be read that way. Those choices failed our outcome-based scoring rule, but they are not clear evidence that Gemma invented a successful outcome. Qwen’s four request-only errors also merely described logged events.

The distinction we wanted to test was whether a conclusion was justified, not just whether it happened to be true. The main cohort of our later test made that distinction concrete: every source history reported success, so every answer scored as a premature success also matched the hidden outcome. An outcome-only score would have counted them all as correct. That agreement did not supply the missing evidence.

## We made the rule harder to misunderstand

Our wording was part of the problem we needed to examine. We replaced `read_observed` with `object_data_response` and spelled out the decision rule, including the distinction between an error field explicitly showing no error and one we had withheld. The clarified task tests adherence to that supplied rule; it is not an open-ended investigation.

On twelve reused histories, answers scored as premature fell from 36 of 48 to 9 of 48: Gemma went from 24 to nine, and Qwen from twelve to zero. Eight of Gemma’s nine remaining errors were explicit false success claims on failed-read histories. All complete-history verdicts remained correct. Because the labels and guidance changed together on cases we had already seen, this was an exploratory clarification, not a demonstrated general remedy.

So we kept both instruction sets unchanged and moved to new public captures from Splunk and OTRF. Before running the models, we fixed the selection, requests and scoring. We checked that the selected events did not overlap the earlier source archive. That establishes a new test for our study; it says nothing about what might have appeared in model training.

The new main cohort contained 25 histories: 24 objects from one Splunk capture and one two-read history from OTRF. Every complete history reported a successful response. For each model, two incomplete views per history produced 50 opportunities to make an unsupported claim.

| Local model | Incomplete views scored premature: original rules | Incomplete views scored premature: clearer rules | Complete histories correct: original → clearer |
|---|---:|---:|---:|
| Gemma | 50 of 50 | 25 of 50 | 25 of 25 → 25 of 25 |
| Qwen | 25 of 50 | 0 of 50 | 25 of 25 → 25 of 25 |

These counts need two qualifications. Gemma’s original-rule explanations only restated that requests were logged; its improvement is consistent with resolving the ambiguous label. We cannot isolate the label change from the added guidance.

The 24 Splunk byte-only inputs also repeat one pattern: a single request logged in the same second, differing only in identifiers and byte count. The uniform results show behavior on that pattern and on the separate two-read OTRF history, not 25 independent confirmations.

Both models still classified all 25 complete histories correctly under both instruction sets. These were all successful source histories. One correct Qwen abstention cited a nonmatching record ID with one extra character. We count its verdict as correct and its citation support as failed.

The clearer rules exposed a less ambiguous error. In all 25 Gemma byte-only explanations, it described the withheld error field as `null`, treating it as showing no reported error. The cited identifiers were real. The claimed field value was not in the input. The instructions even said: “An unavailable errorCode is unknown, not null.”

Assertions about missing error information were not unique to Gemma. Under the original rules, Qwen claimed “no reported error” in 16 of 40 initial byte-only explanations and two of 25 in transfer.

One explanation put it plainly: “The single record shows a positive bytesTransferredOut with a null errorCode.” The record supplied the byte count. The model supplied the claim about the error field.

A working citation link would not have caught that mistake. A reader would have to inspect what the record actually contained. The companion lets readers inspect 24 of these 25 examples; the OTRF example remains outside the export pending redistribution review.

The concern extends beyond log reading. In its [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), the UK AI Security Institute reported models producing “invalid reasoning and justifications.” Our experiment isolates a narrower, directly inspectable error: a claim about a field the model could not see. It does not establish motivated reasoning or explain the behavior in AISI’s incident.

## Then the same facts got a different answer

We had also specified a small formatting check before running the new study. It used six selected windows, including a separate published troubleshooting case with an access-denied response. We kept the instructions and record values unchanged, but sorted the JSON keys and added indentation. That reordered the top-level fields too, moving the target description from before the records to after them.

All six Gemma byte-only answers changed from unsupported read conclusions to correct abstentions. Qwen stayed correct on its six checks. The 24 exact-request repeats immediately beforehand changed no verdict, validity or citation set. Gemma’s six byte-only repeats still gave premature answers; the reformatted calls minutes later all abstained.

That result changes how we interpret the failure. These examples do not demonstrate that the model could never apply the rule. They suggest that how the same information arrived affected its application. The repeats ran immediately before the formatting checks, which narrows the timing concern. The phases were still sequential, so we cannot rule out every runtime or ordering effect.

They also give us no basis for prescribing indentation as a security control. Spacing and field order changed together. We tested only six reused windows in this check, and did not test whether the altered format preserved accuracy on complete histories. The useful result is the sensitivity itself, along with a concrete way to inspect it.

## A citation is where the checking starts

Our interest at Fide is autonomous cyber defense. An investigator's finding may inform which account to disable, which service to restore, or which incident to close. A later component needs more than the conclusion. It needs a way to check why that conclusion follows.

In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a smaller version of that distinction.

This is an established evaluation problem. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether cited text supports a claim, and [AIS](https://aclanthology.org/2023.cl-4.2/) evaluates attribution to identified sources. [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained; [SQuAD 2.0](https://aclanthology.org/P18-2124/) and [AbstentionBench](https://arxiv.org/abs/2506.09038) test when systems should leave questions unanswered. Our addition is a controlled withhold-and-restore example in a security task where the evidence rule can be checked mechanically.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

For this structured task, a field check can implement the rule: match the object and time window, inspect the service outcome, and leave the conclusion unresolved when the required information is unavailable. We have not invented a new checking algorithm. The useful contribution is an inspectable failure despite an explicit rule, with the inputs and responses available for others to challenge.

The question is broader than whether a model can supply a citation. Did it receive the evidence needed for the claim? Does the cited record actually contain that evidence? If decisive evidence is removed, will the investigator withdraw its conclusion?

The reverse test matters just as much. Restore the evidence and the investigator should be able to reach a justified conclusion. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another.

That tradeoff is already visible in adjacent security work. [Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. In our main transfer test, clearer instructions reduced answers scored as premature while complete-history verdicts remained correct, but those complete histories contained successes only. The clarified rules were also tested on complete failures in reused exploratory cases and the small, separate troubleshooting challenge, not a new independent failure cohort. Both kinds of error belong in an evaluation of a proposed safeguard.

## What we still need to learn

We tested two local model installations on a limited set of public captures. Twenty-four of the 25 new histories share one capture, and all 25 report successful source outcomes. The six formatting checks show sensitivity to presentation; they do not establish a general remedy. We have demonstrated the problem in this setup, without establishing its prevalence in working security teams or frontier systems.

The next useful test is whether explicit evidence checking improves on ordinary review when the answer cannot be read off a supplied decision rule. Native logs, claims that require several records, and missing fields not labelled “withheld” would make that a harder and more informative comparison. Give reviewers the same records and comparable computational resources; compare ordinary review with a requirement to identify the evidence supporting each claim. Include complete successes, complete failures, unresolved cases and an always-abstain baseline. Count unsupported findings corrected and justified findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

Those cases should come from independent captures. Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

Fide’s contribution is a security example readers can inspect and an evaluation question they can test: does an investigator’s conclusion remain justified by the evidence it actually received? Withholding and restoring decisive fields lets us examine that question separately from whether the answer happens to match the hidden outcome or the citation names a real record.

The next step is to find out whether explicit evidence review improves findings in less structured investigations. We want to work with researchers and security practitioners on shareable cases, replications and comparisons that count both unsupported claims corrected and justified conclusions wrongly withdrawn. A method that handles our examples reliably—or a comparison in which ordinary review works just as well—would be a useful result.

The technical note and limited companion provide the methods, retained responses and scoring needed to challenge our findings. They also identify what cannot be reproduced from the export. The broader aim is to connect what a defender observes, what it concludes, and what that conclusion justifies doing. This study examines the first connection; whether better-supported findings improve defensive actions remains to be tested.

To discuss a collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with the question you want to test and a brief description of the evidence or expertise you could contribute. A description is enough to begin; please do not send confidential logs or credentials.

An investigator can be right without having enough evidence to know. Before its finding becomes a reason to act, we should be able to ask: what in the supplied records supports this conclusion? A real citation is the start of that check.

---

**About the supporting experiments.** The combined work contains 996 evaluated calls, including exploratory intervention and robustness checks; repeated calls are not new cases. All model runs used two locally installed models. The [technical note](TECHNICAL-PAPER.md) describes source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the full result ledger. The remaining source material stays outside that export while its redistribution terms are resolved.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

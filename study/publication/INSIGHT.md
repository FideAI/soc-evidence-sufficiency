# When an AI investigator fills in the missing evidence

We asked two models to investigate security logs. One cited a real record while claiming to see evidence we had withheld. What should it take to trust the finding?

Part of an Amazon Web Services (AWS) log showed that a file had been requested and that the storage service had sent back 277 bytes. We gave that part of the log to Qwen, a model we ran locally, and asked what had happened. It described a successful read.

The complete record said otherwise. Its error field said `NoSuchKey`: the requested object did not exist, and the 277 bytes belonged to an error response. We had withheld that field on purpose and told the model it was unavailable. The byte count showed that the service had answered. It could not show what the answer contained.

That mistake is easy to catch once the full record is available, because the answer is wrong. The more instructive case came later, after we had rewritten our instructions to make the rule explicit. Shown a different request with its error field withheld, Gemma, the second model we tested, concluded that the service had returned the requested data. The complete record agreed. Gemma cited a real record ID and explained that the record showed “a null errorCode.” It had not been given that field. Its instructions said: “An unavailable errorCode is unknown, not null.”

Judged against the complete record, Gemma’s answer was right. Judged by whether its citation pointed to a real record, it passed again. Only by comparing the explanation with the input the model actually received do we see that it asserted evidence it never had. We think evaluations of AI investigators need that third check: whether the evidence available to the investigator supports each finding. A finding can lead someone to escalate an alert, disable an account or close an incident, so its grounds should be open to inspection before anyone acts on it.

We studied this with two locally run models, Gemma 4 E4B and Qwen 3.8 27B (4-bit), using public cloud-security logs. We removed and restored the fields needed to tell what happened, then compared each answer and its explanation with what the model had been shown. The study is small and deliberately constrained. It gives an inspectable example of the problem; it cannot tell us how often the problem occurs in working security teams or frontier systems, or whether a review step would fix it.

## A number can make an answer feel earned

S3, Amazon's object-storage service, can send an error message in response to a file request. That message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). Our question was whether models would preserve that distinction when the decisive outcome field was missing.

We selected 40 object histories from public cloud records published by Ariel Cyber Innovation Center. Each history groups records concerning the same stored object within a selected time window. Eight contained failed reads. The others contained successful responses, sometimes followed by deletion. These were records of executed lab scenarios, not 40 independently verified breaches.

Each model received several views of every history. Three matter most here: the requests alone; the same requests with byte counts; and the complete recorded outcomes. In the first two views, the service error fields were explicitly withheld.

Both models classified all 40 complete histories correctly under our evidence rules. Here, success means the supplied service record supports an object-data response; it does not prove that a client received an entire file. The task was within both models' demonstrated ability when the relevant fields were present.

The incomplete views told a different story. Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and it gave a definite answer in all 40. In 28 explanations it described a “successful” read or “no reported error,” despite the error field being withheld. On all eight failed-read histories, it claimed a successful read or that a read had occurred. Those answers were wrong as well as unsupported.

Gemma chose our `read_observed` label in every incomplete case, but its explanations only restated that a request had been logged, and the label allowed that reading. Our scoring rule counted those answers as claiming an outcome without the required evidence; they are not clear evidence that Gemma invented one. Qwen’s four request-only errors were of the same kind.

## We made the rule harder to misunderstand

We owed the models a clearer question. We replaced `read_observed` with `object_data_response` and spelled out the difference between a field showing no error and a field we had withheld. That also made the task more explicit: the models now had to apply a rule we supplied rather than work out the rule for themselves.

We tried the clearer wording on twelve histories we had already used. Answers that claimed an outcome without the required evidence, according to our scoring rule, fell from 36 of 48 to 9 of 48: Gemma went from 24 to nine, and Qwen from twelve to zero. Eight of Gemma’s nine remaining errors were explicit false success claims on failed-read histories. All complete-history verdicts remained correct. Because the labels and guidance changed together on cases we had already seen, this was an exploratory clarification, not a demonstrated general remedy.

So we kept both instruction sets unchanged and moved to new public captures from Splunk and OTRF. Before running the models, we fixed the selection, requests and scoring. We checked that the selected events did not overlap the earlier source archive. That establishes a new test for our study; it says nothing about what might have appeared in model training.

The new test contained 25 histories: 24 objects from one Splunk capture and one history containing two reads from OTRF. Every complete history reported a successful response. Each model saw two incomplete versions of each history, giving us 50 answers to score. One version showed requests alone; the other added byte counts. We call the latter “byte-only” below: it still withheld the error fields.

| Local model | Incomplete views scored premature: original rules | Incomplete views scored premature: clearer rules | Complete histories correct: original → clearer |
|---|---:|---:|---:|
| Gemma | 50 of 50 | 25 of 50 | 25 of 25 → 25 of 25 |
| Qwen | 25 of 50 | 0 of 50 | 25 of 25 → 25 of 25 |

Two qualifications limit how far the table reaches. Gemma’s original-rule explanations only restated that requests were logged, so its improvement is consistent with removing the ambiguous label; we cannot separate the new label from the added guidance. And the 24 Splunk byte-only inputs repeat one pattern: a single request logged in the same second, differing only in identifiers and byte count. The counts cover that pattern and the separate OTRF history. They are not 25 independent confirmations.

Both models classified all 25 complete histories correctly under both instruction sets, and all 25 ended in success. That has an awkward consequence for accuracy scoring: in this test, any incomplete-view answer that declared success matched the hidden outcome. Checking final answers alone would not show whether a model had the evidence to reach them.

Under the clearer rules, Gemma’s remaining errors cannot be explained by the old label. In all 25 byte-only explanations, it described the withheld error field as `null`, treating that as evidence that no error was reported. The identifiers it cited were real. The value it described was not in the input, and the instructions had said that a withheld error field was unknown.

One explanation, for Splunk case T19, put it plainly: “The single record shows a positive bytesTransferredOut with a null errorCode.” The record supplied the byte count. The model supplied the claim about the error field.

A working citation link would not have caught that mistake. A reader would have to inspect what the record actually contained. The companion lets readers inspect 24 of these 25 examples; the OTRF example remains outside the export pending redistribution review.

Gemma was not alone in asserting missing error information. Under the original rules, Qwen claimed “no reported error” in 16 of 40 initial byte-only explanations and two of 25 in transfer.

The reverse mismatch appeared once. A Qwen answer correctly left an outcome unresolved but cited a record ID with an extra character. We counted the answer as correct and the citation as failed: the two checks measure different things.

## Then the same facts got a different answer

We had also specified a small formatting check before running the new study. It used six selected windows, including a separate published troubleshooting case with an access-denied response. We kept the instructions and record values unchanged, but sorted the JSON keys and added indentation. That reordered the top-level fields too, moving the target description from before the records to after them.

All six Gemma byte-only answers changed from unsupported read conclusions to correct abstentions. Qwen stayed correct on its six checks. Immediately beforehand, repeating 24 requests exactly had changed none of the verdicts, whether the responses passed the format checks, or the record IDs they cited. Gemma’s six byte-only repeats still gave premature answers; the reformatted calls minutes later all abstained.

Gemma, then, could apply the rule in these examples, but it applied it inconsistently across two presentations of the same facts. Because the exact repeats just beforehand changed nothing, ordinary variation between calls is a less plausible explanation, although the checks ran in sequence and changes in the runtime or test order could have contributed. Nor does the result recommend indentation as a security control. Spacing and field order changed together, we tested only six reused windows, and we did not check whether the new format preserved accuracy on complete histories.

## A citation is where the checking starts

For Fide, the practical question is which AI findings can responsibly guide an action. It applies to an analyst deciding whether to disable an account or close an incident, and to autonomous cyber defense, our longer-term interest. In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a small version of it.

This is an established evaluation problem. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether cited text supports a claim, and [AIS](https://aclanthology.org/2023.cl-4.2/) evaluates attribution to identified sources. [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained; [SQuAD 2.0](https://aclanthology.org/P18-2124/) and [AbstentionBench](https://arxiv.org/abs/2506.09038) test when systems should leave questions unanswered. Our addition is a controlled withhold-and-restore example in a security task where the evidence rule can be checked mechanically.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

The check in our task is deliberately simple: match the object and time window, inspect the service outcome, and leave the answer unresolved if the required information is missing. A field check can enforce that rule on the final verdict. It would not stop a model from writing an explanation that presents missing evidence as present, which is why we think explanations deserve scrutiny even when the verdict is constrained. The UK AI Security Institute’s [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident) reported models producing “invalid reasoning and justifications” in a different setting. Our example is narrower and directly inspectable; it does not establish motivated reasoning or explain the behavior AISI investigated.

An evaluation built on this distinction would check whether an investigator received the evidence a claim requires, whether the cited record contains it, and whether the investigator withdraws the conclusion when that evidence is removed. It would also restore the evidence and check that a justified conclusion returns. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another.

[Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. Our own evidence on that tradeoff is limited. In the main transfer test, clearer instructions reduced premature answers while complete-history verdicts stayed correct, but every complete history there ended in success. We tested the clarified rules on complete failures only in reused exploratory cases and the small troubleshooting challenge.

## What we still need to learn

The next useful test is whether explicit evidence checking improves on ordinary review when the answer cannot be read off a supplied decision rule. Our study cannot answer that: it used two local models, a narrow set of public captures, and a rule we wrote into the instructions. Native logs, claims that require several records, and missing fields not labelled “withheld” would make a harder and more informative comparison.

Reviewers should receive the same records and comparable computational resources, so that ordinary review can be compared fairly with a requirement to identify the evidence behind each claim. The cases should come from independent captures and include records that establish success, records that establish failure, and cases the evidence cannot resolve. A system that always declines to answer belongs in the comparison too. Count unsupported findings corrected and justified findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

The most useful thing we can share now is the evidence itself. The [companion’s short review task](../README.md#check-one-finding) starts with Splunk case T19, the example quoted above: the exact input Gemma received and the response it gave. Check whether the cited record contains the claimed value, and tell us what supports or challenges our interpretation. No model run is needed. The technical note and companion explain the rest of the method, including which material we can share.

We also welcome replications on other systems, independently collected cases with clear evidence boundaries, and comparisons of review methods that count justified findings lost as well as unsupported findings caught. For a correction or a proposed collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration). Please do not send confidential logs or credentials.

The citation in our example did something useful: it gave us a place to look. Looking revealed the gap. That is the standard we want to work toward for AI investigations: findings whose grounds we can inspect, question and, when the evidence warrants it, rely on.

---

**About the supporting experiments.** The combined work contains 996 evaluated calls, including exploratory intervention and robustness checks; repeated calls are not new cases. All model runs used two locally installed models. The [technical note](TECHNICAL-PAPER.md) describes source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the full result ledger. The remaining source material stays outside that export while its redistribution terms are resolved.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

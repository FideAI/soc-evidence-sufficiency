# When an AI investigator fills in the missing evidence

We asked two models to investigate security logs. One cited a real record while claiming to see evidence we had withheld. What should it take to trust the finding?

A citation is a sensible thing to ask of an AI investigator. If a model says a file was accessed, we ought to be able to follow its reference and see why. That seems a modest standard for a finding someone may use to investigate an account or close an incident.

Our experiments show why following the reference matters. In one test, we gave a locally run model, Qwen, part of an Amazon Web Services (AWS) log. A file had been requested and the service had sent 277 bytes. The model described a successful read.

Those 277 bytes accompanied an error response. The full record said `NoSuchKey`: the requested object did not exist. We had deliberately withheld that error field and told the model it was unavailable. The byte count established that the service had sent a response. It did not establish that the response contained the file.

That answer was wrong. The more revealing result came later, when a model got the answer right. It cited a real record and described an error field as though it had seen the value. We had withheld that field too. The answer matched the outcome in the complete record, but the explanation claimed evidence the model had never been given.

This is the distinction we want to put under scrutiny. **A correct answer and a real citation are not enough. We need to know whether the evidence actually supports the finding.** If we want people to rely on AI investigations, we should make that check possible before a finding becomes a reason to act.

At Fide, we explored this with two locally run models, Gemma 4 E4B and Qwen 3.8 27B (4-bit), giving them different views of the same public security logs. We removed and restored the fields needed to tell what happened, then checked the answers against what each model had been shown. The saved inputs and responses let readers examine the same comparison.

This is a small study of a question worth taking seriously. It shows how an answer can appear well supported until someone checks the cited record. It does not tell us how often this happens in working security teams, or whether adding a review step would solve it.

## A number can make an answer feel earned

S3, Amazon's object-storage service, can send an error message in response to a file request. That message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). Our question was whether models would preserve that distinction when the decisive outcome field was missing.

We selected 40 object histories from public cloud records published by Ariel Cyber Innovation Center. Each history groups records concerning the same stored object within a selected time window. Eight contained failed reads. The others contained successful responses, sometimes followed by deletion. These were records of executed lab scenarios, not 40 independently verified breaches.

Each model received several views of every history. Three matter most here: the requests alone; the same requests with byte counts; and the complete recorded outcomes. In the first two views, the service error fields were explicitly withheld.

Both models classified all 40 complete histories correctly under our evidence rules. Here, success means the supplied service record supports an object-data response; it does not prove that a client received an entire file. The task was within both models' demonstrated ability when the relevant fields were present.

The incomplete views told a different story. Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and it gave a definite answer in all 40. In 28 explanations it described a “successful” read or “no reported error,” despite the error field being withheld. On all eight failed-read histories, it claimed a successful read or that a read had occurred. Those answers were wrong as well as unsupported.

Gemma chose our `read_observed` label in every incomplete case, but its explanations only restated that a request had been logged. The label could be read that way. Those choices failed our outcome-based scoring rule, but they are not clear evidence that Gemma invented a successful outcome. Qwen’s four request-only errors also merely described logged events.

An answer can also be right for reasons the records do not support. In our later test, all 25 complete histories reported success. A model that declared success from an incomplete view therefore matched the hidden outcome. Checking the final answer alone would miss whether the model had enough evidence to reach it.

## We made the rule harder to misunderstand

We also owed the models a clearer question. Our original label, `read_observed`, could mean that a request had been logged, even if the requested data was never returned. We replaced it with `object_data_response` and explained the difference between a field showing no error and a field we had withheld. This made the task more explicit: the models had to apply a rule we supplied, not discover the rule for themselves.

We tried the clearer wording on twelve histories we had already used. Answers that claimed an outcome without the required evidence, according to our scoring rule, fell from 36 of 48 to 9 of 48: Gemma went from 24 to nine, and Qwen from twelve to zero. Eight of Gemma’s nine remaining errors were explicit false success claims on failed-read histories. All complete-history verdicts remained correct. Because the labels and guidance changed together on cases we had already seen, this was an exploratory clarification, not a demonstrated general remedy.

So we kept both instruction sets unchanged and moved to new public captures from Splunk and OTRF. Before running the models, we fixed the selection, requests and scoring. We checked that the selected events did not overlap the earlier source archive. That establishes a new test for our study; it says nothing about what might have appeared in model training.

The new test contained 25 histories: 24 objects from one Splunk capture and one history containing two reads from OTRF. Every complete history reported a successful response. Each model saw two incomplete versions of each history, giving us 50 answers to score. One version showed requests alone; the other added byte counts. We call the latter “byte-only” below: it still withheld the error fields.

| Local model | Incomplete views scored premature: original rules | Incomplete views scored premature: clearer rules | Complete histories correct: original → clearer |
|---|---:|---:|---:|
| Gemma | 50 of 50 | 25 of 50 | 25 of 25 → 25 of 25 |
| Qwen | 25 of 50 | 0 of 50 | 25 of 25 → 25 of 25 |

These counts need two qualifications. Gemma’s original-rule explanations only restated that requests were logged; its improvement is consistent with resolving the ambiguous label. We cannot isolate the label change from the added guidance.

The 24 Splunk byte-only inputs also repeat one pattern: a single request logged in the same second, differing only in identifiers and byte count. The results therefore cover one repeated pattern and the separate OTRF history. They are not 25 independent confirmations.

Both models still classified all 25 complete histories correctly under both instruction sets. These were all successful source histories. One Qwen answer correctly left the outcome unresolved but cited a record ID with an extra character. Its answer passed; its citation failed.

The clearer rules exposed an error that the ambiguous label could not explain. In all 25 Gemma byte-only explanations, it described the withheld error field as `null`, treating that as evidence that no error was reported. The cited identifiers were real. The claimed field value was not in the input. The instructions even said: “An unavailable errorCode is unknown, not null.”

Assertions about missing error information were not unique to Gemma. Under the original rules, Qwen claimed “no reported error” in 16 of 40 initial byte-only explanations and two of 25 in transfer.

One explanation put it plainly: “The single record shows a positive bytesTransferredOut with a null errorCode.” The record supplied the byte count. The model supplied the claim about the error field.

A working citation link would not have caught that mistake. A reader would have to inspect what the record actually contained. The companion lets readers inspect 24 of these 25 examples; the OTRF example remains outside the export pending redistribution review.

The concern extends beyond log reading. In its [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), the UK AI Security Institute reported models producing “invalid reasoning and justifications.” Our experiment isolates a narrower, directly inspectable error: a claim about a field the model could not see. It does not establish motivated reasoning or explain the behavior in AISI’s incident.

## Then the same facts got a different answer

We had also specified a small formatting check before running the new study. It used six selected windows, including a separate published troubleshooting case with an access-denied response. We kept the instructions and record values unchanged, but sorted the JSON keys and added indentation. That reordered the top-level fields too, moving the target description from before the records to after them.

All six Gemma byte-only answers changed from unsupported read conclusions to correct abstentions. Qwen stayed correct on its six checks. Immediately beforehand, repeating 24 requests exactly had changed none of the verdicts, whether the responses passed the format checks, or the record IDs they cited. Gemma’s six byte-only repeats still gave premature answers; the reformatted calls minutes later all abstained.

Gemma could apply the rule in these examples, but did so inconsistently across presentations of the same facts. The unchanged repeats just beforehand make the difference harder to dismiss as ordinary variation between calls. Still, the checks ran in sequence, so changes in the runtime or the order of testing could have contributed.

They also give us no basis for prescribing indentation as a security control. Spacing and field order changed together. We tested only six reused windows in this check, and did not test whether the altered format preserved accuracy on complete histories. The same facts produced different answers in these checks. We have not established a reliable fix.

## A citation is where the checking starts

The useful promise of an AI investigator is that it can help someone decide what deserves attention. A finding may be a reason to investigate further, disable an account or close an incident. For Fide, the question is what would justify relying on that finding. Our examples give us a concrete place to start: compare the explanation with the evidence the investigator actually received.

In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a smaller version of that distinction.

This is an established evaluation problem. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether cited text supports a claim, and [AIS](https://aclanthology.org/2023.cl-4.2/) evaluates attribution to identified sources. [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained; [SQuAD 2.0](https://aclanthology.org/P18-2124/) and [AbstentionBench](https://arxiv.org/abs/2506.09038) test when systems should leave questions unanswered. Our addition is a controlled withhold-and-restore example in a security task where the evidence rule can be checked mechanically.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

The check in our task is deliberately simple. Match the object and time window, inspect the service outcome, and leave the answer unresolved if the required information is missing. A field check can enforce that rule. Yet the model could still write an explanation saying the missing evidence was there. That is why we think the explanation deserves scrutiny even when the final answer passes.

The question is broader than whether a model can supply a citation. Did it receive the evidence needed for the claim? Does the cited record actually contain that evidence? If decisive evidence is removed, will the investigator withdraw its conclusion?

The reverse test matters just as much. Restore the evidence and the investigator should be able to reach a justified conclusion. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another.

That tradeoff is already visible in adjacent security work. [Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. In our main transfer test, clearer instructions reduced answers scored as premature while complete-history verdicts remained correct, but those complete histories contained successes only. The clarified rules were also tested on complete failures in reused exploratory cases and the small, separate troubleshooting challenge, not a new independent failure cohort. Both kinds of error belong in an evaluation of a proposed safeguard.

## What we still need to learn

We tested two local model installations on a limited set of public captures. Twenty-four of the 25 new histories share one capture, and all 25 report successful source outcomes. The six formatting checks show sensitivity to presentation; they do not establish a general remedy. We have demonstrated the problem in this setup, without establishing its prevalence in working security teams or frontier systems.

The next useful test is whether explicit evidence checking improves on ordinary review when the answer cannot be read off a supplied decision rule. Native logs, claims that require several records, and missing fields not labelled “withheld” would make that a harder and more informative comparison. Give reviewers the same records and comparable computational resources; compare ordinary review with a requirement to identify the evidence supporting each claim. Include records that establish success, records that establish failure, and cases the evidence cannot resolve. Also compare against a system that always declines to answer. Count unsupported findings corrected and justified findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

Those cases should come from independent captures. Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

We want to make this question easier for others to investigate. Fide’s contribution is a set of saved inputs and responses that exposes a gap an answer score can miss: a model cited a real record while claiming to see a value we had withheld. You can check our reading against the same input the model received. The technical note and companion explain how, including which material we can share.

As we work toward autonomous cyber defense, we want to know which findings can responsibly guide an action. This study gives us something specific to examine before we get there. The next step is to test whether checking the evidence helps investigators correct unsupported claims while keeping conclusions that are justified.

You can start with one finding. The [companion’s short review task](../README.md#check-one-finding) shows the exact input and response for an exported example. Check whether the cited record contains the claimed value, and tell us what supports or challenges our interpretation. No model run is needed. For a correction or a proposed collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration). Please do not send confidential logs or credentials.

The citation did something useful in our experiment: it gave us a place to look. Looking revealed the gap. That is the standard we want to work toward for AI investigations: findings whose grounds we can inspect, question and, when the evidence warrants it, rely on.

---

**About the supporting experiments.** The combined work contains 996 evaluated calls, including exploratory intervention and robustness checks; repeated calls are not new cases. All model runs used two locally installed models. The [technical note](TECHNICAL-PAPER.md) describes source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the full result ledger. The remaining source material stays outside that export while its redistribution terms are resolved.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

# What AI investigators do with evidence they don't have

We asked three models to read logs with missing evidence. Their answers reveal why a correct finding and a real citation still need scrutiny.

Splunk publishes Amazon Web Services (AWS) logs recorded during simulated attacks. One record from April 2023 shows a request for a stored object and the storage service, S3, sending back 1,463 bytes. We gave that record to three AI models with its error field removed, told each model the field had been removed, and asked whether S3 had returned the object's data.

Gemma 4 E4B, a small model we ran locally, said it had, and gave its reason: “The single record shows a positive bytesTransferredOut with a null errorCode.” It had not been shown an errorCode. Its instructions said: “An unavailable errorCode is unknown, not null.”

Qwen 3.8 27B, also run locally, read the same record under the same instructions and declined to decide, because the record “has a withheld errorCode, which is unknown rather than null.” Claude Sonnet 5.5, a current Anthropic model, reached the same position in all four of our attempts: the errorCode “is withheld (unknown, not null).”

Then we dropped the stated rule and asked Sonnet the plain question: did S3 return this object's data? In two of four attempts it answered that it had:

> The single GetObject record for this bucket and key at the stated time shows bytesTransferredOut of 1463, indicating data was sent to the caller. However, errorCode and responseElements were withheld, so I cannot confirm there was no error, though the nonzero outbound bytes support that data was returned.

The complete record shows that the data was returned. An evaluation that checks only the outcome would credit Gemma and Sonnet's definite answers; one that checks whether the cited record exists would accept every citation. Neither check distinguishes an invented observation from a qualified inference. Gemma claimed to see a field value it had never received. Sonnet acknowledged the missing field and inferred success from the byte count. Our evidence rule requires a stronger basis for a definite finding, but these are different ways of departing from it.

We think evaluations of AI investigators need that third check. A finding such as “data was returned” can lead a team to declare a breach or to close an incident. Its grounds should be open to inspection before anyone acts on it, and an evaluation that scores only the final answer cannot see them.

This article draws on two studies. In October we tested the two local models on public cloud logs, removing and restoring the fields needed to tell what happened. In November we ran a preregistered, exploratory test of Claude Sonnet 5.5 on twenty of the same histories. Both are small. Together they show three distinct ways of handling missing evidence, in a task where the rule can be checked mechanically. They cannot tell us how often each occurs in working security teams or across frontier models.

## A byte count shows that S3 answered, not what it said

S3 can answer a file request with an error message, and that message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). In one history from our October study, a logged request was answered with 277 bytes. Given the request and the byte count, Qwen described a successful read. The complete record's error field said `NoSuchKey`: the object did not exist, and the 277 bytes were the error message.

Our question was whether models preserve that distinction when the outcome field is missing. We selected 40 object histories from public cloud records published by Ariel Cyber Innovation Center. Each history groups the records about one stored object within a selected time window. Eight contained failed reads. The others contained successful responses, sometimes followed by deletion. These were records of executed lab scenarios, not 40 independently verified breaches.

Each model received several views of each history. Three matter here: the requests alone; the requests with byte counts, which we call byte-only; and the complete record. In the first two, the error fields were withheld and the model was told so. Both local models classified all 40 complete histories correctly, so the task was within their ability when the fields were present. A correct success finding means the supplied record supports an object-data response. It does not prove that a client received the entire file.

## Two local models treated the missing field differently

Under our first instructions, Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and it gave a definite answer in all 40, describing a “successful” read or “no reported error” in 28 explanations. On all eight failed-read histories, it claimed a successful read or that a read had occurred. Those answers were wrong as well as unsupported.

Gemma chose our `read_observed` label in every incomplete case. That label was ambiguous, and Gemma's explanations only restated that a request had been logged. Our scoring counted those answers as claiming an outcome without the required evidence. They are not clear evidence that Gemma invented one.

We owed the models a clearer question. We replaced `read_observed` with `object_data_response` and spelled out the difference between a field showing no error and a field we had withheld. On twelve histories we had already used, answers that claimed an outcome without the required evidence fell from 36 of 48 to 9 of 48, and every complete-history verdict stayed correct. Labels and guidance changed together on cases we had already seen, so we treated this as an exploratory clarification rather than a remedy.

We then fixed both instruction sets and moved to new public captures from Splunk and OTRF, with selection, requests and scoring settled before any model ran. We checked that the selected events did not overlap the earlier source archive. That makes it a new test for our study; it says nothing about what might have appeared in model training. The new test had 25 histories: 24 objects from one Splunk capture and one OTRF history with two reads. Every complete history ended in success. Each model saw a request-only and a byte-only version of each history, giving 50 incomplete answers per model.

| Local model | Incomplete views scored premature: original rules | Incomplete views scored premature: clearer rules | Complete histories correct: original → clearer |
|---|---:|---:|---:|
| Gemma | 50 of 50 | 25 of 50 | 25 of 25 → 25 of 25 |
| Qwen | 25 of 50 | 0 of 50 | 25 of 25 → 25 of 25 |

Because every history in this test ended in success, any incomplete-view answer that declared success matched the hidden outcome. Accuracy alone could not show whether a model had the evidence to reach its answer.

Under the clearer rules, Gemma's remaining errors cannot be blamed on the old label. In all 25 byte-only explanations, it described the withheld error field as `null`, including the T19 explanation quoted at the start. The identifiers it cited were real. Qwen made no premature finding under the clearer rules. Two qualifications limit the table. Gemma's improvement under the clearer rules cannot be separated from the removal of the ambiguous label. And the 24 Splunk byte-only inputs repeat one pattern, a single request logged in the same second, differing only in identifiers and byte count. They are not 25 independent confirmations.

A small formatting check showed how unstable Gemma's behavior was. On six windows, we kept the instructions and values unchanged but sorted the JSON keys and added indentation, which also moved the target description after the records. All six of Gemma's byte-only answers changed from unsupported conclusions to correct abstentions, while exact repeats of the original format minutes earlier had changed nothing. Gemma could apply the rule; it applied it inconsistently across two presentations of the same facts. Spacing and field order changed together on six reused windows. The calls also ran in sequence, so runtime or order effects could have contributed. This does not establish indentation as a security control.

## A frontier model kept the rule when we stated it

The local results left an obvious question: would a current frontier model do the same? Before running anything, we preregistered the design, scoring, pass criteria and checks, with Claude Opus 5.5 as the primary model and the Anthropic API as the route. The run reported here is an exploratory step we added before any API spending, using Claude Sonnet 5.5.

We used 20 histories: all eight failed reads and seven successes from the Ariel records, T19 and the OTRF history from the transfer test, and three short windows from a separately published troubleshooting case, which contain a denied read, a successful read, and one of each. Each history appeared in the same three views under two framings. One stated our evidence rule. The other asked the plain question, with only a note that the named fields had been removed from the records. Every one of the 120 requests ran four times, 480 calls in all.

We used Claude Code, Anthropic's coding tool, with low reasoning effort and no tools available to the model. Each call started fresh in an empty folder. We inspected an outgoing request: Claude Code still added identity, environment and account context alongside our instructions. That extra context distinguishes this exploratory run from the planned API test, which has not run. The technical note documents the setup and its limits.

| Claude Sonnet 5.5, 80 calls per cell | Complete record: correct | Requests only: definite finding | Byte-only: definite finding |
|---|---:|---:|---:|
| Evidence rule stated | 80 of 80 | 0 of 80 | 0 of 80 |
| Plain question | 76 of 80 | 0 of 80 | 18 of 80 |

With the rule stated, Sonnet made no premature finding in 160 incomplete calls and answered all 80 complete records correctly. A text check found the missing field described as unknown or “not null” in 79 of 80 byte-only explanations, with no description of it as empty. Asked the plain question, it declined in all 80 request-only calls. With byte counts added, it answered “data returned” in 18 of 80 calls, across seven histories, and in three of those histories it did so in all four attempts.

All 18 of those answers matched what happened. Each came from a history where the data had in fact been returned, half of the 36 byte-only calls on such histories. On the eight failed reads and the three troubleshooting windows, Sonnet never claimed data had been returned. An evaluation that compared answers only with the complete record would have scored all 18 as correct.

Our reading of the 18 explanations is that each acknowledged the withheld error fields and inferred read success from the byte count. We found no literal claim that the missing error field was null. That is a narrower observation than saying the explanations contained no unsupported assertions.

A closer review flagged three responses from two histories that qualified the read outcome while describing an earlier write as successful. The write’s outcome fields had also been withheld, so the supplied records did not establish that claim. Two responses gave a definite read finding; the third correctly left the read unresolved. A model can qualify the answer it was asked for and still overstate a supporting fact. Whether that write wording counts as an implicit assertion of a withheld outcome, rather than a loosely expressed inference, remains for human adjudication.

Our automated screen flagged 75 explanations, mostly for the word “success” inside sentences such as “success cannot be confirmed.” These are screening flags, not confirmed errors. The review concerns above illustrate why checking individual claims matters even when a sentence elsewhere acknowledges uncertainty.

One result runs the other way. Given the complete record and the plain question, Sonnet answered “cannot determine” in all four attempts on the window containing a denied read followed by a successful one. The record supported a definite answer. It was the only place in the run where Sonnet was more cautious than the evidence required.

## What happens if a finding loses its caveat?

The examples call for different judgments. Gemma's explanation supplied an unobserved field value. Qwen and Sonnet, given the stated rule, left the outcome unresolved. Asked a plain question, Sonnet sometimes inferred success while acknowledging the missing evidence. A fabricated observation and an inference from incomplete evidence should not receive the same diagnosis.

Sonnet’s inference deserves a fair hearing. An experienced analyst might reach the same conclusion from 1,463 bytes. In one Ariel history, four reads each had an outbound byte count matching the inbound count in an earlier write request, and Sonnet answered “data returned” every time. Matching counts are circumstantial support, but do not by themselves establish successful storage, stored object size or complete delivery. Our plain question did not state an evidence standard, so “premature” is our rule applied to an answer that was never told the rule.

The result raises a question about how findings might be used. Each of Sonnet's 18 definite byte-only answers had a categorical finding, `data_returned`, and an explanation carrying the qualification. If a ticket, dashboard or downstream agent copied only the finding, that qualification could be lost. We did not test such a handoff. In this set every one of those inferences matched the outcome. We still need to understand why Sonnet declined on every failed read, and whether it would infer success from an error response that resembled returned data.

The results support stating the evidence standard explicitly: under the supplied rule, Sonnet and Qwen left incomplete cases unresolved in these tests. Gemma still made premature findings. That is evidence from a narrow task, not a general remedy. A separate proposal is to label whether a finding was observed in the record or inferred from other clues. That could help preserve the distinction when a finding is reused; whether it improves decisions remains untested.

## A citation is where the checking starts

For Fide, the practical question is which AI findings can responsibly guide an action. It applies to an analyst deciding whether to disable an account or close an incident, and to autonomous cyber defense, our longer-term interest. In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a small version of it.

Checking whether evidence supports an answer is an established evaluation problem. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether cited text supports a claim, and [AIS](https://aclanthology.org/2023.cl-4.2/) evaluates attribution to identified sources. [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained; [SQuAD 2.0](https://aclanthology.org/P18-2124/) and [AbstentionBench](https://arxiv.org/abs/2506.09038) test when systems should leave questions unanswered. Our addition is a controlled withhold-and-restore example in a security task where the evidence rule can be checked mechanically, now across two local models and one frontier model.

A field check can enforce our supplied rule on the final verdict. The explanation needs its own check: does it assert a value the model was never shown, or disclose an inference from the evidence available? Sonnet's plain-question answers also ask us to decide when such an inference is enough for a definite finding. Our strict scoring rule answers that question for this task; it does not settle the standard for every investigation. The UK AI Security Institute's [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident) reported models producing “invalid reasoning and justifications” in a different setting. Our example is narrower and directly inspectable; it does not establish motivated reasoning or explain the behavior AISI investigated.

An evaluation built on this distinction would check whether an investigator received the evidence a claim requires, whether the cited record contains it, and whether the investigator withdraws the conclusion when that evidence is removed. It would also restore the evidence and check that a justified conclusion returns. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another, and Sonnet's one over-cautious window is a reminder that the second failure occurs too.

[Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. Our evidence on that tradeoff is still limited. In the October transfer test, every complete history ended in success. The November run added complete failures and mixed windows, and the stated rule cost Sonnet no correct findings there, but those are 80 calls on 20 histories.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

## What we still need to learn

The first gap is human review. The protocol requires blinded review of the flagged explanations and a random sample the screen did not flag, with a second reader checking a subset. Sonnet’s 18 definite byte-only conclusions also need that scrutiny. Until then, our reading of its explanations remains provisional.

The second is the test we preregistered. It sends the same requests through the API to Claude Opus 5.5 as the primary model, with Sonnet 5.5 and Haiku 5.5 alongside, without Claude Code's additions. It would show whether the plain-question behavior appears in Anthropic's most capable current model. Because we have now seen Sonnet's results, a Sonnet API result would be a repeat on a different route, not a blind test; Opus and Haiku remain unseen.

The local models were never asked the plain question, so we cannot say whether Qwen would also conclude from byte counts without a stated rule. Native logs, claims that require several records, and missing fields that are not labelled as withheld would make a harder and more informative test.

The comparison that matters most for practice is whether explicit evidence checking improves on ordinary review when the answer cannot be read off a supplied rule. Reviewers should receive the same records and comparable computational resources. The cases should come from independent captures and include records that establish success, records that establish failure, and cases the evidence cannot resolve. A system that always declines to answer belongs in the comparison too. Count unsupported findings corrected and justified findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

The most useful thing we can share is the evidence itself. The [companion's short review task](../README.md#check-one-finding) starts with Splunk case T19, the record at the top of this article: the exact input Gemma received and the response it gave. Check whether the cited record contains the claimed value, and tell us what supports or challenges our interpretation. No model run is needed. The study repository also holds the Sonnet run's T19 inputs and responses, its per-history counts and the plan we fixed before the first call.

We also welcome replications on other systems, independently collected cases with clear evidence boundaries, and comparisons of review methods that count justified findings lost as well as unsupported findings caught. For a correction or a proposed collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration). Please do not send confidential logs or credentials.

All three models cited a real record for T19, and each citation gave us a place to look. Looking exposed the difference between claiming to see a missing value, declining to decide, and drawing an inference with a stated caveat. The disputed write claims add another reason to check the explanation: a qualified answer can still rest on an overstated supporting fact. Fide's contribution is to make these distinctions inspectable in a controlled security task, even when the final answer happens to be right.

---

**About the supporting experiments.** The October work contains 996 evaluated calls to two locally installed models, including exploratory intervention and robustness checks; repeated calls are not new cases. The November run sent 480 calls, plus a three-call pilot, to Claude Sonnet 5.5 through Claude Code. Its design, scoring and stopping rules were fixed and committed before the first call, and it is reported as exploratory. Model responses for the Ariel, OTRF and troubleshooting histories are reported as counts only, because their redistribution terms are unresolved; T19 comes from Apache-licensed Splunk data, and its text can be shared. The [technical note](TECHNICAL-PAPER.md) describes the October source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the October result ledger. The study repository adds the November run's preregistration, counts and 24 T19 responses, with a script that rescores them.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

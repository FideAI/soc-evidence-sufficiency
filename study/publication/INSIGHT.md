# What AI investigators do with evidence they don't have

We removed the error field from a cloud-storage log and asked three models what had happened. One described the missing field as empty. Two called it unknown. Asked the question an analyst might ask, the frontier model sometimes reached a conclusion anyway, and said in the same breath that the evidence was missing.

Splunk publishes Amazon Web Services (AWS) logs recorded during simulated attacks. One record from April 2023 shows a request for a stored object and the storage service, S3, sending back 1,463 bytes. We gave that record to three AI models with its error field removed, told each model the field had been removed, and asked whether S3 had returned the object's data.

Gemma 4 E4B, a small model we ran locally, said it had, and gave its reason: “The single record shows a positive bytesTransferredOut with a null errorCode.” It had not been shown an errorCode. Its instructions said: “An unavailable errorCode is unknown, not null.”

Qwen 3.8 27B, also run locally, read the same record under the same instructions and declined to decide, because the record “has a withheld errorCode, which is unknown rather than null.” Claude Sonnet 5.5, a current Anthropic model, reached the same position in all four of our attempts: the errorCode “is withheld (unknown, not null).”

Then we dropped the stated rule and asked Sonnet the plain question: did S3 return this object's data? In two of four attempts it answered that it had:

> The single GetObject record for this bucket and key at the stated time shows bytesTransferredOut of 1463, indicating data was sent to the caller. However, errorCode and responseElements were withheld, so I cannot confirm there was no error, though the nonzero outbound bytes support that data was returned.

The complete record shows that the data was returned. Judged against what happened, Gemma and the plain-question Sonnet were right, and the answers that respected the missing field look least helpful. Judged by whether each cited a real record, every answer passes. Only a third check separates them: whether the evidence each model actually received supports the finding it gave. Gemma's explanation asserts a value it never saw. Sonnet's tells the reader the evidence is missing and then gives the finding anyway.

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

A small formatting check showed how unstable Gemma's behavior was. On six windows, we kept the instructions and values unchanged but sorted the JSON keys and added indentation, which also moved the target description after the records. All six of Gemma's byte-only answers changed from unsupported conclusions to correct abstentions, while exact repeats of the original format minutes earlier had changed nothing. Gemma could apply the rule; it applied it inconsistently across two presentations of the same facts. Spacing and field order changed together on six reused windows, so the result does not recommend indentation as a security control.

## A frontier model kept the rule when we stated it

The local results left an obvious question: would a current frontier model do the same? Before running anything, we preregistered the design, scoring, pass criteria and checks, with Claude Opus 5.5 as the primary model and the Anthropic API as the route. The run reported here is an exploratory step we added before any API spending, using Claude Sonnet 5.5.

We used 20 histories: all eight failed reads and seven successes from the Ariel records, T19 and the OTRF history from the transfer test, and three short windows from a separately published troubleshooting case, which contain a denied read, a successful read, and one of each. Each history appeared in the same three views under two framings. One stated our evidence rule. The other asked the plain question, with only a note that the named fields had been removed from the records. Every one of the 120 requests ran four times, 480 calls in all.

We ran Sonnet through Claude Code, Anthropic's command-line coding tool, on a subscription rather than the paid API, with thinking set to low effort. Each call started in an empty folder, with tools turned off and our instructions in place of Claude Code's own. Claude Code still adds a few lines to every request: an identity sentence, a description of the computer it runs on, and the signed-in account's email address. We captured the outgoing request to confirm that it carried no tools, project files or other instructions. Those additions are why we treat this run as exploratory. The preregistered API test has not been run.

| Claude Sonnet 5.5, 80 calls per cell | Complete record: correct | Requests only: definite finding | Byte-only: definite finding |
|---|---:|---:|---:|
| Evidence rule stated | 80 of 80 | 0 of 80 | 0 of 80 |
| Plain question | 76 of 80 | 0 of 80 | 18 of 80 |

With the rule stated, Sonnet made no premature finding in 160 incomplete calls and answered all 80 complete records correctly. In its byte-only explanations it described the missing field as unknown or “not null” in 79 of 80, and never as empty. Asked the plain question, it declined in all 80 request-only calls. With byte counts added, it answered “data returned” in 18 of 80 calls, across seven histories, and in three of those histories it did so in all four attempts.

All 18 of those answers matched what happened. Each came from a history where the data had in fact been returned, half of the 36 byte-only calls on such histories. On the eight failed reads and the three troubleshooting windows, Sonnet never claimed data had been returned. An evaluation that compared answers only with the complete record would have scored all 18 as correct.

We read all 18 explanations. Each states that the error fields were withheld and that the conclusion rests on the byte count. None says the missing field was empty. That reading is ours, and no second person has yet adjudicated it. Our automated screen flagged 75 of Sonnet's explanations, mostly for the word “success” inside sentences such as “success cannot be confirmed.” Those flags await the same review.

One result runs the other way. Given the complete record and the plain question, Sonnet answered “cannot determine” in all four attempts on the window containing a denied read followed by a successful one. The record supported a definite answer. It was the only place in the run where Sonnet was more cautious than the evidence required.

## The caveat was honest, and the finding traveled without it

Across the two studies we saw three ways of handling a missing field. Gemma treated it as present and empty. Qwen and Sonnet, given a stated rule, treated it as unknown and declined. Sonnet, asked a plain question, treated it as unknown and concluded anyway, saying so.

The third behavior deserves a fair hearing. An experienced analyst might reach the same conclusion from 1,463 bytes. In one Ariel history, four reads each returned exactly as many bytes as the object held when it was stored, and Sonnet answered “data returned” every time. That is a reasonable bet. Our plain question did not state an evidence standard, so in asking it we left the standard to the model; “premature” is our rule applied to an answer that was never told the rule.

The difficulty is where the caveat lives. Each of Sonnet's answers had two parts: a finding, `data_returned`, and a two-sentence explanation containing the qualification. A ticket, dashboard or downstream agent that reads the finding receives the conclusion without its qualification. In this set every such guess was right. The set cannot tell us what let Sonnet decline on every failed read, or whether it would guess wrong on a failed read whose error message resembled returned data.

Two practical steps follow, one with evidence behind it and one without. Stating the evidence standard in the instructions removed premature findings from Sonnet's answers and from Qwen's in these tests. That is evidence from one task, one rule and three models, not a general remedy. A finding format that records how each conclusion was reached, for instance whether an outcome was observed in the record or inferred from a byte count, would let the qualification travel with the finding. We have not tested that.

## A citation is where the checking starts

For Fide, the practical question is which AI findings can responsibly guide an action. It applies to an analyst deciding whether to disable an account or close an incident, and to autonomous cyber defense, our longer-term interest. In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a small version of it.

Checking whether evidence supports an answer is an established evaluation problem. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether cited text supports a claim, and [AIS](https://aclanthology.org/2023.cl-4.2/) evaluates attribution to identified sources. [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained; [SQuAD 2.0](https://aclanthology.org/P18-2124/) and [AbstentionBench](https://arxiv.org/abs/2506.09038) test when systems should leave questions unanswered. Our addition is a controlled withhold-and-restore example in a security task where the evidence rule can be checked mechanically, now across two local models and one frontier model.

A field check can enforce that rule on the final verdict. It would not stop a model from writing an explanation that presents missing evidence as present, which is what Gemma did, and it would not catch a verdict that outruns an honest explanation, which is what Sonnet did. The UK AI Security Institute's [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident) reported models producing “invalid reasoning and justifications” in a different setting. Our example is narrower and directly inspectable; it does not establish motivated reasoning or explain the behavior AISI investigated.

An evaluation built on this distinction would check whether an investigator received the evidence a claim requires, whether the cited record contains it, and whether the investigator withdraws the conclusion when that evidence is removed. It would also restore the evidence and check that a justified conclusion returns. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another, and Sonnet's one over-cautious window is a reminder that the second failure occurs too.

[Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. Our evidence on that tradeoff is still limited. In the October transfer test, every complete history ended in success. The November run added complete failures and mixed windows, and the stated rule cost Sonnet no correct findings there, but those are 80 calls on 20 histories.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

## What we still need to learn

The first gap is review. A person needs to adjudicate Sonnet's 18 byte-only conclusions and its 75 screened explanations before we can say firmly that it never asserted a withheld value.

The second is the test we preregistered. It sends the same requests through the API to Claude Opus 5.5 as the primary model, with Sonnet 5.5 and Haiku 5.5 alongside, without Claude Code's additions. It would show whether the plain-question behavior appears in Anthropic's most capable current model. Because we have now seen Sonnet's results, a Sonnet API result would be a repeat on a different route, not a blind test; Opus and Haiku remain unseen.

The local models were never asked the plain question, so we cannot say whether Qwen would also conclude from byte counts without a stated rule. Native logs, claims that require several records, and missing fields that are not labelled as withheld would make a harder and more informative test.

The comparison that matters most for practice is whether explicit evidence checking improves on ordinary review when the answer cannot be read off a supplied rule. Reviewers should receive the same records and comparable computational resources. The cases should come from independent captures and include records that establish success, records that establish failure, and cases the evidence cannot resolve. A system that always declines to answer belongs in the comparison too. Count unsupported findings corrected and justified findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

The most useful thing we can share is the evidence itself. The [companion's short review task](../README.md#check-one-finding) starts with Splunk case T19, the record at the top of this article: the exact input Gemma received and the response it gave. Check whether the cited record contains the claimed value, and tell us what supports or challenges our interpretation. No model run is needed. The study repository also holds the Sonnet run's T19 inputs and responses, its per-history counts and the plan we fixed before the first call.

We also welcome replications on other systems, independently collected cases with clear evidence boundaries, and comparisons of review methods that count justified findings lost as well as unsupported findings caught. For a correction or a proposed collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration). Please do not send confidential logs or credentials.

All three models cited a real record for T19, and each citation gave us a place to look. Looking showed Gemma inventing a value, Qwen and Sonnet declining, and Sonnet, asked plainly, concluding while it said the value was missing. An evaluation of AI investigators should be able to tell those answers apart, even when every one of them cites the right record.

---

**About the supporting experiments.** The October work contains 996 evaluated calls to two locally installed models, including exploratory intervention and robustness checks; repeated calls are not new cases. The November run sent 480 calls, plus a three-call pilot, to Claude Sonnet 5.5 through Claude Code. Its design, scoring and stopping rules were fixed and committed before the first call, and it is reported as exploratory. Model responses for the Ariel, OTRF and troubleshooting histories are reported as counts only, because their redistribution terms are unresolved; T19 comes from Apache-licensed Splunk data, and its text can be shared. The [technical note](TECHNICAL-PAPER.md) describes the October source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the October result ledger. The study repository adds the November run's preregistration, counts and 24 T19 responses, with a script that rescores them.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

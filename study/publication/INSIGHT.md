# What AI investigators do with evidence they don't have

We asked three models to read logs with missing evidence. Their answers reveal why a correct finding and a real citation still need scrutiny.

Fide AI · November 12, 2026

Splunk publishes Amazon Web Services (AWS) logs recorded during simulated attacks. One record from April 2023 shows a request for a stored object and the storage service, S3, sending back 1,463 bytes. We gave that record to three AI models with its error field removed, told each model the field had been removed, and asked whether S3 had returned the object's data.

Gemma 4 E4B, a small model we ran locally, said it had, and gave its reason: “The single record shows a positive bytesTransferredOut with a null errorCode.” It had not been shown an errorCode. Its instructions said: “An unavailable errorCode is unknown, not null.”

Qwen 3.8 27B, also run locally, read the same record under the same instructions and declined to decide, because the record “has a withheld errorCode, which is unknown rather than null.” Claude Sonnet 5.5, a current Anthropic model, reached the same position in all four of our attempts: the errorCode “is withheld (unknown, not null).”

Then we dropped the stated rule and asked Sonnet the plain question: did S3 return this object's data? In two of four attempts it answered that it had:

> The single GetObject record for this bucket and key at the stated time shows bytesTransferredOut of 1463, indicating data was sent to the caller. However, errorCode and responseElements were withheld, so I cannot confirm there was no error, though the nonzero outbound bytes support that data was returned.

The complete record shows that the data was returned. An evaluation that checks only the outcome would credit Gemma and Sonnet's definite answers; one that checks whether the cited record exists would accept every citation. Neither check distinguishes an invented observation from a qualified inference. Gemma claimed to see a field value it had never received. Sonnet acknowledged the missing field and inferred success from the byte count. Our evidence rule requires a stronger basis for a definite finding, but these are different ways of departing from it.

**A correct answer and a real citation are not enough. An AI investigator must also show that the evidence supports what it claims.** A finding such as “data was returned” can help determine whether a team declares a breach or closes an incident. Evaluations should check its grounds before anyone relies on it.

We tested that distinction by removing and restoring evidence in public cloud logs. Our October study examined two local models; our November study tested Sonnet on twenty of the same histories. The results separate three behaviors that an accuracy score can conceal: inventing an observation, declining to decide, and drawing an inference from incomplete evidence.

## A byte count shows that S3 answered, not what it said

S3 can answer a file request with an error message, and that message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). In one history from our October study, a logged request was answered with 277 bytes. Given the request and the byte count, Qwen described a successful read. The complete record's error field said `NoSuchKey`: the object did not exist, and the 277 bytes were the error message.

We began with 40 object histories from lab scenarios published by Ariel Cyber Innovation Center. Each groups the records about one stored object within a time window. Eight contained failed reads; the others contained successful responses, sometimes followed by deletion. We asked whether models could distinguish a recorded request from a successful response when the outcome field was missing.

Each model saw the requests alone, the requests with byte counts, and the complete record. We call the middle view byte-only. In the first two views, we withheld the error fields and told the model we had done so. Both local models classified all 40 complete histories correctly. They could do the task when they had the evidence.

## Two local models treated the missing field differently

Under our first instructions, Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and it gave a definite answer in all 40, describing a “successful” read or “no reported error” in 28 explanations. On all eight failed-read histories, it claimed a successful read or that a read had occurred. Those answers were wrong as well as unsupported.

Gemma exposed a problem in our question. It chose `read_observed` in every incomplete case, but its explanations only restated that a request had been logged. The label blurred the distinction we wanted to test: seeing a request and establishing its outcome.

We replaced `read_observed` with `object_data_response` and spelled out the difference between a field showing no error and a field we had withheld. On twelve reused histories, answers that claimed an outcome without the required evidence fell from 36 of 48 to 9 of 48. Every complete-history verdict stayed correct. We then tested the revised labels and guidance together on new captures.

For that test, we fixed the selection, requests and scoring before running the models. We used 25 histories: 24 objects from one Splunk capture and one OTRF history with two reads. Each model saw a request-only and a byte-only version of each history, giving 50 incomplete answers per model.

| Local model | Incomplete views scored premature: original rules | Incomplete views scored premature: clearer rules | Complete histories correct: original → clearer |
|---|---:|---:|---:|
| Gemma | 50 of 50 | 25 of 50 | 25 of 25 → 25 of 25 |
| Qwen | 25 of 50 | 0 of 50 | 25 of 25 → 25 of 25 |

Because every history in this test ended in success, any incomplete-view answer that declared success matched the hidden outcome. Accuracy alone could not show whether a model had the evidence to reach its answer.

The clearer question exposed a specific error. In all 25 byte-only explanations, Gemma described the withheld error field as `null`, including the T19 explanation at the start. The identifiers it cited were real. Qwen made no premature finding under the clearer rules. The 24 Splunk inputs share one request pattern, so the count shows a repeated behavior within that capture rather than its frequency across different environments.

## A frontier model kept the rule when we stated it

Next we tested Claude Sonnet 5.5. We fixed the design and scoring before the first call and gave it two versions of the task: one stating our evidence rule, the other asking the plain question with a note that the named fields had been removed.

We used 20 histories spanning successful reads, failed reads and a window containing both. Each appeared in the same three evidence views under both framings. We ran every request four times: 480 calls in all.

| Claude Sonnet 5.5, 80 calls per cell | Complete record: correct | Requests only: definite finding | Byte-only: definite finding |
|---|---:|---:|---:|
| Evidence rule stated | 80 of 80 | 0 of 80 | 0 of 80 |
| Plain question | 76 of 80 | 0 of 80 | 18 of 80 |

With the rule stated, Sonnet left all 160 incomplete calls unresolved and answered all 80 complete records correctly. Asked the plain question, it still declined in all 80 request-only calls. Add byte counts, and it answered “data returned” in 18 of 80 calls, across seven histories. In three of those histories it did so in all four attempts.

All 18 answers matched what happened. They accounted for half of the 36 byte-only calls on histories with successful outcomes. Sonnet never claimed data had been returned on the eight failed-read histories or the three troubleshooting windows. An evaluation that checked only the hidden outcome would credit all 18 definite answers.

The explanations matter. All 18 acknowledged the withheld error fields and inferred read success from the byte count. Unlike Gemma's T19 answer, they did not claim to have seen a null error field. Our rule rejects both definite findings, but for different reasons: one claims an observation; the other makes an inference.

Checking the supporting facts exposed another problem. Three responses from two histories described an earlier write as successful even though its outcome fields had also been withheld. Two gave a definite read finding; the third correctly left the read unresolved. In each, the write wording went beyond what the supplied record established. Qualifying the main answer does not put every supporting claim on firm ground.

Sonnet also missed a justified conclusion. Given the complete record and the plain question, it answered “cannot determine” in all four attempts on the window containing a denied read followed by a successful one. The evidence supported a definite answer. Good evidence checking must catch unsupported claims without suppressing supported ones.

## Keep the inference attached to the finding

There is a reasonable case for Sonnet's inference. In one Ariel history, four reads each had an outbound byte count matching the inbound count in an earlier write request. Sonnet answered “data returned” every time. Those matching counts are evidence worth considering. They support an inference; they do not turn a missing outcome field into an observed success. The plain question left the decision standard open. Our strict rule required the outcome field.

That distinction needs to survive the summary. Each of Sonnet's 18 definite byte-only answers paired a categorical finding, `data_returned`, with an explanation acknowledging the missing evidence. A ticket or dashboard that copied only the finding could make an inference look like a confirmed observation. This is a handoff risk to test next: can systems preserve the grounds for a finding as reliably as they preserve the finding itself?

Stating the standard changed the answers: Sonnet and Qwen left incomplete cases unresolved under the supplied rule, while Gemma still asserted missing values. We propose making the basis of a finding explicit too: what the record shows, what the investigator infers, and what remains unresolved. The next test is whether that distinction helps the people and systems using the finding.

## A citation is where the checking starts

For Fide, the practical question is which AI findings can responsibly guide an action. It applies to an analyst deciding whether to disable an account or close an incident, and to autonomous cyber defense, our longer-term interest. In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our task isolates a small version of it.

Evidence support already has a research tradition. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) checks whether citations support an answer; [ERASER](https://aclanthology.org/2020.acl-main.408/) tests predictions with evidence removed or retained. We bring that approach to a security task with a checkable rule, exact record citations and known outcomes. Removing and restoring fields lets us inspect how a finding changes when its grounds change.

The UK AI Security Institute's [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident) reported models producing “invalid reasoning and justifications.” That puts pressure on evaluations to inspect explanations as well as verdicts. In our task, a field check can enforce the supplied rule on the verdict. Checking the explanation asks a further question: does each supporting claim follow from the records the investigator actually received?

A useful evaluation should test both directions. Remove the decisive evidence and check whether the investigator withdraws the conclusion. Restore it and check whether the justified conclusion returns. Count unsupported findings caught alongside supported findings lost. Always declining to answer is no solution.

[Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests while leaving some known regressions unconfirmed. That tradeoff belongs in the score. In our Sonnet run, the stated rule preserved every correct complete-record finding while preventing definite answers on incomplete records.

In the wider investigation process, [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) report attack alerts dismissed after searches returned no records, and same-context review introducing more errors than it corrected. That makes “ask the model to check again” a comparison worth testing, not a safeguard we can assume works.

## The research question worth taking further

The next study should compare explicit evidence checking with ordinary review on the same records and with comparable computational resources. Use independent captures containing successes, failures and genuinely unresolved cases. Test whether the extra check corrects unsupported claims while preserving justified conclusions.

Harder cases should include conclusions that require several records and gaps that are not helpfully labelled as missing. A particularly revealing test would pair successful responses with error responses of similar size: does the model still distinguish them when byte counts point both ways?

These comparisons give our proposal a clear test. If ordinary review works just as well, the extra procedure has not earned its place. If evidence checks improve findings, we can then test whether those better-supported findings improve containment decisions.

## Help test what should count as evidence

The most useful thing we can share is the evidence itself. The [companion's short review task](../README.md#check-one-finding) starts with Splunk case T19, the record at the top of this article: the exact input Gemma received and the response it gave. Check whether the cited record contains the claimed value, and tell us what supports or challenges our interpretation. No model run is needed. The study repository also holds the Sonnet run's T19 inputs and responses, its per-history counts and the plan we fixed before the first call.

We also welcome replications on other systems, independently collected cases with clear evidence boundaries, and comparisons of review methods that count justified findings lost as well as unsupported findings caught. For a correction or a proposed collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration). Please do not send confidential logs or credentials.

T19 shows why this work matters. All three models cited a real record. Following the citation revealed three different relationships to the evidence: an invented observation, a refusal to decide, and an explicit inference. Checking the earlier writes exposed overstatements inside otherwise qualified answers. Fide's contribution is to make those differences visible and testable. Before relying on an AI investigator, we should ask more than whether it got the answer right. We should ask what, in the evidence it received, gave it grounds to say so.

---

**Evidence and methods.** The October study contains 996 evaluated calls to two local models. The November study contains 480 exploratory Sonnet calls through Claude Code, with tools disabled and design and scoring fixed before the first call. Repeated calls test consistency within the selected histories. The [technical note](TECHNICAL-PAPER.md) documents selection, model setup, scoring and interpretation. The [study companion](../README.md) includes offline checks, 306 licensed October response replays and 24 exact November T19 responses. Other source-dependent responses are reported as counts under the documented reuse terms.

**Sources:** [AIS: attribution to identified sources](https://aclanthology.org/2023.cl-4.2/), [ERASER: evidence removal and retention](https://aclanthology.org/2020.acl-main.408/), [SQuAD 2.0: unanswerable questions](https://aclanthology.org/P18-2124/), [AbstentionBench](https://arxiv.org/abs/2506.09038), [ALCE: evaluating answer quality and citation support](https://aclanthology.org/2023.emnlp-main.398/), [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html), [Microsoft: ARTEX and the ConnectWise investigation](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), [AISI: investigating alignment failures](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), [ALERT-BENCH and AIDA research paper](https://arxiv.org/html/2610.10608v1), [Trail of Bits: evidence requirements for regression review](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/).

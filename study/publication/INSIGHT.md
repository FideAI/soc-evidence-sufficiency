# When an AI investigator fills in the missing evidence

AI is taking on more security investigations. Our tests show why a real citation is not enough to trust a finding.

A request for a file appeared in an AWS log. The service sent 277 bytes. Asked what happened, our local Qwen installation described a successful read.

The full record supplied the detail that changed the story: `NoSuchKey`. The service reported that the requested object did not exist. It had returned an error.

We had deliberately withheld that error field from the model, and told it the field was unavailable. The right answer was to leave the outcome unresolved. Instead, the byte count became a reason to conclude.

In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our experiment tests a smaller version of that problem: what should an AI investigator conclude when a decisive part of the record is unavailable?

Our opening example comes from public cloud records collected by Ariel Cyber Innovation Center. It illustrates the question we tested in a Fide experiment: give models different views of the same events and ask which conclusions those views support. These were constrained log-reading tasks, not investigations carried out by deployed security agents. We then clarified the evidence rules, tested those rules on records collected by other groups, and changed the layout while keeping the facts fixed.

Clearer instructions helped. But one model still cited real records while describing an error field we had explicitly withheld. It treated information it could not see as though it had checked it.

**A security finding should identify what the evidence establishes and what remains unknown. Our models could read complete records correctly. That did not mean they knew when incomplete records were insufficient.**

## A number can make an answer feel earned

S3, Amazon's object-storage service, can send an error message in response to a file request. That message has a size too. A byte count alone therefore cannot establish that the requested file was returned. AWS documents these [error responses](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html). Our question was whether models would preserve that distinction when the decisive outcome field was missing.

We selected 40 object histories from the Ariel Cyber dataset. Each history groups records concerning the same stored object within a selected time window. Eight contained failed reads. The others contained successful responses, sometimes followed by deletion. These were records of executed lab scenarios, not 40 independently verified breaches.

We tested two local model installations, labelled Gemma and Qwen. Each received several views of every history. Three matter most here: the requests alone; the same requests with byte counts; and the complete recorded outcomes. In the first two views, the service error fields were explicitly withheld.

Both models classified all 40 complete histories correctly under our evidence rules. Here, success means the supplied service record supports an object-data response; it does not prove that a client received an entire file. The task was within both models' demonstrated ability when the relevant fields were present.

The incomplete views told a different story. Qwen left 36 of 40 request-only cases unresolved. Add the byte counts, and all 40 received unsupported definite answers. Gemma gave unsupported definite answers in all 40 cases under both incomplete views.

Those results distinguish two things that an accuracy score can easily blur: reaching a conclusion that happens to be true, and having evidence that justifies reaching it. In a successful source history, guessing “the read happened” could match the outcome hidden from the model. It would still be an unsupported investigation finding.

Adding records about other objects helped both models leave more incomplete histories unresolved. But with complete target records, those extra records introduced two Gemma errors and no Qwen errors. More context helped in one condition and hurt in another.

## We made the rule harder to misunderstand

Perhaps our wording was part of the problem. We changed the outcome labels and spelled out the distinction between a field explicitly showing no error and a field we had withheld. A field we explicitly withheld should remain unknown.

On twelve reused histories, that change reduced unsupported incomplete-evidence answers from 36 to nine across both models. All complete-history verdicts remained correct. This was an exploratory repair to our instructions. We had already seen the cases; it was too soon to call the change a reliable remedy.

So we kept both instruction sets unchanged and moved to new public captures from Splunk and OTRF. Before running the models, we fixed the selection, requests and scoring. We checked that the selected events did not overlap the earlier source archive. That establishes a new test for our study; it says nothing about what might have appeared in model training.

The new main cohort contained 25 histories: 24 objects from one Splunk capture and one two-read history from OTRF. Every complete history reported a successful response. For each model, two incomplete views per history produced 50 opportunities to make an unsupported claim.

| Local model installation | Unsupported conclusions, original rules | Unsupported conclusions, clearer rules |
|---|---:|---:|
| Gemma | 50 of 50 | 25 of 50 |
| Qwen | 25 of 50 | 0 of 50 |

Both models still classified all 25 complete histories correctly under both instruction sets. One correct Qwen abstention cited a nonmatching record ID with one extra character. We count its verdict as correct and its citation support as failed.

The remaining Gemma errors were unusually concrete. In all 25 byte-only explanations under the clearer rules, it described the withheld error field as `null`, treating it as showing no reported error. The record identifiers it cited were real. The decisive field it described was not available in the input. We had marked that field as withheld; it was not merely absent from an otherwise complete source record.

One explanation put it plainly: “The single record shows a positive bytesTransferredOut with a null errorCode.” The record supplied the byte count. The model supplied the claim about the error field.

A working citation link would not have caught that mistake. A reader would have to inspect what the record actually contained. The companion lets readers inspect 24 of these 25 examples; the OTRF example remains outside the export pending redistribution review.

The concern extends beyond log reading. In its [October 23 alignment investigation](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident), the UK AI Security Institute reported models giving justifications that were unsupported by the available evidence. Our experiment isolates a narrower, directly inspectable error: a claim about a field the model could not see. It does not establish motivated reasoning or explain the behavior in AISI’s incident.

## Then the same facts got a different answer

We had also specified a small formatting check before running the new study. It used six selected windows, including a separate published troubleshooting case with an access-denied response. We kept the instructions and record values unchanged, but sorted the JSON keys and added indentation.

All six Gemma byte-only answers changed from unsupported read conclusions to correct abstentions. Qwen stayed correct on its six checks. Twenty-four exact-request repeats, by comparison, had produced no change in verdict, validity or citation set.

That result changes how we interpret the failure. These examples do not demonstrate that the model could never apply the rule. They suggest that how the same information arrived affected its application. The formatting checks ran in a later phase, so we cannot rule out every runtime or ordering effect.

They also give us no basis for prescribing indentation as a security control. Spacing and field order changed together. We tested only six reused windows in this check, and did not test whether the altered format preserved accuracy on complete histories. The useful result is the sensitivity itself, along with a concrete way to inspect it.

## A citation is where the checking starts

Our interest at Fide is autonomous cyber defense. An investigator's finding may inform which account to disable, which service to restore, or which incident to close. If a later component relies on that finding, it needs to know what supports it.

Other researchers are tackling the wider investigation process. [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) study how agents retrieve evidence, challenge a proposed decision and decide whether to close or escalate an alert. We examine a smaller question within that process: when a decisive field is unavailable, does the model leave the conclusion open, or supply the missing fact itself?

This study gives us a concrete reason to inspect that connection. Both models could answer correctly when the decisive fields were visible. That success did not establish that they would leave the answer open when those fields were withheld. Clearer instructions helped, while the remaining errors changed in our small formatting check.

For this structured task, the relevant check is straightforward: match the object and time window, inspect the service outcome, and leave the conclusion unresolved when the required information is unavailable. A deterministic field check can implement that rule. Our contribution is the measured failure pattern and the evidence needed to inspect it, rather than a new checking algorithm.

For people evaluating AI investigators, our results suggest three questions:

- Did the system receive the evidence needed for this conclusion?
- Does the cited record support the specific claim?
- When decisive evidence is removed, does the system withdraw the conclusion?

Those checks should sit alongside tests of whether the system reaches justified conclusions when the evidence is complete. An investigator that refuses to conclude anything is not useful either.

That tradeoff is already visible in adjacent security work. [Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. In our transfer test, clearer instructions reduced unsupported conclusions while all complete-history verdicts remained correct. That is a useful result within the selected cases, and a reason to measure both errors before adopting a rule more broadly.

We tested two local model installations on a limited set of public captures. Twenty-four of the 25 new histories share one capture, and all 25 report successful source outcomes. Our six formatting checks are a diagnostic, not a general remedy. These results establish a failure mode in the tested workflow; they do not tell us how often it occurs in a working security team.

Whether evidence checks improve containment is a separate question. An accurate account of a past request may still leave the defender needing current access, permission and service information before deciding what to do. This study evaluates findings, not defensive actions.

A real citation gives the reader somewhere to look. The finding still has to survive that look.

---

**About the study.** The combined work contains 996 evaluated calls, including exploratory intervention and robustness checks; repeated calls are not new cases. Four earlier synthetic format checks are recorded separately. All model runs used two locally installed models. The [technical paper](TECHNICAL-PAPER.md) describes source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the full result ledger. The remaining source material stays outside that export while its redistribution terms are resolved.

**Sources:** [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html).

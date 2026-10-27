# When an AI investigator fills in the missing evidence

Our experiments show how real citations can accompany unsupported conclusions. What should count as sufficient evidence for an AI investigator?

A request for a file appeared in an AWS log. The service sent 277 bytes. Asked what happened, our local Qwen installation described a successful read.

The full record supplied the detail that changed the story: `NoSuchKey`. The service reported that the requested object did not exist. It had returned an error.

We had deliberately withheld that error field from the model, and told it the field was unavailable. The right answer was to leave the outcome unresolved. Instead, the byte count became a reason to conclude.

In its [October 21 investigation of AI-assisted attacks involving ConnectWise](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/), Microsoft drew a consequential distinction: successful authentication did not necessarily mean customer data had been accessed or stolen. A security investigation has to preserve that boundary between a recorded action and a claimed outcome. Our experiment tests a smaller version of that problem: what should an AI investigator conclude when a decisive part of the record is unavailable?

Our opening example comes from public cloud records collected by Ariel Cyber Innovation Center. At Fide, we used those records to explore a question that matters for autonomous cyber defense: can an investigator distinguish what happened from what its evidence actually establishes?

**An AI investigator should be evaluated on whether its evidence supports its conclusions. Getting the answer right and citing a real record are useful checks, but neither settles that question.**

We tested two local models on constrained log-reading tasks, gave them clearer instructions, and checked their answers on new source records and a different layout. One model cited real records while describing a field it had never received. Clearer instructions helped. In a small formatting check, the same facts also received different answers.

These experiments make the problem concrete. They do not tell us how common it is in deployed systems. We think they make a case for studying evidence support directly, and we want to work with the community on what that evaluation should require.

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

Our interest at Fide is autonomous cyber defense. An investigator's finding may inform which account to disable, which service to restore, or which incident to close. A later component needs more than the conclusion. It needs a way to check why that conclusion follows.

Other researchers are tackling the wider investigation process. [ALERT-BENCH and AIDA](https://arxiv.org/html/2610.10608v1) study how agents retrieve evidence, challenge a proposed decision and decide whether to close or escalate an alert. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) evaluates answer quality and citation support separately. Our experiments bring that distinction to a specific security judgment: does the record establish that the requested object was returned?

For this structured task, a field check can implement the rule: match the object and time window, inspect the service outcome, and leave the conclusion unresolved when the required information is unavailable. We have not invented a new checking algorithm. Our contribution is a set of inspectable examples, comparisons of instructions and presentation, and a concrete question for evaluating investigators.

The question is broader than whether a model can supply a citation. Did it receive the evidence needed for the claim? Does the cited record actually contain that evidence? If decisive evidence is removed, will the investigator withdraw its conclusion?

The reverse test matters just as much. Restore the evidence and the investigator should be able to reach a justified conclusion. An investigator that answers every question with “we cannot be sure” has avoided one failure by accepting another.

That tradeoff is already visible in adjacent security work. [Trail of Bits reported on October 21](https://blog.trailofbits.com/2026/10/21/your-ai-agent-fixed-the-bug-but-what-else-did-it-change/) that stricter proof requirements reduced false-positive regression findings in preliminary tests, but left some known regressions unconfirmed. In our transfer test, clearer instructions reduced unsupported conclusions while all complete-history verdicts remained correct. Both kinds of error belong in an evaluation of a proposed safeguard.

## What we still need to learn

We tested two local model installations on a limited set of public captures. Twenty-four of the 25 new histories share one capture, and all 25 report successful source outcomes. The six formatting checks show sensitivity to presentation; they do not establish a general remedy. We have demonstrated the problem in this setup, without establishing its prevalence in working security teams or frontier systems.

The next useful test is whether explicit evidence checking improves on ordinary review. Give each reviewer the same records and comparable computational resources. Compare a general request to check the answer with a requirement to identify the exact record and field supporting each claim. Count unsupported findings corrected, but also supported findings wrongly withdrawn. If ordinary review works just as well, the more elaborate procedure has not earned its place.

We would want that test to include independent captures, successful and failed events, and cases whose outcomes remain unresolved. Whether better-supported findings then improve containment is a further question. This work evaluates findings; it does not measure defensive actions or operational outcomes.

## Help test what should count as evidence

We welcome researchers and security practitioners who want to examine this work with us. The most useful contributions would be shareable investigation cases with clear evidence boundaries, replications on other systems, or comparisons of review methods that measure both unsupported claims and missed justified conclusions. Counterexamples matter: a workflow that handles these distinctions reliably would help identify what works.

The accompanying technical note and limited companion provide the methods, retained responses and scoring needed to start. They also identify what cannot be reproduced from the export. You can challenge a reference judgment, trace a claim back to its input, or propose a test that would change our interpretation.

To discuss a collaboration, write to [research@fideai.org](mailto:research@fideai.org?subject=AI%20investigation%20evidence%20collaboration) with the question you want to test and a brief description of the evidence or expertise you could contribute. A description is enough to begin; please do not send confidential logs or credentials.

Fide's aim is to make the evidence behind a security finding easier to check. A real citation gives the reader somewhere to look. The finding still has to survive that look.

---

**About the supporting experiments.** The combined work contains 996 evaluated calls, including exploratory intervention and robustness checks; repeated calls are not new cases. Four earlier synthetic format checks are recorded separately. All model runs used two locally installed models. The [technical note](TECHNICAL-PAPER.md) describes source selection, scoring, model identities and limitations. The [companion](../README.md) supports offline rescoring of 306 responses based on Apache-licensed Splunk data and arithmetic checks of the full result ledger. The remaining source material stays outside that export while its redistribution terms are resolved.

**Sources:** [Ariel Cyber source repository](https://github.com/ArielCyber/cloud_log_sampling/tree/18d3f248f4def592f4e86152c3fcb54506fbcbf6), [Splunk capture](https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject), [OTRF collection metadata](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/atomic/_metadata/SDAWS-200914011940.yaml), [the separate access-denied case](https://yuy-83.hatenablog.com/entry/iam-source-ip-restriction-cloudformation-error), [AWS error-response documentation](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/ErrorResponses.html).

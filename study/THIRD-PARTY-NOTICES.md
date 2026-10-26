# Third-party notices

The normalized Splunk record fields in `data/splunk-replay.jsonl` derive from Splunk's attack_data repository, commit `aafa53ea228fbab8d9ac3e33c9275fab2136909d`, path `datasets/attack_techniques/T1530/aws_exfil_high_no_getobject/cloudtrail.json`. The adjacent capture metadata credits Bhavin Patel and an Attack Range collection dated April 12, 2023.

Source: https://github.com/splunk/attack_data/tree/aafa53ea228fbab8d9ac3e33c9275fab2136909d/datasets/attack_techniques/T1530/aws_exfil_high_no_getobject

The pinned repository Apache-2.0 license is reproduced unchanged in `licenses/Splunk-Apache-2.0.txt`. Fide's transformations select 24 of 100 objects by a fixed hash order, alias identifiers, project selected service fields, normalize absent source error/response fields to null, and explicitly remove fields in incomplete-evidence conditions. Exact prompts and model outputs are added. These modifications are by Fide, not the source publisher. The source's reported successful reads are not Fide-authenticated AWS audit records.

Other source publishers are credited in the paper. Their raw records and verbatim publications are excluded from this candidate. The decision ledger contains Fide's classifications and calculated results, not copies of their source documents. The paper's factual summaries and minimal illustrative quotations require ordinary final editorial/source review; inclusion here is not a blanket rights opinion.

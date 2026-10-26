# Model identities and two different meanings of reproduction

## Rescore the retained responses

This is supported now. The included offline scripts need Python 3.11 and no model. They recompute categorical scores from included inputs and responses. All 996 responses were also reconstructed in a separate private replay; 306 source-cleared Splunk responses are included in this candidate. Arithmetic verification of the full ledger is distinct from source-to-score verification.

## Generate new model responses

This has not been independently reproduced. Both studies used Ollama 0.40.3 with existing local packages:

| Local tag | Exact local manifest SHA256 |
|---|---|
| gemma4:e4b-mlx | aa6f2058d5dcc8a92dad2e24e35d226ac522b12f7a4f1c395b52fe4bab69a2dd |
| qwen3.8:latest | 22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643 |

Explicit request settings are preserved per call: temperature 0, seed 20261016, context 8192, output cap 512, JSON mode, thinking disabled and stateless messages. Artifact-default parameters also matter. The model/projector files for Qwen match the inspected public `qwen3.8:27b-q4_K_M` distribution, whose manifest hash is `25b843619e944cd0ae6069f94ff4e5e26a16e109ccbc0a66a0f05979ed70098e`. The local parameter layer additionally enables `draft_num_predict: 4`. A fresh mutable-tag pull is not the recorded configuration.

The current public Gemma package differs from the local package in 249 audio/vision tensor digests, two configuration layers and a license layer; 1,931 tensor digests match. Text-only study inputs do not establish package equivalence. Exact-local-digest registry lookups returned 404. This limits the claim of independently repeatable fresh inference.

The `model-metadata/` directory preserves local manifests and parameter objects, without model weights. Every referenced local weight blob was hashed in the private provenance audit. These metadata files identify the package required; they do not provide missing weights or certify upstream training lineage.

For a future fresh replication, obtain the permitted exact packages, verify all blob and manifest digests, restore runtime and parameters, and run into a new output directory. Compare the new results to the retained run without replacing it. If only a different public package is available, call that a different-artifact replication and report the difference. No model download or inference is invoked by this companion.

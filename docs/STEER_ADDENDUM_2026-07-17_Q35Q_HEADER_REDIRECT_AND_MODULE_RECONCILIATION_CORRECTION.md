# STEER ADDENDUM — Q35Q header redirect and module-reconciliation correction

Date: 2026-07-17

Status: **binding correction; CPU/storage/network metadata-only repair authorized; no weight staging, GPU execution, model instantiation with weights, scientific capture, early-exit action, routing intervention, correction policy, or production claim authorized.**

This addendum incorporates the complete current `steer.md`, every prior binding
addendum, and remote head `e366df71d6382fff5dc4803ad35b922e094e1fa9`.
It supersedes only the Q35Q metadata-header and source-to-artifact reconciliation
claims identified below. Every sealed-data, verifier, privacy, provenance,
exact-set, exact-gradient, parity, resource, cleanup, comparator,
nuisance-control, multiplicity, production-gating, and stop rule remains binding.

## Executive finding

Commits `feffd91228446b76b105a3cc8fe793659344e347` and
`e366df71d6382fff5dc4803ad35b922e094e1fa9` contain useful engineering progress,
but neither establishes the terminal sub-gate claimed in its aggregate record.
Classify them as:

- `feffd91228446b76b105a3cc8fe793659344e347`:
  `q35q_phase0_metadata_header_gate_repair_partial`;
- `e366df71d6382fff5dc4803ad35b922e094e1fa9`:
  `q35q_phase0_source_artifact_module_reconciliation_partial`.

The overall outcome remains:

`q35q_artifact_admission_blocked`

The following observations may remain descriptive, aggregate-only engineering
evidence:

- strict `206` and exact numeric `Content-Range` checks were added;
- a committed metadata-header CLI and adapter now exist;
- the hardened Safetensors parser remains useful;
- the live run reportedly reconciled 14 shard headers and 124611 tensor names to
  the downloaded weight index without intentionally requesting tensor payloads;
- a coarse packed-source to numbered-artifact module-name normalization was
  implemented and synthetic tests cover several malformed expert layouts;
- the live module observation reportedly produced 693 normalized source modules
  and 693 normalized artifact modules, with zero coarse missing or extra names;
- no GPU, loaded-weight model, hidden state, router telemetry, JVP, VJP, fitting,
  generation, or scientific capture occurred.

These observations do not establish immutable response provenance, a strict pinned
weight-index identity, a reproducible live source-to-artifact comparison, or a
loadable tensor/parameter manifest.

## Binding defects in the metadata-header pass

### 1. Redirect identity is observed only at the final URL and validated only by scheme

`DescriptorBoundFetcher.fetch()` accepts any final URL beginning with `https://`.
It does not require the final host to belong to a frozen permitted host class, does
not validate the redirect chain, and does not reject an intermediate HTTPS-to-HTTP-
to-HTTPS transition. An arbitrary HTTPS endpoint returning a correctly shaped
range response can therefore satisfy the transport check.

This does not satisfy the prior requirement to make redirect behavior observable
and to reject unexpected host classes, changed identity, downgrade at any hop, or
unobservable redirect behavior.

### 2. Request URL identity is still substring-based

The pre-request check uses string containment and suffix tests:

- `desc.repo_id in url`;
- `"/resolve/<revision>/" in url`;
- `url.endswith(desc.path)`.

This is not exact URL identity. A different host, repository containing the
expected repository string, ambiguous percent encoding, query manipulation, or
path constructed to share the expected suffix can pass. Exact repository,
revision, and path binding requires parsed and normalized URL components, not
substring matching.

### 3. The immutable metadata response is not bound back to the requested revision

The live CLI calls `HfApi.model_info(..., revision=REV, files_metadata=True)` and
then labels every descriptor with the local constant `REV`. It does not require the
returned model-info commit identity to equal `REV`. The expected revision is
therefore copied into the descriptor rather than equality-bound to the immutable
metadata response.

A valid live admission must fail closed unless the metadata service reports the
exact requested immutable commit and every admitted sibling belongs to that
response.

### 4. The weight index is not admitted with strict identity and grammar

The live CLI downloads `model.safetensors.index.json` at the requested revision and
loads it with ordinary `json.load`. The production path does not:

- freeze and compare the index file's immutable remote blob/LFS identity and size;
- reject duplicate JSON keys;
- validate the complete top-level and `weight_map` schema;
- reject booleans, non-string tensor names, non-string shard paths, empty names,
  path traversal, or unrecognized fields according to a frozen grammar;
- prove that the local index bytes match the independently frozen remote identity.

Ordinary JSON parsing silently collapses duplicate keys. A header reconciliation
cannot be terminal while its authoritative tensor-to-shard index is admitted
through a fail-open parser and unverified local bytes.

### 5. The LFS OID remains descriptor metadata, not observed response identity

Freezing the public LFS OID is useful. The ranged response, however, is not compared
with a response-side immutable identity such as an exact ETag or equivalent when
available. The permitted claim must remain narrow: the code binds the request to
public descriptor metadata and validates range semantics; it does not
cryptographically authenticate tensor payload bytes or prove that an arbitrary
HTTPS range body came from the declared LFS object.

## Binding defects in the source-to-artifact equality claim

### 6. The live reconciliation composition is not committed

The commit contains the pure normalizer, synthetic tests, an aggregate report, and
a status heartbeat, but no committed CLI or adapter that reproduces the reported
live construction of:

1. the pinned installed source/package identity;
2. the exact source class and meta-device parameter/module enumeration;
3. the strict pinned weight-index parse;
4. canonical artifact tensor-to-module derivation;
5. the frozen representation map;
6. the final equality decision and aggregate evidence.

Repository search finds the reconciliation function only in the pure module and its
tests. The live result is therefore not reproducible or adversarially testable from
the committed production path.

### 7. Coarse module-name equality is not load-manifest equality

The implementation collapses all numbered expert tensors in a layer into only two
source module names:

- `mlp.experts.gate_up_proj`;
- `mlp.experts.down_proj`.

That proves, at most, a coarse naming correspondence. It does not establish:

- exact tensor names and multiplicity;
- quantization auxiliary tensors such as scales, zeros, indices, or packed weight
  records;
- dtype and shape compatibility;
- expert-axis ordering;
- gate/up fusion ordering;
- packed storage layout;
- the exact loader conversion that transforms 256 numbered split experts into the
  source class's fused packed representation;
- successful strict loading without ignored, missing, renamed, or synthesized
  tensors.

No weight may be staged on the basis of module-set equality alone.

### 8. Canonical expert identity and multiplicity are not enforced

Expert identifiers are converted with `int()`. Noncanonical aliases such as `0`
and `00` collapse to the same integer. Inputs are converted to sets, so duplicate
module evidence and alias multiplicity disappear. `num_experts=True` is also
accepted because booleans are integers in Python.

The normalizer must require strict integer types, canonical decimal expert IDs,
unique source and artifact records, exact per-layer expert sets, and exact
multiplicity before normalization.

### 9. Exact layer and parameter-schema coverage is not bound to the pinned config

The pure function counts only layers in which an expert regex match occurs. It does
not independently require the exact expected expert-layer set, the exact number of
hidden layers, or the exact attention/DeltaNet/shared-expert parameter schema from
the pinned source and configuration. Equality can only be meaningful when both
input manifests are independently complete and their construction is committed.

### 10. Source/package identity is still an upstream blocker

The meta-device source set cannot be admitted until the installed Transformers
package, source file, class qualname, source digest/commit, configuration, and
loader/conversion implementation are independently pinned and equality-checked.
The current aggregate record correctly lists source/package identity as open;
therefore its stronger statement that exact source-to-artifact equality is already
established is premature.

## Required repair

### A. Repair immutable metadata, index, URL, and redirect admission

The committed production path must:

1. require the model-info response commit SHA to equal the frozen revision;
2. freeze an exact descriptor for the weight index itself, including repository,
   revision, path, immutable blob/LFS identity, and size;
3. verify local index bytes against the independent remote identity before parsing;
4. parse the index with duplicate-key rejection and a frozen strict schema;
5. use `urllib.parse` or an equivalently strict parser to require exact normalized
   request scheme, host, repository path, revision segment, and shard path;
6. expose the complete redirect chain, including each hop's source URL, status, and
   destination;
7. reject non-HTTPS at any hop, unexpected hosts, credentials, fragments,
   malformed encoding, ambiguous paths, or a final host outside a frozen permitted
   Hugging Face/CDN host set;
8. compare response-side immutable identity headers with the frozen descriptor when
   the service supplies a documented stable identity, while preserving the narrow
   no-payload-cryptographic-verification claim;
9. add adversarial production-path tests for arbitrary HTTPS redirects,
   intermediate downgrade, host substitution, repository substring collisions,
   percent-encoding ambiguity, metadata SHA mismatch, index duplicate keys, index
   cache corruption, and wrong-but-valid-shaped index identity.

Until a fresh live rerun passes this exact composition, the metadata-header result
remains partial.

### B. Commit the real source-to-artifact reconciliation path

Add a single production CLI/adapter used identically by tests and live work. It must
independently derive and then compare:

- pinned source/package/class/config identities;
- the source parameter and module manifest from the admitted text-only class;
- the artifact tensor manifest from the strictly admitted weight index and headers;
- the frozen representation and omission maps;
- exact layer, expert, and parameter-schema coverage;
- aggregate counts plus hashes of canonical public manifests.

Expected and observed manifests may not be produced by the same provider or copied
into both sides of an equality check.

### C. Prove the actual numbered-to-packed load transformation

Before weight staging, identify and pin the exact Transformers/GPTQ loader code that
maps artifact tensors into the source class. Validate, using metadata only where
possible:

- every numbered expert and quantization auxiliary tensor;
- exact shapes, dtypes, and packing parameters;
- canonical expert ordering;
- gate/up fusion order and dimensions;
- down-projection layout;
- shared-expert and router parameters;
- full-attention and Gated DeltaNet parameter paths;
- final normalization, embeddings, and output head;
- zero ignored, missing, unexpected, or synthesized tensors under strict loading.

If no deterministic pinned loader transformation exists, record
`q35q_load_manifest_blocked`; do not improvise a conversion after inspecting weight
values.

### D. Fresh validation and allowed outcomes

After repair, run the full repository tests, production-path integration tests,
privacy/no-text checks, provenance checks, dependency/source checks, and
commit-safety checks. A fresh run may record only:

1. `q35q_phase0_metadata_header_gate_passed` when the corrected immutable metadata,
   strict index, exact URL, and redirect conjunction passes;
2. `q35q_phase0_source_artifact_load_manifest_passed` when the reproducible exact
   tensor/parameter and loader transformation conjunction passes;
3. `q35q_artifact_admission_blocked` or `q35q_provenance_blocked` with the narrow
   failing condition;
4. `host_execution_authority_unavailable` only when the already-authorized
   CPU/storage/network work is genuinely unavailable.

Weight staging remains prohibited until every Phase-0 prerequisite and one final
production-path conjunction pass together.

## Remaining Q35Q order

1. repair and rerun the metadata-header provenance path;
2. commit and pass the exact source-to-artifact tensor/load-manifest path;
3. complete non-self-bound tokenizer and source/package identity admission;
4. route remote enumeration, checksums, storage, cleanup, resume, cache isolation,
   and reconciliation through the repaired staging orchestration;
5. compose one final Phase-0 conjunction with adversarial self-binding and
   provenance tests;
6. stage weights only after the genuine aggregate Phase-0 pass;
7. wait for a separately authorized and verified dual-3090 transition;
8. pin the exact tensor-parallel, quantization, kernel, and autograd runtime before
   any exact JVP/VJP work.

No current GPU tenant may be signalled, stopped, displaced, or treated as released
from low utilization.

## External-evidence boundary

The primary-source scan does not justify changing the active Q35Q execution order.
It adds one useful future comparator:

- *Latent Programming Horizons in Coding Agents* (arXiv:2607.05188) reports that
  simple linear probes over coding-agent residual streams decode current program
  properties and correctness, and predict some future edit outcomes above chance.
  This supports a future M39 comparator sampled at frozen tool/action decision
  points, with project- and benchmark-disjoint outer evaluation, train-fold-only
  layer selection, nuisance controls, and explicit regression accounting. It does
  not establish Jacobian-Lens value, causal monitoring, repair, safe abort, or
  transfer to Agents-A1.

The official `anthropics/jacobian-lens` repository remains a one-commit reference
implementation. Its README states that fitting is dominated by the model backward
pass and is not optimized. It supplies no quantized-MoE parity result, distributed
large-MoE recipe, or Agents-A1 transfer evidence.

Path-constrained MoE work continues to support cross-layer expert paths as an
observational unit, not isolated expert counts. Counterfactual routing and causal
audits continue to prohibit converting route correlations directly into expert
importance, pruning, forced routing, or repair claims.

The current r/LocalLLaMA material remains lead-only. The open-Qwen J-space claim has
not supplied independently frozen evaluation, exact-gradient parity, or credible
Agents-A1-scale evidence requiring a protocol change.

## Claims that remain prohibited

No Q35Q Phase-0 admission, complete artifact provenance, strict loadability, exact
GPTQ/NF4 autograd, quantized Jacobian/JVP/VJP parity, Agents-A1 transfer,
completed-error prediction, universal hidden-state correctness awareness,
semantic-workspace correctness monitoring, safe early exit, safe truncation,
dynamic abstention, causal expert localization, forced routing, correction policy,
activation steering, or production utility is established.

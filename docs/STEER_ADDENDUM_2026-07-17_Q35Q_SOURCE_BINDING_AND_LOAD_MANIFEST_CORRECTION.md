# STEER ADDENDUM — Q35Q source binding and text-only load-manifest correction

Date: 2026-07-17

Status: **binding correction; repository/CPU/storage/network work only; no weight staging or scientific capture authorized.**

This addendum incorporates the complete current `steer.md`, every prior binding
addendum, and remote head
`074e9902fb4d61ed8c5a9d3ccf4f0d8cddae24eb`. It supersedes prior status claims
only where necessary to correct the Q35Q source/load-manifest admission result.
Every sealed-data, verifier, privacy, provenance, exact-set, exact-gradient,
parity, resource, cleanup, comparator, nuisance-control, multiplicity,
production-gating, and stop rule remains binding.

## Executive finding

Commit `074e9902fb4d61ed8c5a9d3ccf4f0d8cddae24eb` is useful partial engineering
work, but `defect_4_source_and_load_manifest_admission` is **not closed**, even
at the logic level. Classify it as:

`q35q_source_admission_repair_partial`

The repository's overall operational outcome remains
`q35q_artifact_admission_blocked`. The claim that live production composition is
the sole remaining gate is superseded. Source identity binding, exact
load-manifest admission, and live production composition all remain open.

No weight staging, model instantiation, GPU execution, generation, hidden-state
capture, router capture, JVP, VJP, fitting, M39 capture, intervention, or
production action is authorized.

## Defects in the source-identity validator

### 1. Source-hash shape is not source binding

`validate_source_identity()` currently accepts any syntactically valid 40- or
64-hex value as `source_sha`. It does not compare the observed source identity
to an independently derived expected commit or file digest.

An arbitrary wrong but well-formed hash therefore passes. The validator must
accept an independently derived expected source identity and require exact
equality. The expected value must come from the pinned immutable implementation
source, not from the same caller object or local bytes used to form the observed
value.

### 2. Module qualname is present but not admitted

The current function requires only a non-empty `module_qualname`. Any unrelated
module name passes. Bind the observed qualname to the exact expected module and
class mapping derived from the pinned runtime source.

Tests must show that a non-empty wrong qualname and a valid-shape wrong source
hash both fail.

## Defects in the text-only load-manifest validator

### 3. Shape binding is optional

`param_shapes` defaults to absent. When omitted, the embed, output-head, and
expert-width checks are not added to the conjunction, and the manifest may pass
without any shape proof.

The final Phase-0 conjunction must require independently derived parameter
shapes for every frozen architecture width needed by admission. Missing,
ambiguous, malformed, or caller-invented shape evidence is a failure, not a
reduced-strength pass.

### 4. Substring matching permits decoy modules

Projection admission uses `leaf in name`. A decoy parameter such as a backup,
shadow, wrapper, or unrelated module containing the expected substring can
satisfy the check without proving the exact projection path used by the admitted
text-only class.

Replace substring admission with exact canonical path or exact parsed path-
segment admission derived from the pinned implementation and weight index.
Require the expected projection set on every linear-attention and
full-attention layer. Unknown aliases do not pass without a separately pinned
mapping.

### 5. Shared and routed expert checks are global rather than per-layer

The current conjunction passes `shared_expert_present` when any shared-expert
name exists anywhere and passes `routed_experts_present` when any one numbered
expert exists anywhere. This does not prove the frozen 40-layer text path has
the required expert construction on every applicable layer.

Require per-layer expert admission from the exact pinned source and public
weight map. Bind the expected routed-expert representation, count or packed
layout, shared-expert representation, and relevant shapes for every MoE layer.
Do not assume individually numbered expert keys when the pinned artifact uses a
packed layout; derive and freeze the exact representation before comparison.

### 6. Deny-list omission checks are not a complete text-only allow-list

The current vision and MTP omission proof depends on regular expressions over a
small alias list. A vision or MTP module under an unrecognized public name can
escape the deny list.

The final admission must positively bind the complete allowed text-only module
set derived from the pinned class and weight index, then reject every module
outside that set. Vision/MTP deny-list checks may remain as defense in depth but
cannot be the sole omission proof.

## Binding status correction

Effective immediately:

- supersede the claim that source/load-manifest defect 4 is closed;
- classify commit `074e990...` as `q35q_source_admission_repair_partial` for
  gate purposes;
- retain its useful pure validators and tests as partial evidence;
- supersede the progress-record statement that live production composition is
  the sole remaining gate;
- keep `q35q_artifact_admission_blocked` active;
- do not stage weights;
- do not run GPU or scientific work;
- preserve the unrelated GPU tenant and every existing resource-transition,
  cleanup, provenance, privacy, and production gate.

No scientific result is invalidated because no Q35Q scientific execution has
occurred.

## Active Q35Q milestone

Before any Phase-0 pass may be emitted, the next host-capable cycle must:

1. Bind observed source commit/file digest to an independently derived expected
   immutable identity by equality.
2. Bind the exact module qualname and admitted class mapping by equality.
3. Make parameter-shape evidence mandatory in the final conjunction.
4. Replace permissive substring checks with exact canonical module-path or
   parsed-segment checks.
5. Prove shared-expert and routed-expert construction per applicable layer under
   the exact pinned packed or unpacked representation.
6. Construct a complete positive allow-list for the text-only load manifest and
   reject every unapproved module; retain vision/MTP deny lists only as defense
   in depth.
7. Add regression tests for a valid-shape wrong source hash, wrong non-empty
   module qualname, omitted shapes, decoy projection substrings, expert evidence
   present in only one layer, unexpected module aliases, and caller-supplied
   source evidence derived from the observed value itself.
8. Wire corrected source/load-manifest admission, tokenizer admission, and
   staging orchestration into the real pinned-repository CLI path.
9. Exercise every failure through the same production composition used for the
   final overall conjunction.
10. Run fresh tests, privacy scans, no-text checks, provenance checks, and
    commit-safety checks, then emit exactly one outcome permitted by the current
    steer.

## External research disposition

The current scan does not justify changing the scientific sequence or weakening
any gate.

- New public Jacobian-lens workbenches and fitted open-model lenses are useful
  replication and engineering leads, not evidence of exact quantized parity or
  transfer to Agents-A1.
- Recent hidden-state verification work reinforces the need for prompt/family
  disjoint evaluation, nuisance residualization, and a strict separation between
  detection and intervention.
- Recent MoE routing work supports observation-only route-path, margin, and
  counterfactual-utility comparators on independent data. It does not authorize
  router updates, forced experts, early exit, truncation, correction, or
  production control.
- The current r/LocalLLaMA scan supplied no independently verified evidence that
  changes the protocol. Reddit remains lead-only.

## Claims boundary

Established now:

- M38E remains terminally closed at `inconclusive`;
- Q35Q remains blocked before weight staging and GPU execution;
- the new source/load-manifest code is partial engineering evidence;
- source identity equality, mandatory shape binding, exact module-set admission,
  per-layer expert proof, and live production composition remain open;
- no Q35Q scientific capture has occurred.

Not established:

- Q35Q artifact or runtime admission;
- exact GPTQ or NF4 gradients, JVPs, or VJPs;
- quantized Qwen3.5 Jacobian parity;
- transfer to Agents-A1;
- completed-error prediction or general error awareness;
- semantic-workspace correctness monitoring;
- safe truncation or early exit;
- causal expert localization;
- router intervention, forced-expert repair, activation steering, correction
  policy, or production utility.

Treat the repository as publicly visible. Raw prompts, fixture text, token IDs,
outputs, hidden states, activations, routes, expert identities, telemetry arrays,
Jacobians, JVPs, VJPs, lens matrices, per-example predictions, process evidence,
weights, caches, local paths, environment values, credentials, and secret-linked
provenance remain private and uncommitted.

# Steer addendum — Q35Q reduced-meta extrapolation and source-independence correction

Date: 2026-07-17

This addendum is binding program control. It preserves every existing sealed-data,
privacy, provenance, verifier, exact-set, resource, production-gating, and claim-
boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `e0896b72e291a05bb64cb0e384ad07270107ba31` added a useful committed
CPU-only source-to-artifact reconciliation path and correctly retained the overall
outcome `q35q_artifact_admission_blocked`. Its narrower outcome
`q35q_phase0_source_artifact_module_equality_established` and the statement that
the providers are "not self-bound" are premature.

The live path downloads `config.json` from the same pinned artifact whose weight
index forms the artifact side, instantiates the source class from that config, and
does not first compose the frozen architecture/config admission conjunction. The
source implementation and weight index are distinct inputs, but the source-side
construction is still conditioned on artifact-supplied configuration that has not
been independently admitted in this path.

The live path also mutates the configuration to construct only four layers and two
experts, enumerates parameters from those four layers, and extrapolates two observed
layer templates over the full 40-layer schedule. That is a useful engineering
probe, but it is not direct enumeration of the complete pinned 40-layer source
manifest. Until the pinned implementation is identity-bound and audited to prove
that no layer-index-dependent parameter branch exists beyond the two assumed
attention kinds, the extrapolation can miss a source module that appears only
outside layers 0-3. Synthetic tests over caller-supplied parameter names do not
close that gap.

## Binding classification

Reclassify commit `e0896b72e291a05bb64cb0e384ad07270107ba31` as:

`q35q_phase0_source_artifact_module_reconciliation_partial`

The following evidence remains usable:

- the strict weight-index admission is composed into a committed CLI;
- a real text-only class is constructed on the meta device without weights or GPU;
- the observed four-layer templates reconcile with the artifact-derived coarse
  module set under the frozen prefix, omission, and packed/numbered map;
- the live run reports zero missing and zero extra names under that bounded
  extrapolation.

The following are not established:

- independently admitted source-side configuration;
- complete 40-layer source parameter-module enumeration;
- absence of layer-index-dependent source branches outside the observed template;
- exact source/package/class identity;
- exact tensor/load-manifest equality or strict loadability.

The overall outcome remains:

`q35q_artifact_admission_blocked`

## Required repair

Before source-to-artifact module equality may be promoted:

1. Admit the exact local `config.json` bytes through an independently frozen
   immutable identity and the complete frozen architecture/config conjunction
   before using the configuration for source construction.
2. Preserve the admitted configuration unchanged. Do not mutate the admitted
   object in place for a reduced construction.
3. Prefer direct meta-device construction and enumeration of the complete frozen
   40-layer text-only source class. Meta tensors allocate metadata rather than
   weight payloads, so a reduced construction requires an explicit measured
   necessity rather than assumption.
4. If reduction remains necessary, use a separate derived configuration and bind
   an immutable source inspection proving that parameter/module construction is
   invariant within each admitted layer kind and has no additional layer-index,
   first-layer, last-layer, expert-count, MTP, or conditional branch. Test every
   source branch used in that proof.
5. Compare the full direct source enumeration with the expanded reduced
   enumeration in an adversarial integration test; require exact equality before
   the reduced path can stand in for the full path.
6. Bind the exact Transformers package, source file, source digest, class
   qualname, configuration class, and model-construction dispatch before treating
   the source provider as admitted and independent.
7. Keep module-set reconciliation separate from exact tensor/load-manifest
   admission. Sets may not establish multiplicity, shapes, dtypes, GPTQ auxiliary
   tensors, expert ordering, gate/up fusion, packed layout, ignored keys,
   synthesized tensors, or strict loadability.
8. Add production-path tests that fail when an extra module exists only after the
   reduced layer window, when the artifact config disagrees with frozen
   expectations, when the source class/package identity is wrong, and when the
   reduced and full meta manifests differ.

## Execution boundary

No weight shard may be staged and no GPU window may be released on the basis of
the current reconciliation. Continue in the existing order:

1. repair complete source/config identity and enumeration;
2. prove exact numbered-GPTQ-to-packed-source tensor/load semantics;
3. run the single adversarial Phase-0 conjunction;
4. stage weights only after that conjunction passes;
5. obtain an independently authorized and verified resource transition;
6. prove exact quantized forward and VJP/JVP parity before fitting.

M38E remains terminally closed at `inconclusive`. No completed-error predictor,
semantic-workspace correctness monitor, safe early-exit or truncation rule,
causal expert localization, routing intervention, correction policy, activation
steering result, Agents-A1 transfer, or production utility is established.

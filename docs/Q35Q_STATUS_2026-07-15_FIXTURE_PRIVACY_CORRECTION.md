# Q35Q status correction — fixture privacy and artifact admission

Date: 2026-07-15

This is a prospective status correction. It does not alter M38E, M39, the GPTQ-then-NF4 order, any frozen task or threshold, any verifier rule, or any production gate.

## Defect found

Commit `29b4168d64feff7770a21c451d67dafaa9f9a3d6` introduced a synthetic token-id fixture derived from a public integer seed and committed that seed alongside the public derivation algorithm. The resulting token IDs were therefore reconstructible from the public artifact despite the repository privacy boundary forbidding committed token IDs.

The same implementation labeled the synthetic sequence a tokenization/text-only-load fixture even though it did not execute the pinned tokenizer or prove a text-only model load. `build_admission_record` accepted any canonical JSON object as `tokenization_fixture`, so the synthetic record or unrelated metadata could satisfy that admission field without the required evidence.

## Corrections committed

- `96b81396fca5825067eaeeef88248628e2929658`: replace the public-seed derivation with domain-separated HMAC-SHA256 using a minimum 32-byte private key retained only in the sealed local ledger; commit only aggregate commitments and explicitly mark tokenizer roundtrip and text-only load as unestablished.
- `f47156381d3b3359374de7d4e151316df6728239`: add fail-closed tests for private-key requirements, schema exactness, legacy public-seed rejection, and admission separation.
- `f84796743cbb5ae74be5daf104f2b431c95b5c9f`: require artifact admission to validate an exact tokenizer-roundtrip/text-only-load schema bound to the admitted tokenizer identity, two or more deterministic repeats, `use_cache=False`, the frozen 32-token/248320-vocabulary shape, and a keyed HMAC commitment to the private input.
- `a3445d5f99e07130c6bf176d21b8aabc68aec677`: add admission tests rejecting synthetic VJP-smoke records, legacy reconstructible seed records, mismatched tokenizer identity, non-Boolean claims, and malformed evidence.

No private key, private text, token ID, raw token array, prompt, model output, hidden state, route, Jacobian, VJP, or lens matrix was committed.

## Test boundary

The changed fixture and admission modules passed 101/101 targeted tests in an isolated Python test harness reconstructed from the committed modules. This is not a fresh repository-wide test or commit-safety heartbeat. The prior 320/320 heartbeat applies only to head `06db22c86afed3e22c721bef61d219d37f9c1a75`, before these corrections.

## Current Q35Q state

The CPU-only synthetic sequence primitive is available for the Phase-1 VJP smoke without publicly reconstructible token IDs. It does not satisfy artifact admission.

Before any backward call, the repository still requires a real record produced by the pinned tokenizer and text-only load harness, with:

- exact tokenizer identity binding;
- at least two identical tokenization runs;
- sequence length 32, batch size 1, vocabulary size 248320, and `use_cache=False`;
- successful text-only load evidence;
- keyed HMAC commitment to the private input;
- sequence digest only, with raw text and token IDs sealed and uncommitted;
- refreshed driver manifests, full repository tests, privacy scan, and commit-safety evidence.

Until that record exists, the correct outcome is `q35q_artifact_admission_blocked`. Q35Q GPU execution also remains barred while M38E owns the dual-RTX-3090 window.

## M38E status boundary

This review did not inspect, interrupt, signal, reconfigure, or otherwise touch the active M38E process, environment, worktree, cache, or private ledger. The latest audited heartbeat remains 253/288 official tasks complete, 35 remaining, with no active-attempt blocker and finalization still pending completion plus every frozen audit.

## Steering decision

No `steer.md` change is warranted. The corrections enforce the existing privacy and artifact-admission rules and narrow an implementation that was claiming more than it established. The research program remains incomplete and production remains gated.

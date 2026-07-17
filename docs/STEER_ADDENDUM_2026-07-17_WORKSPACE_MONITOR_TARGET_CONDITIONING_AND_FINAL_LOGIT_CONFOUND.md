# Steering addendum — workspace-monitor target conditioning and final-logit confounds

Date: 2026-07-17

This addendum is binding for any future semantic-workspace, hidden-state,
Jacobian-lens, prompt-injection, truncation, retry, abstention, or
Agents-A1 monitoring experiment. It does not change the active Q35Q
production-path provenance milestone, authorize weights or GPUs, reopen M38E,
or weaken any privacy, sealed-data, verifier, parity, resource, or production
gate.

## External implementation inspected

Public source inspected at immutable commit:

- repository: `OphanimLLC/silent-thoughts`
- commit: `844980cd460b1740973d334da3ebc58001640972`

The repository is a useful implementation lead for Jacobian-lens readout,
late-layer token tracking, and direct residual-stream intervention. Its own
README limits the evidence to one 26B instruction-tuned MoE and one small dense
model, states that monitor thresholds were tuned on a handful of probes rather
than a benchmark, and describes steering as a causal probe rather than a
control method.

## Binding audit interpretation

The shipped `kernel_monitor` is not evidence of a target-blind semantic monitor
or a Jacobian-lens-specific detector.

1. The operator supplies a list of watched words before inference.
2. Each watched item is resolved to one tokenizer ID, with multi-token items
   reduced to one piece.
3. The score is the best literal-token rank across the last six fitted lens
   layers and the ordinary final model-logit row.
4. The final model logits are included in the same minimum-rank statistic.
5. A fixed rank threshold of 10 is used for the red alert.
6. The implementation also generates the answer and flags literal word
   occurrence anywhere in that answer. That branch is outcome inspection, not
   pre-emission detection.
7. The rewrite path injects a centered unembedding direction at a late layer
   and treats any changed string as a successful causal effect. Output change
   is not correctness, safety, non-degeneracy, or repair.

Therefore the implementation establishes only that a target-conditioned,
literal-token probe can surface selected words in late readouts or final logits
on the demonstrated prompts, and that a strong late residual intervention can
change greedy output. It does not establish:

- target-blind prompt-injection detection;
- semantic equivalence detection under paraphrase or obfuscation;
- completed-error prediction;
- general correctness awareness;
- incremental value from Jacobian transport over ordinary next-token logits;
- safe rewrite, correction, truncation, retry, abstention, or production use;
- transfer to Agents-A1 or another large MoE family.

## Required future comparator decomposition

Any future monitor benchmark must report these systems separately rather than
combining them into one score:

1. ordinary final next-token logits only;
2. prompt-final hidden state only;
3. late raw-layer or logit-lens readout only;
4. Jacobian-lens readout only;
5. router/path telemetry only;
6. metadata and output-confidence baselines;
7. combinations fitted only on the training partition.

A Jacobian-lens claim requires positive sealed incremental value over the final
logit, hidden-state, confidence, metadata, and route/path baselines. Taking the
minimum rank across Jacobian-lens layers and the final output row is not an
admissible Jacobian-specific statistic.

## Target-conditioning and lexical-confound gates

A target-conditioned watch list may be evaluated only as a separate oracle or
known-policy condition. It may not be reported as general detection.

The primary monitor must be target-blind at evaluation time and must include:

- clean prompts containing the watched term as an innocent mention;
- attacks that comply without repeating the attack's literal target token;
- paraphrases, synonyms, translations, homoglyphs, spacing changes,
  tokenization changes, and multi-token concepts;
- matched prompts where lexical content is held constant but instruction
  authority or compliance outcome changes;
- answer-identity, target-token, prompt-family, prompt-length, and tokenizer
  controls;
- family-disjoint and model-family-disjoint outer evaluation;
- per-family effects, calibration, false-positive rate, false-negative rate,
  and sign reversals;
- thresholds and feature-selection rules frozen before sealed evaluation.

Target words, target concepts, layer windows, rank cutoffs, persistence rules,
concentration thresholds, and late-survival rules may not be selected using the
sealed evaluation labels.

## Pre-emission boundary

Generated-answer inspection may be used only to construct outcome labels after
the monitor feature record is frozen. It may not be included in a
`pre_emission` feature or detection claim.

The repository must distinguish:

- feature time: before generation or before the evaluated action;
- label time: after generation, tool execution, verifier execution, or task
  completion;
- intervention time: any retry, abort, rewrite, truncation, routing change, or
  activation edit.

No information available only at label time may leak into the monitor feature
set, threshold selection, or example inclusion rule.

## Intervention separation

Direct residual injection, Jacobian-transpose injection, forced routing,
rewriting, retry, truncation, and abstention remain separate intervention
experiments. A changed output string is insufficient. Any later intervention
protocol must independently measure correctness, right-to-wrong transitions,
wrong-to-right transitions, degeneration, calibration, latency, and privacy.
Detection must pass its sealed gate before intervention begins.

## Program status

The active milestone remains production-path upstream/runtime provenance
composition for Q35Q. The aggregate status remains:

`q35q_artifact_admission_blocked`

No weight staging, model execution, GPU execution, hidden-state capture, router
capture, Jacobian fitting, sealed scientific evaluation, or production use is
authorized by this addendum.

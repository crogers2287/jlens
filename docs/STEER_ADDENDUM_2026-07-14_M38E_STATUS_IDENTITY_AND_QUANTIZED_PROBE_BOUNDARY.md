# Binding addendum — M38E status identity and quantized-probe evidence boundary

Date: 2026-07-14

This addendum supplements `steer.md`, `CODEX_AUTOSTEER.md`, the M38E protocol,
and the M39 design draft. Every sealed-data, verifier, privacy, provenance,
exact-set, cap-escalation, resource, retry, statistical, production, and stop
rule remains in force. Nothing here authorizes a restart, retry, new scientific
capture, threshold change, task-set change, or retrospective reinterpretation.

## 1. Correct the public description of the frozen M38E task set

The frozen M38E development manifest and committed generator define exactly
three families:

1. `mod_chain`;
2. `alg_coeff`;
3. `order_track`.

There are four bands per family and 24 official tasks per band, for exactly 288
unique official tasks. `json_digits` is not an M38E family and may not be run,
counted, substituted, or described as remaining M38E work. Any public status
text saying that `json_digits` is next or part of the sweep is a status-only
error, not authorization to expand the task set.

The next aggregate heartbeat must correct this prospectively without rewriting
Git history and without touching the active process, worktree, model, ledger,
or environment.

## 2. Distinguish official-task progress from execution-row count

The private ledger can contain cap-choice pilot rows in addition to the 288
unique official tasks. Public status must therefore report these separately.
For example, the 2026-07-14T07:05Z heartbeat describes 121 execution rows as 96
official 2,048-token task rows plus 25 4,096-token pilot rows. That is 96 of 288
unique official tasks completed, not 121 of 288.

Future heartbeats and summaries must use unambiguous labels such as:

- `unique_official_tasks_completed`;
- `pilot_rows_completed`;
- `full_band_4096_rows_completed`, if any;
- `total_execution_rows`.

Pilot rows are cap-choice evidence only. They may not inflate task completion,
power, class-balance, family-eligibility, or completed-error counts.

## 3. Preserve the claim boundary around the completed `mod_chain` capture

The aggregate fact that no `mod_chain` band met the frozen 4,096-token material-
reduction rule may be reported as a descriptive execution fact. Before the full
sweep and every finalization audit pass, it must not be called a scientific
finding, final family result, benchmark outcome, or evidence for or against
jLens.

Under the frozen driver, a band whose triggered pilot fails the material-
reduction rule is ineligible by escalation failure. Do not relax that rule,
replace the family, add tasks, increase the cap, reinterpret persistent
truncation as a completed error, or count pilot rows in eligibility arithmetic.
The final public outcome remains contingent on exact-set, escalation,
verifier, provenance, privacy, dependency, resource, cleanup, and commit-safety
audits.

## 4. Quantized hidden-state probe evidence does not change M38E or authorize M39

`Hallucination Is Linearly Decodable from Mid-Layer Hidden States in Quantized
LLMs` (arXiv:2606.02628) is relevant as exploratory evidence that linear
truthfulness signals can survive 4-bit quantization in smaller dense models.
It does not establish completed-error prediction on Agents-A1 or a large MoE.
Its primary protocol classifies benchmark-supplied candidate answers rather
than freely generated model completions, and its reported peak-layer summary
selects the best layer using held-out test AUROC. Those choices cannot be used
as a confirmatory layer-selection rule or effect estimate in this program.

Accordingly:

1. M38E remains unchanged.
2. M39 remains design-only and capture-prohibited.
3. Any M39 hidden-state comparator must use freely generated completed answers,
   the task row as the unit of analysis, and layers frozen before outcome-bearing
   capture.
4. Layer selection, pooling, normalization, projection, classifier choice, and
   calibration must occur only under the already required nested-CV and locked-
   holdout rules.
5. Full raw hidden states may not be retained merely to search for a favorable
   layer. Capture must remain limited to the minimum preregistered private
   representation necessary for the frozen comparator and privacy audit.
6. Attention-weight capture is not added by this addendum. Optimized vLLM/MoE
   serving may not expose exact attention probabilities without changing the
   runtime or parity boundary; any future attention comparator requires a
   separate feasibility and parity amendment.

This paper is therefore a methodological lead, not evidence that M39, a
Jacobian Lens, semantic monitoring, safe truncation, early exit, repair,
steering, or production deployment works on Agents-A1.

## 5. Current authorization

- Continue M38E attempt one undisturbed.
- Keep automatic retry fail-closed.
- Correct only future aggregate status wording.
- Perform no M39 scientific capture before M38E finalization and a complete
  launch amendment.
- Preserve the frozen stop rule: if the M38E frontier gates are not met after
  the exact bounded sweep, record `m38e_completed_error_frontier_not_found` and
  stop rather than expanding the benchmark.

# CODEX_AUTOSTEER.md — bounded autonomous milestone loop

This file is the operating contract for Codex or another coding agent when running `jlens` without chat-app round trips.

The repository remains milestone-driven. `steer.md` is the current source of truth. This file defines how the agent may loop from one milestone to the next.

## Prime directive

Advance `jlens` one milestone at a time using `steer.md` as the source of truth.

Do not invent a new direction until the current milestone stop condition is met.

Do not weaken gates to make progress look better.

## Current strategic direction

The practical runtime track has proved the private local AI supervisor path:

- live local model batches
- deterministic verifiers
- action routing
- safe action execution
- transient full-output checker execution
- fixture-grounded regeneration
- public-safe aggregate reporting
- private local records

The next branch is internal telemetry research using a Hugging Face / safetensors backend, while keeping the GGUF runtime harness intact.

## Autoloop enablement

Autoloop is enabled only when an explicit environment variable or operator instruction says so:

```bash
export CODEX_AUTOSTEER_LOOP=true
```

When this is not set, complete only one milestone, update `steer.md`, commit the steer update, and stop.

When this is set, continue only within the limits below.

## Loop limits

Autoloop may continue for at most:

- 3 milestone completions, or
- 4 wall-clock hours, or
- until any stop condition/blocker appears.

Stop immediately if any of these occur:

- test suite fails and the fix is not obvious
- commit-safety check fails
- public artifacts would require raw prompt/output/context/model text
- private data would need to be committed
- a model download, Hugging Face license, or hardware/VRAM decision is required
- a new dependency materially changes runtime setup
- a real web retrieval adapter would be introduced
- arbitrary shell/code execution from model output would be introduced
- telemetry cannot be verified and would need to be fabricated
- the next milestone changes the research direction significantly

## Per-milestone loop

For each milestone:

1. Read:
   - `steer.md`
   - `STATE.md`
   - `reports/FINDINGS.md`
   - relevant docs/config/source files named in steer
   - this file

2. Execute exactly the current milestone.

3. Preserve invariants:
   - no private prompt/output/context/full-generation text in public artifacts
   - raw logs stay in gitignored private paths
   - `auto_outcome`, `action_result`, and `grounded_result` remain candidates, not gold
   - production remains gated unless a future steer explicitly defines audited unlock criteria
   - no arbitrary shell execution from model output
   - no live web retrieval unless explicitly approved in steer
   - do not fabricate telemetry
   - GGUF paths must mark telemetry missing honestly
   - HF/safetensors telemetry must be marked missing/unsupported when hooks are unavailable
   - model weights, caches, and local env files must not be committed

4. Add or update as needed:
   - source files
   - schemas
   - public aggregate artifacts only
   - docs for the milestone
   - tests
   - `STATE.md`
   - `reports/FINDINGS.md`

5. Run the full test suite.

6. Run commit-safety/no-text checks for public artifacts.

7. Commit the milestone with a clear message, for example:

```text
M21 HF safetensors telemetry backend
```

8. If the milestone stop condition is met, update `steer.md` for the next milestone and commit it as a separate steer commit.

9. Stop unless `CODEX_AUTOSTEER_LOOP=true` and all loop limits still allow continuation.

## Required stop report

At each stop, print:

- latest commit SHA
- milestone completed
- tests passed
- public artifacts created
- private artifacts intentionally not committed
- next steer target
- blockers or decisions needed

## Autosteer commit discipline

Use separate commits:

1. milestone implementation commit
2. steer update commit

Do not combine them unless there is a documented reason.

## Milestone selection rules

When choosing the next milestone after a completed milestone:

1. Prefer the next item already listed under `After Mxx` in `steer.md`.
2. Prefer milestones that close a known blocker before scaling.
3. Prefer one architectural change at a time.
4. Do not jump from GGUF runtime work to HF telemetry work unless `steer.md` says to.
5. Do not jump from fixture retrieval to live web retrieval without explicit approval.
6. Do not claim production readiness from candidate-only artifacts.

## Telemetry-specific rules

For HF/safetensors telemetry milestones:

- Do not download or commit model weights.
- Provide loader contracts and fixture/fake-model tests first.
- Support local paths and environment-driven model ids.
- If a real model is required, stop and ask for model/path/hardware approval.
- Capture final logits/entropy/selected-token probability/top-k margin when available.
- Capture hidden/router/expert telemetry only if the model actually exposes it.
- Mark telemetry fields as `missing`, `unsupported`, or `not_moe` honestly.
- Never infer router/expert data from a dense model.

## Definition of done for the current research track

The practical supervisor track is mature when `jlens` can:

- run local model batches
- verify checkable tasks
- route current-info tasks to retrieval
- regenerate grounded answers after retrieval
- review escalations
- compare models
- summarize trust by task category
- keep private details local

The telemetry track is mature when `jlens` can:

- load a HF/safetensors backend from a local path or approved model id
- collect logits/entropy/top-k telemetry on a shared task batch
- collect router/expert telemetry when the architecture exposes it
- align telemetry records with verifier/action/review outcomes
- report whether telemetry improves prediction of retrieval/checker/review needs

## Absolute non-goals

Do not:

- commit model weights
- commit raw private logs
- commit raw retrieved context
- commit full model outputs
- add live web retrieval without explicit approval
- add arbitrary command execution from model output
- turn candidate labels into gold labels without human/audited review
- hide failures by changing task definitions after seeing results

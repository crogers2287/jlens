# jlens Roadmap — router-first ("routerguard") decision

Date: 2026-07-08. Basis: FINDINGS.md #1–33 (r2 analyses + token probe) and
external review (ChatGPT) of the findings. Decision: build the router-only
sidecar before any hidden-state/Jacobian (J-lens) work.

## Rationale (data-backed)
- Router signatures carry domain identity: r2 cosine NN retrieval 6/8,
  intra-domain cosine > inter-domain, code langs cluster (#FINDINGS).
- Token-level signal confirmed with prompt-held-out splits: 0.578 grouped-CV
  acc vs 0.208 chance (#33).
- Expert ablation deferred: mean pairwise Jaccard overlap 0.29–0.43 means
  global expert surgery has collateral damage. Only measured, per-expert
  experiments later.
- Depth terciles near-flat -> sidecar taps a spread of layers, not just late
  stack (e.g. 4,8,12 / 16,20,24,28 / 32,36,39 of 40).

## Planned split (applied AFTER r3 analyses commit, to avoid path churn)
    jlens/
      routerguard/   # router-logit capture + signatures + sidecar heads
      hiddenlens/    # phase 2: hidden-state / Jacobian probes
      expertmap/     # expert profiling / (careful) ablation experiments
      policyengine/  # runtime risk policy

## Experimental order
1. r3 lands -> rerun overlap + token probe + per-layer sweep (task #18).
2. Freeze capture schema v1 (per-run JSON: model, run_id, prompt_id, domain,
   tokens, per-layer topk_experts/topk_probs/entropy, logits shape).
3. Sidecar head bakeoff on routing signatures only:
   centroid -> logistic -> linear SVM -> GBM -> tiny MLP.
   Metrics: domain acc, top-2 acc, calibration (ECE), false-high-risk rate,
   latency + VRAM overhead.
4. Label set beyond domain: needs_current_info, needs_exact_citation,
   needs_math_verification, needs_code_execution, needs_user_file_context,
   unsafe_or_high_stakes, prompt_injection_present, answerable_from_memory.
5. Decode-step capture mode (NEW - current pipeline is prefill-only):
   per-generated-token router logits to study drift/entropy spikes
   mid-generation. Prereq for hallucination-risk head.
6. Risk head: LEARNED + calibrated, not hand-weighted. The external review's
   fixed linear blend (0.25*entropy_z + ...) is kept only as a feature list;
   weights come from fitting against labeled outcomes.
7. Only after router baselines are exhausted: hiddenlens/J-space work.

## Runtime policy sketch (thresholds TBD from calibration, not preset)
low -> normal decode | med -> conservative sampling + self-check |
high -> force retrieval/tool verification | critical -> block autonomous
tool action, require grounded path.

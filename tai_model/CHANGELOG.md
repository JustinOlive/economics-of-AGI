# Rebuild notes (what changed from the Excel v2)

- **Single source of truth:** all numbers now live in `parameters.csv`; the Quarto report,
  the HTML preview and the Excel all read from it.
- **Removed** the `rev/chip decline` hack and the standalone `duty cycle` (folded into
  effective concurrency). Fewer baked-in assumptions.
- **Merged** the old "Inputs summary" sheet into one Raw-data layer.
- **Inference fraction** is now an explicit 20-50% parameter (Triangular) used by 3 of 4 methods.
- **Method 4 (OpenRouter)** integrated: concurrency is a parameter with the Epoch/FLOP/production
  data points documented in its note.
- **Four framings:** DeepSeek bottom-up (GPU=token, an upper bound), GPU macro, Anthropic
  model-based, Epoch token-capacity. Pooled = model + Epoch (the two best-anchored).
- **Distributions:** mostly bounded (triangular/uniform); lognormal only where justified
  (token capacity, 2031 model size). Lognormal `value` = median.
- **Reviewed** by an independent agent and a 71-check programmatic audit (all pass).

Headline: pooled 2031 revenue median ~$17T (P5-P95 ~$3-99T). The per-GPU/token framing
exceeds world GDP and is shown only as an upper bound.

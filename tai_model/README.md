# TAI revenue model (editable simulation)

**Edit `parameters.csv`** to change the simulation — every value, range, distribution and
source lives there. Then:

- **Render the report:** `quarto render report.qmd` (opens `report.html`).
- **Or just run the model:** `python model.py` (prints central values + Monte Carlo).
- **No Quarto?** Open `report_preview.html` to view the latest results.

Files: `parameters.csv` (source of truth) · `model.py` (engine, 4 methods + MC) ·
`report.qmd` (Quarto report) · `render_preview.py` (HTML twin) · `report_preview.html` (viewable).

## Limitations
- The per-GPU / token framing runs hotter than world GDP at its centre - an upper bound only.
- No price-deflation is assumed (2031 revenue-per-GPU held at current levels).
- `eff_concurrency`, `inference_fraction_2031` and `model_params_2031` are the swing inputs.
- Token-parity with human cognition is a capacity statement, not a labour-substitution claim.

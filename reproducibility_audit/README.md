# Reproducibility audit (Supporting Information S3)

**Author:** Paola Vera-Licona (Vera-Licona Research Group)

The audit matrix lives in [`../data/SI_3_ReproducibilityAudit.xlsx`](../data/SI_3_ReproducibilityAudit.xlsx).

Scores were assigned by manual review of each method's public code deposit and
web tool (Reproducibility 0–4, FAIR4RS 0–5). There is no automated scoring
pipeline — the spreadsheet is the authoritative record.

## Related scripts

| Script | Purpose |
| --- | --- |
| [`../figure3/fig3_reproducibility.py`](../figure3/fig3_reproducibility.py) | Regenerate Figure 3 from the audit spreadsheet |
| [`patch_si_3_offline_legend.py`](patch_si_3_offline_legend.py) | Idempotent patch that inserts the OFFLINE definition into the xlsx legend (already applied in the submitted file) |

## Regenerate Figure 3

```bash
pip install -r ../requirements.txt
python ../figure3/fig3_reproducibility.py
```

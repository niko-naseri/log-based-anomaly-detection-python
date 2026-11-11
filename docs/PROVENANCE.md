# Provenance and verification audit

**Read this before using the project in applications or publishing external claims.**

## What was actually available when the portfolio was built

From the earlier conversation-generated project bundle, we could inspect:

- `src/anomaly_detection_prototype.py`: log parser, 30-minute features, rule detector and custom anomaly scoring (no scikit-learn IsolationForest imported or fitted).
- `data/simulated_auth.log`: 423 synthetic authentication events with seven unique IP strings.
- `data/simulated_auth_windows.csv`: 48 windows, 5 positive `true_anomaly` labels at window indices 9, 17, 29, 38, 44.
- `results/evaluation_metrics.csv`: exported 5 TP / 0 FP / 0 FN for rules and 5 TP / 1 FP / 0 FN for the previously named `isolation_forest_anomaly` and hybrid columns; not actual IF predictions.
- `data/hdfs_template_counts.csv`: six hardcoded event-template count records. No corresponding raw public HDFS log sample or parsing script was available to verify them.
- Earlier figures: some were created from illustrative/static values and are **not primary evidence**. Not reused in the public repo.

## Discrepancies identified

1. **Model identity:** the prior code implemented standardized Euclidean-distance-based scoring with a quantile cutoff. Calling that an Isolation Forest was incorrect.
2. **Metrics mismatch:** the thesis's illustrative Table 2 reported rule P/R/F1 1.00/0.83/0.91, and IF & hybrid 0.75/1.00/0.86. The available CSV reported rule 1.00/1.00/1.00 and custom score & hybrid 0.83/1.00/0.91. We could not reproduce the thesis table with available underlying data and code.
3. **Anomaly count:** the available 48 windows contain **5** pre-existing injected positive labels, not 6. No separate off-hours attack injection is evident from the file.
4. **HDFS provenance:** the raw HDFS log and exact dataset slice are absent. The old template-count chart cannot be substantiated by the source artifacts available here.
5. **Earlier anomalous score figure:** the old figure showed values without an auditable model run; it has been replaced by a chart from this new execution.

## What the new repository does (November 2026)

- **New code, clearly labeled:** fresh `src/logqa/` modules written as a portfolio reconstruction, not passed off as the original thesis implementation.
- Reuses the **available synthetic authentication events**, with 1:1 IP mapping of public-looking strings to TEST-NET addresses.
- Retains earlier synthetic-window labels from `simulated_auth_windows.csv` as an *academic demonstration* ground truth, not as field-verified incidents.
- Implements a real **`sklearn.ensemble.IsolationForest`** with fixed parameters.
- Computes confusion matrices and all metrics by code, instead of copying thesis Table 2.
- Regenerates plots from these detections and metrics.
- Includes an automated test suite and a GitHub Actions workflow to provide inspectable evidence.

## Scope and evaluation caveats

- The model is fitted and evaluated on the **same** synthetic windows. There is no held-out set, cross-system validation, realistic base rate, or external field evaluation.
- Labels represent generation-time injection indicators for failed-login bursts. They were recovered from the prior processed data and independently verified to align with the 48-window sequence, but the original generator script was not available.
- We **cannot confirm** that the historical thesis experiments as described were originally run with the exact code/data supplied here.
- Neither a production system nor company/customer log data has been used.
- This portfolio showcases engineering practice in a **new, reproducible recreation of an academic project**; it does not retroactively validate all figures in the archived thesis.

## Missing originals

- Verifiable HDFS raw log sample, extraction instructions and parsing implementation.
- Original thesis-specific scikit-learn training script, model artifact, and independent experiment logs.
- Original simulation generator source / injection recipe / training and validation protocol.
- Original records that support the published thesis Table 2 values or all earlier figure traces.

If these files are discovered later, they can be audited and added in a separate, clearly labeled update.

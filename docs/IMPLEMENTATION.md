# Implementation and data path

## Processing sequence

1. `parse_auth_logs` strictly parses only a controlled synthetic authentication line format: `YYYY-MM-DD HH:MM:SS login_success|login_failed user IPv4`.
2. `aggregate_windows` groups entries into complete contiguous 30-minute windows, including zero-event windows. Features are computed from each window, without an external database.
3. `attach_labels` validates one-to-one correspondence to a separate file of pre-existing simulation injection labels.
4. `score_windows` runs an interpretable rule, a real scikit-learn Isolation Forest, and an OR hybrid.
5. `evaluate` computes TP/FP/FN/TN and precision/recall/F1 against synthetic injection labels.
6. `create_figures` generates three plots from the freshly computed outputs.

## Feature definitions

| Feature | Meaning |
|---|---|
| `success_login_count` | Successful authentication records in the window |
| `failed_login_count` | Failed authentication records in the window |
| `unique_ip_count` | Distinct source IPs in the window |
| `event_type_count` | Distinct event names observed (at most 2 in this schema) |
| `event_frequency` | Total auth log records in the window |
| `off_hours` | Window start before 08:00 or at/after 18:00, as an illustrative cutoff |

**Limitations:** `event_frequency` is exactly the sum of the first two counts, so some features are correlated. These choices were kept close to the thesis feature list, not optimized for production. No user identity or IP-based correlation across windows is modeled. **This parser is not a general-purpose log parser.**

## Detector configuration

- Rule: `failed_login_count >= 12 OR (failed_login_count >= 8 AND unique_ip_count >= 3)`.
- `IsolationForest(n_estimators=200, contamination=0.125, random_state=42, n_jobs=1)`. Uses six numerical features, no labels in `.fit()`.
- Isolation Forest score exported here is `-decision_function`. A positive value corresponds to an IF anomaly prediction; higher values are more unusual.
- OR hybrid: anomalous if **either** method flags the window.
- Evaluation: labels **not used** in training or threshold selection; however, the evaluated records are the same data used in unsupervised fitting. No separation into train/test sets.

## Testing strategy

- Input format validation rejects malformed lines and unknown event tokens.
- Time windows are contiguous, aligned to the input period and labels.
- Conservation: `event_frequency = success_login_count + failed_login_count`.
- Ground truth must contain each window ID exactly once.
- Seeded IF execution is deterministic in the tested runtime.
- OR decision must be a superset of either individual detector's flagged windows.
- Confusion counts must add up to the number of evaluation windows.

## Future, not implemented

- Streaming ingestion and real-time alerts.
- Generalized parsing of HDFS or other system log formats.
- Train/validation splits across days or systems.
- Benchmarking against human-annotated field incident data.
- Security performance claims, latency profiling, production deployment.

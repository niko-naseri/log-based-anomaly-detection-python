"""Parse synthetic authentication logs and compare two anomaly detectors.

Reconstruction written for portfolio publication in November 2026.
This is NOT the original thesis implementation. See docs/PROVENANCE.md.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(?P<event>login_success|login_failed) "
    r"(?P<user>[a-zA-Z0-9_-]+) (?P<source_ip>\d{1,3}(?:\.\d{1,3}){3})$"
)
FEATURE_COLUMNS = [
    "success_login_count", "failed_login_count", "unique_ip_count",
    "event_type_count", "event_frequency", "off_hours",
]


def parse_auth_logs(path: str | Path) -> pd.DataFrame:
    """Strictly parse the synthetic demonstration format (not arbitrary syslog)."""
    records = []
    with Path(path).open(encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, 1):
            if not raw_line.strip():
                continue
            match = LOG_PATTERN.fullmatch(raw_line.strip())
            if not match:
                raise ValueError(f"Invalid auth log line {line_number}: {raw_line.strip()!r}")
            fields = match.groupdict()
            ipaddress.ip_address(fields["source_ip"])
            timestamp = pd.to_datetime(fields["timestamp"], format="%Y-%m-%d %H:%M:%S")
            records.append({"timestamp": timestamp, "event": fields["event"],
                            "user": fields["user"], "source_ip": fields["source_ip"]})
    if not records:
        raise ValueError("No authentication events found")
    return pd.DataFrame.from_records(records).sort_values("timestamp", kind="stable").reset_index(drop=True)


def aggregate_windows(events: pd.DataFrame, window_minutes: int = 30) -> pd.DataFrame:
    """Produce complete contiguous fixed windows including zero-event windows."""
    if window_minutes <= 0 or 60 % window_minutes != 0:
        raise ValueError("window_minutes must divide an hour (e.g. 5, 10, 15, 30, 60)")
    if events.empty:
        raise ValueError("events cannot be empty")
    interval = f"{window_minutes}min"
    starts = events["timestamp"].dt.floor(interval)
    grouped = events.assign(window_start=starts).groupby("window_start", sort=True)
    counts = grouped.agg(
        success_login_count=("event", lambda s: int((s == "login_success").sum())),
        failed_login_count=("event", lambda s: int((s == "login_failed").sum())),
        unique_ip_count=("source_ip", "nunique"),
        event_type_count=("event", "nunique"),
        event_frequency=("event", "size"),
    )
    all_windows = pd.date_range(starts.min(), starts.max(), freq=interval)
    counts = counts.reindex(all_windows, fill_value=0)
    counts.index.name = "window_start"
    counts = counts.reset_index()
    counts.insert(0, "window_id", np.arange(len(counts), dtype=int))
    counts["off_hours"] = ((counts["window_start"].dt.hour < 8) |
                            (counts["window_start"].dt.hour >= 18)).astype(int)
    counts["window_start"] = counts["window_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return counts


def attach_labels(windows: pd.DataFrame, labels_csv: str | Path) -> pd.DataFrame:
    """Join independent injection-label metadata; do not derive truth from model output."""
    labels = pd.read_csv(labels_csv)
    required = {"window_id", "is_injected_anomaly", "scenario"}
    if not required.issubset(labels.columns):
        raise ValueError(f"Label CSV must include {sorted(required)}")
    if labels["window_id"].duplicated().any():
        raise ValueError("Duplicate window IDs in label file")
    if not set(labels["is_injected_anomaly"].unique()).issubset({0, 1}):
        raise ValueError("Labels must be binary")
    merged = windows.merge(labels, on="window_id", how="left", validate="one_to_one")
    if len(merged) != len(labels) or merged["is_injected_anomaly"].isna().any():
        raise ValueError("Labels must match every observation window exactly")
    return merged


def score_windows(windows: pd.DataFrame, contamination: float = 0.125,
                  random_state: int = 42) -> pd.DataFrame:
    """Fit a REAL scikit-learn IsolationForest (exploratory, same-dataset evaluation).

    No labels are used for training or choosing parameters. Higher decision_score
    means more abnormal. This is *not* an unbiased held-out test-set estimate.
    """
    if not 0 < contamination < 0.5:
        raise ValueError("contamination must be between 0 and 0.5")
    features = windows[FEATURE_COLUMNS].astype(float)
    if features.isna().any().any():
        raise ValueError("Features may not contain missing values")
    scored = windows.copy()
    scored["rule_based_anomaly"] = (
        (scored["failed_login_count"] >= 12) |
        ((scored["failed_login_count"] >= 8) & (scored["unique_ip_count"] >= 3))
    ).astype(int)
    forest = IsolationForest(n_estimators=200, contamination=contamination,
                             random_state=random_state, n_jobs=1)
    forest.fit(features)
    # scikit-learn: negative decision_function -> anomaly.
    scored["iforest_decision_score"] = -forest.decision_function(features)
    scored["isolation_forest_anomaly"] = (forest.predict(features) == -1).astype(int)
    scored["hybrid_anomaly"] = (
        (scored["rule_based_anomaly"] == 1) |
        (scored["isolation_forest_anomaly"] == 1)
    ).astype(int)
    return scored


def evaluate(scored: pd.DataFrame) -> pd.DataFrame:
    """Confusion counts and P/R/F1 for each method against injected labels."""
    if "is_injected_anomaly" not in scored:
        raise ValueError("Ground-truth labels required for evaluation")
    truth = scored["is_injected_anomaly"].astype(int).to_numpy()
    out = []
    for method in ("rule_based_anomaly", "isolation_forest_anomaly", "hybrid_anomaly"):
        preds = scored[method].astype(int).to_numpy()
        tn, fp, fn, tp = confusion_matrix(truth, preds, labels=[0, 1]).ravel()
        precision, recall, f1, _ = precision_recall_fscore_support(
            truth, preds, average="binary", zero_division=0
        )
        out.append({"method": method, "tp": int(tp), "fp": int(fp),
                    "fn": int(fn), "tn": int(tn), "precision": float(precision),
                    "recall": float(recall), "f1": float(f1)})
    return pd.DataFrame(out)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(input_file: Path, label_file: Path, output_dir: Path,
        contamination: float = 0.125, random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parsed = parse_auth_logs(input_file)
    windows = aggregate_windows(parsed)
    windows = attach_labels(windows, label_file)
    scored = score_windows(windows, contamination=contamination, random_state=random_state)
    metrics = evaluate(scored)
    windows.to_csv(output_dir / "window_features.csv", index=False)
    scored.to_csv(output_dir / "detections.csv", index=False, float_format="%.8f")
    metrics.to_csv(output_dir / "metrics.csv", index=False, float_format="%.8f")
    summary = {
        "provenance": "2026 portfolio reconstruction; NOT reported thesis experiment",
        "input_sha256": sha256(input_file), "label_sha256": sha256(label_file),
        "event_count": int(len(parsed)), "window_count": int(len(windows)),
        "injected_anomaly_windows": int(windows["is_injected_anomaly"].sum()),
        "window_duration_minutes": 30,
        "model": "sklearn.ensemble.IsolationForest",
        "features": FEATURE_COLUMNS,
        "n_estimators": 200, "contamination": contamination,
        "random_state": random_state, "evaluation": "same data used for unsupervised fitting and scoring; no hold-out",
        "scikit_learn_version": sklearn.__version__,
        "numpy_version": np.__version__, "pandas_version": pd.__version__,
    }
    (output_dir / "run_metadata.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return scored, metrics

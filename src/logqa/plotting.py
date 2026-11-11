"""Create plots ONLY from freshly computed detection results."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_figures(detections: pd.DataFrame, metrics: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "figure.dpi": 110, "savefig.dpi": 180})

    # Time-indexed failures with independently injected labels and method flags.
    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = detections["window_id"].to_numpy()
    y = detections["failed_login_count"].to_numpy()
    ax.plot(x, y, marker=".", label="Failed authentication events per window")
    truth = detections["is_injected_anomaly"].eq(1)
    flagged = detections["hybrid_anomaly"].eq(1)
    ax.scatter(x[truth], y[truth], s=85, marker="x", label="Injected anomaly windows")
    ax.scatter(x[flagged], y[flagged], s=90, marker="o", facecolors="none", linewidths=1.8,
               label="Hybrid-detected windows")
    ax.set(xlabel="30-minute window index", ylabel="Failed authentication attempts",
           title="Authentication activity and anomaly flags (synthetic data)")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output / "01_authentication_activity.png")
    plt.close(fig)

    # scikit-learn IF decision_function: positive in our reversed sign indicates anomaly.
    fig, ax = plt.subplots(figsize=(9, 5.2))
    scores = detections["iforest_decision_score"].to_numpy()
    ax.hist(scores[~truth.to_numpy()], bins=12, alpha=0.6, label="Non-injected windows")
    ax.hist(scores[truth.to_numpy()], bins=7, alpha=0.6, label="Injected anomaly windows")
    ax.axvline(0, linestyle="--", label="IsolationForest threshold (score = 0)")
    ax.set(xlabel="Negative sklearn decision_function (higher = more anomalous)",
           ylabel="Number of 30-minute windows",
           title="Actual Isolation Forest score distribution (synthetic data)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "02_isolation_forest_scores.png")
    plt.close(fig)

    # Model comparison; values must be loaded from generated metrics.csv, not typed into plotting code.
    fig, ax = plt.subplots(figsize=(9.2, 5))
    indices = np.arange(len(metrics))
    width = 0.24
    for i, name in enumerate(["precision", "recall", "f1"]):
        ax.bar(indices+(i-1)*width, metrics[name], width, label=name.title())
    ax.set_xticks(indices, ["Rule-based", "Isolation Forest", "OR hybrid"])
    ax.set_ylim(0, 1.12)
    ax.set(ylabel="Score", title="Method comparison on injected synthetic labels")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(output / "03_method_comparison.png")
    plt.close(fig)

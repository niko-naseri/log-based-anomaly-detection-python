"""Tests exercise actual processing logic instead of checking fabricated values."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from logqa.pipeline import (parse_auth_logs, aggregate_windows, attach_labels,
                            score_windows, evaluate, FEATURE_COLUMNS)

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic"


def load_labelled():
    return attach_labels(aggregate_windows(parse_auth_logs(DATA / "authentication.log")),
                         DATA / "labels.csv")


def test_parse_known_synthetic_log_size():
    records = parse_auth_logs(DATA / "authentication.log")
    assert len(records) == 423
    assert set(records["event"]) == {"login_success", "login_failed"}
    assert records["timestamp"].is_monotonic_increasing


def test_reject_invalid_line(tmp_path):
    invalid = tmp_path / "invalid.log"
    invalid.write_text("not an authentication log\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid auth log line"):
        parse_auth_logs(invalid)


def test_48_windows_5_injected_labels():
    labelled = load_labelled()
    assert len(labelled) == 48
    assert labelled["window_id"].tolist() == list(range(48))
    assert labelled["is_injected_anomaly"].sum() == 5


def test_event_counts_are_conserved():
    parsed = parse_auth_logs(DATA / "authentication.log")
    windows = aggregate_windows(parsed)
    assert windows["event_frequency"].sum() == len(parsed)
    assert (windows["success_login_count"]+windows["failed_login_count"] == windows["event_frequency"]).all()


def test_feature_schema_and_positive_injections():
    labelled = load_labelled()
    assert set(FEATURE_COLUMNS).issubset(labelled.columns)
    assert (labelled.loc[labelled["is_injected_anomaly"].eq(1), "failed_login_count"] >= 12).all()


def test_forest_and_hybrid_logic():
    scored = score_windows(load_labelled())
    assert "iforest_decision_score" in scored.columns
    assert (scored.loc[scored["isolation_forest_anomaly"].eq(1), "iforest_decision_score"] >= 0).all()
    assert (scored["hybrid_anomaly"] >= scored["rule_based_anomaly"]).all()
    assert (scored["hybrid_anomaly"] >= scored["isolation_forest_anomaly"]).all()


def test_model_is_deterministic_with_fixed_seed():
    records = load_labelled()
    a = score_windows(records)
    b = score_windows(records)
    assert np.allclose(a["iforest_decision_score"], b["iforest_decision_score"])
    assert a["isolation_forest_anomaly"].tolist() == b["isolation_forest_anomaly"].tolist()


def test_evaluation_confusion_counts_are_complete():
    scored = score_windows(load_labelled())
    out = evaluate(scored)
    assert len(out) == 3
    assert ((out["tp"]+out["fp"]+out["tn"]+out["fn"]) == 48).all()
    assert ((out[["precision", "recall", "f1"]] >= 0) & (out[["precision", "recall", "f1"]] <= 1)).all().all()


def test_unmatched_label_ids_rejected(tmp_path):
    labels = tmp_path / "labels.csv"
    pd.DataFrame({"window_id":[999],"is_injected_anomaly":[1],"scenario":["test"]}).to_csv(labels,index=False)
    with pytest.raises(ValueError, match="exactly"):
        attach_labels(aggregate_windows(parse_auth_logs(DATA / "authentication.log")),labels)


def test_evaluation_requires_ground_truth():
    scored = score_windows(load_labelled().drop(columns=["is_injected_anomaly"]))
    with pytest.raises(ValueError, match="Ground-truth"):
        evaluate(scored)

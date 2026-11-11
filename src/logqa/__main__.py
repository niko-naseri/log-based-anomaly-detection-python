"""Command line runner: python -m logqa run [options]."""
import argparse
from pathlib import Path
from .pipeline import run
from .plotting import create_figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible synthetic-log anomaly detection demo")
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--input", type=Path, default=Path("data/synthetic/authentication.log"))
    parser.add_argument("--labels", type=Path, default=Path("data/synthetic/labels.csv"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--figures", type=Path, default=Path("figures"))
    parser.add_argument("--contamination", type=float, default=0.125)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.command == "run":
        scored, metrics = run(args.input, args.labels, args.output, args.contamination, args.seed)
        create_figures(scored, metrics, args.figures)
        print("Events/windows/injected anomalies:",
              int(scored["event_frequency"].sum()), len(scored),
              int(scored["is_injected_anomaly"].sum()))
        print(metrics.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        print(f"Wrote results to {args.output}/ and charts to {args.figures}/")

if __name__ == "__main__":
    main()

# Engineering hiring manager's quick review

This is an academic-origin, **post-thesis portfolio reconstruction**, not prior employment and not a production system.

## 3-minute assessment

1. Read the `README.md` provenance box and experiment results.
2. Examine `src/logqa/pipeline.py` for strict parsing, aggregation, label validation, deterministic scoring, confusion matrix computation.
3. Run `python -m pytest`, then `python -m logqa run`.
4. Compare generated `results/metrics.csv` and charts with the README. Confirm results are not hardcoded into the plotting code.
5. Read `docs/PROVENANCE.md` for a frank account of missing sources and why the thesis metrics were not copied.

## Relevant role competencies

| Role family | Demonstrated here | Not claimed |
|---|---|---|
| Software QA / Test Automation | Python verification tests, edge-case handling, assertions, reproducible CLI and CI config | Professional Playwright/Selenium or customer-facing production automation |
| System & Integration Testing | Stage-wise data flow, strict parsing, end-to-end validation, artifact-based failure investigation | Hardware-in-the-loop or actual distributed-system test lab |
| Python Validation | Typed modular functions, deterministic model configuration, validation of labels and confusion counts | Enterprise data platform or deployed microservice |
| Data / AI | Feature engineering, IsolationForest, ground-truth evaluation, metrics and chart generation | Optimized ML model, large-scale benchmarks or unbiased generalization claims |

## Suggested discussion points

- Why do we need ground truth for precision/recall even with unsupervised fitting?
- Why can an OR hybrid perform no better than the best individual method?
- What tests catch a mismatch between archived thesis metrics and current code output?
- Why is there no HDFS benchmark figure in the repo despite its mention in the thesis?
- How would time-based train/test splitting and realistic, low-prevalence anomaly evaluation change the next version?

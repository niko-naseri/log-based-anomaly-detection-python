# GitHub release checklist

- [x] Create a GitHub repository, e.g. `log-based-anomaly-detection-python`.
- [x] Upload **the GitHub-ready ZIP contents only** (do not publish the separate legacy audit archive).
- [ ] Confirm repository status and authorship: academic-inspired **2026 portfolio reconstruction**, not historical original source.
- [ ] Open README, inspect figures, and verify all links in GitHub rendering.
- [ ] Confirm no company/customer log data, passwords, secrets, real user identities, or project-manager email addresses.
- [ ] Confirm that external IP addresses in the published synthetic log are only private or RFC5737 documentation values.
- [ ] Run `python -m pip install -e ".[dev]"`, `python -m pytest`, then `python -m logqa run` locally.
- [ ] Inspect generated results against README; expect the 423 / 48 / 5 summary.
- [x] Verify that the `Python checks` workflow passes on GitHub for Python 3.10 and 3.12 (confirmed 11 November 2026, initial commit `dde9c83`).
- [ ] Only then share the repository under LinkedIn Projects and optionally add it to Featured.
- [ ] Avoid claiming earlier thesis numerical metrics as independently reproduced; refer to the portfolio rerun instead.

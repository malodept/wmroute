# Public release checklist

## Before making the GitHub repository public

- [ ] Confirm that the repository owner is `malodept` and the repository name is `wmroute`.
- [ ] Run `bash scripts/run_all_checks.sh` from a clean environment.
- [ ] Confirm that GitHub Actions passes on Python 3.10 and 3.12.
- [ ] Inspect the rendered README and `docs/index.html` on GitHub.
- [ ] Keep `LICENSE.md` as the source-available notice until ownership and redistribution review is complete.
- [ ] Confirm that no additional institutional data, checkpoints, logs, or private archives were added.
- [ ] Enable GitHub Pages from the `docs/` folder.
- [ ] Create tag `v0.1.0-preprint`.
- [ ] Keep the repository description factual: `Paired exact-reset evaluation of prediction-derived Medium-to-Full world-model routing.`
- [ ] Add topics: `world-models`, `adaptive-compute`, `robotics`, `decision-making`, `reproducibility`.

## After the arXiv submission is public

- [ ] Add the arXiv identifier to `README.md`, `docs/index.html`, and `CITATION.cff`.
- [ ] Replace `arXiv submission pending` with the public citation.
- [ ] Tag a new release such as `v0.2.0-arxiv`.
- [ ] Consider a standard open-source licence only after the rights review.

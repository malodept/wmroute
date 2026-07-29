# Contributing

Changes fall into two categories:

1. `src/`, `tests/`, `scripts/`, and `docs/` may be improved through ordinary
   pull requests with tests.
2. `experiments/*/frozen_source/` and compact sealed outputs are historical
   scientific records. Never edit them in place. Add a new replication
   directory and protocol instead.

Every change must preserve the claim boundaries in
`docs/claims_and_limitations.md` and pass:

```bash
bash scripts/run_all_checks.sh
```

For a new empirical result, record the protocol before opening audit outcomes,
use fresh physical reset seeds, retain exact source hashes, state the clustering
unit, and distinguish development from confirmation.

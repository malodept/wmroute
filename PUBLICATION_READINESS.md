# Publication readiness

## Automated checks

- Public-surface placeholder and credential-pattern scan: pass.
- Prospective confirmation hash and bootstrap reconstruction: pass.
- Public release value snapshots: pass.
- Frozen-source tests: pass.
- Full test suite: all public-release tests passed.
- Table and figure regeneration: pass.
- Largest tracked file: below 5 MB; Git LFS is not required.

## Deliberately retained provenance

Some released audit protocols and lineage tables retain original HPC paths.
They contain no access credentials and are included only to preserve the
scientific record; the public-facing code and project page do not depend on
those paths.

## Remaining manual decision

The repository is safe to expose for scientific inspection, but it intentionally
uses a source-available `LICENSE.md` rather than an open-source licence. Before
applying MIT, Apache-2.0, BSD, or another reuse licence, confirm ownership and
redistribution rights for all files under `artifacts/`.

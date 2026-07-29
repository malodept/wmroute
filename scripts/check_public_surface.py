#!/usr/bin/env python3
"""Check the presentation-facing repository surface before publication."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SURFACE = [
    ROOT / "README.md",
    ROOT / "CITATION.cff",
    ROOT / "LICENSE.md",
    ROOT / "THIRD_PARTY_NOTICES.md",
    ROOT / "docs/index.html",
    *ROOT.glob("docs/*.md"),
]
PATTERNS = {
    "private key": re.compile(r"BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY", re.I),
    "credential assignment": re.compile(r"(?:api[_-]?key|client_secret|password)\s*[:=]\s*[^\s]+", re.I),
    "unresolved placeholder": re.compile(r"TO_BE_ADDED|XXXXXXXX|CHANGEME", re.I),
}

for path in PUBLIC_SURFACE:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for label, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            raise SystemExit(f"{label} in {path.relative_to(ROOT)}: {match.group(0)!r}")
print("WMROUTE_PUBLIC_SURFACE_CHECK_PASS")

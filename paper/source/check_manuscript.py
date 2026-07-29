#!/usr/bin/env python3
"""Static consistency checks for the editorial arXiv manuscript package."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.tex"
BIB = ROOT / "references.bib"


def comma_items(pattern: str, text: str) -> set[str]:
    items: set[str] = set()
    for match in re.finditer(pattern, text, flags=re.MULTILINE):
        items.update(item.strip() for item in match.group(1).split(","))
    return {item for item in items if item}


def referenced_files(tex: str) -> list[Path]:
    paths: list[Path] = []
    for raw in re.findall(r"\\input\{([^}]+)\}", tex):
        path = Path(raw)
        paths.append(path if path.suffix else path.with_suffix(".tex"))
    paths.extend(Path(raw) for raw in re.findall(
        r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex))
    return paths


def require(pattern: str, text: str, description: str) -> None:
    if not re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
        raise RuntimeError(f"required repaired claim absent: {description}")


def main() -> None:
    tex = MAIN.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

    citation_keys = comma_items(r"\\cite[a-zA-Z]*\{([^}]+)\}", tex)
    bibliography_keys = set(re.findall(
        r"@\w+\{\s*([^,\s]+)\s*,", bib, flags=re.MULTILINE))
    missing_citations = sorted(citation_keys - bibliography_keys)
    if missing_citations:
        raise RuntimeError("citation keys absent from references.bib: " +
                           ", ".join(missing_citations))

    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    duplicate_labels = sorted({x for x in labels if labels.count(x) > 1})
    if duplicate_labels:
        raise RuntimeError("duplicate labels: " + ", ".join(duplicate_labels))
    references = comma_items(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", tex)
    missing_labels = sorted(references - set(labels))
    if missing_labels:
        raise RuntimeError("undefined references: " + ", ".join(missing_labels))

    missing_files = sorted(str(path) for path in referenced_files(tex)
                           if not (ROOT / path).is_file())
    if missing_files:
        raise RuntimeError("missing manuscript inputs: " + ", ".join(missing_files))

    guards = [
        (r"post-audit repair.*shared-state pairing|post-audit statistical repair.*shared-state pairing", "PyBullet repair disclosure"),
        (r"prospectively\s+seal.*second.*1,600-state.*confirmation", "prospective seal disclosure"),
        (r"dimension-matched.*current-DINO", "matched current-DINO control"),
        (r"0\.002549", "prospective primary point"),
        (r"-0\.002286", "prospective one-sided upper bound"),
        (r"does not establish prediction causality|does not prove.*causally", "prospective causal boundary"),
        (r"descriptive rather than a\s+hypothesis-test.*p.*value", "1/5001 non-p-value disclosure"),
        (r"clairvoyant.*lower bound.*not the Bayes", "clairvoyant/Bayes distinction"),
        (r"does not independently isolate the\s+prediction", "PyBullet attribution boundary"),
        (r"loses to every listed reference at.*0\.025.*0\.05", "full price-grid failure region"),
        (r"slower than\s+both fixed policies", "no compute-saving claim"),
        (r"not a\s+Blackwell-incomparability\s+claim|do not establish.*Blackwell", "Blackwell guardrail"),
        (r"\\G_0=\\sigma\(T,R\).*\\G_1=\\sigma\(T,R,S_M\)", "held-fixed sigma fields"),
        (r"conditional on a known frozen Medium/Full checkpoint pair", "checkpoint-pair conditioning"),
        (r"99\.1453", "task-only escalation-rate disclosure"),
        (r"NumPy float32.*strict comparison", "float32 strict-threshold semantics"),
        (r"not an exhaustive replay test", "exact-reset validation scope"),
        (r"not confidence intervals for a broader checkpoint-generating population", "crossed sensitivity semantics"),
        (r"public compact release provides the weaker property", "compact-release boundary"),
        (r"17,600.*6,400", "full-grid threshold portability disclosure"),
    ]
    for pattern, description in guards:
        require(pattern, tex, description)

    print(json.dumps({
        "status": "MANUSCRIPT_STATIC_CHECK_PASS",
        "citations": len(citation_keys),
        "labels": len(labels),
        "referenced_files": len(referenced_files(tex)),
        "human_release_blockers": {
            "anonymous_author_metadata": "Anonymous Authors" in tex,
            "permanent_contact_present": "depastorm@gmail.com" in tex,
            "orcid_present": "0009-0009-1913-0052" in tex,
            "repository_and_artifact_urls": True,
            "license_decision": True,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

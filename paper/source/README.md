# Routing World-Model Compute from Predicted Consequences - arXiv editorial candidate v7.1

This package is the editorial revision of the technically closed v7 manuscript.
It changes title, abstract, visible experiment naming, environment visualisation,
model-table completeness, and figure presentation without changing any scientific
result.

## Compile

```bash
python check_manuscript.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

`main.bbl` is included, so BibTeX is not required for the archived source.

## Descriptive names and artifact IDs

The main paper uses descriptive names. Appendix C maps them to the internal
artifact identifiers V106, V107, and V104E and maps checkpoint pairs A/B/C to
the exact training seeds.

# Build the papers

The DOI record is the canonical rendered publication:
[10.5281/zenodo.22233638](https://doi.org/10.5281/zenodo.22233638).

To rebuild both the branded and double-blind PDFs from their public Markdown sources,
install:

- Pandoc
- XeLaTeX (for example, TeX Live or MacTeX)
- Mermaid CLI (`@mermaid-js/mermaid-cli`)

Then run:

```bash
python paper/build_pdfs.py
```

Mermaid CLI normally discovers its own Chromium installation. In a controlled build
image, set `WIND_TUNNEL_CHROMIUM_PATH` to the exact Chromium executable; the build
script validates the path and creates a temporary Puppeteer config. Generated PDFs,
temporary Markdown, and Mermaid intermediates are ignored by Git so the repository has
one canonical rendered record rather than two drifting copies.

#!/usr/bin/env python3
"""Render the Wind Tunnel paper to PDF (mermaid → PNG, then pandoc→xelatex).
Builds the Zenodo/DOI (non-anon) PDF and the TMLR (anon) PDF. Run from paper/.
"""
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
MMD_DIR = PAPER / "figures" / "_mermaid"; MMD_DIR.mkdir(parents=True, exist_ok=True)
PP = PAPER / "_pp.json"


def preflight():
    PP.unlink(missing_ok=True)
    missing = [tool for tool in ("mmdc", "pandoc", "xelatex") if shutil.which(tool) is None]
    if missing:
        raise SystemExit(
            "paper build dependencies missing: " + ", ".join(missing) + "\n"
            "See paper/BUILD.md. The canonical rendered PDF remains available at "
            "https://doi.org/10.5281/zenodo.22233638"
        )

    chromium = os.environ.get("WIND_TUNNEL_CHROMIUM_PATH")
    if chromium:
        chrome_path = Path(chromium).expanduser().resolve()
        if not chrome_path.is_file():
            raise SystemExit(f"WIND_TUNNEL_CHROMIUM_PATH is not a file: {chrome_path}")
        PP.write_text(json.dumps({
            "executablePath": str(chrome_path),
            "args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        }))
HDR = PAPER / "_header.tex"
HDR.write_text(
    "\\usepackage[export]{adjustbox}\n"
    "\\setkeys{Gin}{max width=\\linewidth,keepaspectratio}\n"
    "\\usepackage{longtable,booktabs,array}\n"
    "\\usepackage{ragged2e}\n"
    "\\raggedbottom\n"
    # symbol fallback: render glyphs DejaVu Serif lacks in DejaVu Sans (broad coverage)
    "\\usepackage{newunicodechar}\n"
    "\\newfontfamily\\symfont{DejaVu Sans}\n"
    + "".join(f"\\newunicodechar{{{ch}}}{{{{\\symfont {ch}}}}}\n"
             for ch in "✓✗✔⁺⁻₀₁₂₃₄₅ⁿ∧∨≡≈≤≥∈⊆×·→←↦√γΓδΔθκρφ①②③④⑤⑥⑦□■◆●▶")
)

def render_mermaid(md_text, tag):
    """Replace ```mermaid fences with rendered PNG image includes."""
    blocks = re.findall(r"```mermaid\n(.*?)```", md_text, flags=re.S)
    for i, code in enumerate(blocks):
        h = hashlib.sha1((tag+str(i)+code).encode()).hexdigest()[:10]
        mmd = MMD_DIR / f"m_{tag}_{i}_{h}.mmd"
        png = MMD_DIR / f"m_{tag}_{i}_{h}.png"
        mmd.write_text(code)
        if not png.exists():
            command = ["mmdc", "-i", str(mmd), "-o", str(png), "-b", "white", "-w", "1600"]
            if PP.exists():
                command.extend(["-p", str(PP)])
            r = subprocess.run(command,
                               capture_output=True, text=True, timeout=180)
            if not png.exists():
                print("  mermaid FAIL", i, r.stderr[-300:]); continue
        rel = png.relative_to(PAPER)
        md_text = md_text.replace(f"```mermaid\n{code}```",
                                  f"\n![]({rel})\n", 1)
    return md_text

def unicode_safe(t):
    # a couple of glyphs DejaVu Serif lacks; keep the meaning
    t = t.replace("𝟙", "1")
    # keep the byline date as one unbreakable unit (no orphaned day digit on wrap)
    t = t.replace("September 1, 2026", "September 1, 2026")
    return t

def build(src_name, out_name, title_suffix):
    src = PAPER / src_name
    t = src.read_text()
    t = unicode_safe(t)
    t = render_mermaid(t, out_name.replace(".pdf",""))
    # constrain every embedded figure/diagram to the text width; drop alt text so pandoc
    # doesn't emit a redundant "Figure N:" caption (our bold **Figure N —** line follows)
    t = re.sub(r"!\[[^\]]*\]\((figures/[^)]+\.png)\)", r"![](\1){width=100%}", t)
    tmp = PAPER / (out_name + ".tmp.md")
    tmp.write_text(t)
    cmd = ["pandoc", str(tmp), "-o", str(PAPER/out_name),
           "--pdf-engine=xelatex", "--from", "markdown+pipe_tables+yaml_metadata_block+tex_math_dollars-raw_html-implicit_figures",
           "--toc", "--toc-depth=2",
           "-V","geometry:margin=0.9in",
           "-V","mainfont=DejaVu Serif","-V","sansfont=DejaVu Sans",
           "-V","monofont=DejaVu Sans Mono","-V","fontsize=9pt",
           "-V","colorlinks=true","-V","linkcolor=RoyalBlue","-V","urlcolor=RoyalBlue","-V","toccolor=black",
           "-H", str(HDR)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = (PAPER/out_name).exists() and (PAPER/out_name).stat().st_size > 20000
    print(f"{'OK ' if ok else 'FAIL'} {out_name}  ({(PAPER/out_name).stat().st_size if ok else 0} bytes)")
    if not ok:
        print(r.stdout[-1500:]); print("STDERR", r.stderr[-1500:])
    tmp.unlink(missing_ok=True)
    return ok

if __name__ == "__main__":
    preflight()
    a = build("WIND-TUNNEL-PAPER-FULL.md", "WIND-TUNNEL-PAPER-Zenodo.pdf", "")
    b = build("WIND-TUNNEL-PAPER-TMLR-anon.md", "WIND-TUNNEL-PAPER-TMLR-anon.pdf", " (anon)")
    sys.exit(0 if (a and b) else 1)

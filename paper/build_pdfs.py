#!/usr/bin/env python3
"""Render the Wind Tunnel paper to PDF (mermaid → PNG, then pandoc→xelatex).
Builds the Zenodo/DOI (non-anon) PDF and the TMLR (anon) PDF. Run from paper/.
"""
import re, subprocess, sys, os, hashlib
from pathlib import Path

PAPER = Path(__file__).resolve().parent
MMD_DIR = PAPER / "figures" / "_mermaid"; MMD_DIR.mkdir(parents=True, exist_ok=True)
PP = PAPER / "_pp.json"
PP.write_text('{"executablePath":"/opt/pw-browsers/chromium-1194/chrome-linux/chrome",'
              '"args":["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"]}')
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
            r = subprocess.run(["mmdc","-i",str(mmd),"-o",str(png),"-b","white",
                                "-w","1600","-p",str(PP)],
                               capture_output=True, text=True, timeout=180)
            if not png.exists():
                print("  mermaid FAIL", i, r.stderr[-300:]); continue
        rel = png.relative_to(PAPER)
        md_text = md_text.replace(f"```mermaid\n{code}```",
                                  f"\n![]({rel})\n", 1)
    return md_text

def unicode_safe(t):
    # a couple of glyphs DejaVu Serif lacks; keep the meaning
    return t.replace("𝟙", "1")

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
    a = build("WIND-TUNNEL-PAPER-FULL.md", "WIND-TUNNEL-PAPER-Zenodo.pdf", "")
    b = build("WIND-TUNNEL-PAPER-TMLR-anon.md", "WIND-TUNNEL-PAPER-TMLR-anon.pdf", " (anon)")
    sys.exit(0 if (a and b) else 1)

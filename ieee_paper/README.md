# IEEE Paper — Compile Guide & TODO List

**Paper title:** *Post-Quantum Readiness of a Lightweight XOR+Hash Mutual
Authentication Scheme: An ECC Comparison for Cloud-IoT*

**Author:** Surya Pratap Singh Raikuni (24BYB1114), VIT Chennai

---

## Directory Structure

```
ieee_paper/
├── main.tex                     ← Main LaTeX source (IEEEtran journal format)
├── references.bib               ← BibTeX bibliography (IEEEtran style)
├── README.md                    ← This file
└── figures/
    ├── fig_hash_flow.tex        ← TikZ: Hash+XOR protocol sequence diagram
    ├── fig_ecc_flow.tex         ← TikZ: ECC P-256 protocol sequence diagram
    ├── fig_performance.tex      ← TikZ/pgfplots: performance bar charts
    └── fig_security_matrix.tex  ← TikZ: security property comparison matrix
```

---

## Compile Steps (Overleaf — Recommended)

1. **Create a new blank Overleaf project.**
2. **Upload all files** preserving the directory structure:
   - `main.tex` → project root
   - `references.bib` → project root
   - `figures/fig_hash_flow.tex` → `figures/` folder
   - `figures/fig_ecc_flow.tex` → `figures/` folder
   - `figures/fig_performance.tex` → `figures/` folder
   - `figures/fig_security_matrix.tex` → `figures/` folder
3. **Set compiler** to `pdfLaTeX` (Menu → Compiler → pdfLaTeX).
4. **Click Compile.** The paper should compile with no errors.
5. For the bibliography to resolve, Overleaf runs BibTeX automatically.
   If citations show `[?]`, click the **Recompile** button twice.

> **Tip:** If you see an overfull `\hbox` warning in the performance figure,
> try adding `width=0.46\linewidth` instead of `0.48\linewidth` in
> `fig_performance.tex`.

---

## Compile Steps (Local — pdfLaTeX)

```bash
cd ieee_paper/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Required LaTeX packages (all available on TeX Live / MiKTeX):
- `IEEEtran` (document class) — install via your TeX distribution
- `amsmath`, `amssymb`, `amsthm`
- `booktabs`
- `graphicx`
- `tikz` + `pgfplots` (with `pgfplotstheis` for groupplot)
- `algorithm`, `algpseudocode` (from `algorithmicx`)
- `xcolor`, `url`, `hyperref`, `cite`
- `multirow`, `array`, `tabularx`

---

## Layout & Formatting Modes (Single-Column vs. Two-Column)

At the top of `main.tex` (lines 13–24), you can switch between layouts with one toggle:

- **Mode A (Default — Standard IEEE Two-Column):**
  ```latex
  \documentclass[journal]{IEEEtran}
  ```
  Standard published IEEE Transactions format. Text flows down column 1, then down column 2.

- **Mode B (Single-Column Continuous — NOT divided into 2 parts):**
  ```latex
  \documentclass[journal,11pt,onecolumn]{IEEEtran}
  ```
  Uncomment this line if your professor or university Review 3 guidelines require a continuous, single-column paper where the page is NOT split into two columns. In this mode, text and diagrams flow across the full page width.

- **Mode C (IEEE Conference Mode):**
  ```latex
  \documentclass[conference]{IEEEtran}
  ```

---

## Data Provenance

All performance numbers in the paper are taken directly from:
```
research/results/benchmark_baseline.json
```
(100 iterations, 10 warmup, AMD64 Family 23 Model 96, Windows 11, Python 3.12.6)

| Metric | Hash+XOR | ECC P-256 | Source key |
|--------|----------|-----------|------------|
| Total mean | 250.3 µs | 270.9 µs | `comparison.{proto}.total.mean_ms × 1000` |
| Reg. mean | 31.1 µs | 8.7 µs | `comparison.{proto}.registration.mean_ms × 1000` |
| Auth. mean | 219.2 µs | 262.2 µs | `comparison.{proto}.authentication.mean_ms × 1000` |
| Comm. bits | 4,224 | 1,872 | `comparison.{proto}.communication_bits` |

---

## TODO — Items Requiring Attention Before Submission

### 🔴 Critical (must fix before submission)

- [x] **Citation key `Bernstein2017`:** Fixed in `references.bib` (previously caused `[?]` on Overleaf).
- [x] **Diagram/Table Overlaps:** Fixed! All TikZ diagrams and tables are now scaled with `\resizebox{\columnwidth}{!}{...}` or `\resizebox{\textwidth}{!}{...}`, eliminating all text collision and margin overflow.
- [ ] **Section IX placeholder:** The `Additional Features` section describes
  the `reduced_roundtrip` variant and ML-KEM prototype based on code inspection.
  **Verify** these descriptions match the actual implementation in
  `backend/cryptomaka/protocols/reduced_roundtrip.py` and `ml_kem.py`.

- [ ] **pgfplots groupplot:** `main.tex` uses `\usepgfplotslibrary{groupplots}`.
  This is correct and bundled with pgfplots on Overleaf — no action needed.

- [ ] **Abstract word count:** Verify abstract is 150–200 words (currently
  estimated ~175 words). Adjust if over/under.

### 🟡 Verify References (unverified entries — marked with TODO in .bib)

- [ ] **`Odabasietal2023`** — "Post-Quantum Secure Authentication for IoT
  Devices Using Hash-Based Signatures," *Sensors* 2023, 23(8), 3987.
  DOI: `10.3390/s23083987`. **Please verify** this paper exists and matches
  the claimed content before submission.

- [ ] **`Challaetal2018`** — Cited as IEEE TIFS in the context summary but
  filed as IEEE Access in the .bib. Verify the correct venue.
  DOI: `10.1109/ACCESS.2017.2676119` — double-check.

- [ ] **`Liuetal2020`** and **`Yanetal2023`** — Added as supporting ECC
  references. Please verify DOIs and that the content matches the description
  in Section II.

- [ ] **`Ferragetal2022`** — Survey paper. Verify DOI `10.1155/2022/6715894`
  and publication year (may be 2017 original, republished 2022).

- [ ] **`Brechteletal2023`** — Bos et al. CRYSTALS-Kyber EuroS&P 2018.
  Verify DOI `10.1109/EuroSP.2018.00032` and all author names.

### 🟢 Enhancements (nice to have)

- [ ] **Machine specs:** Add exact CPU model name (e.g., "AMD Ryzen 5 4600H")
  to Section VIII-A if available. Currently described generically as
  "AMD64 Family 23 Model 96."

- [ ] **Section IX:** If you have implemented any additional features beyond
  `reduced_roundtrip` and ML-KEM, add them to Section IX with their benchmark
  numbers.

- [ ] **Figures:** The TikZ figures render as vectors; consider compiling
  locally and saving as PDF for faster Overleaf compilation on large projects.

- [ ] **IEEEtran.cls version:** Overleaf bundles IEEEtran automatically.
  If compiling locally, ensure you have a recent version from
  https://ctan.org/pkg/ieeetran

- [ ] **Conference mode test:** Compile once in conference mode to confirm
  no layout issues before submitting to a conference.

---

## Claims Requiring Confirmation

| Claim | Location | Status |
|-------|----------|--------|
| hash+XOR lacks forward secrecy | Sections VI, X | Correct (structural property) |
| ECC FS lost under Shor | Section VII-D | Correct (primitive argument) |
| 576 bits not compared to 3776 bits | Table III scope note | Correctly scoped ✓ |
| Python overhead dominates timing | Section VIII-A caveat | Correctly stated ✓ |
| Reduced roundtrip: 222.3 µs mean | Section IX | Taken from benchmark JSON ✓ |
| ML-KEM prototype exists in codebase | Section IX | Verify ml_kem.py is production-quality or note prototype status |

---

## Text Proximity to Sources — Rewrite Candidates

The following passages summarise base-paper ideas; review to confirm wording
is sufficiently original:

1. **Section II, ¶1** (Turkanović et al. summary) — rewritten at concept
   level; no direct sentence from the paper.
2. **Section VII-B** (Shor/ECDLP) — describes a well-known mathematical
   result; wording is original.
3. **Algorithm 2 (Hash+XOR login)** — pseudocode derived from Ju-Park protocol
   logic; figures and tables are freshly drawn as required.

---

*Last updated: 2026-10-22*

# Log — 2026-11-15

Pipeline tested: `pipeline_test.py` against `C:\Users\zakar\Downloads\png2pdf.pdf` (1 page, no text layer, embedded image 827x517, producer png2pdf.com). Interpreter: Python 3.14 at `C:\Users\zakar\AppData\Local\Python\pythoncore-3.14-64\python.exe`. Tesseract languages installed: eng, ita, ita_old, osd. No spa.

## What was wrong

The fallback was not broken. `png2pdf.pdf` has an empty text layer, `len(testo) < 50` is true, and `metodo` was already `ocr`. The OCR text was the problem.

`--psm 3` (fully automatic page segmentation) treated the table rules as a column of characters. On the same grayscale render, before any code change:

- `--psm 3`: 6/15 anchor phrases, 93 lines, 62 garbage lines (length <= 2 or mostly symbols). Output started with `EC _  —_ | e error rrrrere rr` and then a column of single characters.
- `--psm 6`: 12/15 anchors, 18 lines, 0 garbage lines.
- `--psm 1`: same failure as psm 3.
- `--psm 4`: 0 garbage, but only 6/15 anchors (drops most of the table).
- `--psm 11`: 26 garbage lines.

The page is a straight, readable form. Pixmap stride equals width, so `Image.frombytes` was not scrambling this file. Mean gray 163, std 34: low contrast, but not the cause of the garbage column.

## Preprocessing that was tried and not kept

Every filter stack was scored on the same page, same anchors, against raw grayscale at 300 DPI + `--psm 6` (12-13/16 depending on the anchor list). All of them scored worse. They are not in the code.

- Autocontrast + contrast 1.4 + unsharp, psm 6, ita+eng: 7 hits, and it destroyed the header (`ALVARO ALEMAN`, the NIT, `1.160.000`).
- Native 827x517, no upscale: 10/12, slightly worse than the 300 DPI render.
- Otsu binarization: 4/12. Gray table bands collapse and the text in them goes with them.
- 2x Lanczos + Otsu: 9/12.
- Adaptive threshold (local mean) + morphological rule removal, on the 300 DPI render: 2/12.
- White padding of 12, 24, or 40 px: 8-9 hits. Padding did not recover the clipped first letters and lost other anchors.
- Whitening long dark runs (table rules) on the grayscale image: 7/16, or 0/16 if the dark threshold is loose. Strict rule removal still lost anchors versus the raw image (11 vs 13).

So the image does not want a contrast boost or a hard threshold. Tesseract's own binarizer does better on this page than a preprocess that flattens the gray rows.

## Code changes

File: `src/controllo_doc.py` only. `pipeline_test.py` and `src/chunker.py` were not modified.

1. OCR config `--psm 3` changed to `--psm 6`. This is the fix for the garbage column.
2. `Image.frombytes("L", ...)` replaced with `pix.pil_image()`. On this file they match (stride == width). `frombytes` shifts rows when a pixmap has alignment padding; `pil_image()` does not. On this page the score is the same.
3. Removed `from PIL import Image`. Nothing in the file uses it after change 2.

## Checked, not changed

- `pipeline_test.py` runs and exits 0. It prints each chunk twice (full text, then a one-line summary). Redundant, not a bug.
- Hardcoded paths exist on this machine: `png2pdf.pdf`, `circolare_test_scolastica.pdf`, `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- `circolare_test_scolastica.pdf`, the five LSA PDFs, and all 68 pages of `Linee-guida-PTCO-con-allegati.pdf` have a real text layer. The fallback correctly does not OCR them. Re-checked the circolare after the edit: `text_extraction`, 2021 characters.
- `png2pdf.pdf` is a Spanish employment contract. The OCR language is `ita+eng`, and Spanish traineddata is not installed. A probe with `spa` (tessdata_fast, not installed system-wide) went from 12 to 14 anchors and fixed words like `cláusulas`, `consideraciones`, `Antioquia`, `CONTRATO DE TRABAJO POR OBRA`. It did not fix dropped first letters (`ABOR`, `IRO`, `incargada`). Language was left at `ita+eng` because the rest of this project is Italian and `spa` is not in the Tesseract install.
- `src/chunker.py` is fine. After the fix the second chunk is the overlap of the real paragraph, not the garbage column.

## Verification

`python pipeline_test.py` from the project root, after the edit:

- `metodo_estrazione`: `ocr` (fallback still fires)
- 2 chunks, 1441 and 210 characters
- no single-character column
- readable header: `ALVARO ALEMAN PARACO`, `AYUDANTE DE PRODUCCION`, `C.I. SAN FRANCISCO GARDENS SAS`, `RIONEGRO`, `$ 1.160.000`, `8 HORAS`, `CONTRATO DE TRABAJO`
- residual errors are character-level (Spanish under an Italian model, plus a few dropped first letters), not a failed fallback

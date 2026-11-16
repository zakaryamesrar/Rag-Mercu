
from pathlib import Path
import pymupdf
import pytesseract

# Configurazione Tesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

MIN_TEXT_LENGTH = 50
DPI = 300


def estrazione_testo(pagina):
    return pagina.get_text("text").strip()


def ocr_pagina(pagina):

    pix = pagina.get_pixmap(
        dpi=DPI,
        colorspace=pymupdf.csGRAY,
        alpha=False
    )

    # pil_image() rispetta lo stride; frombytes sposta le righe se c'è padding.
    immagine = pix.pil_image()

    # PSM 6: un unico blocco. PSM 3 legge i bordi della tabella come caratteri.
    testo = pytesseract.image_to_string(
        immagine,
        lang="ita+eng",
        config="--psm 6"
    )

    return testo.strip()


def process_pdf(pdf_path):

    percorso = Path(pdf_path)

    if not percorso.is_file():
        raise FileNotFoundError(
            f"File non trovato: {percorso}"
        )

    risultato = []

    with pymupdf.open(percorso) as doc:

        for n_pagina, pagina in enumerate(doc, start=1):

            testo = estrazione_testo(pagina)
            metodo = "text_extraction"

            if len(testo) < MIN_TEXT_LENGTH:

                try:
                    testo = ocr_pagina(pagina)
                    metodo = "ocr"

                except pytesseract.TesseractNotFoundError:
                    raise RuntimeError(
                        "Tesseract non trovato. "
                        "Controlla il percorso di installazione."
                    )

            risultato.append({
                "pagina": n_pagina,
                "testo": testo,
                "metodo": metodo,
                "caratteri": len(testo)
            })

    return {
        "nome_file": percorso.name,
        "totale_pagine": len(risultato),
        "pagine": risultato
    }


if __name__ == "__main__":

    risultato = process_pdf(
        r"C:\Users\zakar\Downloads\circolare_test_scolastica.pdf"
    )

    print("Documento:", risultato["nome_file"])
    print("Totale pagine:", risultato["totale_pagine"])

    for pagina in risultato["pagine"]:

        print(
            f"Pagina {pagina['pagina']} | "
            f"Metodo: {pagina['metodo']} | "
            f"Caratteri: {pagina['caratteri']}"
        )

        print(pagina["testo"][:200])
        print("-" * 50)

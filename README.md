# Rag Mercu

Pipeline che prepara PDF per un RAG: estrae il testo pagina per pagina e lo spezza in chunk con metadati. Non fa embedding e non interroga nulla. Si ferma ai chunk.

Per ogni pagina prova prima il text layer. Se il testo estratto è sotto i 50 caratteri, renderizza la pagina in scala di grigi a 300 DPI e la passa a Tesseract (`ita+eng`, `--psm 6`). Il chunking è per pagina, così un chunk non attraversa il cambio pagina.

## Uso

Dalla root del progetto, con Tesseract installato:

```python
from src.controllo_doc import process_pdf
from src.chunker import crea_chunk

documento = process_pdf("data/testdata/pdf/circolare_30525_2024-08-01.pdf")
chunks = crea_chunk(documento)
```

`process_pdf` restituisce:

```python
{
    "nome_file": "circolare_30525_2024-08-01.pdf",
    "totale_pagine": 1,
    "pagine": [
        {
            "pagina": 1,
            "testo": "...",
            "metodo": "text_extraction",  # oppure "ocr"
            "caratteri": 2773,
        }
    ],
}
```

`crea_chunk` restituisce una lista di:

```python
{
    "testo": "...",
    "metadati": {
        "nome_file": "circolare_30525_2024-08-01.pdf",
        "pagina": 1,
        "chunk_id": 0,
        "metodo_estrazione": "text_extraction",
    },
}
```

Lo splitter è `RecursiveCharacterTextSplitter`: 1500 caratteri, overlap 200, separatori `\n\n`, `\n`, `. `, spazio, stringa vuota.

`pipeline_test.py` esegue gli stessi due passi e stampa i chunk. Il percorso del PDF lì dentro è hardcoded su un file locale (`C:\Users\zakar\Downloads\png2pdf.pdf`), non su un file del repo.

## Requisiti

- Python 3.14
- Tesseract OCR in `C:\Program Files\Tesseract-OCR\tesseract.exe`, con i language pack `ita` e `eng`. Il percorso è scritto in `src/controllo_doc.py`.
- Pacchetti usati in questo ambiente: `pymupdf` 2.1, `pytesseract` 0.3.13, `langchain-text-splitters` 1.1.3, `pillow` 12.3.0

```
pip install pymupdf pytesseract langchain-text-splitters pillow
```

## Struttura

```
src/controllo_doc.py    estrazione testo + fallback OCR
src/chunker.py          split in chunk con metadati
pipeline_test.py        prova end-to-end su un PDF locale
log.md                  perché l'OCR usa --psm 6 e niente preprocessing
data/rawdata/           PDF di lavoro (LSA, linee guida PTCO)
data/testdata/pdf/      PDF con text layer
data/testdata/jpeg/     pagine rese come immagine
data/testdata/pdf_da_jpeg/   le stesse pagine reimpacchettate in PDF, senza text layer
data/testdata/risultati_pipeline.json   esito di una corsa sui testdata
data/processeddata/     vuota
```

## OCR

Il fallback scatta solo se `len(testo) < 50`. Una pagina con text layer vero (circolari, LSA, le 68 pagine delle linee guida PTCO) non passa da Tesseract.

`--psm 6` tratta la pagina come un unico blocco di testo. `--psm 3` leggeva i bordi di una tabella come una colonna di caratteri singoli. Il render è grayscale a 300 DPI, senza autocontrast, senza binarizzazione, senza rimozione delle righe: su una pagina di prova quelle trasformazioni peggioravano il riconoscimento rispetto all'immagine grezza. Il dettaglio delle prove è in `log.md`.

L'OCR è `ita+eng`. Su un contratto in spagnolo il testo resta leggibile ma con errori di carattere. I manoscritti (Leibniz, Marx, Rosa Croce) escono illeggibili: il fallback parte, il testo no.

## Limiti

- Il percorso di Tesseract è Windows e fisso.
- `pipeline_test.py` e il `__main__` di `controllo_doc.py` puntano a PDF fuori dal repo.
- Nessun embedding, nessun indice, nessuna query.

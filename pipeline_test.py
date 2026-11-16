
from src.chunker import crea_chunk
from src.controllo_doc import process_pdf

# Percorso del PDF
pdf_path = r"C:\Users\zakar\Downloads\png2pdf.pdf"

# STEP 1: Estrazione del testo
documento = process_pdf(pdf_path)

# STEP 2: Generazione dei chunk
chunks = crea_chunk(documento)

# STEP 3: Visualizzazione
print("Documento:", documento["nome_file"])
print("Numero chunk:", len(chunks))

for chunk in chunks:
    print("\n--- CHUNK ---")
    print("Metadati:", chunk["metadati"])
    print("Testo:", chunk["testo"])
for chunk in chunks:
    print(
        f"Pagina {chunk['metadati']['pagina']} | "
        f"Chunk {chunk['metadati']['chunk_id']} | "
        f"Caratteri: {len(chunk['testo'])}"
    )
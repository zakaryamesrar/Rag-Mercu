
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1500       # Numero massimo indicativo di caratteri per chunk
CHUNK_OVERLAP = 200     # Caratteri condivisi tra chunk consecutivi


def crea_chunk(doc):

    # Inizializziamo il Recursive Character Text Splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunk_generati = []

    # Iteriamo sulle pagine del documento
    for pagina in doc["pagine"]:

        # Recuperiamo il testo della pagina corrente
        testo = pagina["testo"]

        # Suddividiamo il testo in chunk
        chunks = splitter.split_text(testo)

        # Iteriamo sui chunk generati
        for indice, chunk in enumerate(chunks):

            chunk_generati.append({
                "testo": chunk,
                "metadati": {
                    "nome_file": doc["nome_file"],
                    "pagina": pagina["pagina"],
                    "chunk_id": indice,
                    "metodo_estrazione": pagina["metodo"]
                }
            })

    return chunk_generati

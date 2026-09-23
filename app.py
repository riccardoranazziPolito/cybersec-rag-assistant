import os
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents.stuff import create_stuff_documents_chain

# Costanti
DATA_DIR = "./data"
CHROMA_PERSIST_DIR = "./chroma_db"

def load_documents(data_dir: str):
    """
    Carica i documenti PDF e TXT dalla directory specificata.
    """
    documents = []
    
    # Crea la cartella se non esiste
    if not os.path.exists(data_dir):
        print(f"Cartella '{data_dir}' non trovata. Creazione in corso...")
        os.makedirs(data_dir)
        print("Aggiungi file PDF o TXT in questa cartella e riavvia l'applicazione.")
        return documents

    # Caricamento file PDF
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    for file in pdf_files:
        try:
            loader = PyPDFLoader(file)
            documents.extend(loader.load())
            print(f"Caricato: {file}")
        except Exception as e:
            print(f"Errore durante il caricamento di {file}: {e}")

    # Caricamento file TXT
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
    for file in txt_files:
        try:
            loader = TextLoader(file, encoding="utf-8")
            documents.extend(loader.load())
            print(f"Caricato: {file}")
        except Exception as e:
            print(f"Errore durante il caricamento di {file}: {e}")

    return documents

def split_documents(documents):
    """
    Suddivide i documenti in chunk ottimali.
    Utilizza RecursiveCharacterTextSplitter per mantenere il contesto semantico,
    impostando chunk size a 1000 con overlap di 200.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def initialize_vector_store(chunks):
    """
    Inizializza il Vector Database su ChromaDB e ne garantisce la persistenza locale.
    """
    # Utilizzo di nomic-embed-text, un modello open source ottimizzato per gli embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Se ci sono nuovi documenti, si crea o aggiorna il database e si salva su disco
    if chunks:
        print(f"Creazione del vector store con {len(chunks)} frammenti (chunks) e salvataggio in {CHROMA_PERSIST_DIR}...")
        vectorstore = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory=CHROMA_PERSIST_DIR
        )
    else:
        # Se non ci sono documenti passati ma il db esiste, lo carichiamo dal disco
        if os.path.exists(CHROMA_PERSIST_DIR):
            print(f"Caricamento del vector database esistente da '{CHROMA_PERSIST_DIR}'...")
            vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR, 
                embedding_function=embeddings
            )
        else:
            print("Nessun documento trovato e nessun database esistente.")
            print("Per favore, inserisci dei documenti nella cartella 'data' e riavvia.")
            return None
            
    return vectorstore

def create_rag_chain(vectorstore):
    """
    Crea la catena RAG (Retrieval-Augmented Generation) impostando un prompt molto severo, 
    così da evitare allucinazioni in contesto di Threat Intelligence.
    """
    # Usiamo llama3 in locale tramite Ollama. Temperatura 0 per risposte deterministiche.
    llm = ChatOllama(model="llama3", temperature=0)
    
    # Prompt ottimizzato per il dominio Cybersecurity
    prompt_template = """Sei un CyberSec Threat Intelligence Assistant esperto. 
Il tuo compito è rispondere alle domande di analisti SOC e responsabili di sicurezza utilizzando ESCLUSIVAMENTE il contesto fornito di seguito, che proviene dalla documentazione di sicurezza interna (es. policy, manuali IR, report CVE).

Se le informazioni contenute nel contesto non sono sufficienti per rispondere in maniera accurata alla domanda, devi dichiarare esplicitamente: "Le informazioni fornite nei documenti non contengono la risposta a questa domanda."
NON inventare informazioni, NON formulare ipotesi al di fuori dei testi forniti e NON richiamare conoscenze pregresse esterne ai documenti.

Contesto:
{context}

Domanda:
{input}

Risposta:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "input"]
    )
    
    # Catena per i documenti e il retrieval
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # Configurazione del retriever per recuperare i top 4 frammenti più rilevanti
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain

def main():
    print("="*50)
    print("🛡️ CyberSec Threat Intelligence Assistant")
    print("="*50)
    print("Inizializzazione in corso...\n")
    
    # Nessuna API Key necessaria con Ollama! Il sistema gira 100% in locale.

    # 1. Lettura Documenti
    docs = load_documents(DATA_DIR)
    
    # 2. Suddivisione Documenti (Chunking)
    chunks = []
    if docs:
        print(f"Trovati {len(docs)} documenti complessivi. Suddivisione in chunk semantici...")
        chunks = split_documents(docs)
    
    # 3. Vector Database (Embeddings)
    vectorstore = initialize_vector_store(chunks)
    if not vectorstore:
        return
        
    # 4. Creazione della Catena di Risposta (RAG Chain)
    rag_chain = create_rag_chain(vectorstore)
    
    print("\n✅ Inizializzazione completata. L'assistente è pronto e operativo!")
    print("Digita 'exit', 'quit' o 'esci' per terminare la sessione.\n")
    
    # 5. Interfaccia a Riga di Comando (CLI Interactive Loop)
    while True:
        try:
            query = input("❓ Fai una domanda: ")
            
            # Condizione di uscita
            if query.lower().strip() in ['exit', 'quit', 'esci']:
                print("Chiusura dell'assistente in corso. Arrivederci!")
                break
                
            if not query.strip():
                continue
                
            print("⏳ Analisi documentale e formulazione risposta...\n")
            
            # Interrogazione della catena RAG
            response = rag_chain.invoke({"input": query})
            
            print("🟢 Risposta:")
            print(response["answer"])
            print("-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\nChiusura forzata dell'assistente. Arrivederci!")
            break
        except Exception as e:
            print(f"\n❌ Si è verificato un errore inaspettato: {e}\n")

if __name__ == "__main__":
    main()

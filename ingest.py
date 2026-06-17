import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

def processar_documentos():
    print("=== 1. Carregando documentos da pasta 'dados/' ===")
    if not os.path.exists("dados") or not os.listdir("dados"):
        print("Erro: Coloque pelo menos um arquivo PDF dentro da pasta 'dados' antes de rodar!")
        return
        
    loader = PyPDFDirectoryLoader("dados/")
    documentos = loader.load()
    print(f"Total de páginas carregadas: {len(documentos)}")

    print("\n=== 2. Dividindo o texto em pedaços (Chunks) ===")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)
    print(f"Total de pedaços de texto gerados: {len(chunks)}")

    print("\n=== 3. Inicializando o modelo de Embedding local (Ollama) ===")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print("\n=== 4. Criando o banco vetorial ChromaDB e salvando os dados ===")
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="chroma_db_storage"
    )
    
    print("\n Sucesso! Banco de dados vetorial criado e salvo localmente!")

if __name__ == "__main__":
    processar_documentos()
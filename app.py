import streamlit as st
import os
import pandas as pd
import docx2txt
import pypdf
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Configuração da página
st.set_page_config(page_title="Centro de Conhecimento IA", page_icon="🧠", layout="wide")

# --- INJEÇÃO DE CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #161A22 !important; border-right: 1px solid #21262D; }
    h1, h2, h3 { color: #F0F6FC !important; font-weight: 700 !important; }
    .stChatMessage {
        background-color: #161A22 !important;
        border: 1px solid #21262D !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #1F242C !important;
        border-left: 4px solid #1F6FEB !important;
    }
    .fonte-citada {
        background-color: #1F242C;
        border-left: 3px solid #238636;
        padding: 8px 12px;
        margin-top: 5px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #8B949E;
    }
    .stButton>button {
        background-color: #21262D !important; color: #F0F6FC !important;
        border: 1px solid #30363D !important; border-radius: 8px !important;
    }
    .stButton>button:hover {
        background-color: #8B0000 !important; color: #FFFFFF !important; border-color: #FF0000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa estados
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_ready" not in st.session_state:
    st.session_state.db_ready = os.path.exists("chroma_db_storage")

# --- FUNÇÃO AUXILIAR PARA EXTRAÇÃO DE TEXTO MULTIFORMATO ---
def extrair_texto(file):
    ext = file.name.split(".")[-1].lower()
    texto = ""
    
    if ext == "pdf":
        pdf_reader = pypdf.PdfReader(file)
        for page in pdf_reader.pages:
            texto += page.extract_text() or ""
            
    elif ext == "txt" or ext == "md":
        texto = file.read().decode("utf-8", errors="ignore")
        
    elif ext == "docx":
        texto = docx2txt.process(file)
        
    elif ext in ["csv", "xlsx"]:
        try:
            df = pd.read_excel(file) if ext == "xlsx" else pd.read_csv(file)
            # Converte linhas da tabela em strings textuais estruturadas para o RAG
            linhas = []
            for idx, row in df.iterrows():
                linhas.append(f"Linha {idx}: " + ", ".join([f"{col}: {val}" for col, val in row.items()]))
            texto = "\n".join(linhas)
        except Exception as e:
            st.error(f"Erro ao ler tabela: {e}")
            
    return texto.strip()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("## ⚙️ Painel de Controle")
    st.write("")
    
    modelo_selecionado = st.selectbox(
        "🧠 Cérebro do Agente:",
        ["llama3", "llama3.1", "llama3.2"],
        index=0
    )
    
    st.write("---")
    
    st.markdown("### 📁 Ingestão de Documentos")
    # Modificado para aceitar múltiplos arquivos de vários formatos
    uploaded_files = st.file_uploader(
        "Suba arquivos (PDF, TXT, DOCX, CSV, XLSX):", 
        type=["pdf", "txt", "md", "docx", "csv", "xlsx"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        arquivos_para_processar = []
        for f in uploaded_files:
            # Aqui conferimos se o arquivo já não foi processado nesta sessão para evitar duplicados
            if f"proc_{f.name}" not in st.session_state:
                arquivos_para_processar.append(f)
                
        if arquivos_para_processar:
            with st.spinner("Indexando novos formatos na base vetorial..."):
                todos_docs = []
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
                
                for f in arquivos_para_processar:
                    conteudo = extrair_texto(f)
                    if conteudo:
                        chunks = text_splitter.split_text(conteudo)
                        for chunk in chunks:
                            # Passamos metadados para saber a origem do chunk
                            todos_docs.append(Document(page_content=chunk, metadata={"fonte": f.name}))
                        st.session_state[f"proc_{f.name}"] = True
                
                if todos_docs:
                    embeddings = OllamaEmbeddings(model="nomic-embed-text")
                    banco_vetorial = Chroma.from_documents(
                        documents=todos_docs,
                        embedding=embeddings,
                        persist_directory="chroma_db_storage"
                    )
                    st.session_state.db_ready = True
                    st.success(f"✅ {len(arquivos_para_processar)} arquivo(s) adicionado(s)!")

    st.write("---")
    if st.button("🧹 Limpar Histórico do Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ÁREA PRINCIPAL DO CHAT ---
st.title("🤖 Centro de Conhecimento Multiformato")
st.markdown("##### Faça perguntas cruzadas sobre PDFs, Documentos Word, Notas e Planilhas locais.")
st.write("")

if not st.session_state.db_ready:
    st.info("👋 Olá, Pedro! Insira seus documentos ou tabelas na barra lateral para ativar a inteligência do agente.")
else:
    @st.cache_resource(show_spinner=False)
    def configurar_motores(nome_modelo):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        banco_vetorial = Chroma(persist_directory="chroma_db_storage", embedding_function=embeddings)
        retriever = banco_vetorial.as_retriever(search_kwargs={"k": 4}) # k=4 para buscar mais fatias de arquivos distintos
        llm = Ollama(model=nome_modelo, temperature=0.1)
        return retriever, llm

    retriever, llm = configurar_motores(modelo_selecionado)

    # Exibe histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Se a mensagem do assistente guardou fontes citadas, exibe-as de forma elegante
            if "fontes" in message and message["fontes"]:
                st.markdown("**Fontes consultadas:**")
                for fonte in message["fontes"]:
                    st.markdown(f"<div class='fonte-citada'>📄 {fonte}</div>", unsafe_allow_html=True)

    # Entrada do usuário
    if user_input := st.chat_input("O que deseja extrair dos seus arquivos hoje?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analisando bases de dados e documentos..."):
                docs_relevantes = retriever.invoke(user_input)
                
                # Monta contexto e captura metadados das fontes exclusivas
                contexto_documentos = "\n\n".join([doc.page_content for doc in docs_relevantes])
                fontes_usadas = sorted(list(set([doc.metadata.get("fonte", "Desconhecido") for doc in docs_relevantes])))
                
                historico_texto = ""
                for msg in st.session_state.messages[-6:-1]: 
                    papel = "Usuário" if msg["role"] == "user" else "Assistente"
                    historico_texto += f"{papel}: {msg['content']}\n"
                
                prompt_sistema = (
                    "Você é um especialista em análise de dados e suporte técnico corporativo.\n"
                    "Responda à pergunta do usuário usando estritamente o contexto fornecido abaixo.\n"
                    "Se o contexto envolver linhas de tabelas (ex: Linha X: Coluna Y), sintetize a resposta de forma clara e profissional.\n"
                    "Se não souber, diga apenas que a informação não consta na base de dados.\n\n"
                    f"--- CONTEXTO DE ARQUIVOS ---\n{contexto_documentos}\n\n"
                    f"--- HISTÓRICO RECENTE ---\n{historico_texto}\n"
                    f"Usuário: {user_input}\n"
                    "Assistente:"
                )
                
                resposta_texto = llm.invoke(prompt_sistema)
                st.markdown(resposta_texto)
                
                # Mostra fontes dinamicamente na resposta atual
                if fontes_usadas:
                    st.markdown("**Fontes consultadas:**")
                    for fonte in fontes_usadas:
                        st.markdown(f"<div class='fonte-citada'>📄 {fonte}</div>", unsafe_allow_html=True)
                
        st.session_state.messages.append({
            "role": "assistant", 
            "content": resposta_texto,
            "fontes": fontes_usadas
        })
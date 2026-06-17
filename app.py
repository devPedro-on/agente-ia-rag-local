import streamlit as st
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import pypdf

# Configuração da página (deve ser o primeiro comando)
st.set_page_config(page_title="Agente de Suporte IA", page_icon="🤖", layout="wide")

# --- INJEÇÃO DE CSS PARA DESIGN PREMIUM ---
st.markdown("""
    <style>
    /* Customização do fundo geral e fontes */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Customização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #161A22 !important;
        border-right: 1px solid #21262D;
    }
    
    /* Títulos e Subtítulos */
    h1, h2, h3 {
        color: #F0F6FC !important;
        font-weight: 700 !important;
    }
    
    /* Customização das caixas de mensagem do chat */
    .stChatMessage {
        background-color: #161A22 !important;
        border: 1px solid #21262D !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Dar um destaque sutil para a mensagem do usuário */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #1F242C !important;
        border-left: 4px solid #1F6FEB !important;
    }
    
    /* Botão de limpar histórico customizado */
    .stButton>button {
        background-color: #21262D !important;
        color: #F0F6FC !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        border-color: #FF0000 !important;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
    }
    
    /* Área de Drag and Drop do PDF */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #0E1117 !important;
        border: 2px dashed #30363D !important;
        border-radius: 10px !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #1F6FEB !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa as variáveis de estado para o histórico e controle do banco
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_ready" not in st.session_state:
    st.session_state.db_ready = os.path.exists("chroma_db_storage")

# --- BARRA LATERAL (CONFIGURAÇÕES E UPLOAD) ---
with st.sidebar:
    st.markdown("## ⚙️ Painel de Controle")
    st.write("")
    
    # 1. Seleção de Modelo
    modelo_selecionado = st.selectbox(
        "🧠 Cérebro do Agente:",
        ["llama3", "llama3.1", "llama3.2"],
        index=0
    )
    
    st.write("---")
    
    # 2. Upload de Arquivos Dinâmico
    st.markdown("### 📁 Base de Conhecimento")
    uploaded_file = st.file_uploader("Arraste um novo PDF para indexar:", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Processando e indexando o documento..."):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            texto_completo = ""
            for page in pdf_reader.pages:
                texto_completo += page.extract_text() or ""
            
            if texto_completo.strip():
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
                docs = [Document(page_content=t) for t in text_splitter.split_text(texto_completo)]
                
                embeddings = OllamaEmbeddings(model="nomic-embed-text")
                banco_vetorial = Chroma.from_documents(
                    documents=docs,
                    embedding=embeddings,
                    persist_directory="chroma_db_storage"
                )
                st.session_state.db_ready = True
                st.success(f"✅ '{uploaded_file.name}' integrado!")
            else:
                st.error("Não foi possível extrair texto deste PDF.")
                
    st.write("---")
    
    # 3. Botão de Limpar Conversa
    if st.button("🧹 Limpar Histórico do Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ÁREA PRINCIPAL DO CHAT ---
st.title("🤖 Agente de IA Privado")
st.markdown("##### Converse de forma segura e local com seus documentos e manuais.")
st.write("")

# Se o banco de dados ainda não existe e nenhum arquivo foi upado
if not st.session_state.db_ready:
    st.info("👋 Olá, Pedro! Para começar, arraste um arquivo PDF no painel lateral para que o agente possa analisar.")
else:
    # Inicializa o motor de busca e o LLM escolhido
    @st.cache_resource(show_spinner=False)
    def configurar_motores(nome_modelo):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        banco_vetorial = Chroma(persist_directory="chroma_db_storage", embedding_function=embeddings)
        retriever = banco_vetorial.as_retriever(search_kwargs={"k": 3})
        llm = Ollama(model=nome_modelo, temperature=0.2)
        return retriever, llm

    retriever, llm = configurar_motores(modelo_selecionado)

    # Conteiner para envelopar o chat de forma elegante
    chat_container = st.container()

    with chat_container:
        # Exibe as mensagens do histórico na tela
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Entrada do usuário
    if user_input := st.chat_input("Pergunte algo sobre os manuais..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento privada..."):
                docs_relevantes = retriever.invoke(user_input)
                contexto_documentos = "\n\n".join([doc.page_content for doc in docs_relevantes])
                
                historico_texto = ""
                for msg in st.session_state.messages[-6:-1]: 
                    papel = "Usuário" if msg["role"] == "user" else "Assistente"
                    historico_texto += f"{papel}: {msg['content']}\n"
                
                prompt_sistema = (
                    "Você é um assistente de suporte técnico prestativo e profissional.\n"
                    "Use estritamente os seguintes pedaços de contexto para responder à pergunta.\n"
                    "Se não souber, diga apenas que não encontrou nos manuais.\n\n"
                    f"--- CONTEXTO ---\n{contexto_documentos}\n\n"
                    f"--- HISTÓRICO ---\n{historico_texto}\n"
                    f"Usuário: {user_input}\n"
                    "Assistente:"
                )
                
                resposta_texto = llm.invoke(prompt_sistema)
                st.markdown(resposta_texto)
                
        st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
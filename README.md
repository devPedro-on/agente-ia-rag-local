# 🤖 Agente de IA Privado com RAG e Memória Local

Este projeto consiste em um assistente de suporte técnico inteligente operando de forma 100% local, privada e segura. A aplicação utiliza a arquitetura **RAG (Retrieval-Augmented Generation)** para consultar documentos PDF de forma dinâmica e possui uma janela de contexto para lembrar do histórico da conversa recente, mantendo a experiência fluida no estilo ChatGPT.

## 🚀 Funcionalidades

- **Privacidade Total:** Roda inteiramente na sua máquina (via WSL 2 e Ollama), sem envio de dados para APIs externas.
- **Ingestão Dinâmica:** Interface gráfica que permite arrastar e soltar (Drag and Drop) qualquer arquivo PDF para indexação imediata.
- **Memória de Curto Prazo:** O agente compreende pronomes e perguntas complementares baseado nas últimas mensagens trocadas.
- **Interface:** Visual escuro customizado via injeção de CSS no Streamlit para melhor experiência de uso.

## 🛠️ Tecnologias Utilizadas

- **Ambiente:** WSL 2 (Ubuntu 22.04+)
- **Interface:** [Streamlit](https://streamlit.io/)
- **Orquestração de IA:** [LangChain](https://www.langchain.com/)
- **Banco Vetorial:** [ChromaDB](https://www.trychroma.com/)
- **LLM Local:** `llama3` via [Ollama](https://ollama.com/)
- **Embeddings:** `nomic-embed-text` via Ollama

## 🔧 Como Executar o Projeto

### Pró-requisitos

Certifique-se de ter o **Ollama** rodando no seu ambiente e os modelos instalados:

```bash
ollama pull llama3
ollama pull nomic-embed-text


____________________________________________________________________________________________
## Como executar o ambiente virtual (venv):
### Abra o terminal (Ctrl + ') e rode **source venv/bin/activate** e veja se aparece o (venv).

### Para rodar o streamlite via terminal, rode **streamlit run app.py**.
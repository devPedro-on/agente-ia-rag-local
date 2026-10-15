# Centro de Conhecimento IA - Agente RAG Local (V2)

Agente de IA local com **RAG (Retrieval-Augmented Generation)**: você sobe seus documentos e faz perguntas sobre eles. Roda inteiro na sua máquina (WSL2/Ubuntu), sem mandar dados para fora.

Nesta versão **V2**, o agente evoluiu de um leitor de PDFs para uma plataforma capaz de cruzar dados entre múltiplos formatos textuais e tabulares, além de expor as fontes exatas utilizadas para responder às perguntas.

---

## Funcionalidades Principais

* **Ingestão Dinâmica Multiformato:** Suporte a arquivos de texto, documentos corporativos e planilhas de dados:
 * **PDF** (`.pdf`)
 * **Word** (`.docx`)
 * **Notas/Markdown** (`.txt`, `.md`)
 * **Tabelas/Planilhas** (`.csv`, `.xlsx`)
* **Processamento em Lote (Drag & Drop):** Permite arrastar e soltar múltiplos arquivos simultaneamente na barra lateral.
* **Transparência com Fontes Citadas:** Abaixo de cada resposta, o agente exibe um card com os nomes dos arquivos consultados no banco vetorial para formular a resposta.
* **Seleção Dinâmica de Modelos:** Interface integrada para alternar entre diferentes versões do Llama (`Llama 3`, `3.1` ou `3.2`) em tempo de execução.
* **Tema escuro:** CSS customizado no Streamlit.

---

## Stack Tecnológica

* **Interface Web:** Streamlit
* **Orquestração da IA:** LangChain
* **Banco de Dados Vetorial:** ChromaDB
* **Modelos de Linguagem (LLM):** Ollama (`Llama3`)
* **Embeddings Locais:** Ollama (`nomic-embed-text`)
* **Processadores de Arquivos:** PyPDF, Docx2txt, Pandas, Openpyxl

---

## Pré-requisitos & Instalação

### 1. Dependências do Sistema
Certifique-se de ter o **Ollama** instalado e rodando no seu ambiente Linux/WSL, com os modelos baixados:
```bash
ollama run llama3
ollama pull nomic-embed-text
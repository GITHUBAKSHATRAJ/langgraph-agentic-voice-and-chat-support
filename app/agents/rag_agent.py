import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# vector DB
_vector_db = None

def init_vector_db():
    """
    Initializes and loads the local ChromaDB vector store.
    PyPDFLoader: Extracts structured text pages directly from company_policy.pdf.
    nomic-embed-text: Generates high-quality 768-dimension embeddings locally via Ollama.
    """
    global _vector_db 
    if _vector_db is not None:
        return _vector_db

    data_dir = Path(__file__).parent.parent / "data"
    pdf_path = data_dir / "company_policy.pdf"
    txt_path = data_dir / "company_policy.txt"
    
    docs = []
    
    if pdf_path.exists():
        print(f"\n[RAG Agent] Loading & Parsing PDF Policy Document: {pdf_path.name}")
        pdf_loader = PyPDFLoader(str(pdf_path))
        docs.extend(pdf_loader.load())
    elif txt_path.exists():
        print(f"\n[RAG Agent] Loading & Parsing Text Policy Document: {txt_path.name}")
        txt_loader = TextLoader(str(txt_path))
        docs.extend(txt_loader.load())
    
    # Chunk PDF into 500-char semantic chunks with 50-char overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    
    # save vector embeddings into local ./chroma_db folder
    _vector_db = Chroma.from_documents(
        documents=splits, 
        embedding=OllamaEmbeddings(model="nomic-embed-text"),
        persist_directory="./chroma_db"
    )
    return _vector_db

def query_company_policies(user_question: str) -> str:
    """
    Executes RAG chain to retrieve relevant policy chunks and generate voice answer.
    Why k=6: Retrieves 6 most relevant policy chunks to provide complete context for general & specific queries.
    """
    db = init_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 6})
    
    # Ollama Llama 3.2 Chat Model
    llm = ChatOllama(model="llama3.2", temperature=0)
    
    # System Prompt guiding RAG answer formatting for voice delivery
    system_prompt = (
        "You are Nova, an expert customer support voice assistant for NovaTech Solutions.\n"
        "Use the retrieved policy context below to answer the customer's question clearly and conversationally.\n"
        "If the customer asks generally about company policies, what you can do, or store rules, summarize our core policies: 30-day money-back guarantee, free replacements for damaged goods, 24/7 Nova voice tracking, and human support hours (Mon-Fri 9am-5pm EST).\n"
        "Keep your answer short, friendly, and under 3 sentences.\n\n"
        "Retrieved Policy Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Format retrieved document objects into raw string context
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    # Flow: retriever | format_docs -> prompt -> llm -> StrOutputParser
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()} 
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("\n[RAG Agent] Searching local company_policy.pdf using Vector Search...")
    response = rag_chain.invoke(user_question)
    return response 
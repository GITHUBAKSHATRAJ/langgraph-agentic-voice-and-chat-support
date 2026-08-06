# 📚 Technologies & Libraries Reference Guide

This document provides a comprehensive technical breakdown of every library, framework, and tool used in the **Voice-Enabled AI Customer Support Hotline** capstone project, detailing **why** it was chosen, **what version** is pinned in `requirements.txt`, **online vs offline status**, and **what role** it plays in the overall system architecture.

---

## 1. 🕸️ Orchestration & Multi-Agent Frameworks

### 1. `langgraph==1.2.10`
* **Why it was used:** Traditional linear chains (like LCEL) cannot handle cyclic agent loops, conditional state branching, or complex multi-agent handoffs. `langgraph` allows us to build a compiled **`StateGraph`** workflow where specialized agent nodes (`action_agent`, `policy_agent`, `feedback_agent`) execute based on dynamic routing decisions.
* **Online/Offline Status:** **100% OFFLINE** (Runs locally on your CPU/GPU).
* **Key Components Used:** `StateGraph`, `END`, `add_conditional_edges()`, `AgentState` (TypedDict central memory schema).

### 2. `langchain==1.3.14`, `langchain-core==1.5.3`, `langchain-community==0.4.2`
* **Why it was used:** Serves as the foundational AI framework for composing components via LangChain Expression Language (LCEL). It provides standardized abstractions for prompts, LLM invocations, output parsers, document loaders, and custom database tools.
* **Online/Offline Status:** **100% OFFLINE** (Local Python framework).
* **Key Components Used:** `PromptTemplate`, `ChatPromptTemplate`, `@tool` decorator, `StrOutputParser`, `JsonOutputParser`, `RunnablePassthrough`, `PyPDFLoader`.

### 3. `langchain-ollama==1.1.0`
* **Why it was used:** Connects LangChain to the local **Ollama** engine, enabling 100% offline, privacy-focused open-source model execution without cloud API costs or latency overhead.
* **Online/Offline Status:** **100% OFFLINE** (Runs local GGUF models on your PC).
* **Key Components Used:** 
  - `ChatOllama(model="llama3.2")`: Drives reasoning for routing, tool selection, and voice response synthesis.
  - `OllamaEmbeddings(model="nomic-embed-text")`: Generates 768-dimension vector embeddings locally for RAG policy document retrieval.

---

## 2. 📄 RAG & Vector Database Technologies

### 4. `chromadb==1.5.9`
* **Why it was used:** A fast, lightweight, local vector database required to index and retrieve semantic policy chunks from `company_policy.pdf`. It eliminates the need for expensive cloud vector databases (like Pinecone) while offering instant vector similarity search.
* **Online/Offline Status:** **100% OFFLINE** (Local vector index stored in `./chroma_db`).
* **Key Components Used:** `Chroma.from_documents()`, `as_retriever(search_kwargs={"k": 6})`.

### 5. `pypdf==6.14.2`
* **Why it was used:** PyPDF is the robust underlying PDF parsing engine leveraged by `PyPDFLoader` to read, extract text pages, and chunk multi-page LaTeX policy handbooks into clean semantic document objects.
* **Online/Offline Status:** **100% OFFLINE** (Local document parser).
* **Key Components Used:** `PyPDFLoader("company_policy.pdf")`.

---

## 3. 📊 Relational Database & Validation

### 6. `mysql-connector-python==26.7.0`
* **Why it was used:** Official MySQL driver used to connect Python to the relational database (`orders`, `couriers`, `customers`, `support_tickets`, `customer_feedback`). It enables SQL `JOIN` queries, transactional inserts, and record updates.

* **Online/Offline Status:** **100% OFFLINE** (Connects to `localhost:3306`).
* **Key Components Used:** `mysql.connector.connect()`, `cursor(dictionary=True)`.

### 7. `pydantic==2.13.4`
* **Why it was used:** Provides strict runtime type validation, structural guardrails, and data schema enforcement. It ensures LLM JSON outputs strictly conform to required data types (e.g. converting `RouteDecision` or tool arguments into valid Pydantic models).
* **Online/Offline Status:** **100% OFFLINE** (Local Python validation).
* **Key Components Used:** `BaseModel`, `Field`.

---

## 4. 🎙️ Voice & Audio Processing Pipeline

### 8. `edge-tts==7.2.8`
* **Why it was used:** Provides access to Microsoft Edge's cloud-grade **Neural Text-to-Speech** voices (`en-US-JennyNeural`). Unlike legacy robotic TTS engines (like `pyttsx3`), `edge-tts` produces hyper-realistic, human-sounding adult female voice synthesis.
* **Online/Offline Status:** **ONLINE** (Connects over WebSockets to Microsoft Speech API).
* **Key Components Used:** `edge_tts.Communicate(text, voice)`.

### 9. `pygame==2.6.1`
* **Why it was used:** Cross-platform game and multimedia library. We specifically use **`pygame.mixer`** to load and play generated MP3 voice audio files smoothly with zero audio clipping, lag, or device locking.
* **Online/Offline Status:** **100% OFFLINE** (Local hardware audio playback).
* **Key Components Used:** `pygame.mixer.init()`, `pygame.mixer.music.load()`, `pygame.mixer.music.play()`.

### 10. `SpeechRecognition==3.17.0`
* **Why it was used:** Provides an easy-to-use API for capturing live microphone audio from hardware devices and converting spoken voice into text using Google Speech Recognition (`recognize_google`).
* **Online/Offline Status:** **ONLINE** (Connects to Google Speech-to-Text API).
* **Key Components Used:** `sr.Recognizer()`, `sr.Microphone()`, `recognizer.listen()`, `pause_threshold = 1.8`.

### 11. `PyAudio==0.2.14`
* **Why it was used:** The underlying low-level PortAudio C/C++ bindings required by `SpeechRecognition` to access microphone hardware streams across Windows audio drivers.
* **Online/Offline Status:** **100% OFFLINE** (Local C/C++ audio driver binding).

---

## 5. 📡 Environment & Observability

### 12. `python-dotenv==1.2.2`
* **Why it was used:** Loads configuration settings and API keys (such as `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`) from `.env` files into environment variables without hardcoding secret keys into source code.
* **Online/Offline Status:** **100% OFFLINE** (Local `.env` loader).
* **Key Components Used:** `dotenv.load_dotenv()`.

---

## 6. 🌐 Web Backend & REST API Frameworks

### 13. `fastapi==0.115.8`
* **Why it was used:** High-performance, modern Python web framework used to build REST API endpoints (`/chat`, `/health`) and serve the built-in dark-mode Web UI dashboard.
* **Online/Offline Status:** **100% OFFLINE** (Runs local web server on `localhost:8000`).
* **Key Components Used:** `FastAPI()`, `HTMLResponse`, `JSONResponse`, `HTTPException`.

### 14. `uvicorn==0.34.0`
* **Why it was used:** Lightning-fast ASGI web server implementation used to run the FastAPI application with auto-reload support (`uvicorn app.main:app --reload`).
* **Online/Offline Status:** **100% OFFLINE** (Local ASGI server).

---

## 💡 Summary Architecture Matrix

| Library Name | Pinned Version | Layer / Category | Execution Mode | Primary Purpose in Project |
| :--- | :--- | :--- | :--- | :--- |
| `langgraph` | `1.2.10` | Agent Orchestration | 100% Offline | StateGraph workflow graph & node routing |
| `langchain-ollama` | `1.1.0` | LLM & Embeddings | 100% Offline | Local Llama 3.2 reasoning & vector embeddings |
| `chromadb` | `1.5.9` | Vector Storage | 100% Offline | Local PDF policy document similarity search |
| `mysql-connector-python` | `26.7.0` | Relational DB | 100% Offline | Relational SQL queries and transactional logging |

| `pydantic` | `2.13.4` | Data Validation | 100% Offline | Strict JSON schema routing guardrails |
| `fastapi` | `0.115.8` | Web API & UI | 100% Offline | REST endpoints & Web Dashboard UI serving |
| `uvicorn` | `0.34.0` | ASGI Server | 100% Offline | Asynchronous web server execution |
| `edge-tts` | `7.2.8` | Audio Generation | Online | Microsoft Neural Voice synthesis (`JennyNeural`) |
| `pygame` | `2.6.1` | Audio Playback | 100% Offline | Stream audio playback without device lock |
| `SpeechRecognition` | `3.17.0` | Audio Capture | Online | Live microphone speech-to-text transcription |


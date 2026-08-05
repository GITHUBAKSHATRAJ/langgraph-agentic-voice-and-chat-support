# Voice-Enabled Customer Support Agent - Architecture & System Specifications

This document provides comprehensive technical specifications for the **Voice-Enabled AI Customer Support Hotline Capstone Project**. It covers the **LangGraph StateGraph Workflow**, **Relational Database Schema**, **Multi-Page PDF Vector RAG**, **Clean Sequential Voice Pipeline**, and **LangSmith Cloud Observability**.



---

## 1. System Architecture Diagram

The system follows a **LangGraph StateGraph Orchestration Architecture** that routes user requests across specialized sub-agent graph nodes running 100% locally with **Ollama**, **ChromaDB**, and **MySQL**, with telemetry streamed to **LangSmith**.

```mermaid
flowchart TD
    subgraph Presentation_Layer["1. Presentation & Input Layer"]
        VoiceUI["🎙️ Voice Hotline & Web UI Dashboard<br/>- local_voice_chat.py & app/main.py<br/>- SpeechRecognition (Google STT)<br/>- Microsoft Edge Neural TTS (en-US-JennyNeural)<br/>- FastAPI REST API & Dark Web UI"]
    end


    subgraph Orchestration_Layer["2. LangGraph Orchestration Layer"]
        Supervisor["🕸️ Supervisor Router (app/agents/supervisor.py)<br/>- StateGraph Workflow Graph<br/>- ChatOllama (llama3.2)<br/>- RouteDecision Pydantic Validation<br/>- Dynamic Conditional Edge Routing"]
    end

    subgraph Specialized_Agents_Layer["3. Specialized Graph Node Agents"]
        ActionAgent["🛠️ Multi-Tool Action Agent (action_agent.py)<br/>- ReAct Tool Selection & Reasoning<br/>- Order ID Memory Recall & Conversational Synthesizer"]
        PolicyAgent["📄 RAG Policy Agent (rag_agent.py)<br/>- PyPDFLoader & Text Splitter<br/>- ChromaDB Vector Retriever (k=6)"]
        FeedbackAgent["⭐ CSAT Feedback Agent (feedback_agent.py)<br/>- 1-5 Star Rating & Review Extractor<br/>- String Type Enforcement & MySQL Logger"]
    end

    subgraph Data_Tools_Layer["4. Data & Persistence Layer"]
        ChromaStore[("📚 Chroma Vector DB<br/>- nomic-embed-text<br/>- company_policy.pdf")]
        MySQLStore[("🛢️ MySQL Database<br/>- customer_support_db<br/>- customers, couriers, orders,<br/>  support_tickets, customer_feedback")]


        
        subgraph Tool_Box["Database Toolbox (app/tools/database_tools.py)"]
            T1["get_order_status()"]
            T2["get_live_courier_tracking()"]
            T3["cancel_order()"]
            T4["update_shipping_address()"]
            T5["process_damaged_item()"]
            T6["create_urgent_ticket()"]
            T7["log_customer_feedback()"]
        end
    end

    subgraph Telemetry_Layer["5. Observability"]
        LangSmith["📡 LangSmith Cloud Dashboard<br/>- LANGCHAIN_TRACING_V2=true<br/>- Real-time Trace & Token Telemetry"]
    end

    VoiceUI --> Supervisor

    Supervisor -->|"Order Actions & Tools"| ActionAgent
    Supervisor -->|"Policy & General Queries"| PolicyAgent
    Supervisor -->|"CSAT Rating & Feedback"| FeedbackAgent

    PolicyAgent -->|Vector Similarity Search| ChromaStore
    ActionAgent -->|Select & Invoke Tool| Tool_Box
    FeedbackAgent -->|Log CSAT Review| Tool_Box
    Tool_Box -->|Execute SQL JOIN / Insert| MySQLStore

    Orchestration_Layer -.-|"Auto Cloud Tracing"| Telemetry_Layer
```

---

### 1.1 File Module Dependency Graph

This diagram illustrates the explicit Python import dependencies and file relationships across all layers of the codebase.

```mermaid
graph TD
    subgraph CLI_Entry_Point["1. CLI Presentation Layer"]
        MainCLI["local_voice_chat.py"]
    end

    subgraph Orchestration_Layer["2. Graph Orchestration Layer"]
        Supervisor["app/agents/supervisor.py"]
    end

    subgraph Agent_Layer["3. Specialized Sub-Agent Layer"]
        ActionAgent["app/agents/action_agent.py"]
        PolicyAgent["app/agents/rag_agent.py"]
        FeedbackAgent["app/agents/feedback_agent.py"]
    end

    subgraph Tool_Layer["4. Tool & Helper Layer"]
        DBTools["app/tools/database_tools.py"]
    end

    subgraph Config_Data_Layer["5. Configuration & Persistence Layer"]
        Env[".env (MySQL & LangSmith Credentials)"]
        SetupDB["setup_db.py (Database Initializer)"]
        PDF["app/data/company_policy.pdf"]
        MySQL[("MySQL Database: customer_support_db")]
        Chroma[("ChromaDB Vector Store: ./chroma_db")]
    end

    MainCLI -->|Imports route_question| Supervisor
    
    Supervisor -->|Imports query_action_agent| ActionAgent
    Supervisor -->|Imports query_company_policies| PolicyAgent
    Supervisor -->|Imports query_feedback_agent| FeedbackAgent

    ActionAgent -->|Imports SQL Tools| DBTools
    FeedbackAgent -->|Imports log_customer_feedback| DBTools

    PolicyAgent -->|Reads & Parses| PDF
    PolicyAgent -->|Creates & Queries| Chroma

    DBTools -->|Loads Credentials| Env
    DBTools -->|Executes SQL Queries| MySQL
    SetupDB -->|Initializes Schema & Seeds Data| MySQL
```

---

## 2. LangGraph State Machine Workflow Diagram

```mermaid
flowchart TD
    Start([Start: User Query Received]) --> InitState[Initialize AgentState: user_question, chat_history, destination, final_response]
    
    InitState --> SupervisorNode[Node: supervisor_router_node]
    SupervisorNode --> EvaluateIntent{Classify Intent via Llama 3.2}
    
    EvaluateIntent -->|policy_agent| PolicyNode[Node: policy_agent_node]
    EvaluateIntent -->|action_agent| ActionNode[Node: action_agent_node]
    EvaluateIntent -->|feedback_agent| FeedbackNode[Node: feedback_agent_node]

    %% Policy Branch
    PolicyNode --> LoadPDF[Load & Chunk company_policy.pdf via PyPDFLoader]
    LoadPDF --> VectorSearch[ChromaDB Similarity Vector Search k=6]
    VectorSearch --> FormatPolicy[Generate Grounded RAG Response]
    FormatPolicy --> UpdatePolicyState[Update state.final_response]

    %% Action Branch
    ActionNode --> ReasonTool[Reason Tool Selection & Args via Llama 3.2]
    ReasonTool --> CheckOrderID{Is order_id == 0?}
    CheckOrderID -->|Yes| PromptOrderID[Prompt Caller for Order ID]
    CheckOrderID -->|No| ExecTool[Execute MySQL Tool: JOIN orders + couriers]
    ExecTool --> FormatAction[Synthesize Conversational Reply with Memory Context]
    PromptOrderID --> UpdateActionState
    FormatAction --> UpdateActionState[Update state.final_response]

    %% Feedback Branch
    FeedbackNode --> ExtractRating[Extract 1-5 Star Rating & Review Text]
    ExtractRating --> CheckRating{Rating Provided?}
    CheckRating -->|No| PromptRating[Prompt Caller for 1-5 Star Rating]
    CheckRating -->|Yes| LogFeedback[Execute log_customer_feedback Tool]
    PromptRating --> UpdateFeedbackState
    LogFeedback --> FormatFeedback[Synthesize Sincere Confirmation Reply]
    FormatFeedback --> UpdateFeedbackState[Update state.final_response]

    %% Graph Termination
    UpdatePolicyState --> EndGraph([Graph END: Return Response to local_voice_chat.py])
    UpdateActionState --> EndGraph
    UpdateFeedbackState --> EndGraph
```

---

## 3. Data Flow Diagrams (DFD)

### 3.1 DFD Level 0 (System Context Diagram)
A high-level view representing the entire AI Voice Hotline as a single central system interacting with external entities.

```mermaid
graph LR
    subgraph External_Entities["External Entities"]
        Customer["Customer / Caller"]
        Admin["System Administrator / Manager"]
    end

    subgraph System["Central System"]
        VoiceHotline["0.0 Voice-Enabled AI Customer Support System"]
    end

    Customer -->|Spoken Audio Queries| VoiceHotline
    VoiceHotline -->|Synthesized Neural Speech Responses| Customer
    
    VoiceHotline -.->|Telemetry Traces & Analytics| Admin
```

---

### 3.2 DFD Level 1 (Detailed Functional Process Decomposition)
Detailed breakdown of system processes (P1-P6), data stores (DS1-DS3), and data flows.

```mermaid
graph LR
    subgraph External_Entities["External Entities"]
        Customer["Customer / Caller"]
    end

    subgraph Processes["Processes"]
        P1["P1: Audio Capture & Speech-to-Text (Google STT)"]
        P2["P2: LangGraph Supervisor Routing"]
        P3["P3: PDF Vector Search RAG (ChromaDB)"]
        P4["P4: Action Selection & SQL JOIN Execution"]
        P5["P5: CSAT Feedback Extraction & DB Insertion"]
        P6["P6: Edge Neural Text-to-Speech (JennyNeural)"]
    end

    subgraph Data_Stores["Data Stores"]
        DS1[("DS1: Policy PDFs & Chroma Vector DB")]
        DS2[("DS2: MySQL Database")]


        DS3[("DS3: LangSmith Telemetry Cloud")]
    end

    Customer -->|Spoken Audio| P1
    P1 -->|Text Query| P2

    P2 -->|Policy Inquiry| P3
    P2 -->|Order Action / Tracking Request| P4
    P2 -->|Rating / Service Review| P5

    DS1 <-->|Embeddings & PDF Context| P3
    P4 <-->|SQL JOIN Queries & Updates| DS2
    P5 -->|Insert CSAT Rating Record| DS2

    P3 -->|Text Response| P6
    P4 -->|Text Response| P6
    P5 -->|Text Response| P6

    P2 & P3 & P4 & P5 -.->|Stream Execution Traces| DS3

    P6 -->|Neural Speech Stream| Customer
```

---

## 4. System Sequence Diagram (Voice & Tool Execution)

```mermaid
sequenceDiagram
    autonumber
    actor User as Customer (Voice Hotline)
    participant VUI as Voice Interface (local_voice_chat.py)
    participant LG as LangGraph Supervisor (supervisor.py)
    participant ACT as Action Agent (action_agent.py)
    participant DB as MySQL Database
    participant OLL as Ollama (Llama 3.2)
    participant LS as LangSmith Cloud Dashboard

    User->>VUI: Speak ("Where is my courier truck for order 123?")
    VUI->>VUI: STT Transcription ("Where is my order 123?")
    VUI->>LG: route_question(user_question, chat_history)
    
    LG->>LS: Start Trace: LangGraph Execution
    LG->>OLL: Classify Intent (RouteDecision)
    OLL-->>LG: Return RouteDecision(destination="action_agent")
    
    LG->>ACT: Execute Node: action_agent_node
    ACT->>OLL: Reason Tool Calling JSON
    OLL-->>ACT: Return Tool Call JSON<br/>(get_live_courier_tracking, order_id=123)
    
    ACT->>DB: Execute SQL JOIN Query<br/>(SELECT FROM orders JOIN couriers)

    DB-->>ACT: Return Courier Tracking Record<br/>(Blue Dart Express, Bengaluru, Shipped)
    
    ACT->>OLL: Synthesize Conversational Voice Response
    OLL-->>ACT: Return Spoken Text Response<br/>("Your package is in transit near Bengaluru")
    
    ACT-->>LG: Return final_response
    LG->>LS: End Trace: Execution Status 200
    LG-->>VUI: Return response text
    VUI->>VUI: Edge Neural TTS Synthesis & Playback
    VUI-->>User: Play Spoken Audio Output
```


---

## 5. MySQL Relational Schema



```sql
-- 1. Customers Table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    shipping_address VARCHAR(255) NOT NULL
);

-- 2. Couriers Table
CREATE TABLE couriers (
    courier_id INT AUTO_INCREMENT PRIMARY KEY,
    courier_name VARCHAR(50) NOT NULL,
    contact_number VARCHAR(20) NOT NULL
);

-- 3. Orders Table (FK referencing customers & couriers)
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    courier_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    estimated_delivery VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    current_location VARCHAR(255) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (courier_id) REFERENCES couriers(courier_id) ON DELETE CASCADE
);

-- 4. Support Tickets Table (Manager Escalations)
CREATE TABLE support_tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_issue TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'URGENT',
    status VARCHAR(20) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 5. Customer Feedback Table (CSAT Ratings)
CREATE TABLE customer_feedback (

    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NULL,
    rating INT NOT NULL,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);
```

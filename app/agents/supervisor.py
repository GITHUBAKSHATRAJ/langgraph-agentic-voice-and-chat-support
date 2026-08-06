from typing import TypedDict, List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agents.rag_agent import query_company_policies # rag_agent
from agents.action_agent import query_action_agent
from agents.feedback_agent import query_feedback_agent


class RouteDecision(BaseModel):
    destination: str = Field(description="Must be either 'policy_agent', 'action_agent', or 'feedback_agent'")
    
# LangGraph Central Memory Schema 
class AgentState(TypedDict):
    user_question: str
    chat_history: Optional[List[Dict]] 
    destination: str
    final_response: str


def supervisor_router_node(state: AgentState) -> Dict:
    
    # Supervisor Router Node: Evaluates user query and outputs the target graph node destination.
    llm = ChatOllama(model="llama3.2", temperature=0)
    prompt = PromptTemplate.from_template(
        "You are a routing supervisor for a customer support voice hotline. Route the user's query to the correct department.\n"
        "- If they ask about order status, live courier tracking, delivery truck location, courier carrier queries, cancelling an order, changing shipping address, reporting damaged goods, or speaking to a manager, route to 'action_agent'.\n"
        "- If they provide feedback, rating, CSAT score, star rating (1 to 5 stars), service review, express gratitude, thanks ('thank you', 'thanks', 'great service', 'awesome'), or compliments/complaints, route to 'feedback_agent'.\n"
        "- For all other inquiries, company policies, rules, refund rules, operating hours, upgrades, store terms, greetings, or general assistance, route to 'policy_agent'.\n\n"
        "User Query: {query}"
    )
    router = prompt | llm.with_structured_output(RouteDecision)
    
    print("\n[LangGraph Orchestrator] Analyzing state graph and selecting next node...")
    decision = router.invoke({"query": state["user_question"]})
    return {"destination": decision.destination} 


def policy_agent_node(state: AgentState) -> Dict:
    
    # Invokes RAG Policy Agent (Vector search over company_policy.pdf)
    print("--> LangGraph Node Executing: RAG Policy Agent")
    response = query_company_policies(state["user_question"])
    return {"final_response": response}


def action_agent_node(state: AgentState) -> Dict:
    
    # Invokes Multi-Tool Action Agent (Executes MySQL DB tools)
    print("--> LangGraph Node Executing: Multi-Tool Action Agent")
    response = query_action_agent(state["user_question"], state.get("chat_history")) # Safe Access .get("key"): Used for Optional Fields
    return {"final_response": response}


def feedback_agent_node(state: AgentState) -> Dict:
    
    # Invokes  Feedback Agent (Logs star ratings and customer reviews)
    print("--> LangGraph Node Executing: Feedback Agent")
    response = query_feedback_agent(state["user_question"], state.get("chat_history"))
    return {"final_response": response}


# Build and Compiles node topology and conditional routing edges into an executable workflow graph.
def _build_supervisor_graph():
    workflow = StateGraph(AgentState)
    
    # Register Node Functions
    workflow.add_node("supervisor", supervisor_router_node) #The LLM Orchestrator Node
    workflow.add_node("policy_agent", policy_agent_node)
    workflow.add_node("action_agent", action_agent_node)
    workflow.add_node("feedback_agent", feedback_agent_node)
    
    # Set Graph Entry Point
    workflow.set_entry_point("supervisor")
    
    # Define Dynamic Conditional Routing Edges
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["destination"], 
        {
            "policy_agent": "policy_agent",
            "action_agent": "action_agent",
            "feedback_agent": "feedback_agent"
        }
    )
    
    # Define Terminal static Edges
    workflow.add_edge("policy_agent", END)
    workflow.add_edge("action_agent", END)
    workflow.add_edge("feedback_agent", END)
    
    return workflow.compile()

_compiled_graph = _build_supervisor_graph()

def route_question(user_question: str, chat_history: list = None) -> str:
    """
    Entry Point called by local_voice_chat.py.
    """
    initial_state: AgentState = {
        "user_question": user_question,
        "chat_history": chat_history or [],
        "destination": "",
        "final_response": ""
    }
    
    output_state = _compiled_graph.invoke(initial_state)
    return output_state["final_response"]

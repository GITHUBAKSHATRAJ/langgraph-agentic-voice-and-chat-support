from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from tools.database_tools import (
    get_order_status, 
    get_live_courier_tracking,
    cancel_order, 
    update_shipping_address, 
    process_damaged_item, 
    create_urgent_ticket
)

# mapping LLM tool names to Python database functions ,Enables dynamic tool invocation after LLM reasoning
TOOL_MAP = {
    "get_order_status": get_order_status,
    "get_live_courier_tracking": get_live_courier_tracking,
    "cancel_order": cancel_order,
    "update_shipping_address": update_shipping_address,
    "process_damaged_item": process_damaged_item,
    "create_urgent_ticket": create_urgent_ticket
}

def query_action_agent(user_question: str, chat_history: list = None) -> str:
    """
    Executes 2-step tool decision & voice response synthesis pipeline.
    Step 1: Reason over query & history to select tool and extract arguments.
    Step 2: Execute selected MySQL tool(s) and synthesize natural voice response.
    """
    llm = ChatOllama(model="llama3.2", format="json", temperature=0)
    
    formatted_history = "None"
    if chat_history:
        recent = chat_history[-6:]
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent])
    
    # Prompt forcing Llama 3.2 to select tools and output structured JSON payload
    prompt = PromptTemplate.from_template("""
    You are a voice customer support assistant. Determine which tool(s) to execute for the user request.
    Available Tools:
    1. 'get_order_status': Check general shipping status. Required args: order_id (int)
    2. 'get_live_courier_tracking': Get live courier GPS location, carrier name, tracking # and courier phone. Required args: order_id (int)
    3. 'cancel_order': Cancel a processing order. Required args: order_id (int)
    4. 'update_shipping_address': Change delivery address. Required args: order_id (int), new_address (str)
    5. 'process_damaged_item': Report broken item & replace. Required args: order_id (int), item_description (str)
    6. 'create_urgent_ticket': Escalate issue to human manager. Required args: order_id (int), customer_issue (str)

    Use the Conversation History below to resolve references like "it", "that order", or order IDs mentioned in earlier turns.
    If no numeric order ID is explicitly mentioned or resolved from context, set "order_id": 0 in args.

    Recent Conversation History:
    {history}

    Return JSON format:
    {{
        "tool_calls": [
            {{
                "tool_name": "<one of the tool names above>",
                "args": {{ ... }}
            }}
        ]
    }}

    User Request: {query}
    """)

    chain = prompt | llm | JsonOutputParser()
    
    print("\n[Action Agent] Analyzing intent & selecting tool(s) from toolbox... (Llama3.2 Reasoning...)")
    
    try:
        # Step 1: Execute tool decision chain
        result = chain.invoke({"query": user_question, "history": formatted_history})
        
        tool_calls = result.get("tool_calls", [])
        if not tool_calls and "tool_name" in result:
            tool_calls = [{"tool_name": result["tool_name"], "args": result.get("args", {})}] 
            
        print(f"--> Executing {len(tool_calls)} Tool Call(s): {tool_calls}")
        
        # Step 2: Execute MySQL database tools
        db_responses = []
        for call in tool_calls:
            t_name = call.get("tool_name")
            t_args = call.get("args", {})
            order_id = int(t_args.get("order_id", 0))
            
            if order_id == 0 and t_name in TOOL_MAP:
                db_responses.append(f"Action '{t_name}': No order number was provided in the request.")
            elif t_name in TOOL_MAP:
                res = TOOL_MAP[t_name].invoke(t_args) 
                db_responses.append(f"Action '{t_name}': {res}")
            else:
                db_responses.append(f"Invalid tool selected: '{t_name}'.")
                
        combined_db_results = "\n".join(db_responses)
            
        # Step 3: Synthesize conversational voice reply using tool outputs & memory context
        llm_speech = ChatOllama(model="llama3.2", temperature=0)
        speech_prompt = PromptTemplate.from_template(
            "You are Nova, an AI voice support assistant.\n"
            "Customer Question: {query}\n"
            "Database Action Results:\n{combined_db_results}\n\n"
            "Recent Conversation History:\n{history}\n\n"
            "Instructions:\n"
            "- You MUST state the exact tracking details from 'Database Action Results' (such as carrier name, current location, tracking number, or delivery status).\n"
            "- If the customer specifically asks 'what is my order ID?' or 'which order?', state the order ID number directly (e.g. 'Your order ID is 123.').\n"
            "- Speak in a natural, warm, conversational voice under 3 sentences."
        )
        speech_chain = speech_prompt | llm_speech
        final_response = speech_chain.invoke({
            "query": user_question, 
            "combined_db_results": combined_db_results,
            "history": formatted_history
        })
        return final_response.content

        
    except Exception as e:
        print(f"\n[DEBUG Action Agent Error] {e}")
        return "I'm sorry, I couldn't process that request properly. Could you please repeat your order details?"

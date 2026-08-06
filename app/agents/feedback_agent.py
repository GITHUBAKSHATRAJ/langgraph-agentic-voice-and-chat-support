from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from tools.database_tools import log_customer_feedback

def query_feedback_agent(user_question: str, chat_history: list = None) -> str:
    """
    Processes customer CSAT ratings (1 to 5 stars) and feedback comments.
    order_id resolution: Reads conversation history to attach ratings to the active order ID.
    rating prompt fallback: If no numerical rating is found, asks caller to rate 1-5 stars.
    """
    llm = ChatOllama(model="llama3.2", format="json", temperature=0)
    
    formatted_history = "None"
    if chat_history:
        recent = chat_history[-6:]
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent])
        
    # Prompt parsing JSON rating payload
    prompt = PromptTemplate.from_template("""
    You are a customer feedback processing agent. Extract the satisfaction rating (1 to 5 stars), 
    feedback comments, and order ID from the user's request and recent conversation history.

    Rules:
    - If the user provides a rating (1-5) or comments, extract them.
    - If an Order ID was mentioned in recent history or current query, extract it as an integer. Otherwise set order_id to 0.
    - If rating is missing from both user query and history, set rating to 0.

    Recent Conversation History:
    {history}

    Return JSON format:
    {{
        "rating": <int between 1 and 5, or 0 if missing>,
        "feedback_text": "<customer feedback comment string>",
        "order_id": <int order id, or 0 if not disclosed>
    }}

    User Query: {query}
    """)
    
    chain = prompt | llm | JsonOutputParser()
    
    print("\n[Feedback Agent] Analyzing customer rating & feedback... (Llama3.2 Reasoning...)")
    
    try:
        data = chain.invoke({"query": user_question, "history": formatted_history})
        
        # Parse rating with safety fallbacks
        try:
            rating = int(data.get("rating", 0))
        except (ValueError, TypeError):
            rating = 0
            
        # Parse feedback_text string 
        if not raw_feedback or not isinstance(raw_feedback, str) or not raw_feedback.strip():
            feedback_text = user_question.strip() if (user_question and user_question.strip()) else "Support experience rating"
        else:
            feedback_text = raw_feedback.strip()
            
        # Parse order_id with safety fallbacks
        try:
            order_id = int(data.get("order_id", 0))
        except (ValueError, TypeError):
            order_id = 0
        
        if rating <= 0 or rating > 5:
            prompt_missing = (
                "Thank you so much! We value your feedback. "
                "On a scale of 1 to 5 stars, how would you rate your support experience with Nova today?"
            )
            return prompt_missing
            
        # Execute MySQL Database Tool to log CSAT rating record
        result = log_customer_feedback.invoke({
            "rating": rating,
            "feedback_text": feedback_text,
            "order_id": order_id
        })
        
        # Synthesize voice confirmation
        llm_speech = ChatOllama(model="llama3.2", temperature=0)
        speech_prompt = PromptTemplate.from_template(
            "The customer gave a {rating}-star rating with feedback: '{feedback_text}'.\n"
            "Write a warm, sincere, 2-sentence voice response thanking them for their feedback and wishing them a great day."
        )
        speech_chain = speech_prompt | llm_speech
        response = speech_chain.invoke({"rating": rating, "feedback_text": feedback_text})
        return response.content
        
    except Exception as e:
        print(f"[DEBUG Feedback Agent Error] {e}")
        return "Thank you so much for your feedback! We truly appreciate your time and hope you have a wonderful day."

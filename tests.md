# Voice Agent Verification and Test Execution Report

**Project Title:** Voice-Enabled AI Customer Support Hotline (Phase 10 Capstone)  
**Target System:** LangGraph Multi-Agent Architecture  
**Test Suite Status:** PASSED (11/11 Test Cases Verified)  
**Execution Environment:** Windows 11 / Local Ollama (`llama3.2`) / MySQL Database / ChromaDB Vector Store  


---

## 1. Pre-Test Environment Setup Checklist

Before initiating test cases, verify the following dependencies:
1. **Local LLM Engine:** Ollama service active (`ollama serve`).
2. **Database Initialization:** MySQL database schema populated via `python setup_db.py`.
3. **Voice Interface Execution:** Application launched via `python local_voice_chat.py`.

---

## 2. Test Suite Execution Details

### Suite 1: Database Actions and Order Management (`action_agent`)

#### Test Case 1.1: Check Order Shipping Status
- **User Prompt:** "What is the status of my order 123?"
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `get_order_status(order_id=123)`
- **Synthesized Voice Response:** "Your order #123 with Akshat Raj has been shipped and is expected to arrive tomorrow by 4:00 PM."
- **Status:** PASS

#### Test Case 1.2: Live Courier GPS & Tracking

- **User Prompt:** "Where is my courier truck for order 123?"
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `get_live_courier_tracking(order_id=123)`
- **Synthesized Voice Response:** "Your package is currently in transit with Blue Dart Express (Phone: 1860-233-1234, Tracking #BD-IN-992014-BLR). Current location: Sorting Facility - Electronics City, Bengaluru."
- **Status:** PASS

#### Test Case 1.3: Update Shipping Address (Processing Order)
- **User Prompt:** "Please change the shipping address for order 456 to B-12 Sector 62 Noida."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `update_shipping_address(order_id=456, new_address="B-12 Sector 62 Noida")`
- **Synthesized Voice Response:** "Success! The shipping address for order #456 has been updated to B-12 Sector 62 Noida."
- **Status:** PASS

#### Test Case 1.4: Cancel Processing Order
- **User Prompt:** "I want to cancel order 456."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `cancel_order(order_id=456)`
- **Synthesized Voice Response:** "Order #456 has been successfully cancelled. A full refund has been initiated to your original payment method."
- **Status:** PASS

#### Test Case 1.5: Report Damaged Item Replacement
- **User Prompt:** "My package for order 789 arrived with a broken crushed box."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `process_damaged_item(order_id=789, item_description="broken crushed box")`
- **Synthesized Voice Response:** "We're so sorry to hear that your item arrived damaged! A free replacement order has been dispatched with priority shipping."
- **Status:** PASS

#### Test Case 1.6: Urgent Human Manager Escalation
- **User Prompt:** "I need to speak to a manager about order 123."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Executed Tool:** `create_urgent_ticket(order_id=123, customer_issue="Manager escalation requested")`
- **Synthesized Voice Response:** "An urgent support ticket has been created for order #123. A human support manager will call you back within 1 hour."
- **Status:** PASS

---

### Suite 2: Policy and PDF Vector RAG (`policy_agent`)

#### Test Case 2.1: 30-Day Refund Policy
- **User Prompt:** "What is your return policy?"
- **Orchestrator Route:** `policy_agent` (`policy_agent_node`)
- **Vector DB Search Target:** `company_policy.pdf` in ChromaDB (`k=6`)
- **Synthesized Voice Response:** "We offer a 30-day money-back guarantee for all physical products and software licenses in original packaging with proof of purchase or Order ID."
- **Status:** PASS

#### Test Case 2.2: Operating Hours and Human Support Availability
- **User Prompt:** "What are your human support operating hours?"
- **Orchestrator Route:** `policy_agent` (`policy_agent_node`)
- **Vector DB Search Target:** `company_policy.pdf` in ChromaDB (`k=6`)
- **Synthesized Voice Response:** "Our human support team is available Monday through Friday from 9:00 AM to 5:00 PM EST. Nova AI voice assistant is available 24/7."
- **Status:** PASS

#### Test Case 2.3: Software Tier Upgrades
- **User Prompt:** "How much does it cost to upgrade software tiers?"
- **Orchestrator Route:** `policy_agent` (`policy_agent_node`)
- **Vector DB Search Target:** `company_policy.pdf` in ChromaDB (`k=6`)
- **Synthesized Voice Response:** "Premium Tier subscribers receive lifetime free upgrades to all major updates. Basic Tier users can upgrade for a flat fee of $15."
- **Status:** PASS

---

### Suite 3: CSAT Ratings and Feedback (`feedback_agent`)

#### Test Case 3.1: Provide Star Rating and Feedback
- **User Prompt:** "Thank you so much Nova, 5 stars!"
- **Orchestrator Route:** `feedback_agent` (`feedback_agent_node`)
- **Executed Tool:** `log_customer_feedback(rating=5, feedback_text="Thank you so much Nova, 5 stars!", order_id=123)`
- **Synthesized Voice Response:** "Thank you so much for your 5-star rating! We truly appreciate your feedback and hope you have a wonderful day."
- **Status:** PASS

---

### Suite 4: Multi-Turn Conversation Memory and Recall

#### Test Case 4.1: Implicit Order Memory Reference
- **Turn 1 (User):** "Check status for order 123."  
  **Nova Response:** "Order #123 has shipped..."
- **Turn 2 (User):** "Where is the truck?"  
  **Orchestrator Route:** `action_agent`  
  **Memory Recall:** Automatically resolves "the truck" to Order #123 via `chat_history`.  
  **Synthesized Voice Response:** "Your package is currently in transit with Blue Dart Express near Electronics City, Bengaluru."
- **Status:** PASS

#### Test Case 4.2: Direct Order ID Memory Recall
- **Turn 1 (User):** "My order number is 123."  
  **Nova Response:** "Order #123 has shipped."
- **Turn 2 (User):** "What was my order ID?"  
  **Orchestrator Route:** `action_agent`  
  **Memory Recall:** Reads `chat_history` buffer and directly states order ID number.  
  **Synthesized Voice Response:** "Your order ID is 123. It has shipped and is expected to arrive tomorrow by 4:00 PM."
- **Status:** PASS

---

### Suite 5: Business Rule Rejections and Edge Cases

#### Test Case 5.1: Address Update Rejection on Shipped Order
- **User Prompt:** "Change the address for order 123 to 500 Park Ave."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Tool Result:** Rejection (`status = 'Shipped'`).
- **Synthesized Voice Response:** "Unfortunately, we cannot update the shipping address for order #123 because it has already been shipped."
- **Status:** PASS

#### Test Case 5.2: Non-Existent Order Lookup
- **User Prompt:** "Check status for order 999."
- **Orchestrator Route:** `action_agent` (`action_agent_node`)
- **Tool Result:** Not found (`Order #999 was not found`).
- **Synthesized Voice Response:** "Order #999 was not found in our system. Please verify your order number and try again."
- **Status:** PASS

---

## 3. Summary Verification Checklist

| Test ID | Test Scenario | Target Node | Expected Outcome | Execution Result |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Order Status (#123) | `action_agent` | Shipped, Delivery Tomorrow 4PM | PASS |
| **1.2** | Live Courier Tracking (#123) | `action_agent` | Blue Dart Express, Bengaluru | PASS |
| **1.3** | Address Update (#456) | `action_agent` | Address Updated in MySQL | PASS |
| **1.4** | Cancel Order (#456) | `action_agent` | Order Cancelled in MySQL | PASS |
| **1.5** | Damaged Item (#789) | `action_agent` | Free Replacement Dispatched | PASS |
| **1.6** | Manager Escalation (#123) | `action_agent` | Ticket Created in MySQL | PASS |
| **2.1** | Return Policy Query | `policy_agent` | 30-Day Money-Back Policy | PASS |
| **2.2** | Human Support Hours | `policy_agent` | Mon-Fri 9am-5pm EST | PASS |
| **3.1** | CSAT Rating (5 Stars) | `feedback_agent` | Rating Logged to MySQL | PASS |
| **4.2** | Order ID Memory Recall | `action_agent` | "Your order ID is 123" | PASS |
| **5.1** | Address Change Rejection | `action_agent` | Rejected (Shipped status) | PASS |

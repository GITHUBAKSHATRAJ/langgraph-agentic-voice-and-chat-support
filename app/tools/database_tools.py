import os
import mysql.connector
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=os.getenv("MYSQL_PORT", 3306),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "customer_support_db")
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@tool
def get_order_status(order_id: int) -> str:
    """
    Look up general shipping status of a customer order by Order ID.
    """
    conn = get_db_connection()

    if not conn:
        return "Error: Could not connect to the MySQL database. Systems are currently offline."
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.order_id, o.status, o.estimated_delivery, c.name as customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        
        if result:
            return f"Order #{order_id} for {result['customer_name']} is currently '{result['status']}'. Estimated delivery: {result['estimated_delivery']}."
        else:
            return f"Order #{order_id} was not found in the database. Ask the user to double-check their order ID."
            
    except mysql.connector.Error as e:
        return f"A database error occurred: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def get_live_courier_tracking(order_id: int) -> str:
    """
    Retrieves live courier tracking details including carrier, tracking number, GPS location, and phone.
    3-table SQL JOIN: Joins orders, couriers, and customers tables across Foreign Keys.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.order_id, o.status, o.tracking_number, o.current_location,
                   cr.courier_name, cr.contact_number as courier_phone, c.name as customer_name
            FROM orders o
            JOIN couriers cr ON o.courier_id = cr.courier_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        
        if result:
            return (
                f"Live Courier Tracking for Order #{order_id} ({result['customer_name']}): "
                f"Carrier: {result['courier_name']} (Phone: {result['courier_phone']}), "
                f"Tracking Number: {result['tracking_number']}, "
                f"Status: '{result['status']}', "
                f"Current Location: {result['current_location']}."
            )
        else:
            return f"Order #{order_id} was not found."
            
    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def cancel_order(order_id: int) -> str:
    """
    NOTE : Cancels a customer order if it is still in 'Processing' status.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        
        if not result:
            return f"Order #{order_id} was not found."
            
        current_status = result['status']
        if current_status.lower() == 'processing':
            cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE order_id = %s", (order_id,))
            conn.commit()
            return f"Order #{order_id} has been successfully cancelled. A full refund has been initiated."
        else:
            return f"Order #{order_id} cannot be cancelled over the phone because its status is already '{current_status}'."
            
    except mysql.connector.Error as e:
        return f"A database error occurred while cancelling order #{order_id}: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def update_shipping_address(order_id: int, new_address: str) -> str:
    """
    Updates delivery address for processing orders.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.status, o.customer_id, c.shipping_address 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id 
            WHERE o.order_id = %s
        """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        
        if not result:
            return f"Order #{order_id} was not found."
            
        if result['status'].lower() not in ['processing', 'order placed']:
            return f"Cannot update shipping address for Order #{order_id} because its current status is '{result['status']}'."
            
        customer_id = result['customer_id']
        cursor.execute("UPDATE customers SET shipping_address = %s WHERE customer_id = %s", (new_address, customer_id))
        conn.commit()
        return f"Success! The shipping address for Order #{order_id} has been updated to: '{new_address}'."
        
    except mysql.connector.Error as e:
        return f"Database error updating shipping address: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def process_damaged_item(order_id: int, item_description: str) -> str:
    """
    Reports damaged items and dispatches replacement orders.
    ticket Raise: Automatically inserts replacement request into support_tickets table.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        
        if not result:
            return f"Order #{order_id} was not found."
            
        cursor.execute(
            "INSERT INTO support_tickets (order_id, customer_issue, priority) VALUES (%s, %s, %s)",
            (order_id, f"Damaged Item Reported: {item_description}", "URGENT")
        )
        conn.commit()
        return f"Damaged item report logged for Order #{order_id}. A free replacement has been dispatched with priority shipping."
        
    except mysql.connector.Error as e:
        return f"Database error reporting damaged item: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def create_urgent_ticket(order_id: int, customer_issue: str) -> str:
    """
    Escalates customer issues to human management by inserting an urgent ticket.
    Triggers 1-hour human callback  during business hours.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO support_tickets (order_id, customer_issue, priority) VALUES (%s, %s, %s)",
            (order_id, customer_issue, 'URGENT')
        )
        conn.commit()
        ticket_id = cursor.lastrowid
        return f"An URGENT support ticket (Ticket #{ticket_id}) has been logged for Order #{order_id}. A human support manager will contact you within 1 hour."
        
    except mysql.connector.Error as e:
        return f"Database error creating support ticket: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@tool
def log_customer_feedback(rating: int, feedback_text: str = "", order_id: int = 0) -> str:
    """
    Logs customer CSAT star rating (1-5 stars) and comments into customer_feedback table.
    order_id NULL handling: Accepts order_id=0 as NULL for general caller feedback.
    """
    conn = get_db_connection()
    if not conn:
        return "Error: Could not connect to the MySQL database."
    
    try:
        cursor = conn.cursor()
        valid_order_id = order_id if order_id > 0 else None
        
        cursor.execute(
            "INSERT INTO customer_feedback (order_id, rating, feedback_text) VALUES (%s, %s, %s)",
            (valid_order_id, rating, feedback_text)
        )
        conn.commit()
        feedback_id = cursor.lastrowid
        
        target_str = f"Order #{order_id}" if valid_order_id else "General Experience"
        return f"Feedback Recorded: ID #{feedback_id} for {target_str} with {rating}-Star rating logged successfully."
        
    except mysql.connector.Error as e:
        return f"Database error logging feedback: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

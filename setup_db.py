import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def setup_database():
   
    print("--- MySQL Database Setup ---")
    password = os.getenv("MYSQL_PASSWORD") 
    
    try:
        # Establish connection to MySQL server on localhost:3306
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password
        )
        cursor = conn.cursor()
        
        # Create Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS customer_support_db")
        print("[+] Database 'customer_support_db' created or already exists.")
        
        # Switch context to customer_support_db
        cursor.execute("USE customer_support_db")
        print("[+] Using customer_support_db.")
        
        # Disable foreign key checks for clean table recreation
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0") 
        cursor.execute("DROP TABLE IF EXISTS customer_feedback")
        cursor.execute("DROP TABLE IF EXISTS support_tickets")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS couriers")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1") 

        # 1. Create Customers Table 
        cursor.execute("""
            CREATE TABLE customers (
                customer_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                shipping_address VARCHAR(255) NOT NULL
            )
        """)
        print("[+] Table 'customers' created.")

        # 2. Create Couriers Table 
        cursor.execute("""
            CREATE TABLE couriers (
                courier_id INT PRIMARY KEY AUTO_INCREMENT,
                courier_name VARCHAR(50) NOT NULL,
                contact_number VARCHAR(20) NOT NULL
            )
        """)
        print("[+] Table 'couriers' created.")

        # 3. Create Orders Table 
        cursor.execute("""
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
            )
        """)
        print("[+] Table 'orders' created with Foreign Keys.")

        # 4. Create Support Tickets Table 
        cursor.execute("""
            CREATE TABLE support_tickets (
                ticket_id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL,
                customer_issue TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'URGENT',
                status VARCHAR(20) DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)
        print("[+] Table 'support_tickets' created with Foreign Keys.")

        # 5. Create Customer Feedback Table 
        cursor.execute("""
            CREATE TABLE customer_feedback (
                feedback_id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NULL,
                rating INT NOT NULL,
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
            )
        """)
        print("[+] Table 'customer_feedback' created with Foreign Keys.")

        # Customers
        cursor.executemany(
            "INSERT INTO customers (customer_id, name, email, phone, shipping_address) VALUES (%s, %s, %s, %s, %s)",
            [
                (1, 'Akshat Raj', 'akshat@example.com', '+91-98765-43210', 'Flat 402, Green Glen Layout, Bellandur, Bengaluru, Karnataka 560103'),
                (2, 'Sakshi Sharma', 'sakshi@example.com', '+91-98110-12345', 'B-12, Sector 62, Noida, Uttar Pradesh 201301'),
                (3, 'Rohan Verma', 'rohan@example.com', '+91-97234-56789', 'Plot 45, Jubilee Hills, Hyderabad, Telangana 500033')
            ]
        )

        # Couriers 
        cursor.executemany(
            "INSERT INTO couriers (courier_id, courier_name, contact_number) VALUES (%s, %s, %s)",
            [
                (1, 'Blue Dart Express', '1860-233-1234'),
                (2, 'Delhivery Logistics', '0124-6719500'),
                (3, 'DTDC Express', '080-25365032')
            ]
        )

        # Orders (Links customer_id & courier_id)
        cursor.executemany(
            """INSERT INTO orders 
               (order_id, customer_id, courier_id, status, estimated_delivery, tracking_number, current_location) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            [
                (123, 1, 1, 'Shipped', 'Tomorrow by 4:00 PM', 'BD-IN-992014-BLR', 'Sorting Facility - Electronics City, Bengaluru (5 km from destination)'),
                (456, 2, 2, 'Processing', 'Monday by 6:00 PM', 'DEL-IN-441029-DEL', 'Fulfillment Hub - Gurgaon Sector 18, Haryana (Preparing for dispatch)'),
                (789, 3, 3, 'Delivered', 'Yesterday at 2:30 PM', 'DTDC-IN-881203-HYD', 'Delivered at Security Gate - Jubilee Hills, Hyderabad')
            ]
        )

        conn.commit()
        print("[+] Successfully seeded relational data (Customers, Couriers, Orders).")

        
    except mysql.connector.Error as err:
        print(f"Error setting up database: {err}")
        print("Please check your password and ensure MySQL server is running on port 3306.")
    finally:
        if 'cursor' in locals() and cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if 'conn' in locals() and conn and conn.is_connected():
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    setup_database()

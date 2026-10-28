def main(conn):
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT 
                Orders.Order_id, Customer_id, Order_date, Status, Total_amount, Payment_method, Payment_status
            FROM Orders
            LEFT JOIN Payments
                ON Orders.Order_id = Payments.Order_id
            ORDER BY Order_date DESC
        """)
        rows = cursor.fetchall()
        if not rows:
            print("No Order found")
            return
        print("\n================ ORDER HISTORY ================")
        for r in rows:
            Order_id = r[0]
            Customer_id = r[1]
            Order_date = r[2]
            Status = r[3]
            Total_amount = r[4]
            Payment_method = r[5]
            Payment_status = r[6]
            
            print(f"Order ID: {Order_id} | Customer: {Customer_id}")
            print(f"Date: {Order_date} | Status: {Status}")
            print(f"Total: ₹{Total_amount} | Payment: {Payment_method} ({Payment_status})")
            print("=" * 45)

    finally:
        cursor.close()

if __name__ == "__main__":
    main()

        




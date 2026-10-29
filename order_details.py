import mysql.connector

def main(conn):
    cursor = conn.cursor()
    try:
        order_id = int(input("Enter Order ID: "))
        cursor.execute("""
                SELECT 
                    o.Order_id,c.Customer_name,o.Order_date,
                    o.Status, o.Total_amount,oi.food_id,
                    oi.Order_item_id,oi.Quantity,oi.Unit_price,
                    m.Food_name,p.Payment_method,p.Payment_status
                FROM Orders AS o
                    INNER JOIN Order_items AS oi 
                        ON oi.Order_id = o.Order_id
                    INNER JOIN MENU AS m 
                        ON m.food_id = oi.food_id
                    INNER JOIN Customers AS c 
                        ON c.customer_id = o.customer_id
                    LEFT JOIN Payments as p 
                        ON p.order_id = o.Order_id
                    WHERE o.Order_id = %s
                    """,(order_id,)
            )        
        order = cursor.fetchall()
        if not order:
            print("No order found with this ID.")
            return
        first = order[0]
        print("\n" + "=" * 65)
        print("                 ORDER DETAILS")
        print("=" * 65)
        print(f"Order ID      : {first[0]}")
        print(f"Customer Name : {first[1]}")
        print(f"Order Date    : {first[2]}")
        print(f"Order Status  : {first[3]}")
        print("-" * 65)
        print(f"{'Item':<25} {'Qty':>5} {'Unit Price':>13} {'Subtotal':>13}")
        print("-" * 65)
        
        for row in order:
            item_name = row[9]
            quantity = row[7]
            unit_price = row[8]
            subtotal = quantity * unit_price
            print(
                f"{item_name:<25} "
                f"{quantity:>5} "
                f"₹{unit_price:>11.2f} "
                f"₹{subtotal:>11.2f}"
            )

        print("-" * 65)
        payment_method = first[10] or "Not recorded"
        payment_status = first[11] or "Not recorded"
        print(f"{'Total Amount:':<43} ₹{first[4]:>11.2f}")
        print(f"Payment Method : {payment_method}")
        print(f"Payment Status : {payment_status}")
        print("=" * 65)
        print("\n")   

    except ValueError:
        print("Please Enter a valid order ID.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    
    finally:
        cursor.close()

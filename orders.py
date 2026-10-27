import os
import mysql.connector
from dotenv import load_dotenv
import customers

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def main():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        print("========== NEW ORDER ==========")
        customer_id = customers.main(conn) 
        if not customer_id:
            print("No valid customer selected.")
            return
        print(f"Creating Orders for Customer ID: {customer_id}")
        cursor.execute("SELECT * FROM MENU")
        menu = cursor.fetchall()
        menu_dict = {}
        for row in menu:
            food_id = row[0]
            menu_dict[food_id] = row
        order_items = {}
        
        while True:
            print("\n=====menu======")
            for row in menu:
                print(
                    f"ID: {row[0]} | {row[1]} | "
                    f"Price: ₹ {row[2]} | {row[3]} | {row[4]}"
                )
            try:
                user_inp = input("Enter a food_id(or 'done' to finish the order): ").strip().lower()
                if user_inp == "done":
                    break
                else:
                    food_id = int(user_inp)
            except ValueError:
                print("Write a Valid id")
                continue
            selected_item = menu_dict.get(food_id)
            if selected_item is None:
                print("Food id is invalid, Enter a new id")
                continue
            try:
                quant = int(input("Enter quantity:"))
                if quant<=0:
                    print("Quantity must be Greater than 0")
                    continue
            except ValueError:
                print("Enter a valid qauntity")
                continue
            if food_id in order_items:
                order_items[food_id]["quantity"]+=quant
            else:
                order_items[food_id] = {
                            "food_id": selected_item[0],
                            "name": selected_item[1],
                            "price": selected_item[2],
                            "quantity": quant
                }
            subtotal = selected_item[2]*quant
            print(f"{selected_item[1]} x {quant}")
            print(f"Subtotal: ₹{subtotal:.2f}")
            
            while True:
                any_else = input("Another order? Yes/no:").lower().strip()
                if any_else in ("yes", "y","no", "n"):
                    break
                print("Invalid input. Please enter yes or no.")
            if any_else in ("no", "n"):
                break

        if order_items:
            print("\n========== ORDER SUMMARY ==========")
            total = 0
            
            for item in order_items.values():
                subtotal = item["price"] * item["quantity"]
                total += subtotal
                print(
                f'{item["name"]} x {item["quantity"]} '
                f'= ₹{subtotal:.2f}'
                )
            print(f"Total amount: ₹{total:.2f}")
            while True:
                confirmation = input("Confirm Order Yes/No: ").strip().lower()
                if confirmation == "yes":
                    print("Order Confirmed")
                    break
                elif confirmation == "no":
                    print("Order Cancelled")
                    conn.rollback()
                    return
                else:
                    print("Enter A valid response")

            while True:
                payee = input("CASH/CARD/UPI: ").strip().lower()
                if payee in ["cash", "card", "upi"]:
                    print("Method Confirmed")
                    break
                else:
                    print("Invalid Payment method Choose CASH,CARD or UPI]")
            
            try:
                conn.commit()
                conn.start_transaction()
                cursor.execute("""INSERT INTO Orders(Customer_id,Status,Total_amount)
                               VALUES (%s, %s, %s)""", (customer_id, "Pending", total)
                            )
                order_id = cursor.lastrowid
                print(f"Order Created!, Order ID: {order_id}")
                
                items_data = [
                    (order_id, item["food_id"], item["quantity"], item["price"])
                    for item in order_items.values()
                        ]
                cursor.executemany(
                            """ INSERT INTO Order_items(Order_id, Food_id, Quantity, unit_price)
                                VALUES (%s, %s, %s, %s)""",
                                    items_data
                                )
                
                cursor.execute(
                    """INSERT INTO Payments(Order_id, Payment_method, Payment_status)
                        VALUES(%s, %s, %s)""",
                        (order_id,payee,"Pending")
                )
                conn.commit()
                print("Order and all items saved successfully!")
                print(f"Customer ID: {customer_id}")
                print(f"Order ID: {order_id}")
                print(f"Total amount: ₹{total:.2f}")
                
            
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"Database Error saving order {err}")
                return
            print("=================================")
            
            while True:
                pay_confirmation = input("Has the Payment be completed[Yes/No]: ").strip().lower()
                if pay_confirmation == "yes":
                    try:
                        cursor.execute("""
                                    UPDATE Payments
                                    SET Payment_status = %s
                                    WHERE Order_id = %s""",
                                    ("Paid",order_id)
                        )
                        conn.commit()
                        print("Payment status Updated to 'PAID'")
                    except mysql.connector.Error as err:
                        conn.rollback()
                        print(f"Could not update payment system as {err}")
                        print("Payment remains 'Pending'")
                    break
                elif pay_confirmation == "no":
                    print("Payment remains 'Pending'")
                    break
                else:
                    print("Invalid RESPONSE")
            print("\n========== RESTAURANT RECEIPT ==========")
            print(f"Order ID: {order_id}")
            print(f"Customer ID: {customer_id}")
            print("----------------------------------------")

            for item in order_items.values():
                subtotal = item["price"] * item["quantity"]
                print(
                f'{item["name"]} x {item["quantity"]} '
                f'= ₹{subtotal:.2f}'
            )

            print("----------------------------------------")
            print(f"Total: ₹{total:.2f}")
            print(f"Payment method: {payee.upper()}")

            cursor.execute("""
                SELECT Payment_status
                FROM Payments
                WHERE Order_id = %s
                """,
                (order_id,)
            )

            payment_result = cursor.fetchone()

            if payment_result:
                print(f"Payment status: {payment_result[0]}")

            print("========================================")
            print("Thank you for your order!")
        else:
            print("No items were added to the order.")
    
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()

if __name__ == "__main__":
    main()

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
                food_id = int(input("Enter a food_id: "))
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
            
            any_else = input("Another order Yes/no:").lower().strip()
            if any_else not in ("yes", "y"):
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
        else:
            print("No items were added to the order.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()

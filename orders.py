import os
import mysql.connector
from dotenv import load_dotenv
import customers

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

def main():
    print("========== NEW ORDER ==========")
    customer_id = customers.main(conn)
    print(f"Creating Orders for Customer ID: {customer_id}")
    order_items = []
    while True:
        cursor.execute("SELECT * FROM MENU")
        menu = cursor.fetchall()
        for row in menu:
            print(
                f"ID: {row[0]} | {row[1]} |"
                f"Price: $ {row[2]} | {row[3]} | {row[4]}"
                )
        try:
            food_id = int(input("Enter a food_id: "))
        except ValueError:
            print("Write a Valid id")
            continue
        selected_item = None

        for item in menu:
            if item[0] == food_id:
                selected_item = item
                break
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

        order_items.append({
            "food_id": selected_item[0],
            "name": selected_item[1],
            "price": selected_item[2],
            "quantity": quant
        })
        subtotal = selected_item[2]*quant
        print(f"{selected_item[1]} x {quant}")
        print(f"Subtotal: ${subtotal:.2f}")
        

        any_else = input("Another order Yes/no:").lower().strip()
        if any_else == "yes":
            continue 
        else:
            break
    if order_items:
        print("\n========== ORDER SUMMARY ==========")

        total = 0

        for item in order_items:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            
            print(
                f'{item["name"]} x {item["quantity"]} '
                f'= ₹{subtotal:.2f}'
            )
                
        print(f"Total amount: ₹{total:.2f}")

        print("=================================")
    else:
        print("No items were added to the order.")

main()
cursor.close()
conn.close()

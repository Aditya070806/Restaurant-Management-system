import mysql.connector
import csv
import os

def daily_sales(cursor):
    cursor.execute("""
                SELECT 
                    DATE(o.Order_date) AS DATE,
                    COUNT(o.Order_id) AS Total_Order,
                    SUM(o.Total_amount) AS Total,
                    AVG(o.Total_amount) AS Average
                FROM Orders AS o
                INNER JOIN Payments AS p
                    ON o.Order_id=p.Order_id
                WHERE p.Payment_status = 'Paid'
                GROUP BY DATE(Order_date)
                ORDER BY DATE(Order_date) DESC"""
        )
    row = cursor.fetchall()
    if not row:
        print("No sales data found")
        return
    print("\n" + "=" * 65)
    print("                      DAILY SALES REPORT")
    print("=" * 65)
    print(f"{'Date':<15} {'Total Orders':>14} {'Total Sales':>16} {'Average Order':>16}")
    print("-" * 65)
    for r in row:
        DATE = str(r[0])
        Total_Order = r[1]
        Total = r[2]
        Average = r[3]
        print(
            f"{DATE:<15} "
            f"{Total_Order:>14} "
            f"₹{Total:>14.2f} "
            f"₹{Average:>14.2f}"
        )
    print("=" * 65 + "\n")
    export_csv("daily_sales.csv",["DATE","Total_order","Total","Average"],row)

def top_selling_item(cursor):
    cursor.execute("""
                SELECT 
                    m.food_id,m.Food_name,
                    SUM(oi.quantity) AS Total_quantity,
                    SUM(oi.unit_price * oi.quantity) AS Total_revenue
                FROM Order_items AS oi
                INNER JOIN MENU AS m
                    ON m.food_id = oi.food_id
                INNER JOIN Payments AS p
                    ON oi.Order_id = p.Order_id
                WHERE p.Payment_status = 'Paid'
                GROUP BY m.food_id,m.Food_name
                ORDER BY Total_quantity DESC
                LIMIT 5"""
        )
    row = cursor.fetchall()
    if not row:
        print("No item sales found")
        return
    print("\n" + "=" * 65)
    print("                  TOP 5 BEST-SELLING ITEMS")
    print("=" * 65)
    print(f"{'ID':<6} {'Food Name':<25} {'Qty Sold':>12} {'Total Revenue':>18}")
    print("-" * 65)
    for r in row:
        food_id = r[0]
        Food_name = r[1]
        Total_quantity = r[2]
        Total_revenue = r[3]
        print(
            f"{food_id:<6} "
            f"{Food_name:<25} "
            f"{Total_quantity:>12} "
            f"₹{Total_revenue:>16.2f}"
        )
    print("=" * 65 + "\n")
    export_csv("top_selling_item.csv",["food_id","food_name","total_quantity","total_revenue"],row)

def top_customer(cursor):
    cursor.execute("""
                SELECT 
                    c.Customer_id,c.Customer_name,
                    COUNT(o.order_id) AS Total_order,
                    SUM(o.Total_amount) AS Total_spend
                FROM Customers AS c
                INNER JOIN Orders AS o
                ON c.Customer_id = o.Customer_id
                INNER JOIN Payments AS p
                    ON o.Order_id = p.Order_id
                WHERE p.Payment_status = 'Paid'
                GROUP BY c.Customer_id,c.Customer_name
                ORDER BY Total_spend DESC
                LIMIT 5"""
        )
    row = cursor.fetchall()
    if not row:
        print("No top customer found")
        return
    print("\n" + "=" * 65)
    print("                     TOP 5 VIP CUSTOMERS")
    print("=" * 65)
    print(f"{'ID':<6} {'Customer Name':<25} {'Total Orders':>14} {'Total Spend':>16}")
    print("-" * 65)
    for r in row:
        Customer_id = r[0]
        Customer_name = r[1]
        Total_order = r[2]
        Total_spend = r[3]
        print(
            f"{Customer_id:<6} "
            f"{Customer_name:<25} "
            f"{Total_order:>14} "
            f"₹{Total_spend:>14.2f}"
        )
    print("=" * 65 + "\n")
    export_csv("top_customer.csv",["Customer_id","Customer_name","Total_order","Total_spend"],row)

def export_csv(filename,header,rows):
    while True:
        choice = input("Export this report to CSV? (y/n): ").strip().lower()
        if choice =="y":
            os.makedirs("reports", exist_ok=True)
            filepath = os.path.join("reports",filename)
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header) 
                writer.writerows(rows)
                print(f"File exported to {filepath}")
                return
        elif choice == "n":
           break
        else:
            print("Enter a valid response")

def main(conn):
    cursor = conn.cursor()
    try:
        while True:
            print("\n========== ANALYTICS & REPORTS ==========")
            print("1. Daily Sales Report\n2. Top 5 Best-Selling Items\n3. Top 5 VIP Customers\n4. Back to Main Menu")
            try:
                opt = int(input("Enter a option: "))
                if opt == 1:
                    daily_sales(cursor)
                elif opt == 2:
                    top_selling_item(cursor)
                elif opt == 3:
                    top_customer(cursor)
                elif opt == 4:
                    break
                else:
                    print("Enter a given option")
            except ValueError:
                print("Enter a valid option")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()


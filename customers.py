import mysql.connector

def main(conn):
    cursor = conn.cursor()
    print(f"========== RESTAURANT SYSTEM ==========\n 1. Existing customer\n 2. Register new customer\n")
    while True:
        try:
            option = int(input("Choose an option: "))
            if option == 1:
                cust_id = int(input("Enter existing id:"))
                cursor.execute("SELECT * FROM Customers WHERE Customer_id = %s",(cust_id,))
                result = cursor.fetchone()
                if result:
                    print("Valid Id")
                    print(f"Customer Name:{result[1]}")
                    print(f"Phone No:{result[2]}")
                    cursor.close()
                    return result[0]
                else:
                    print("Enter a valid id")
            elif option == 2:
                cust_name = input("Enter your name:").strip()
                cust_phone = int(input("Enter your phone no:")).strip()
                if not cust_name:
                    print("Name cannot be empty.")
                    continue
                cursor.execute("INSERT INTO Customers (Customer_name, Phone_no) VALUES (%s, %s)",(cust_name, cust_phone))
                conn.commit()
                new_cust_id = cursor.lastrowid
                print(f"Registration successfull, Your new id is {new_cust_id}")
                cursor.close()
                return new_cust_id
                
            else:
                print("Enter a valid option")
        except ValueError:
            print("Error: Please enter a valid numerical value.")
    


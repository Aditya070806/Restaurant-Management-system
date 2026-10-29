import orders
import order_history
import order_details
import analytics

def main():
    while True:
        print("========== RESTAURANT MANAGEMENT SYSTEM ==========")
        print("1. Create a new order\n2. View order history\n3. View order details\n4. View business analytics\n5. Exit")
        try:
            opt = int(input("Choose an Option: "))
            if opt == 1:
                orders.main()
            elif opt == 2:
                try:
                    conn = orders.get_connection()
                    order_history.main(conn)
                finally:
                    conn.close()
            elif opt == 3:
                conn = orders.get_connection()
                try:
                    order_details.main(conn)
                finally:
                    conn.close()
            elif opt == 4:
                try:
                    conn = orders.get_connection()
                    analytics.main(conn)
                finally:
                    conn.close()
            elif opt == 5:
                break
            else:
                print("Invalid Choice")
        except ValueError:
            print("Use a option")
            continue

if __name__ == "__main__":
    main()


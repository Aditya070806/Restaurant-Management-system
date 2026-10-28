# 🍽️ Restaurant Management System

A modular, command-line Restaurant Management System built using **Python and MySQL**. The application supports customer management, menu-based order creation, payment-status tracking, and order-history retrieval.

This project demonstrates practical Python programming, relational database design, SQL joins, parameterized queries, database transactions, batch insertions, and environment-variable configuration.

**Project status:** Work in Progress

---

## ✨ Features

- **Customer Management:** Register new customers or select existing customers using their customer IDs.
- **Interactive Menu:** Retrieve menu items from MySQL and validate food IDs and quantities.
- **Order Cart:** Select multiple food items, combine repeated selections, and calculate subtotals and the final order total.
- **Order Confirmation:** Review an itemized order summary and confirm or cancel before saving the order.
- **Database Persistence:** Save orders, order items, and payment records to MySQL.
- **Payment Management:** Record Cash, Card, or UPI as the selected payment method and track pending or paid statuses through a simulated confirmation workflow.
- **Order History:** Retrieve saved orders and associated payment information using SQL `LEFT JOIN` queries, with the newest orders displayed first.
- **Order Receipts:** Display order details, itemized totals, payment methods, and saved payment statuses.
- **Modular Structure:** Separate customer management, order processing, and order-history functionality into individual Python modules.

> **Payment limitation:** This project does not currently integrate a real payment gateway. Payment completion is simulated through user confirmation and is not independently verified against an actual financial transaction.

---

## 📂 Project Structure

```text
restaurant-management-system/
├── app.py              # Main entry point and navigation menu
├── customers.py        # Customer selection and registration
├── orders.py           # Menu selection, order creation, payments and receipts
├── order_history.py    # Order and payment history viewer
├── restaurant.py       # Standalone menu viewer utility
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── .gitignore          # Files excluded from Git
└── README.md           # Project documentation
```

The `.env` and `.venv` files are created locally and should not be committed to GitHub.

---

## 🛠️ Built With

- **Python** — application logic and command-line interface
- **MySQL** — relational database management
- **mysql-connector-python** — MySQL connectivity from Python
- **python-dotenv** — loading database configuration from environment variables
- **DBeaver** — database exploration and SQL development

---

## 🗄️ Database Schema

The application uses five related tables:

| Table | Purpose |
|---|---|
| `MENU` | Stores available food items, prices, types, and courses |
| `Customers` | Stores customer information |
| `Orders` | Stores order details, dates, statuses, and totals |
| `Order_items` | Stores individual food items belonging to each order |
| `Payments` | Stores payment methods and payment statuses |

The following schema reflects the column structure used by the application.

### Create the database

```sql
CREATE DATABASE IF NOT EXISTS restaurants_db;
USE restaurants_db;
```

### 1. MENU

```sql
CREATE TABLE MENU (
    food_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(6,2) NOT NULL,
    type VARCHAR(10),
    course VARCHAR(50),
    PRIMARY KEY (food_id)
);
```

### 2. Customers

```sql
CREATE TABLE Customers (
    Customer_id INT NOT NULL AUTO_INCREMENT,
    Customer_name VARCHAR(50) NOT NULL,
    Phone_no VARCHAR(20),
    Email VARCHAR(100),
    Created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Customer_id)
);
```

### 3. Orders

```sql
CREATE TABLE Orders (
    Order_id INT NOT NULL AUTO_INCREMENT,
    Customer_id INT NOT NULL,
    Order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(50),
    Total_amount DECIMAL(8,2),
    PRIMARY KEY (Order_id),
    FOREIGN KEY (Customer_id)
        REFERENCES Customers(Customer_id)
);
```

### 4. Order_items

```sql
CREATE TABLE Order_items (
    Order_item_id INT NOT NULL AUTO_INCREMENT,
    Order_id INT NOT NULL,
    Food_id INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    unit_price DECIMAL(8,2) NOT NULL,
    PRIMARY KEY (Order_item_id),
    FOREIGN KEY (Order_id)
        REFERENCES Orders(Order_id),
    FOREIGN KEY (Food_id)
        REFERENCES MENU(food_id)
);
```

The `unit_price` column stores the price associated with an item when the order is placed. This helps preserve the historical order value if menu prices change later.

### 5. Payments

```sql
CREATE TABLE Payments (
    Payment_id INT NOT NULL AUTO_INCREMENT,
    Order_id INT NOT NULL,
    Payment_method VARCHAR(25) NOT NULL,
    Payment_status VARCHAR(20) NOT NULL,
    PRIMARY KEY (Payment_id),
    FOREIGN KEY (Order_id)
        REFERENCES Orders(Order_id)
);
```

### Sample menu data

The application expects menu items to exist before an order can be placed. The following records provide sample data for a new installation; adapt them to your preferred menu.

```sql
INSERT INTO MENU (name, price, type, course)
VALUES
    ('Paneer Tikka', 220.00, 'Veg', 'Starter'),
    ('Chicken Biryani', 280.00, 'Non-Veg', 'Main Course'),
    ('Chocolate Brownie', 120.00, 'Veg', 'Dessert'),
    ('Soft Drink', 60.00, 'Veg', 'Beverage');
```

If your database and tables already exist, **do not run the `CREATE TABLE` statements again**. Use this section as a reference for the expected schema.

---

## 🚀 Getting Started

### 1. Prerequisites

Install the following:

- Python
- MySQL Server
- Git

DBeaver is optional but useful for inspecting tables and running SQL queries.

### 2. Clone the repository

```bash
git clone https://github.com/Aditya070806/Restaurant-Management-system.git
cd Restaurant-Management-system
```

### 3. Create a virtual environment

On Ubuntu or another Linux distribution:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

Install the packages listed in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

The application requires:

- `mysql-connector-python`
- `python-dotenv`

If either package is missing from `requirements.txt`, install it with:

```bash
python -m pip install mysql-connector-python python-dotenv
```

### 5. Configure environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` and supply your local MySQL connection details:

```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=restaurants_db
```

Replace the example values with your own credentials.

**Security:** Never commit your actual `.env` file or database password to GitHub. Ensure `.env` is included in `.gitignore`.

### 6. Set up the database

Create the `restaurants_db` database and the required tables using the schema above, or use your existing database if it already matches the application's expected structure.

Add menu records before testing order creation.

### 7. Run the application

Start the main application from the project directory:

```bash
python app.py
```

The application menu provides options to create a new order, view order history, or exit.

### 8. Run Automated Tests

Run the unit test suite (uses `unittest.mock` to test edge cases without modifying your live database):
```bash
pytest -v
```
---

## 🖥️ Example Workflow

A typical order follows this sequence:

```text
========== RESTAURANT MANAGEMENT SYSTEM ==========

1. Create a new order
2. View order history
3. Exit

        ↓

Select or register a customer
        ↓
Choose menu items and quantities
        ↓
Review the order summary
        ↓
Confirm or cancel the order
        ↓
Select a payment method
        ↓
Save the order, items and pending payment
        ↓
Optionally simulate payment completion
        ↓
Display the final receipt
```

### Example receipt

The following output is illustrative. IDs, menu items, totals, and payment statuses depend on the data in your database.

```text
========== RESTAURANT RECEIPT ==========

Order ID: 12
Customer ID: 5
----------------------------------------
Paneer Tikka x 2       = ₹440.00
Chocolate Brownie x 1  = ₹120.00
----------------------------------------
Total: ₹560.00
Payment method: UPI
Payment status: Paid
========================================
Thank you for your order!
```

---

## 🔍 SQL Concepts Demonstrated

This project provides practical experience with:

- **Parameterized queries:** Passing values separately from SQL statements.
- **Joins:** Combining order and payment information using `LEFT JOIN`.
- **Aggregate calculations in Python:** Computing line subtotals and order totals.
- **Transactions:** Saving an order and its items together using `COMMIT` and `ROLLBACK`.
- **Batch insertions:** Using `cursor.executemany()` to insert multiple order items.
- **Foreign keys:** Connecting customers, orders, menu items, and payments through relational constraints.
- **Sorting:** Displaying the newest orders first using `ORDER BY ... DESC`.

---

## 🛣️ Future Improvements

Planned enhancements include:

- Detailed order lookup by order ID
- Order-status management
- More comprehensive input validation and error handling
- Sales summaries and revenue reports
- Popular-item and customer analytics
- Improved automated testing
- A graphical interface or web-based dashboard
- Integration with a verified payment gateway

---

## 📌 Project Status

This project is actively being developed as a learning project using Python and MySQL.

The current implementation supports customer selection and registration, order creation, database persistence, payment-status tracking through a simulated workflow, receipt generation, and order-history retrieval.

The long-term goal is to extend it into a more complete restaurant operations and analytics system.
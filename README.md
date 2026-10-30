# Restaurant Management System

A modular, command-line Restaurant Management System built with **Python and MySQL**. The application handles customer registration, order creation, payment status tracking, order history lookup, itemized receipt retrieval, and sales analytics with CSV export.

It covers practical Python development alongside relational database design, multi-table SQL joins (`INNER JOIN`, `LEFT JOIN`), SQL aggregations (`SUM`, `COUNT`, `AVG`, `GROUP BY`), database transactions (`COMMIT` / `ROLLBACK`), file I/O (`csv`), and unit testing (`pytest` + `unittest.mock`).

---

## Features

- **Customer Management (`customers.py`):** Register new customers or look up existing customers by ID before starting an order.
- **Interactive Menu & Cart (`orders.py`):** Load menu items from MySQL, validate food IDs and quantities, merge duplicate item selections in the cart, and calculate order totals.
- **Transactional Order Saving (`orders.py`):** Save orders, line items (`executemany`), and payment records inside a database transaction so incomplete orders roll back cleanly on error.
- **Payment Tracking (`orders.py`):** Record `Cash`, `Card`, or `UPI` payments and update statuses from `Pending` to `Paid` through a confirmation workflow.
- **Order History (`order_history.py`):** View past orders with customer details, order status, total amount, and payment status using `LEFT JOIN`, sorted newest first.
- **Order Details Lookup (`order_details.py`):** Look up any past order by `Order_id` to view its full itemized receipt, customer info, and payment status.
- **Analytics & CSV Export (`analytics.py`):** Generate reports for **Daily Sales**, **Top 5 Best-Selling Items**, and **Top 5 VIP Customers**. Queries filter for `Paid` orders so pending payments do not skew revenue figures, and any report can be exported to a `.csv` file in the `reports/` directory.
- **Automated Test Suite (`test_restaurant.py`):** 18 unit tests covering normal workflows, empty states, invalid inputs, database errors, and CSV export using `pytest` and `unittest.mock`.

> **Note on payments:** Payment completion is simulated through user confirmation in the terminal and does not connect to an external payment gateway.

---

## Project Structure

```text
restaurant-management-system/
├── app.py               # Main entry point and navigation menu
├── customers.py         # Customer lookup and registration
├── orders.py            # Menu display, cart logic, payments, and receipts
├── order_history.py     # Order and payment history viewer
├── order_details.py     # Itemized receipt lookup by Order ID
├── analytics.py         # Sales, item, and customer analytics with CSV export
├── restaurant.py        # Standalone menu viewer utility
├── test_restaurant.py   # Automated unit test suite (18 tests)
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variable configuration
├── .gitignore           # Ignored files and directories (.env, .venv, reports/)
└── README.md            # Project documentation
```

The `.env`, `.venv`, and generated `reports/` files are kept local and excluded from Git via `.gitignore`.

---

## Built With

- **Python** — CLI application logic, CSV file handling, and input validation
- **MySQL** — Relational database storage and aggregation queries
- **mysql-connector-python** — MySQL driver for Python
- **python-dotenv** — Environment variable management for database credentials
- **pytest & unittest.mock** — Unit testing without requiring a live database connection
- **DBeaver** — Database inspection and SQL query testing

---

## Database Schema

The application uses five related tables in the `restaurants_db` database:

| Table | Purpose |
|---|---|
| `MENU` | Food items, prices, types, and courses |
| `Customers` | Customer contact records |
| `Orders` | Order headers, timestamps, statuses, and total amounts |
| `Order_items` | Individual line items and historical unit prices for each order |
| `Payments` | Payment methods and payment statuses (`Pending` / `Paid`) |

### Create the database

```sql
CREATE DATABASE IF NOT EXISTS restaurants_db;
USE restaurants_db;
```

### 1. MENU

```sql
CREATE TABLE MENU (
    food_id INT NOT NULL AUTO_INCREMENT,
    Food_name VARCHAR(100) NOT NULL,
    Price DECIMAL(6,2) NOT NULL,
    Type VARCHAR(10),
    Category VARCHAR(50),
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
    food_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(8,2) NOT NULL,
    PRIMARY KEY (Order_item_id),
    FOREIGN KEY (Order_id)
        REFERENCES Orders(Order_id),
    FOREIGN KEY (food_id)
        REFERENCES MENU(food_id)
);
```

`unit_price` records the item's price at the moment the order was placed so historical receipts and revenue analytics remain accurate if menu prices change later.

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

Insert sample menu items before creating your first order:

```sql
INSERT INTO MENU (Food_name, Price, Type, Category)
VALUES
    ('Paneer Tikka', 220.00, 'Veg', 'Starter'),
    ('Chicken Biryani', 280.00, 'Non-Veg', 'Main Course'),
    ('Chocolate Brownie', 120.00, 'Veg', 'Dessert'),
    ('Soft Drink', 60.00, 'Veg', 'Beverage');
```

---

## Getting Started

### 1. Prerequisites

- Python 3
- MySQL Server
- Git

### 2. Clone the repository

```bash
git clone [https://github.com/Aditya070806/Restaurant-Management-system.git](https://github.com/Aditya070806/Restaurant-Management-system.git)
cd Restaurant-Management-system
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Or install the packages directly:

```bash
python -m pip install mysql-connector-python python-dotenv pytest
```

### 5. Configure environment variables

Copy the example file and add your MySQL credentials:

```bash
cp .env.example .env
```

Update `.env`:

```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=restaurants_db
```

### 6. Run the application

```bash
python3 app.py
```

### 7. Run automated tests

The test suite mocks the database connection and user input, so it runs without touching your live MySQL data:

```bash
pytest -v
```

---

## Example Workflow

```text
========== RESTAURANT MANAGEMENT SYSTEM ==========

1. Create a new order
2. View order history
3. View Order details
4. Analytics & Reports
5. Exit
```

- **Option 1 (Create a new order):** Select or register a customer $\rightarrow$ pick menu items and quantities $\rightarrow$ confirm order summary $\rightarrow$ choose payment method (`Cash`, `Card`, `UPI`) $\rightarrow$ confirm payment status $\rightarrow$ print receipt.
- **Option 2 (View order history):** Display a formatted table of all orders with customer names, dates, totals, and payment statuses.
- **Option 3 (View Order details):** Enter an `Order_id` to retrieve the itemized breakdown and payment details for that order.
- **Option 4 (Analytics & Reports):** View **Daily Sales**, **Top 5 Best-Selling Items**, or **Top 5 VIP Customers**, and optionally export the results to `reports/*.csv`.

---

## SQL & Python Concepts Used

- **Parameterized queries (`%s`):** Prevents SQL injection by passing values separately from SQL statements.
- **Multi-table joins:** Combines data across `Orders`, `Customers`, `Order_items`, `MENU`, and `Payments` using `INNER JOIN` and `LEFT JOIN`.
- **SQL aggregations:** Computes daily revenue, order counts, average order value, item quantities sold, and top customer spend using `COUNT()`, `SUM()`, `AVG()`, and `GROUP BY`.
- **Transactions:** Uses `conn.commit()` and `conn.rollback()` to keep order, item, and payment records consistent.
- **Batch insertions:** Uses `cursor.executemany()` to insert all items for an order in a single operation.
- **CSV export:** Uses Python's `csv` and `os` modules to write query results into the `reports/` folder.
- **Unit testing with mocks:** Uses `pytest`, `monkeypatch`, `capsys`, and `unittest.mock.MagicMock` to test CLI flows and edge cases.

---

## Future Improvements

- Menu management (add, update, or remove dishes from the CLI)
- Bulk menu import from CSV
- Date-range filtering for sales analytics
- Web dashboard or GUI interface
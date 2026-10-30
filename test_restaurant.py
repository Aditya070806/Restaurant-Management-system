import pytest
from unittest.mock import MagicMock
import mysql.connector

import app
import customers
import orders
import order_history
import order_details
import analytics


@pytest.fixture
def mock_db():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# --- customers.py ---

def test_existing_customer_flow(mock_db, monkeypatch):
    conn, cursor = mock_db
    cursor.fetchone.side_effect = [None, (1, "Aditya", "9876543210")]

    inputs = iter(["abc", "9", "1", "999", "1", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    cust_id = customers.main(conn)

    assert cust_id == 1
    assert cursor.execute.call_count == 2
    cursor.close.assert_called_once()


def test_new_customer_registration(mock_db, monkeypatch):
    conn, cursor = mock_db
    cursor.lastrowid = 42

    inputs = iter([
        "2", "   ", "9876543210",
        "2", "Aditya", "not_a_number",
        "2", "Aditya", "9876543210"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    new_id = customers.main(conn)

    assert new_id == 42
    conn.commit.assert_called_once()
    cursor.close.assert_called_once()


# --- order_history.py ---

def test_order_history_empty(mock_db, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = []

    order_history.main(conn)
    captured = capsys.readouterr()

    assert "No Order found" in captured.out
    cursor.close.assert_called_once()


def test_order_history_null_payment(mock_db, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (101, 1, "2026-10-29 12:00:00", "Pending", 500.00, None, None)
    ]

    order_history.main(conn)
    captured = capsys.readouterr()

    assert "Order ID: 101" in captured.out
    assert "Payment: None (None)" in captured.out
    cursor.close.assert_called_once()


# --- orders.py ---

def test_order_empty_cart(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (1, "Margherita Pizza", 250.0, "Veg", "Main Course")
    ]

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)
    monkeypatch.setattr("builtins.input", lambda _: "done")

    orders.main()
    captured = capsys.readouterr()

    assert "No items were added to the order." in captured.out
    conn.commit.assert_not_called()
    conn.close.assert_called_once()


def test_order_validation_and_item_merging(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (1, "Pizza", 200.0, "Veg", "Main"),
        (2, "Coffee", 100.0, "Veg", "Drink")
    ]
    cursor.lastrowid = 505
    cursor.fetchone.return_value = ("Paid",)

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter([
        "xyz", "999",
        "1", "-5",
        "1", "0",
        "1", "ten",
        "1", "2",
        "maybe", "yes",
        "1", "3",
        "no",
        "maybe", "yes",
        "bitcoin", "upi",
        "invalid", "yes"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "Pizza x 5 = ₹1000.00" in captured.out
    assert "Total amount: ₹1000.00" in captured.out
    assert "Payment status: Paid" in captured.out


def test_order_cancelled(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [(1, "Pizza", 200.0, "Veg", "Main")]

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter(["1", "2", "no", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "Order Cancelled" in captured.out
    conn.rollback.assert_called_once()
    cursor.executemany.assert_not_called()


def test_order_db_error_rollback(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [(1, "Pizza", 200.0, "Veg", "Main")]
    cursor.executemany.side_effect = mysql.connector.Error("Foreign Key Failure")

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter(["1", "1", "no", "yes", "cash"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "Database Error saving order" in captured.out
    conn.rollback.assert_called()
    conn.close.assert_called_once()


# --- app.py ---

def test_app_menu_inputs(monkeypatch, capsys):
    inputs = iter(["invalid", "99", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    app.main()
    captured = capsys.readouterr()

    assert "Use a option" in captured.out
    assert "Invalid Choice" in captured.out


# --- order_details.py ---

def test_order_details_valid(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (101, "Aditya", "2026-10-29 12:00:00", "Pending", 400.00,
         1, 1001, 2, 200.00, "Pizza", "UPI", "Paid")
    ]

    monkeypatch.setattr("builtins.input", lambda _: "101")

    order_details.main(conn)
    captured = capsys.readouterr()

    assert "ORDER DETAILS" in captured.out
    assert "101" in captured.out
    assert "Aditya" in captured.out
    assert "Pizza" in captured.out
    assert "UPI" in captured.out
    cursor.close.assert_called_once()


def test_order_details_not_found(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = []

    monkeypatch.setattr("builtins.input", lambda _: "999")

    order_details.main(conn)
    captured = capsys.readouterr()

    assert "No order found with this ID." in captured.out or "No record" in captured.out
    cursor.close.assert_called_once()


def test_order_details_invalid_id(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    monkeypatch.setattr("builtins.input", lambda _: "abc")

    order_details.main(conn)
    captured = capsys.readouterr()

    assert "Please Enter a valid order ID" in captured.out
    cursor.execute.assert_not_called()
    cursor.close.assert_called_once()


def test_order_details_db_error(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.execute.side_effect = mysql.connector.Error("DB failure")

    monkeypatch.setattr("builtins.input", lambda _: "101")

    order_details.main(conn)
    captured = capsys.readouterr()

    assert "DB failure" in captured.out
    cursor.close.assert_called_once()


# --- analytics.py ---

def test_analytics_reports(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.side_effect = [
        [("2026-10-29", 5, 1250.00, 250.00)],
        [(1, "Margherita Pizza", 10, 2500.00)],
        [(1, "Aditya", 5, 1250.00)]
    ]

    inputs = iter(["1", "2", "3", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    analytics.main(conn)
    captured = capsys.readouterr()

    assert "DAILY SALES REPORT" in captured.out
    assert "Margherita Pizza" in captured.out
    assert "Aditya" in captured.out
    assert cursor.execute.call_count == 3
    cursor.close.assert_called_once()


def test_analytics_empty(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.fetchall.return_value = []

    inputs = iter(["1", "2", "3", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    analytics.main(conn)
    captured = capsys.readouterr()

    assert "No sales data found" in captured.out
    assert "No item sales found" in captured.out
    assert "No top customer found" in captured.out
    cursor.close.assert_called_once()


def test_analytics_invalid_input(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    inputs = iter(["abc", "99", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    analytics.main(conn)
    captured = capsys.readouterr()

    assert "Enter a valid option" in captured.out
    assert "Enter a given option" in captured.out
    cursor.execute.assert_not_called()
    cursor.close.assert_called_once()


def test_analytics_db_error(mock_db, monkeypatch, capsys):
    conn, cursor = mock_db
    cursor.execute.side_effect = mysql.connector.Error("Connection lost")

    monkeypatch.setattr("builtins.input", lambda _: "1")

    analytics.main(conn)
    captured = capsys.readouterr()

    assert "Database Error: Connection lost" in captured.out
    cursor.close.assert_called_once()
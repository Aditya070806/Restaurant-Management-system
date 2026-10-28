import pytest
from unittest.mock import MagicMock, patch
import mysql.connector

import app
import customers
import orders
import order_history


# ==========================================
# FIXTURES: Mock Database & Cursor
# ==========================================
@pytest.fixture
def mock_db():
    """Creates a fake MySQL connection and cursor for safe testing."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ==========================================
# 1. CUSTOMERS.PY EXTREME CASES
# ==========================================
def test_existing_customer_invalid_inputs_then_valid(mock_db, monkeypatch):
    """Tests non-numeric menu option, non-existent ID, then valid ID."""
    conn, cursor = mock_db
    # First query returns None (ID 999 not found), second returns valid row
    cursor.fetchone.side_effect = [None, (1, "Aditya", "9876543210")]

    # Simulate user typing: "abc" (invalid option) -> "9" (out of range) ->
    # "1" (existing) -> "999" (not found) -> "1" (existing) -> "1" (valid ID)
    inputs = iter(["abc", "9", "1", "999", "1", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    cust_id = customers.main(conn)

    assert cust_id == 1
    assert cursor.execute.call_count == 2
    cursor.close.assert_called_once()


def test_register_customer_empty_name_and_bad_phone(mock_db, monkeypatch):
    """Tests empty whitespace name, non-numeric phone number, then valid registration."""
    conn, cursor = mock_db
    cursor.lastrowid = 42

    # Simulate user typing:
    # 1st attempt: Option "2" -> Name "   " (empty) -> Phone "9876543210" (rejected due to empty name)
    # 2nd attempt: Option "2" -> Name "Aditya" -> Phone "not_a_number" (raises ValueError)
    # 3rd attempt: Option "2" -> Name "Aditya" -> Phone "9876543210" (valid)
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


# ==========================================
# 2. ORDER_HISTORY.PY EXTREME CASES
# ==========================================
def test_order_history_empty_database(mock_db, capsys):
    """Tests when the database has 0 orders."""
    conn, cursor = mock_db
    cursor.fetchall.return_value = []

    order_history.main(conn)
    captured = capsys.readouterr()

    assert "No Order found" in captured.out
    cursor.close.assert_called_once()


def test_order_history_with_null_payments(mock_db, capsys):
    """Tests LEFT JOIN edge case where Payment_method and Payment_status are None."""
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (101, 1, "2026-10-29 12:00:00", "Pending", 500.00, None, None)
    ]

    order_history.main(conn)
    captured = capsys.readouterr()

    assert "Order ID: 101" in captured.out
    assert "Payment: None (None)" in captured.out
    cursor.close.assert_called_once()


# ==========================================
# 3. ORDERS.PY EXTREME & BOUNDARY CASES
# ==========================================
def test_order_immediate_done_empty_cart(mock_db, monkeypatch, capsys):
    """Tests user typing 'done' immediately without adding any items."""
    conn, cursor = mock_db
    cursor.fetchall.return_value = [
        (1, "Margherita Pizza", 250.0, "Veg", "Main Course")
    ]

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter(["done"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "No items were added to the order." in captured.out
    conn.commit.assert_not_called()
    conn.close.assert_called_once()


def test_order_extreme_input_validation_and_duplicate_merging(mock_db, monkeypatch, capsys):
    """
    Tests all extreme input edge cases in one flow:
    - Invalid text food_id ("xyz")
    - Non-existent food_id ("999")
    - Negative and zero quantities ("-5", "0")
    - Non-numeric quantity ("ten")
    - Duplicate item merging (ordering Food ID 1 twice: 2 + 3 = 5)
    - Invalid 'Another order?' input ("maybe")
    - Invalid payment method ("bitcoin")
    """
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
        "xyz",       # Invalid food_id (ValueError)
        "999",       # Non-existent food_id
        "1", "-5",   # Negative quantity
        "1", "0",    # Zero quantity
        "1", "ten",  # Non-numeric quantity (ValueError)
        "1", "2",    # Valid: Pizza x 2 (₹400)
        "maybe",     # Invalid 'Another order?' prompt
        "yes",       # Continue ordering
        "1", "3",    # Valid: Pizza x 3 more -> merges to 5 (total ₹1000)
        "no",        # Finish adding items
        "maybe",     # Invalid confirmation
        "yes",       # Confirm order
        "bitcoin",   # Invalid payment method
        "upi",       # Valid payment method
        "invalid",   # Invalid payment completion response
        "yes"        # Payment completed -> Paid
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    # Verify quantity merging (2 + 3 = 5 Pizzas @ ₹200 = ₹1000.00)
    assert "Pizza x 5 = ₹1000.00" in captured.out
    assert "Total amount: ₹1000.00" in captured.out
    assert "Payment status: Paid" in captured.out


def test_order_cancelled_by_user(mock_db, monkeypatch, capsys):
    """Tests that cancelling at confirmation rolls back and does NOT insert into DB."""
    conn, cursor = mock_db
    cursor.fetchall.return_value = [(1, "Pizza", 200.0, "Veg", "Main")]

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter([
        "1", "2",  # Pizza x 2
        "no",      # No more items
        "no"       # Confirm Order -> No (Cancel)
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "Order Cancelled" in captured.out
    conn.rollback.assert_called_once()
    cursor.executemany.assert_not_called()


def test_order_database_crash_triggers_rollback(mock_db, monkeypatch, capsys):
    """Tests that a MySQL error during order insertion safely rolls back the transaction."""
    conn, cursor = mock_db
    cursor.fetchall.return_value = [(1, "Pizza", 200.0, "Veg", "Main")]

    # Simulate a database crash when executemany is called
    cursor.executemany.side_effect = mysql.connector.Error("Simulated Foreign Key Failure")

    monkeypatch.setattr(orders, "get_connection", lambda: conn)
    monkeypatch.setattr(customers, "main", lambda c: 1)

    inputs = iter([
        "1", "1",  # Pizza x 1
        "no",      # Done ordering
        "yes",     # Confirm order
        "cash"     # Payment method
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orders.main()
    captured = capsys.readouterr()

    assert "Database Error saving order" in captured.out
    conn.rollback.assert_called()
    conn.close.assert_called_once()


# ==========================================
# 4. APP.PY EXTREME CASES
# ==========================================
def test_app_navigation_and_connection_failure(monkeypatch, capsys):
    """Tests invalid menu inputs in app.py and checks if Option 2 crashes when DB fails."""
    inputs = iter(["invalid", "99", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    app.main()
    captured = capsys.readouterr()

    assert "Use a option" in captured.out
    assert "Invalid Choice" in captured.out

    
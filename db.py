"""Database connection and queries with intentional brute-force unindexed scans."""
from __future__ import annotations

import pathlib
import sqlite3
from typing import Any

SCHEMA_PATH = pathlib.Path(__file__).parent / "schema.sql"


def get_connection(db_path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def seed_data(conn: sqlite3.Connection, num_customers: int = 1000, num_orders: int = 15000) -> None:
    """Populate database with synthetic customer and order records."""
    customers = [
        (
            f"Customer_{i}",
            f"user_{i}@example.com",
            "US" if i % 2 == 0 else "EU",
            "PREMIUM" if i % 5 == 0 else "STANDARD",
        )
        for i in range(1, num_customers + 1)
    ]
    conn.executemany(
        "INSERT INTO customers (name, email, country, tier) VALUES (?, ?, ?, ?)",
        customers,
    )

    orders = [
        (
            (i % num_customers) + 1,  # customer_id
            round(10.0 + (i % 500) * 1.5, 2),  # amount
            "COMPLETED" if i % 3 != 0 else "PENDING",  # status
            "2026-11-01T12:00:00Z",
        )
        for i in range(1, num_orders + 1)
    ]
    conn.executemany(
        "INSERT INTO orders (customer_id, amount, status, created_at) VALUES (?, ?, ?, ?)",
        orders,
    )
    conn.commit()


def query_orders_by_customer(conn: sqlite3.Connection, customer_id: int) -> list[dict[str, Any]]:
    """Query orders for a customer.
    
    INTENTIONAL BRUTE FORCE:
    Without an index on customer_id, SQLite performs a full table scan on orders.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, customer_id, amount, status FROM orders WHERE customer_id = ?",
        (customer_id,),
    )
    return [dict(row) for row in cursor.fetchall()]


def query_pending_orders_by_customer(conn: sqlite3.Connection, customer_id: int) -> list[dict[str, Any]]:
    """Query pending orders for a customer (another unindexed table scan)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, amount FROM orders WHERE customer_id = ? AND status = 'PENDING'",
        (customer_id,),
    )
    return [dict(row) for row in cursor.fetchall()]

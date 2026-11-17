"""Correctness test suite.

Cloud-Surgeon executes tests to ensure optimizations do not break functionality.
"""
import sqlite3
import pytest

from db import get_connection, init_db, query_orders_by_customer, seed_data
from service import (
    aggregate_tier_revenue,
    filter_allowed_transactions,
    process_customer_batch,
)


@pytest.fixture
def db_conn():
    conn = get_connection(":memory:")
    init_db(conn)
    seed_data(conn, num_customers=100, num_orders=500)
    yield conn
    conn.close()


def test_filter_allowed_transactions():
    tx_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    blacklisted = [2, 4, 6, 8]
    assert filter_allowed_transactions(tx_ids, blacklisted) == [1, 3, 5, 7, 9, 10]
    assert filter_allowed_transactions([], [1, 2]) == []
    assert filter_allowed_transactions([1, 2], []) == [1, 2]


def test_query_orders_by_customer(db_conn):
    orders = query_orders_by_customer(db_conn, customer_id=10)
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert all(o["customer_id"] == 10 for o in orders)


def test_process_customer_batch(db_conn):
    result = process_customer_batch(db_conn, target_customer_ids=[1, 2, 3, 4, 5])
    assert result["processed_customers"] == 5
    assert result["total_orders"] > 0
    assert result["total_revenue"] > 0


def test_aggregate_tier_revenue():
    orders = [
        {"customer_id": 1, "amount": 100.0},
        {"customer_id": 2, "amount": 50.0},
        {"customer_id": 3, "amount": 25.0},
    ]
    summary = aggregate_tier_revenue(orders, premium_customer_ids=[1, 3])
    assert summary["premium"] == 125.0
    assert summary["standard"] == 50.0

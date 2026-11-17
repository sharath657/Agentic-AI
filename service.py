"""E-Commerce business logic with intentional brute-force computational bottlenecks."""
from __future__ import annotations

import sqlite3
from typing import Any

from db import query_orders_by_customer


def filter_allowed_transactions(transaction_ids: list[int], blacklisted_ids: list[int]) -> list[int]:
    """Filter allowed transaction IDs.
    
    INTENTIONAL BRUTE FORCE:
    Linear list membership check inside loop (O(N * M)).
    Cloud-Surgeon detects this 'list-membership-in-loop' rule and converts blacklisted_ids to a set (O(1)).
    """
    allowed: list[int] = []
    for tid in transaction_ids:
        if tid not in blacklisted_ids:
            allowed.append(tid)
    return allowed


def process_customer_batch(conn: sqlite3.Connection, target_customer_ids: list[int]) -> dict[str, Any]:
    """Process a batch of customers by querying orders and calculating totals.
    
    INTENTIONAL BRUTE FORCE:
    Repeatedly queries unindexed SQLite orders table in a loop (O(C * O) full table scans).
    """
    total_revenue = 0.0
    processed_count = 0
    orders_by_customer: dict[int, list[dict[str, Any]]] = {}

    for cid in target_customer_ids:
        cust_orders = query_orders_by_customer(conn, cid)
        orders_by_customer[cid] = cust_orders
        for ord_info in cust_orders:
            total_revenue += ord_info["amount"]
            processed_count += 1

    return {
        "processed_customers": len(target_customer_ids),
        "total_orders": processed_count,
        "total_revenue": round(total_revenue, 2),
    }


def aggregate_tier_revenue(orders: list[dict[str, Any]], premium_customer_ids: list[int]) -> dict[str, float]:
    """Aggregate total revenue for premium vs standard customer tiers."""
    premium_total = 0.0
    standard_total = 0.0

    # Brute-force linear scan against premium_customer_ids list
    for ord_info in orders:
        if ord_info["customer_id"] in premium_customer_ids:
            premium_total += ord_info["amount"]
        else:
            standard_total += ord_info["amount"]

    return {
        "premium": round(premium_total, 2),
        "standard": round(standard_total, 2),
    }

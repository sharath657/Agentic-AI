"""Benchmark workload for measuring baseline vs optimized execution performance.

Cloud-Surgeon executes this script repeatedly across interleaved A/B benchmark runs
to calculate CPU time, latency, confidence intervals, and projected cloud savings.
"""
import time
from db import get_connection, init_db, seed_data
from service import filter_allowed_transactions, process_customer_batch


def run_workload():
    conn = get_connection(":memory:")
    init_db(conn)
    # Seed 1,000 customers and 20,000 orders
    seed_data(conn, num_customers=1000, num_orders=20000)

    # 1. Brute-force SQLite queries (unindexed full table scans over 20,000 rows repeated 350 times)
    targets = list(range(1, 351))
    batch_res = process_customer_batch(conn, targets)
    assert batch_res["total_orders"] > 0

    # 2. Brute-force Python O(N * M) list-membership checks
    transaction_pool = list(range(1, 6001))
    blacklist = list(range(3000, 9000))
    for _ in range(5):
        allowed = filter_allowed_transactions(transaction_pool, blacklist)
        assert len(allowed) == 2999

    conn.close()


if __name__ == "__main__":
    t0 = time.perf_counter()
    run_workload()
    elapsed = time.perf_counter() - t0
    print(f"Benchmark finished in {elapsed:.4f}s")

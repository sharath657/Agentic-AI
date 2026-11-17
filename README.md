# Brute-Force E-Commerce Data & Codebase

This repository contains intentional algorithmic and database query anti-patterns designed for autonomous performance discovery, benchmarking, and optimization by **Cloud-Surgeon**.

---

## What Makes This "Brute-Force" (High Latency & Cloud Cost)?

1. **Unindexed Database Scans (`schema.sql` & `db.py`)**:
   - The `orders` table contains 15,000+ records and lacks an index on `customer_id`.
   - Every lookup triggers SQLite's `SCAN TABLE orders` (Full Table Scan), inspecting 15,000 rows per query.
   - Batch lookups waste substantial CPU cycles and memory bandwidth.
   - **Target Optimization**: Cloud-Surgeon DB Agent detects `SCAN TABLE orders` via `EXPLAIN QUERY PLAN` and adds:
     ```sql
     CREATE INDEX idx_orders_customer_id ON orders(customer_id);
     ```

2. **$O(N \times M)$ List Scans in Python (`service.py`)**:
   - `filter_allowed_transactions()` performs `if tid not in blacklisted_ids:` where `blacklisted_ids` is a Python `list`.
   - For 5,000 items checked against 5,000 items, this requires up to 25,000,000 comparisons.
   - **Target Optimization**: Cloud-Surgeon Code Agent detects `list-membership-in-loop` and transforms the lookup to `set(blacklisted_ids)` ($O(1)$ amortized lookup).

---

## Running Tests & Benchmark Locally

### 1. Run Unit Tests (Correctness)
```bash
pytest -v
```

### 2. Run Benchmark (Performance Baseline)
```bash
python benchmark.py
```
*(Baseline execution typically takes ~1.5 - 3.0 seconds. After optimization, execution drops to ~0.03 seconds — a ~50x speedup).*

---

## How to Optimize with Cloud-Surgeon

### Option A: Local Fixture Optimization (Without GitHub)
If running Cloud-Surgeon locally with `ALLOW_LOCAL_FIXTURE_REPOS=true`:
1. In Cloud-Surgeon UI, choose **Local Fixture**.
2. Enter path: `D:\Brute Database`.
3. Click **Start Optimization**.

### Option B: GitHub Repository (With Automated Pull Request)
1. Create a new repository on your GitHub account (e.g. `brute-database-service`).
2. Push this folder to your repository:
   ```bash
   git remote add origin https://github.com/<your-username>/brute-database-service.git
   git branch -M main
   git push -u origin main
   ```
3. In Cloud-Surgeon UI, enter your repository URL: `https://github.com/<your-username>/brute-database-service`.
4. Cloud-Surgeon will discover the bottlenecks, run A/B benchmarks, show projected dollar savings, and open an automated Pull Request!

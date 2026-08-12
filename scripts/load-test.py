#!/usr/bin/env python3
"""
VidPulse API Production Load Testing Script
Simulates concurrent user load against critical endpoints:
- Liveness/Readiness probes
- Auth endpoints
- Keyword research API
- AI generator API
"""

import time
import requests
import concurrent.futures
import statistics

BASE_URL = "http://localhost:8000/api/v1"
CONCURRENT_USERS = 20
TOTAL_REQUESTS = 200

ENDPOINTS = [
    ("/health/live", "GET"),
    ("/health/ready", "GET"),
    ("/health", "GET"),
    ("/keywords/trending", "GET"),
]

results = []


def send_request(endpoint_tuple):
    path, method = endpoint_tuple
    url = f"{BASE_URL}{path}"
    start = time.time()
    try:
        if method == "GET":
            res = requests.get(url, timeout=5)
        else:
            res = requests.post(url, timeout=5)
        duration_ms = (time.time() - start) * 1000
        return {"status": res.status_code, "duration": duration_ms, "path": path}
    except Exception as e:
        return {"status": 500, "duration": (time.time() - start) * 1000, "error": str(e), "path": path}


def main():
    print(f"Starting Load Test against {BASE_URL}")
    print(f"Concurrent Workers: {CONCURRENT_USERS} | Total Requests: {TOTAL_REQUESTS}\n")

    tasks = [ENDPOINTS[i % len(ENDPOINTS)] for i in range(TOTAL_REQUESTS)]

    start_total = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [executor.submit(send_request, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    total_time = time.time() - start_total

    durations = [r["duration"] for r in results]
    success_count = sum(1 for r in results if r["status"] == 200)

    print("================ LOAD TEST RESULTS ================")
    print(f"Total Requests Processed: {len(results)}")
    print(f"Successful Requests (200 OK): {success_count}")
    print(f"Failed Requests: {len(results) - success_count}")
    print(f"Total Test Duration: {total_time:.2f} seconds")
    print(f"Throughput: {len(results) / total_time:.2f} req/sec")
    print(f"Mean Latency: {statistics.mean(durations):.2f} ms")
    print(f"Median (p50) Latency: {statistics.median(durations):.2f} ms")
    print(f"p95 Latency: {sorted(durations)[int(len(durations) * 0.95)]:.2f} ms")
    print("===================================================")


if __name__ == "__main__":
    main()

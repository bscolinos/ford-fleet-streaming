#!/usr/bin/env python3
"""
Ford Fleet Management Demo - Load Testing Harness

Simulates concurrent users hitting the API endpoints.
Scales from 1 to 100 to 200 to 500 users with latency tracking.
"""

import argparse
import asyncio
import json
import random
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import aiohttp

from scenarios import demo_users, select_scenario


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    scenario: str
    latency_ms: float
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None


@dataclass
class TestResults:
    """Aggregated test results."""
    concurrent_users: int
    duration_seconds: float
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    latencies: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    scenarios_run: dict = field(default_factory=dict)
    
    def add_metric(self, metric: RequestMetrics):
        self.total_requests += 1
        if metric.success:
            self.successful_requests += 1
            self.latencies.append(metric.latency_ms)
        else:
            self.failed_requests += 1
            if metric.error:
                self.errors.append(metric.error)
        
        self.scenarios_run[metric.scenario] = self.scenarios_run.get(metric.scenario, 0) + 1
    
    def get_percentile(self, p: float) -> float:
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * p / 100)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]
    
    def get_summary(self) -> dict:
        return {
            "concurrent_users": self.concurrent_users,
            "duration_seconds": self.duration_seconds,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate": self.failed_requests / max(self.total_requests, 1) * 100,
            "throughput_rps": self.total_requests / max(self.duration_seconds, 1),
            "latency_p50": self.get_percentile(50),
            "latency_p95": self.get_percentile(95),
            "latency_p99": self.get_percentile(99),
            "latency_avg": statistics.mean(self.latencies) if self.latencies else 0,
            "latency_min": min(self.latencies) if self.latencies else 0,
            "latency_max": max(self.latencies) if self.latencies else 0,
            "scenarios_run": self.scenarios_run,
        }


class LoadTestUser:
    """Simulates a single concurrent user."""
    
    def __init__(self, user_id: int, base_url: str, results: TestResults):
        self.user_id = user_id
        self.base_url = base_url
        self.results = results
        self.token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def login(self):
        """Authenticate and get JWT token."""
        creds = random.choice(demo_users)
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=creds,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.token = data["access_token"]
                    return True
                return False
        except Exception as e:
            print(f"User {self.user_id} login failed: {e}")
            return False
    
    async def run_scenario(self):
        """Run a randomly selected scenario."""
        if not self.token:
            return
        
        scenario_name, scenario_func = select_scenario()
        
        start_time = time.perf_counter()
        success = False
        error = None
        
        try:
            success = await scenario_func(self.session, self.base_url, self.token)
        except asyncio.TimeoutError:
            error = "timeout"
        except Exception as e:
            error = str(e)[:100]
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        metric = RequestMetrics(
            scenario=scenario_name,
            latency_ms=latency_ms,
            success=success,
            error=error
        )
        
        self.results.add_metric(metric)
    
    async def run(self, duration: float, think_time: tuple[float, float] = (0.5, 2.0)):
        """Run user simulation for specified duration."""
        connector = aiohttp.TCPConnector(limit=10, force_close=True)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            
            if not await self.login():
                return
            
            end_time = time.time() + duration
            
            while time.time() < end_time:
                await self.run_scenario()
                
                # Random think time between requests
                await asyncio.sleep(random.uniform(*think_time))


class LoadTestHarness:
    """Main load testing harness."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    async def run_test(
        self,
        concurrent_users: int,
        duration_seconds: float,
        ramp_up_seconds: float = 10.0
    ) -> TestResults:
        """Run a load test with specified parameters."""
        
        print(f"\n{'='*60}")
        print(f"Load Test: {concurrent_users} users for {duration_seconds}s")
        print(f"Ramp-up: {ramp_up_seconds}s")
        print(f"Target: {self.base_url}")
        print(f"{'='*60}\n")
        
        results = TestResults(
            concurrent_users=concurrent_users,
            duration_seconds=duration_seconds
        )
        
        # Calculate ramp-up delay per user
        ramp_delay = ramp_up_seconds / concurrent_users if concurrent_users > 1 else 0
        
        # Create and start users
        tasks = []
        for i in range(concurrent_users):
            user = LoadTestUser(i, self.base_url, results)
            
            # Stagger user starts
            async def run_with_delay(u, delay):
                await asyncio.sleep(delay)
                await u.run(duration_seconds)
            
            task = asyncio.create_task(run_with_delay(user, i * ramp_delay))
            tasks.append(task)
            
            if (i + 1) % 50 == 0:
                print(f"Started {i + 1}/{concurrent_users} users...")
        
        print(f"All {concurrent_users} users started. Running for {duration_seconds}s...\n")
        
        # Wait for all users to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def print_results(self, results: TestResults):
        """Print formatted test results."""
        summary = results.get_summary()
        
        print(f"\n{'='*60}")
        print("LOAD TEST RESULTS")
        print(f"{'='*60}")
        print(f"Concurrent Users: {summary['concurrent_users']}")
        print(f"Duration: {summary['duration_seconds']:.1f}s")
        print(f"{'='*60}")
        print(f"Total Requests: {summary['total_requests']:,}")
        print(f"Successful: {summary['successful_requests']:,}")
        print(f"Failed: {summary['failed_requests']:,}")
        print(f"Error Rate: {summary['error_rate']:.2f}%")
        print(f"Throughput: {summary['throughput_rps']:.1f} req/s")
        print(f"{'='*60}")
        print("LATENCY (ms)")
        print(f"  p50: {summary['latency_p50']:.1f}")
        print(f"  p95: {summary['latency_p95']:.1f}")
        print(f"  p99: {summary['latency_p99']:.1f}")
        print(f"  avg: {summary['latency_avg']:.1f}")
        print(f"  min: {summary['latency_min']:.1f}")
        print(f"  max: {summary['latency_max']:.1f}")
        print(f"{'='*60}")
        print("SCENARIOS")
        for scenario, count in sorted(summary['scenarios_run'].items()):
            print(f"  {scenario}: {count:,}")
        print(f"{'='*60}\n")
        
        return summary


async def main():
    parser = argparse.ArgumentParser(description="Ford Fleet Demo Load Test")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Base URL of the API"
    )
    parser.add_argument(
        "--users", 
        type=int, 
        default=10,
        help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", 
        type=int, 
        default=60,
        help="Test duration in seconds"
    )
    parser.add_argument(
        "--ramp-up", 
        type=float, 
        default=10.0,
        help="Ramp-up time in seconds"
    )
    parser.add_argument(
        "--scale-test",
        action="store_true",
        help="Run scaling test: 1, 100, 200, 500 users"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for JSON results"
    )
    
    args = parser.parse_args()
    
    harness = LoadTestHarness(args.url)
    all_results = []
    
    if args.scale_test:
        # Run scaling test
        user_counts = [1, 100, 200, 500]
        print("\n" + "="*60)
        print("SCALING TEST")
        print("="*60)
        print(f"Will test with: {user_counts} users")
        print("Each test runs for 60 seconds")
        print("="*60 + "\n")
        
        for users in user_counts:
            results = await harness.run_test(
                concurrent_users=users,
                duration_seconds=60,
                ramp_up_seconds=min(users / 10, 30)
            )
            summary = harness.print_results(results)
            all_results.append(summary)
            
            if users < user_counts[-1]:
                print("Waiting 10 seconds before next test...\n")
                await asyncio.sleep(10)
        
        # Print comparison
        print("\n" + "="*60)
        print("SCALING COMPARISON")
        print("="*60)
        print(f"{'Users':>8} | {'RPS':>10} | {'p50':>8} | {'p95':>8} | {'p99':>8} | {'Errors':>8}")
        print("-"*60)
        for r in all_results:
            print(f"{r['concurrent_users']:>8} | {r['throughput_rps']:>10.1f} | "
                  f"{r['latency_p50']:>8.1f} | {r['latency_p95']:>8.1f} | "
                  f"{r['latency_p99']:>8.1f} | {r['error_rate']:>7.2f}%")
        print("="*60 + "\n")
        
        print("\nNotes for production scaling (1000-3000 users):")
        print("- Ensure database connection pooling is properly configured")
        print("- Consider horizontal scaling of API servers")
        print("- Monitor SingleStore query latencies")
        print("- Use connection pooling in the backend")
        print("- Consider read replicas for heavy read workloads")
        
    else:
        # Single test
        results = await harness.run_test(
            concurrent_users=args.users,
            duration_seconds=args.duration,
            ramp_up_seconds=args.ramp_up
        )
        summary = harness.print_results(results)
        all_results.append(summary)
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())


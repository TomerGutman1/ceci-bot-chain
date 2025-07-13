#!/usr/bin/env python3
"""
Performance and load testing suite for context handling improvements.
Tests cache efficiency, memory usage, and concurrent session handling.
"""

import requests
import json
import time
import uuid
import threading
import psutil
import os
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import statistics

# Configuration
BACKEND_URL = "http://localhost:5001"
CHAT_API = f"{BACKEND_URL}/api/chat"
STATS_API = f"{BACKEND_URL}/api/statistics"

class PerformanceTester:
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {
            "response_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "memory_usage": [],
            "concurrent_errors": 0
        }
        self.lock = threading.Lock()
    
    def make_query(self, message: str, session_id: str) -> Tuple[Dict[str, Any], float]:
        """Make a query and return result with timing."""
        payload = {
            "message": message,
            "sessionId": session_id,
            "includeMetadata": True
        }
        
        start_time = time.time()
        try:
            response = requests.post(CHAT_API, json=payload, timeout=30)
            response.raise_for_status()
            elapsed = time.time() - start_time
            
            with self.lock:
                self.performance_metrics["response_times"].append(elapsed)
            
            return response.json(), elapsed
        except Exception as e:
            with self.lock:
                self.performance_metrics["concurrent_errors"] += 1
            return {"success": False, "error": str(e)}, time.time() - start_time
    
    def log_result(self, test_name: str, passed: bool, details: str):
        """Log test results."""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{'✅' if passed else '❌'} {test_name}: {details}")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage of the backend process."""
        try:
            # This is a simplified approach - in production you'd monitor the actual container
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    def test_cache_performance(self):
        """Test cache hit rates and performance improvement."""
        print("\n=== Testing Cache Performance ===")
        session_id = f"cache_perf_{uuid.uuid4()}"
        
        # Cacheable queries (no specific entities)
        cacheable_queries = [
            "החלטות אחרונות",
            "מהן ההחלטות החשובות?",
            "החלטות בנושא כללי"
        ]
        
        # Non-cacheable queries (with specific entities)
        non_cacheable = [
            "החלטה 1234",
            "תן לי את זה",
            "ההחלטה הראשונה"
        ]
        
        print("\nTesting cacheable queries...")
        for query in cacheable_queries:
            # First query (cache miss)
            result1, time1 = self.make_query(query, session_id)
            time.sleep(0.1)
            
            # Second query (should be cache hit)
            result2, time2 = self.make_query(query, session_id)
            
            if result1.get('success') and result2.get('success'):
                # Cache hit should be significantly faster
                speedup = time1 / time2 if time2 > 0 else 0
                
                if speedup > 2:  # At least 2x faster
                    self.performance_metrics["cache_hits"] += 1
                    self.log_result(f"Cache Performance - '{query[:30]}...'", True, 
                                  f"Cache hit! Speedup: {speedup:.1f}x")
                else:
                    self.performance_metrics["cache_misses"] += 1
                    self.log_result(f"Cache Performance - '{query[:30]}...'", False, 
                                  f"No speedup detected: {speedup:.1f}x")
        
        print("\nTesting non-cacheable queries...")
        for query in non_cacheable:
            result1, time1 = self.make_query(query, session_id)
            time.sleep(0.1)
            result2, time2 = self.make_query(query, session_id)
            
            if result1.get('success') and result2.get('success'):
                # Should NOT be cached
                speedup = time1 / time2 if time2 > 0 else 0
                
                if speedup < 1.5:  # Similar times = no cache
                    self.log_result(f"Cache Bypass - '{query[:30]}...'", True, 
                                  f"Correctly bypassed cache")
                else:
                    self.log_result(f"Cache Bypass - '{query[:30]}...'", False, 
                                  f"Unexpectedly cached: {speedup:.1f}x speedup")
    
    def test_concurrent_sessions(self):
        """Test handling of multiple concurrent sessions."""
        print("\n=== Testing Concurrent Sessions ===")
        
        num_sessions = 20
        queries_per_session = 5
        
        def session_workload(session_num: int) -> Dict[str, Any]:
            session_id = f"concurrent_{session_num}_{uuid.uuid4()}"
            decision_num = 1000 + session_num
            
            results = []
            for i in range(queries_per_session):
                if i == 0:
                    query = f"החלטה {decision_num}"
                elif i == 1:
                    query = "תן לי את התוכן המלא"
                elif i == 2:
                    query = "מה הסעיפים?"
                elif i == 3:
                    query = "יש תקציב?"
                else:
                    query = "נתח את ההחלטה"
                
                result, elapsed = self.make_query(query, session_id)
                results.append({
                    "query": query,
                    "success": result.get('success', False),
                    "time": elapsed,
                    "has_correct_decision": str(decision_num) in str(result.get('response', ''))
                })
                
                time.sleep(0.1)
            
            return {
                "session": session_num,
                "decision": decision_num,
                "results": results
            }
        
        print(f"Running {num_sessions} concurrent sessions...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(num_sessions):
                future = executor.submit(session_workload, i)
                futures.append(future)
            
            completed = 0
            correct_isolation = 0
            
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                
                # Check if session maintained correct decision context
                correct_refs = sum(1 for r in result['results'] 
                                 if r['has_correct_decision'] or not r['success'])
                
                if correct_refs == len(result['results']):
                    correct_isolation += 1
                
                print(f"  Completed {completed}/{num_sessions} sessions", end='\r')
        
        total_time = time.time() - start_time
        
        self.log_result("Concurrent Sessions", 
                       correct_isolation == num_sessions,
                       f"{correct_isolation}/{num_sessions} sessions maintained isolation. "
                       f"Total time: {total_time:.1f}s")
        
        # Check error rate
        error_rate = self.performance_metrics["concurrent_errors"] / (num_sessions * queries_per_session)
        self.log_result("Concurrent Error Rate", 
                       error_rate < 0.05,  # Less than 5% errors
                       f"Error rate: {error_rate:.1%}")
    
    def test_memory_usage(self):
        """Test memory usage with many active sessions."""
        print("\n=== Testing Memory Usage ===")
        
        initial_memory = self.get_memory_usage()
        print(f"Initial memory: {initial_memory:.1f} MB")
        
        # Create many sessions with stored entities
        num_sessions = 100
        sessions = []
        
        print(f"Creating {num_sessions} sessions...")
        for i in range(num_sessions):
            session_id = f"memory_test_{i}_{uuid.uuid4()}"
            sessions.append(session_id)
            
            # Each session makes queries that store entities
            self.make_query(f"החלטה {1000 + i} של ממשלה {30 + i % 10}", session_id)
            
            if i % 10 == 0:
                current_memory = self.get_memory_usage()
                self.performance_metrics["memory_usage"].append(current_memory)
                print(f"  Sessions: {i+1}, Memory: {current_memory:.1f} MB", end='\r')
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        memory_per_session = memory_increase / num_sessions if num_sessions > 0 else 0
        
        print(f"\nFinal memory: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        print(f"Memory per session: {memory_per_session:.3f} MB")
        
        # Less than 1MB per 100 sessions is good
        self.log_result("Memory Usage", 
                       memory_per_session < 0.01,
                       f"{memory_per_session:.3f} MB per session")
    
    def test_response_time_distribution(self):
        """Test response time consistency across query types."""
        print("\n=== Testing Response Time Distribution ===")
        
        query_types = [
            ("simple", ["החלטה 1234", "החלטה 5678", "החלטה 9999"]),
            ("search", ["החלטות חינוך", "החלטות בריאות", "החלטות תחבורה"]),
            ("context", ["תן לי את זה", "ספר לי עוד", "מה היה שם?"]),
            ("analysis", ["נתח את החלטה 1000", "נתח את החלטה 2000", "נתח את החלטה 3000"])
        ]
        
        results_by_type = {}
        
        for query_type, queries in query_types:
            print(f"\nTesting {query_type} queries...")
            times = []
            
            for query in queries:
                session_id = f"timing_{query_type}_{uuid.uuid4()}"
                
                # Warm-up for context queries
                if query_type == "context":
                    self.make_query("החלטה 1234", session_id)
                    time.sleep(0.5)
                
                result, elapsed = self.make_query(query, session_id)
                
                if result.get('success'):
                    times.append(elapsed)
                    print(f"  {query[:30]}... : {elapsed:.2f}s")
                
                time.sleep(0.5)
            
            if times:
                results_by_type[query_type] = {
                    "mean": statistics.mean(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                    "p95": sorted(times)[int(len(times) * 0.95)] if times else 0,
                    "max": max(times)
                }
        
        # Log results
        print("\nResponse Time Summary:")
        for query_type, stats in results_by_type.items():
            print(f"{query_type}:")
            print(f"  Mean: {stats['mean']:.2f}s")
            print(f"  StDev: {stats['stdev']:.2f}s")
            print(f"  P95: {stats['p95']:.2f}s")
            print(f"  Max: {stats['max']:.2f}s")
            
            # Check if times are reasonable
            expected_max = {
                "simple": 5.0,
                "search": 8.0,
                "context": 6.0,
                "analysis": 20.0
            }
            
            self.log_result(f"Response Time - {query_type}", 
                           stats['p95'] <= expected_max.get(query_type, 10.0),
                           f"P95: {stats['p95']:.2f}s (expected <{expected_max.get(query_type, 10.0)}s)")
    
    def test_cache_invalidation_performance(self):
        """Test performance impact of cache invalidation."""
        print("\n=== Testing Cache Invalidation Performance ===")
        
        session_id = f"invalidation_perf_{uuid.uuid4()}"
        
        # Step 1: Warm cache with general query
        print("Warming cache...")
        self.make_query("החלטות בנושא חינוך", session_id)
        time.sleep(0.5)
        
        # Step 2: Measure cached response time
        _, cached_time = self.make_query("החלטות בנושא חינוך", session_id)
        print(f"Cached response time: {cached_time:.2f}s")
        
        # Step 3: Trigger cache invalidation
        print("Triggering cache invalidation...")
        self.make_query("החלטה 2989 בנושא חינוך", session_id)
        time.sleep(0.5)
        
        # Step 4: Measure post-invalidation time
        _, invalidated_time = self.make_query("החלטות בנושא חינוך", session_id)
        print(f"Post-invalidation time: {invalidated_time:.2f}s")
        
        # Invalidated query should be slower (no cache)
        if invalidated_time > cached_time * 1.5:
            self.log_result("Cache Invalidation Performance", True, 
                          f"Cache properly invalidated. Time increased from {cached_time:.2f}s to {invalidated_time:.2f}s")
        else:
            self.log_result("Cache Invalidation Performance", False, 
                          f"Cache may not be invalidated. Times too similar: {cached_time:.2f}s vs {invalidated_time:.2f}s")
    
    def test_stress_test(self):
        """Stress test with high load."""
        print("\n=== Running Stress Test ===")
        
        duration = 30  # seconds
        print(f"Running stress test for {duration} seconds...")
        
        start_time = time.time()
        queries_sent = 0
        successes = 0
        
        def stress_worker():
            nonlocal queries_sent, successes
            while time.time() - start_time < duration:
                session_id = f"stress_{uuid.uuid4()}"
                query = f"החלטה {1000 + queries_sent % 1000}"
                
                result, _ = self.make_query(query, session_id)
                
                with self.lock:
                    queries_sent += 1
                    if result.get('success'):
                        successes += 1
                
                time.sleep(0.1)  # 10 queries/second per thread
        
        # Run with multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(stress_worker) for _ in range(5)]
            
            # Monitor progress
            while time.time() - start_time < duration:
                print(f"  Queries: {queries_sent}, Success rate: {successes/queries_sent*100:.1f}%", end='\r')
                time.sleep(1)
            
            # Wait for completion
            for future in futures:
                future.result()
        
        total_time = time.time() - start_time
        qps = queries_sent / total_time
        success_rate = successes / queries_sent if queries_sent > 0 else 0
        
        print(f"\nStress test complete:")
        print(f"  Total queries: {queries_sent}")
        print(f"  Queries per second: {qps:.1f}")
        print(f"  Success rate: {success_rate:.1%}")
        
        self.log_result("Stress Test", 
                       success_rate > 0.95 and qps > 20,
                       f"QPS: {qps:.1f}, Success rate: {success_rate:.1%}")
    
    def run_all_tests(self):
        """Run all performance tests."""
        print("Starting Performance Test Suite")
        print("=" * 50)
        
        self.test_cache_performance()
        self.test_concurrent_sessions()
        self.test_memory_usage()
        self.test_response_time_distribution()
        self.test_cache_invalidation_performance()
        self.test_stress_test()
        
        # Summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Performance metrics summary
        if self.performance_metrics["response_times"]:
            times = self.performance_metrics["response_times"]
            print(f"\nResponse Time Statistics:")
            print(f"  Total requests: {len(times)}")
            print(f"  Mean: {statistics.mean(times):.2f}s")
            print(f"  Median: {statistics.median(times):.2f}s")
            print(f"  P95: {sorted(times)[int(len(times) * 0.95)]:.2f}s")
            print(f"  Max: {max(times):.2f}s")
        
        print(f"\nCache Performance:")
        total_cache_requests = self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
        if total_cache_requests > 0:
            hit_rate = self.performance_metrics["cache_hits"] / total_cache_requests
            print(f"  Hit rate: {hit_rate:.1%}")
        
        # Failed tests
        failed = [r for r in self.test_results if not r['passed']]
        if failed:
            print("\nFailed Tests:")
            for r in failed:
                print(f"  - {r['test']}: {r['details']}")

if __name__ == "__main__":
    # Check if backend is accessible
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Backend is not healthy!")
            exit(1)
    except:
        print("❌ Cannot connect to backend at http://localhost:5001")
        print("Please ensure all services are running with: docker compose up")
        exit(1)
    
    tester = PerformanceTester()
    tester.run_all_tests()
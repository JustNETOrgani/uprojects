#!/usr/bin/env python3
"""
Load Testing Script for Anti-Counterfeit System
Tests system performance under various load conditions
"""

import time
import requests
import json
import statistics
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import argparse

class LoadTester:
    def __init__(self, base_url: str = "http://localhost:8000", bearer_token: str = None):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}" if bearer_token else None
        }
        self.results = {
            "response_times": [],
            "error_count": 0,
            "success_count": 0,
            "status_codes": {},
            "errors": []
        }

    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[Dict, float, str]:
        """Make a single HTTP request and measure response time"""
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Record status code
            status_code = response.status_code
            self.results["status_codes"][status_code] = self.results["status_codes"].get(status_code, 0) + 1
            
            if response.status_code == 200:
                self.results["success_count"] += 1
                self.results["response_times"].append(duration)
                return response.json(), duration, None
            else:
                self.results["error_count"] += 1
                error_msg = f"HTTP {status_code}: {response.text}"
                self.results["errors"].append(error_msg)
                return None, duration, error_msg
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            self.results["error_count"] += 1
            error_msg = str(e)
            self.results["errors"].append(error_msg)
            return None, duration, error_msg

    def test_verification_endpoint(self, num_requests: int = 100, concurrent_users: int = 10) -> Dict:
        """Test the verification endpoint under load"""
        print(f"🔄 Testing Verification Endpoint")
        print(f"   Requests: {num_requests}, Concurrent Users: {concurrent_users}")
        
        # Sample verification data
        verification_data = {
            "product_id": 51,
            "location": "Load Test Location",
            "notes": "Load testing",
            "qr_data": json.dumps({
                "product_id": 51,
                "product_name": "Load Test Product",
                "batch_number": "LOAD-TEST-001",
                "qr_hash": "load_test_hash_12345",
                "timestamp": "2025-01-01T00:00:00Z"
            })
        }
        
        def worker(worker_id: int, requests_per_worker: int):
            """Worker function for concurrent requests"""
            for i in range(requests_per_worker):
                result, duration, error = self.make_request(
                    "POST",
                    "/api/v1/verifications/",
                    verification_data
                )
                
                if i % 10 == 0:  # Progress indicator
                    print(f"    Worker {worker_id}: Request {i+1}/{requests_per_worker}")
        
        # Calculate requests per worker
        requests_per_worker = num_requests // concurrent_users
        remaining_requests = num_requests % concurrent_users
        
        # Start workers
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            # Submit workers
            for i in range(concurrent_users):
                worker_requests = requests_per_worker + (1 if i < remaining_requests else 0)
                future = executor.submit(worker, i, worker_requests)
                futures.append(future)
            
            # Wait for completion
            for future in as_completed(futures):
                future.result()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate statistics
        if self.results["response_times"]:
            stats = {
                "total_requests": num_requests,
                "successful_requests": self.results["success_count"],
                "failed_requests": self.results["error_count"],
                "success_rate": (self.results["success_count"] / num_requests) * 100,
                "total_duration": total_duration,
                "requests_per_second": num_requests / total_duration,
                "response_times": {
                    "average": statistics.mean(self.results["response_times"]),
                    "min": min(self.results["response_times"]),
                    "max": max(self.results["response_times"]),
                    "median": statistics.median(self.results["response_times"]),
                    "p95": self._percentile(self.results["response_times"], 95),
                    "p99": self._percentile(self.results["response_times"], 99)
                },
                "status_codes": self.results["status_codes"],
                "concurrent_users": concurrent_users
            }
        else:
            stats = {
                "total_requests": num_requests,
                "successful_requests": 0,
                "failed_requests": self.results["error_count"],
                "success_rate": 0,
                "total_duration": total_duration,
                "requests_per_second": 0,
                "response_times": {
                    "average": 0,
                    "min": 0,
                    "max": 0,
                    "median": 0,
                    "p95": 0,
                    "p99": 0
                },
                "status_codes": self.results["status_codes"],
                "concurrent_users": concurrent_users
            }
        
        return stats

    def test_api_endpoints_load(self, requests_per_endpoint: int = 50) -> Dict:
        """Test various API endpoints under load"""
        print(f"🌐 Testing API Endpoints Load")
        print(f"   Requests per endpoint: {requests_per_endpoint}")
        
        endpoints = [
            ("/api/v1/products/", "GET"),
            ("/api/v1/analytics/overview", "GET"),
            ("/api/v1/verifications/", "GET"),
        ]
        
        endpoint_results = {}
        
        for endpoint, method in endpoints:
            print(f"  Testing {method} {endpoint}...")
            
            # Reset results for this endpoint
            self.results = {
                "response_times": [],
                "error_count": 0,
                "success_count": 0,
                "status_codes": {},
                "errors": []
            }
            
            start_time = time.time()
            
            # Make requests
            for i in range(requests_per_endpoint):
                result, duration, error = self.make_request(method, endpoint)
                
                if i % 10 == 0:  # Progress indicator
                    print(f"    Request {i+1}/{requests_per_endpoint}")
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Calculate statistics
            if self.results["response_times"]:
                endpoint_results[endpoint] = {
                    "total_requests": requests_per_endpoint,
                    "successful_requests": self.results["success_count"],
                    "failed_requests": self.results["error_count"],
                    "success_rate": (self.results["success_count"] / requests_per_endpoint) * 100,
                    "total_duration": total_duration,
                    "requests_per_second": requests_per_endpoint / total_duration,
                    "response_times": {
                        "average": statistics.mean(self.results["response_times"]),
                        "min": min(self.results["response_times"]),
                        "max": max(self.results["response_times"]),
                        "median": statistics.median(self.results["response_times"]),
                        "p95": self._percentile(self.results["response_times"], 95),
                        "p99": self._percentile(self.results["response_times"], 99)
                    },
                    "status_codes": self.results["status_codes"]
                }
            else:
                endpoint_results[endpoint] = {
                    "total_requests": requests_per_endpoint,
                    "successful_requests": 0,
                    "failed_requests": self.results["error_count"],
                    "success_rate": 0,
                    "total_duration": total_duration,
                    "requests_per_second": 0,
                    "response_times": {
                        "average": 0,
                        "min": 0,
                        "max": 0,
                        "median": 0,
                        "p95": 0,
                        "p99": 0
                    },
                    "status_codes": self.results["status_codes"]
                }
        
        return endpoint_results

    def test_ramp_up_load(self, max_concurrent_users: int = 20, ramp_duration: int = 60) -> Dict:
        """Test system behavior under gradually increasing load"""
        print(f"📈 Testing Ramp-Up Load")
        print(f"   Max concurrent users: {max_concurrent_users}")
        print(f"   Ramp duration: {ramp_duration} seconds")
        
        ramp_results = []
        ramp_interval = ramp_duration // max_concurrent_users
        
        for concurrent_users in range(1, max_concurrent_users + 1):
            print(f"  Testing with {concurrent_users} concurrent users...")
            
            # Reset results
            self.results = {
                "response_times": [],
                "error_count": 0,
                "success_count": 0,
                "status_codes": {},
                "errors": []
            }
            
            # Test with current number of concurrent users
            verification_data = {
                "product_id": 51,
                "location": f"Ramp Test {concurrent_users}",
                "notes": f"Ramp up test with {concurrent_users} users",
                "qr_data": json.dumps({
                    "product_id": 51,
                    "product_name": f"Ramp Test Product {concurrent_users}",
                    "batch_number": f"RAMP-{concurrent_users}-001",
                    "qr_hash": f"ramp_test_hash_{concurrent_users}",
                    "timestamp": "2025-01-01T00:00:00Z"
                })
            }
            
            def worker():
                result, duration, error = self.make_request(
                    "POST",
                    "/api/v1/verifications/",
                    verification_data
                )
            
            # Run test for ramp_interval seconds
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                while time.time() - start_time < ramp_interval:
                    future = executor.submit(worker)
                    futures.append(future)
                
                # Wait for all requests to complete
                for future in as_completed(futures):
                    future.result()
            
            # Record results for this level
            if self.results["response_times"]:
                ramp_results.append({
                    "concurrent_users": concurrent_users,
                    "successful_requests": self.results["success_count"],
                    "failed_requests": self.results["error_count"],
                    "success_rate": (self.results["success_count"] / (self.results["success_count"] + self.results["error_count"])) * 100 if (self.results["success_count"] + self.results["error_count"]) > 0 else 0,
                    "average_response_time": statistics.mean(self.results["response_times"]),
                    "max_response_time": max(self.results["response_times"]),
                    "requests_per_second": (self.results["success_count"] + self.results["error_count"]) / ramp_interval
                })
            else:
                ramp_results.append({
                    "concurrent_users": concurrent_users,
                    "successful_requests": 0,
                    "failed_requests": self.results["error_count"],
                    "success_rate": 0,
                    "average_response_time": 0,
                    "max_response_time": 0,
                    "requests_per_second": 0
                })
        
        return ramp_results

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def generate_load_report(self, verification_stats: Dict, endpoint_stats: Dict, ramp_stats: List[Dict]) -> str:
        """Generate a comprehensive load testing report"""
        report = []
        report.append("📊 LOAD TESTING REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Verification Endpoint Load Test
        report.append("🔄 Verification Endpoint Load Test:")
        report.append(f"  Total Requests: {verification_stats['total_requests']}")
        report.append(f"  Successful Requests: {verification_stats['successful_requests']}")
        report.append(f"  Failed Requests: {verification_stats['failed_requests']}")
        report.append(f"  Success Rate: {verification_stats['success_rate']:.1f}%")
        report.append(f"  Total Duration: {verification_stats['total_duration']:.2f}s")
        report.append(f"  Requests/Second: {verification_stats['requests_per_second']:.2f}")
        report.append(f"  Concurrent Users: {verification_stats['concurrent_users']}")
        report.append("")
        
        report.append("  Response Time Statistics:")
        rt = verification_stats['response_times']
        report.append(f"    Average: {rt['average']:.3f}s")
        report.append(f"    Min: {rt['min']:.3f}s")
        report.append(f"    Max: {rt['max']:.3f}s")
        report.append(f"    Median: {rt['median']:.3f}s")
        report.append(f"    95th Percentile: {rt['p95']:.3f}s")
        report.append(f"    99th Percentile: {rt['p99']:.3f}s")
        report.append("")
        
        # API Endpoints Load Test
        report.append("🌐 API Endpoints Load Test:")
        for endpoint, stats in endpoint_stats.items():
            report.append(f"  {endpoint}:")
            report.append(f"    Success Rate: {stats['success_rate']:.1f}%")
            report.append(f"    Requests/Second: {stats['requests_per_second']:.2f}")
            report.append(f"    Average Response Time: {stats['response_times']['average']:.3f}s")
            report.append(f"    95th Percentile: {stats['response_times']['p95']:.3f}s")
        report.append("")
        
        # Ramp-Up Test
        report.append("📈 Ramp-Up Load Test Results:")
        report.append("  Concurrent Users | Success Rate | Avg Response | RPS")
        report.append("  " + "-" * 50)
        for result in ramp_stats:
            report.append(f"  {result['concurrent_users']:15} | {result['success_rate']:10.1f}% | {result['average_response_time']:10.3f}s | {result['requests_per_second']:6.2f}")
        report.append("")
        
        # Performance Assessment
        report.append("📈 Performance Assessment:")
        
        # Check if system meets performance targets
        avg_response_time = verification_stats['response_times']['average']
        success_rate = verification_stats['success_rate']
        rps = verification_stats['requests_per_second']
        
        if avg_response_time < 3.0 and success_rate > 95.0:
            report.append("  Status: ✅ EXCELLENT - System meets all performance targets")
        elif avg_response_time < 5.0 and success_rate > 90.0:
            report.append("  Status: ✅ GOOD - System meets most performance targets")
        elif avg_response_time < 10.0 and success_rate > 80.0:
            report.append("  Status: ⚠️ ACCEPTABLE - System has some performance issues")
        else:
            report.append("  Status: ❌ POOR - System has significant performance issues")
        
        report.append(f"  Average Response Time: {avg_response_time:.3f}s (Target: <3.0s)")
        report.append(f"  Success Rate: {success_rate:.1f}% (Target: >95%)")
        report.append(f"  Throughput: {rps:.2f} requests/second")
        
        return "\n".join(report)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Load Testing for Anti-Counterfeit System")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--bearer-token", help="Bearer token for authentication")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests for load test")
    parser.add_argument("--concurrent-users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--ramp-max-users", type=int, default=20, help="Maximum concurrent users for ramp test")
    parser.add_argument("--ramp-duration", type=int, default=60, help="Duration of ramp test in seconds")
    
    args = parser.parse_args()
    
    # Default bearer token if not provided
    if not args.bearer_token:
        args.bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"
    
    print("🚀 Load Testing for Anti-Counterfeit System")
    print("=" * 60)
    print(f"Base URL: {args.base_url}")
    print(f"Requests: {args.requests}")
    print(f"Concurrent Users: {args.concurrent_users}")
    print("=" * 60)
    
    # Initialize load tester
    tester = LoadTester(args.base_url, args.bearer_token)
    
    try:
        # Run load tests
        print("\n1. Testing Verification Endpoint Load...")
        verification_stats = tester.test_verification_endpoint(args.requests, args.concurrent_users)
        
        print("\n2. Testing API Endpoints Load...")
        endpoint_stats = tester.test_api_endpoints_load(50)
        
        print("\n3. Testing Ramp-Up Load...")
        ramp_stats = tester.test_ramp_up_load(args.ramp_max_users, args.ramp_duration)
        
        # Generate and display report
        report = tester.generate_load_report(verification_stats, endpoint_stats, ramp_stats)
        print("\n" + report)
        
        # Save results
        results = {
            "verification_stats": verification_stats,
            "endpoint_stats": endpoint_stats,
            "ramp_stats": ramp_stats
        }
        
        with open("load_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: load_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Load testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

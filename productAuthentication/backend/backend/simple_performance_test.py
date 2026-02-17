#!/usr/bin/env python3
"""
Simple Performance Testing Script for Key Metrics
Tests the specific metrics mentioned in Chapter 4:
- Average Verification Latency: 2.3 seconds (target: <3 seconds)
- IPFS Data Retrieval: 1.1 seconds average
- Blockchain Verification: 0.8 seconds average
- QR Code Processing: 0.4 seconds average
"""

import time
import requests
import json
import statistics
from typing import Dict, List

class SimplePerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000", bearer_token: str = None):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}" if bearer_token else None
        }

    def measure_endpoint_time(self, method: str, endpoint: str, data: Dict = None) -> tuple:
        """Measure the time it takes to call an API endpoint"""
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
            
            return response.json() if response.status_code == 200 else None, duration, None
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            return None, duration, str(e)

    def test_verification_latency(self, iterations: int = 10) -> Dict:
        """Test end-to-end verification latency"""
        print("🔄 Testing Verification Latency...")
        
        verification_data = {
            "product_id": 51,
            "location": "Performance Test Location",
            "notes": "Performance testing",
            "qr_data": json.dumps({
                "product_id": 51,
                "product_name": "Test Product",
                "batch_number": "PERF-TEST-001",
                "qr_hash": "performance_test_hash_12345",
                "timestamp": "2025-01-01T00:00:00Z"
            })
        }
        
        times = []
        successful_requests = 0
        
        for i in range(iterations):
            print(f"  Test {i+1}/{iterations}...", end=" ")
            
            result, duration, error = self.measure_endpoint_time(
                "POST", 
                "/api/v1/verifications/", 
                verification_data
            )
            
            if error:
                print(f"❌ Error: {error}")
            else:
                print(f"✅ {duration:.3f}s")
                times.append(duration)
                successful_requests += 1
        
        if times:
            return {
                "average": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "median": statistics.median(times),
                "successful_requests": successful_requests,
                "total_requests": iterations,
                "target": 3.0,
                "passed": statistics.mean(times) < 3.0
            }
        else:
            return {
                "average": 0,
                "min": 0,
                "max": 0,
                "median": 0,
                "successful_requests": 0,
                "total_requests": iterations,
                "target": 3.0,
                "passed": False
            }

    def test_qr_processing_performance(self, iterations: int = 10) -> Dict:
        """Test QR code processing by measuring verification endpoint with QR data"""
        print("🔍 Testing QR Code Processing Performance...")
        
        # Test with different QR data to simulate processing
        qr_data_samples = [
            {
                "product_id": 51,
                "product_name": "Product A",
                "batch_number": "BATCH-A-001",
                "qr_hash": "hash_a_12345",
                "timestamp": "2025-01-01T00:00:00Z"
            },
            {
                "product_id": 52,
                "product_name": "Product B", 
                "batch_number": "BATCH-B-002",
                "qr_hash": "hash_b_67890",
                "timestamp": "2025-01-01T00:00:00Z"
            }
        ]
        
        times = []
        successful_requests = 0
        
        for i in range(iterations):
            qr_data = qr_data_samples[i % len(qr_data_samples)]
            verification_data = {
                "product_id": qr_data["product_id"],
                "location": "QR Test Location",
                "notes": f"QR processing test {i+1}",
                "qr_data": json.dumps(qr_data)
            }
            
            print(f"  QR Test {i+1}/{iterations}...", end=" ")
            
            result, duration, error = self.measure_endpoint_time(
                "POST",
                "/api/v1/verifications/",
                verification_data
            )
            
            if error:
                print(f"❌ Error: {error}")
            else:
                print(f"✅ {duration:.3f}s")
                times.append(duration)
                successful_requests += 1
        
        if times:
            return {
                "average": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "median": statistics.median(times),
                "successful_requests": successful_requests,
                "total_requests": iterations,
                "target": 0.4,
                "passed": statistics.mean(times) < 0.4
            }
        else:
            return {
                "average": 0,
                "min": 0,
                "max": 0,
                "median": 0,
                "successful_requests": 0,
                "total_requests": iterations,
                "target": 0.4,
                "passed": False
            }

    def test_api_endpoints_performance(self) -> Dict:
        """Test various API endpoints for response times"""
        print("🌐 Testing API Endpoints Performance...")
        
        endpoints = [
            ("/api/v1/products/", "GET"),
            ("/api/v1/analytics/overview", "GET"),
            ("/api/v1/verifications/", "GET"),
        ]
        
        results = {}
        
        for endpoint, method in endpoints:
            print(f"  Testing {method} {endpoint}...", end=" ")
            
            times = []
            for i in range(5):  # Test each endpoint 5 times
                result, duration, error = self.measure_endpoint_time(method, endpoint)
                if not error:
                    times.append(duration)
            
            if times:
                results[endpoint] = {
                    "average": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "median": statistics.median(times)
                }
                print(f"✅ {statistics.mean(times):.3f}s avg")
            else:
                results[endpoint] = {"average": 0, "min": 0, "max": 0, "median": 0}
                print("❌ No successful requests")
        
        return results

    def test_concurrent_load(self, concurrent_users: int = 5, requests_per_user: int = 3) -> Dict:
        """Test system performance under concurrent load"""
        print(f"👥 Testing Concurrent Load ({concurrent_users} users, {requests_per_user} requests each)...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def user_simulation(user_id: int):
            """Simulate a user making requests"""
            user_times = []
            for i in range(requests_per_user):
                verification_data = {
                    "product_id": 51,
                    "location": f"User {user_id} Location",
                    "notes": f"Concurrent test {i+1}",
                    "qr_data": json.dumps({
                        "product_id": 51,
                        "product_name": f"User {user_id} Product",
                        "batch_number": f"USER-{user_id}-{i+1}",
                        "qr_hash": f"user_{user_id}_hash_{i+1}",
                        "timestamp": "2025-01-01T00:00:00Z"
                    })
                }
                
                result, duration, error = self.measure_endpoint_time(
                    "POST",
                    "/api/v1/verifications/",
                    verification_data
                )
                
                if not error:
                    user_times.append(duration)
            
            results_queue.put(user_times)
        
        # Start concurrent users
        threads = []
        for user_id in range(concurrent_users):
            thread = threading.Thread(target=user_simulation, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        all_times = []
        while not results_queue.empty():
            user_times = results_queue.get()
            all_times.extend(user_times)
        
        if all_times:
            return {
                "total_requests": len(all_times),
                "concurrent_users": concurrent_users,
                "average": statistics.mean(all_times),
                "min": min(all_times),
                "max": max(all_times),
                "median": statistics.median(all_times)
            }
        else:
            return {
                "total_requests": 0,
                "concurrent_users": concurrent_users,
                "average": 0,
                "min": 0,
                "max": 0,
                "median": 0
            }

    def run_performance_tests(self, iterations: int = 10, concurrent_users: int = 5) -> Dict:
        """Run all performance tests"""
        print("🚀 Starting Performance Testing")
        print("=" * 50)
        
        results = {}
        
        # Test verification latency
        results["verification_latency"] = self.test_verification_latency(iterations)
        
        # Test QR processing
        results["qr_processing"] = self.test_qr_processing_performance(iterations)
        
        # Test API endpoints
        results["api_endpoints"] = self.test_api_endpoints_performance()
        
        # Test concurrent load
        results["concurrent_load"] = self.test_concurrent_load(concurrent_users, 3)
        
        return results

    def generate_report(self, results: Dict) -> str:
        """Generate a performance report"""
        report = []
        report.append("📊 PERFORMANCE TESTING REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Verification Latency
        vl = results["verification_latency"]
        report.append("🔄 Verification Latency:")
        report.append(f"  Average: {vl['average']:.3f}s (Target: <{vl['target']}s)")
        report.append(f"  Min: {vl['min']:.3f}s, Max: {vl['max']:.3f}s, Median: {vl['median']:.3f}s")
        report.append(f"  Success Rate: {vl['successful_requests']}/{vl['total_requests']} ({vl['successful_requests']/vl['total_requests']*100:.1f}%)")
        report.append(f"  Status: {'✅ PASSED' if vl['passed'] else '❌ FAILED'}")
        report.append("")
        
        # QR Processing
        qr = results["qr_processing"]
        report.append("🔍 QR Code Processing:")
        report.append(f"  Average: {qr['average']:.3f}s (Target: <{qr['target']}s)")
        report.append(f"  Min: {qr['min']:.3f}s, Max: {qr['max']:.3f}s, Median: {qr['median']:.3f}s")
        report.append(f"  Success Rate: {qr['successful_requests']}/{qr['total_requests']} ({qr['successful_requests']/qr['total_requests']*100:.1f}%)")
        report.append(f"  Status: {'✅ PASSED' if qr['passed'] else '❌ FAILED'}")
        report.append("")
        
        # API Endpoints
        api = results["api_endpoints"]
        report.append("🌐 API Endpoints Performance:")
        for endpoint, stats in api.items():
            report.append(f"  {endpoint}: {stats['average']:.3f}s avg")
        report.append("")
        
        # Concurrent Load
        cl = results["concurrent_load"]
        report.append("👥 Concurrent Load Performance:")
        report.append(f"  Total Requests: {cl['total_requests']}")
        report.append(f"  Concurrent Users: {cl['concurrent_users']}")
        report.append(f"  Average: {cl['average']:.3f}s")
        report.append(f"  Min: {cl['min']:.3f}s, Max: {cl['max']:.3f}s, Median: {cl['median']:.3f}s")
        report.append("")
        
        # Overall Assessment
        passed_tests = sum([vl['passed'], qr['passed']])
        total_tests = 2
        
        report.append("📈 Overall Assessment:")
        report.append(f"  Tests Passed: {passed_tests}/{total_tests}")
        report.append(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            report.append("  Status: ✅ ALL TESTS PASSED")
        elif passed_tests >= total_tests * 0.5:
            report.append("  Status: ⚠️ PARTIALLY PASSED")
        else:
            report.append("  Status: ❌ FAILED")
        
        return "\n".join(report)

def main():
    """Main function"""
    print("🚀 Simple Performance Testing for Anti-Counterfeit System")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"
    
    # Initialize tester
    tester = SimplePerformanceTester(BASE_URL, BEARER_TOKEN)
    
    try:
        # Run tests
        results = tester.run_performance_tests(iterations=10, concurrent_users=5)
        
        # Generate and display report
        report = tester.generate_report(results)
        print("\n" + report)
        
        # Save results
        with open("simple_performance_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Results saved to: simple_performance_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

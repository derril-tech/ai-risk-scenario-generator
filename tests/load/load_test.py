"""Load testing for AI Risk Scenario Generator"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import json
import random
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result metrics"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]


class LoadTester:
    """Load testing framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    result = await response.json()
                    status = response.status
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
                    status = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            return {
                'success': 200 <= status < 300,
                'status_code': status,
                'response_time': response_time,
                'data': result,
                'error': None
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'success': False,
                'status_code': 0,
                'response_time': response_time,
                'data': None,
                'error': str(e)
            }
    
    async def run_load_test(
        self,
        endpoint: str,
        method: str = 'GET',
        concurrent_users: int = 10,
        requests_per_user: int = 100,
        data_generator: callable = None
    ) -> LoadTestResult:
        """Run load test with specified parameters"""
        
        logger.info(f"Starting load test: {endpoint}")
        logger.info(f"Concurrent users: {concurrent_users}")
        logger.info(f"Requests per user: {requests_per_user}")
        logger.info(f"Total requests: {concurrent_users * requests_per_user}")
        
        start_time = time.time()
        
        # Create tasks for concurrent users
        tasks = []
        for user_id in range(concurrent_users):
            task = self._user_session(
                user_id, endpoint, method, requests_per_user, data_generator
            )
            tasks.append(task)
        
        # Execute all user sessions concurrently
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_results = []
        for user_results in results:
            all_results.extend(user_results)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate metrics
        successful_requests = sum(1 for r in all_results if r['success'])
        failed_requests = len(all_results) - successful_requests
        response_times = [r['response_time'] for r in all_results]
        errors = [r['error'] for r in all_results if r['error']]
        
        return LoadTestResult(
            endpoint=endpoint,
            total_requests=len(all_results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=statistics.mean(response_times),
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if response_times else 0,
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if response_times else 0,
            requests_per_second=len(all_results) / total_duration,
            error_rate=(failed_requests / len(all_results)) * 100,
            errors=errors[:10]  # First 10 errors
        )
    
    async def _user_session(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        requests: int,
        data_generator: callable
    ) -> List[Dict[str, Any]]:
        """Simulate single user session"""
        
        results = []
        
        for request_id in range(requests):
            # Generate request data if needed
            data = None
            if data_generator:
                data = data_generator(user_id, request_id)
            
            # Make request
            result = await self.make_request(method, endpoint, data)
            results.append(result)
            
            # Small delay to simulate realistic user behavior
            await asyncio.sleep(0.01)
        
        return results


class ScenarioLoadTest:
    """Load tests for scenario-specific endpoints"""
    
    @staticmethod
    def scenario_data_generator(user_id: int, request_id: int) -> Dict[str, Any]:
        """Generate scenario creation data"""
        scenario_types = ['financial', 'cyber', 'supply_chain', 'operational']
        
        return {
            'name': f'Load Test Scenario {user_id}-{request_id}',
            'type': random.choice(scenario_types),
            'description': f'Load test scenario created by user {user_id}',
            'assumptions': {
                'test_parameter': random.uniform(0.1, 1.0),
                'user_id': user_id,
                'request_id': request_id
            }
        }
    
    @staticmethod
    def simulation_data_generator(user_id: int, request_id: int) -> Dict[str, Any]:
        """Generate simulation request data"""
        return {
            'scenario_id': f'scenario-{user_id}',
            'method': 'monte_carlo',
            'runs': random.choice([1000, 5000, 10000]),
            'seed': user_id * 1000 + request_id,
            'monte_carlo_config': {
                'scenario_type': 'financial',
                'parameters': {
                    'market_drop_percent': {
                        'distribution': 'normal',
                        'mean': random.uniform(0.1, 0.5),
                        'std': 0.05
                    }
                }
            }
        }


async def run_comprehensive_load_test():
    """Run comprehensive load test suite"""
    
    async with LoadTester() as tester:
        
        # Test 1: Health check endpoint (baseline)
        logger.info("=== Testing Health Check Endpoint ===")
        health_result = await tester.run_load_test(
            endpoint="/health",
            method="GET",
            concurrent_users=50,
            requests_per_user=20
        )
        print_results(health_result)
        
        # Test 2: Scenario templates (read-heavy)
        logger.info("=== Testing Scenario Templates ===")
        templates_result = await tester.run_load_test(
            endpoint="/api/v1/scenarios/templates",
            method="GET",
            concurrent_users=30,
            requests_per_user=50
        )
        print_results(templates_result)
        
        # Test 3: Scenario creation (write-heavy)
        logger.info("=== Testing Scenario Creation ===")
        scenario_result = await tester.run_load_test(
            endpoint="/api/v1/scenarios/generate",
            method="POST",
            concurrent_users=20,
            requests_per_user=10,
            data_generator=ScenarioLoadTest.scenario_data_generator
        )
        print_results(scenario_result)
        
        # Test 4: Simulation execution (compute-heavy)
        logger.info("=== Testing Simulation Execution ===")
        simulation_result = await tester.run_load_test(
            endpoint="/api/v1/simulations/run",
            method="POST",
            concurrent_users=10,
            requests_per_user=5,
            data_generator=ScenarioLoadTest.simulation_data_generator
        )
        print_results(simulation_result)
        
        # Test 5: Visualization generation
        logger.info("=== Testing Visualization Generation ===")
        viz_data_generator = lambda u, r: {
            'scenario_id': f'scenario-{u}',
            'viz_type': 'impact_matrix',
            'data': {
                'risks': [
                    {'name': f'Risk {i}', 'likelihood': random.uniform(0.1, 0.9), 'impact': random.uniform(0.1, 0.9)}
                    for i in range(5)
                ]
            }
        }
        
        viz_result = await tester.run_load_test(
            endpoint="/api/v1/visualizations/generate",
            method="POST",
            concurrent_users=15,
            requests_per_user=8,
            data_generator=viz_data_generator
        )
        print_results(viz_result)
        
        # Test 6: Report generation (I/O heavy)
        logger.info("=== Testing Report Generation ===")
        report_data_generator = lambda u, r: {
            'scenario_id': f'scenario-{u}',
            'format': 'pdf',
            'sections': ['executive_summary', 'scenario_details', 'simulation_results'],
            'title': f'Load Test Report {u}-{r}'
        }
        
        report_result = await tester.run_load_test(
            endpoint="/api/v1/reports/generate",
            method="POST",
            concurrent_users=5,
            requests_per_user=3,
            data_generator=report_data_generator
        )
        print_results(report_result)
        
        # Summary
        logger.info("=== Load Test Summary ===")
        all_results = [
            health_result, templates_result, scenario_result,
            simulation_result, viz_result, report_result
        ]
        
        print_summary(all_results)


def print_results(result: LoadTestResult):
    """Print load test results"""
    print(f"\n📊 Results for {result.endpoint}")
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful: {result.successful_requests} ({100-result.error_rate:.1f}%)")
    print(f"Failed: {result.failed_requests} ({result.error_rate:.1f}%)")
    print(f"Avg Response Time: {result.avg_response_time*1000:.1f}ms")
    print(f"P95 Response Time: {result.p95_response_time*1000:.1f}ms")
    print(f"P99 Response Time: {result.p99_response_time*1000:.1f}ms")
    print(f"Requests/Second: {result.requests_per_second:.1f}")
    
    if result.errors:
        print(f"Sample Errors: {result.errors[:3]}")


def print_summary(results: List[LoadTestResult]):
    """Print overall summary"""
    total_requests = sum(r.total_requests for r in results)
    total_successful = sum(r.successful_requests for r in results)
    avg_rps = sum(r.requests_per_second for r in results)
    
    print(f"\n🎯 Overall Summary")
    print(f"Total Requests: {total_requests}")
    print(f"Success Rate: {(total_successful/total_requests)*100:.1f}%")
    print(f"Total RPS: {avg_rps:.1f}")
    
    # Performance benchmarks
    print(f"\n📈 Performance Benchmarks")
    for result in results:
        status = "✅" if result.error_rate < 5 and result.p95_response_time < 10 else "⚠️"
        print(f"{status} {result.endpoint}: {result.p95_response_time*1000:.0f}ms P95, {result.error_rate:.1f}% errors")


class ChaosTest:
    """Chaos engineering tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def test_high_memory_scenario(self):
        """Test system behavior under high memory usage"""
        logger.info("🔥 Starting high memory chaos test")
        
        async with LoadTester(self.base_url) as tester:
            # Generate large simulation requests
            large_sim_generator = lambda u, r: {
                'scenario_id': f'chaos-scenario-{u}',
                'method': 'monte_carlo',
                'runs': 50000,  # Large number of runs
                'monte_carlo_config': {
                    'scenario_type': 'financial',
                    'parameters': {
                        'market_drop_percent': {
                            'distribution': 'normal',
                            'mean': 0.3,
                            'std': 0.1
                        }
                    }
                }
            }
            
            result = await tester.run_load_test(
                endpoint="/api/v1/simulations/run",
                method="POST",
                concurrent_users=5,
                requests_per_user=2,
                data_generator=large_sim_generator
            )
            
            print_results(result)
            return result.error_rate < 20  # Allow some failures under stress
    
    async def test_concurrent_report_generation(self):
        """Test concurrent report generation (I/O stress)"""
        logger.info("🔥 Starting concurrent report generation chaos test")
        
        async with LoadTester(self.base_url) as tester:
            report_generator = lambda u, r: {
                'scenario_id': f'chaos-scenario-{u}',
                'format': 'pdf',
                'sections': [
                    'executive_summary', 'scenario_details', 'simulation_results',
                    'risk_matrix', 'mitigation_strategies', 'appendices'
                ],
                'title': f'Chaos Test Report {u}-{r}'
            }
            
            result = await tester.run_load_test(
                endpoint="/api/v1/reports/generate",
                method="POST",
                concurrent_users=20,  # High concurrency
                requests_per_user=3,
                data_generator=report_generator
            )
            
            print_results(result)
            return result.error_rate < 15
    
    async def test_mixed_workload(self):
        """Test mixed workload with different endpoint types"""
        logger.info("🔥 Starting mixed workload chaos test")
        
        async with LoadTester(self.base_url) as tester:
            # Run different types of requests concurrently
            tasks = [
                # Read-heavy
                tester.run_load_test("/api/v1/scenarios/templates", "GET", 20, 30),
                # Write-heavy
                tester.run_load_test(
                    "/api/v1/scenarios/generate", "POST", 10, 10,
                    ScenarioLoadTest.scenario_data_generator
                ),
                # Compute-heavy
                tester.run_load_test(
                    "/api/v1/simulations/run", "POST", 5, 5,
                    ScenarioLoadTest.simulation_data_generator
                )
            ]
            
            results = await asyncio.gather(*tasks)
            
            for result in results:
                print_results(result)
            
            # All endpoints should maintain reasonable performance
            return all(r.error_rate < 25 for r in results)


async def run_chaos_tests():
    """Run chaos engineering test suite"""
    logger.info("🔥 Starting Chaos Engineering Tests")
    
    chaos = ChaosTest()
    
    tests = [
        ("High Memory Usage", chaos.test_high_memory_scenario),
        ("Concurrent Reports", chaos.test_concurrent_report_generation),
        ("Mixed Workload", chaos.test_mixed_workload)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"Running: {test_name}")
        try:
            success = await test_func()
            results[test_name] = "✅ PASSED" if success else "⚠️ DEGRADED"
        except Exception as e:
            results[test_name] = f"❌ FAILED: {str(e)}"
        
        # Cool down between tests
        await asyncio.sleep(2)
    
    print(f"\n🔥 Chaos Test Results:")
    for test_name, result in results.items():
        print(f"{result} {test_name}")


if __name__ == "__main__":
    print("🚀 AI Risk Scenario Generator - Load Testing")
    print("=" * 50)
    
    # Run load tests
    asyncio.run(run_comprehensive_load_test())
    
    print("\n" + "=" * 50)
    
    # Run chaos tests
    asyncio.run(run_chaos_tests())

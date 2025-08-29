"""Advanced simulation service with Monte Carlo, Bayesian networks, and stress testing"""

import uuid
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import networkx as nx

from ..models.simulation import (
    SimulationRequest, SimulationResponse, MonteCarloConfig,
    BayesianNetworkConfig, StressTestConfig, SimulationResults
)
from ..core.database import db_manager
from ..core.messaging import messaging_manager
from ..config import settings

logger = structlog.get_logger()


class MonteCarloEngine:
    """Monte Carlo simulation engine"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            np.random.seed(seed)
    
    def run_simulation(self, config: MonteCarloConfig, runs: int) -> Dict[str, Any]:
        """Run Monte Carlo simulation"""
        try:
            logger.info("Starting Monte Carlo simulation", runs=runs)
            
            results = []
            
            for i in range(runs):
                # Sample from parameter distributions
                sample = self._sample_parameters(config.parameters)
                
                # Calculate impact based on scenario type
                impact = self._calculate_impact(sample, config.scenario_type)
                
                results.append({
                    'run': i,
                    'total_impact': impact['total'],
                    'financial_impact': impact['financial'],
                    'operational_impact': impact['operational'],
                    'reputational_impact': impact['reputational'],
                    'parameters': sample
                })
            
            # Calculate statistics
            total_impacts = [r['total_impact'] for r in results]
            financial_impacts = [r['financial_impact'] for r in results]
            operational_impacts = [r['operational_impact'] for r in results]
            
            statistics = self._calculate_statistics(total_impacts)
            
            return {
                'runs': runs,
                'statistics': statistics,
                'financial_stats': self._calculate_statistics(financial_impacts),
                'operational_stats': self._calculate_statistics(operational_impacts),
                'distribution': total_impacts,
                'detailed_results': results[:100],  # Sample for analysis
                'percentiles': {
                    'p50': np.percentile(total_impacts, 50),
                    'p75': np.percentile(total_impacts, 75),
                    'p90': np.percentile(total_impacts, 90),
                    'p95': np.percentile(total_impacts, 95),
                    'p99': np.percentile(total_impacts, 99)
                }
            }
            
        except Exception as e:
            logger.error("Monte Carlo simulation failed", error=str(e))
            raise
    
    def _sample_parameters(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """Sample from parameter distributions"""
        sample = {}
        
        for param_name, param_config in parameters.items():
            dist_type = param_config.get('distribution', 'normal')
            
            if dist_type == 'normal':
                mean = param_config.get('mean', 0)
                std = param_config.get('std', 1)
                sample[param_name] = np.random.normal(mean, std)
                
            elif dist_type == 'lognormal':
                mean = param_config.get('mean', 0)
                sigma = param_config.get('sigma', 1)
                sample[param_name] = np.random.lognormal(mean, sigma)
                
            elif dist_type == 'uniform':
                low = param_config.get('low', 0)
                high = param_config.get('high', 1)
                sample[param_name] = np.random.uniform(low, high)
                
            elif dist_type == 'triangular':
                left = param_config.get('left', 0)
                mode = param_config.get('mode', 0.5)
                right = param_config.get('right', 1)
                sample[param_name] = np.random.triangular(left, mode, right)
                
            elif dist_type == 'beta':
                alpha = param_config.get('alpha', 2)
                beta = param_config.get('beta', 5)
                sample[param_name] = np.random.beta(alpha, beta)
                
            else:
                # Default to normal
                sample[param_name] = np.random.normal(0, 1)
        
        return sample
    
    def _calculate_impact(self, parameters: Dict[str, float], scenario_type: str) -> Dict[str, float]:
        """Calculate impact based on parameters and scenario type"""
        
        if scenario_type == 'financial':
            return self._calculate_financial_impact(parameters)
        elif scenario_type == 'cyber':
            return self._calculate_cyber_impact(parameters)
        elif scenario_type == 'supply_chain':
            return self._calculate_supply_chain_impact(parameters)
        elif scenario_type == 'operational':
            return self._calculate_operational_impact(parameters)
        else:
            return self._calculate_generic_impact(parameters)
    
    def _calculate_financial_impact(self, params: Dict[str, float]) -> Dict[str, float]:
        """Calculate financial scenario impact"""
        market_drop = params.get('market_drop_percent', 0.2)
        duration = params.get('duration_months', 6)
        portfolio_value = params.get('portfolio_value', 100000000)
        
        # Direct financial loss
        direct_loss = portfolio_value * market_drop
        
        # Indirect costs (liquidity, opportunity cost)
        indirect_multiplier = 1 + (duration / 12) * 0.1
        indirect_loss = direct_loss * indirect_multiplier * 0.2
        
        # Operational impact (reduced capacity)
        operational_impact = direct_loss * 0.05
        
        # Reputational impact
        reputational_impact = direct_loss * 0.1
        
        total = direct_loss + indirect_loss + operational_impact + reputational_impact
        
        return {
            'total': total,
            'financial': direct_loss + indirect_loss,
            'operational': operational_impact,
            'reputational': reputational_impact
        }
    
    def _calculate_cyber_impact(self, params: Dict[str, float]) -> Dict[str, float]:
        """Calculate cyber scenario impact"""
        downtime_hours = params.get('downtime_hours', 72)
        systems_affected = params.get('systems_affected_count', 5)
        hourly_revenue = params.get('hourly_revenue', 50000)
        
        # Direct revenue loss
        revenue_loss = downtime_hours * hourly_revenue
        
        # Recovery costs
        recovery_cost = systems_affected * 100000
        
        # Regulatory fines
        regulatory_fine = revenue_loss * 0.1
        
        # Reputational damage
        reputational_impact = revenue_loss * 0.3
        
        total = revenue_loss + recovery_cost + regulatory_fine + reputational_impact
        
        return {
            'total': total,
            'financial': revenue_loss + recovery_cost + regulatory_fine,
            'operational': recovery_cost,
            'reputational': reputational_impact
        }
    
    def _calculate_supply_chain_impact(self, params: Dict[str, float]) -> Dict[str, float]:
        """Calculate supply chain scenario impact"""
        outage_days = params.get('supplier_outage_duration', 14)
        production_impact = params.get('production_capacity_impact', 0.7)
        daily_revenue = params.get('daily_revenue', 1000000)
        
        # Production loss
        production_loss = outage_days * daily_revenue * production_impact
        
        # Alternative sourcing costs
        alt_sourcing_cost = production_loss * 0.2
        
        # Customer penalties
        customer_penalties = production_loss * 0.1
        
        # Operational disruption
        operational_impact = production_loss * 0.15
        
        total = production_loss + alt_sourcing_cost + customer_penalties + operational_impact
        
        return {
            'total': total,
            'financial': production_loss + alt_sourcing_cost + customer_penalties,
            'operational': operational_impact,
            'reputational': customer_penalties * 0.5
        }
    
    def _calculate_operational_impact(self, params: Dict[str, float]) -> Dict[str, float]:
        """Calculate operational scenario impact"""
        workforce_impact = params.get('workforce_availability', 0.6)
        duration_months = params.get('duration_months', 3)
        monthly_revenue = params.get('monthly_revenue', 10000000)
        
        # Revenue impact
        revenue_impact = monthly_revenue * duration_months * (1 - workforce_impact)
        
        # Additional operational costs
        additional_costs = revenue_impact * 0.3
        
        # Compliance costs
        compliance_costs = revenue_impact * 0.1
        
        total = revenue_impact + additional_costs + compliance_costs
        
        return {
            'total': total,
            'financial': revenue_impact + additional_costs + compliance_costs,
            'operational': additional_costs,
            'reputational': revenue_impact * 0.1
        }
    
    def _calculate_generic_impact(self, params: Dict[str, float]) -> Dict[str, float]:
        """Calculate generic impact"""
        base_impact = params.get('base_impact', 1000000)
        severity = params.get('severity_multiplier', 1.0)
        
        total = base_impact * severity
        
        return {
            'total': total,
            'financial': total * 0.7,
            'operational': total * 0.2,
            'reputational': total * 0.1
        }
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical measures"""
        values_array = np.array(values)
        
        return {
            'mean': float(np.mean(values_array)),
            'median': float(np.median(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'skewness': float(stats.skew(values_array)),
            'kurtosis': float(stats.kurtosis(values_array))
        }


class BayesianNetworkEngine:
    """Bayesian network simulation engine"""
    
    def __init__(self):
        self.network = nx.DiGraph()
    
    def build_network(self, config: BayesianNetworkConfig) -> Dict[str, Any]:
        """Build Bayesian network from configuration"""
        try:
            # Create network structure
            for node in config.nodes:
                self.network.add_node(node['name'], **node.get('properties', {}))
            
            for edge in config.edges:
                self.network.add_edge(
                    edge['source'], 
                    edge['target'], 
                    weight=edge.get('strength', 1.0)
                )
            
            # Perform inference
            results = self._perform_inference(config.evidence)
            
            return {
                'network_structure': {
                    'nodes': list(self.network.nodes()),
                    'edges': list(self.network.edges()),
                    'node_count': self.network.number_of_nodes(),
                    'edge_count': self.network.number_of_edges()
                },
                'inference_results': results,
                'network_metrics': self._calculate_network_metrics()
            }
            
        except Exception as e:
            logger.error("Bayesian network construction failed", error=str(e))
            raise
    
    def _perform_inference(self, evidence: Dict[str, float]) -> Dict[str, Any]:
        """Perform Bayesian inference"""
        # Simplified inference - in production, use proper Bayesian network library
        results = {}
        
        for node in self.network.nodes():
            if node in evidence:
                results[node] = evidence[node]
            else:
                # Calculate based on parent nodes
                parents = list(self.network.predecessors(node))
                if parents:
                    parent_values = [evidence.get(p, 0.5) for p in parents]
                    results[node] = np.mean(parent_values) * 0.8  # Simplified calculation
                else:
                    results[node] = 0.5  # Prior probability
        
        return results
    
    def _calculate_network_metrics(self) -> Dict[str, float]:
        """Calculate network topology metrics"""
        return {
            'density': nx.density(self.network),
            'average_clustering': nx.average_clustering(self.network.to_undirected()),
            'average_path_length': nx.average_shortest_path_length(self.network.to_undirected()) 
                if nx.is_connected(self.network.to_undirected()) else 0
        }


class StressTestEngine:
    """Stress testing engine"""
    
    def run_stress_test(self, config: StressTestConfig) -> Dict[str, Any]:
        """Run stress test scenarios"""
        try:
            results = {}
            
            for scenario_name, scenario_config in config.scenarios.items():
                scenario_results = self._run_single_stress_test(scenario_config)
                results[scenario_name] = scenario_results
            
            # Calculate aggregate metrics
            aggregate_results = self._calculate_aggregate_stress_results(results)
            
            return {
                'individual_scenarios': results,
                'aggregate_results': aggregate_results,
                'stress_test_summary': self._generate_stress_test_summary(results)
            }
            
        except Exception as e:
            logger.error("Stress test failed", error=str(e))
            raise
    
    def _run_single_stress_test(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run single stress test scenario"""
        stress_level = scenario_config.get('stress_level', 'moderate')
        parameters = scenario_config.get('parameters', {})
        
        # Apply stress multipliers
        stress_multipliers = {
            'mild': 1.5,
            'moderate': 2.5,
            'severe': 4.0,
            'extreme': 6.0
        }
        
        multiplier = stress_multipliers.get(stress_level, 2.5)
        
        # Calculate stressed impacts
        base_impact = parameters.get('base_impact', 1000000)
        stressed_impact = base_impact * multiplier
        
        # Calculate recovery metrics
        recovery_time = parameters.get('recovery_time_days', 30) * multiplier
        recovery_cost = stressed_impact * 0.2
        
        return {
            'stress_level': stress_level,
            'multiplier': multiplier,
            'stressed_impact': stressed_impact,
            'recovery_time_days': recovery_time,
            'recovery_cost': recovery_cost,
            'total_cost': stressed_impact + recovery_cost,
            'break_even_time': recovery_time * 1.5
        }
    
    def _calculate_aggregate_stress_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate stress test results"""
        total_impacts = [r['stressed_impact'] for r in results.values()]
        total_costs = [r['total_cost'] for r in results.values()]
        recovery_times = [r['recovery_time_days'] for r in results.values()]
        
        return {
            'worst_case_impact': max(total_impacts),
            'average_impact': np.mean(total_impacts),
            'total_portfolio_impact': sum(total_impacts),
            'longest_recovery': max(recovery_times),
            'average_recovery': np.mean(recovery_times),
            'total_recovery_cost': sum([r['recovery_cost'] for r in results.values()])
        }
    
    def _generate_stress_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stress test summary"""
        return {
            'scenarios_tested': len(results),
            'highest_risk_scenario': max(results.keys(), 
                                       key=lambda k: results[k]['total_cost']),
            'risk_concentration': self._calculate_risk_concentration(results),
            'resilience_score': self._calculate_resilience_score(results)
        }
    
    def _calculate_risk_concentration(self, results: Dict[str, Any]) -> float:
        """Calculate risk concentration metric"""
        impacts = [r['stressed_impact'] for r in results.values()]
        total_impact = sum(impacts)
        
        if total_impact == 0:
            return 0
        
        # Calculate Herfindahl index for concentration
        shares = [impact / total_impact for impact in impacts]
        herfindahl = sum(share ** 2 for share in shares)
        
        return herfindahl
    
    def _calculate_resilience_score(self, results: Dict[str, Any]) -> float:
        """Calculate organizational resilience score (0-100)"""
        recovery_times = [r['recovery_time_days'] for r in results.values()]
        recovery_costs = [r['recovery_cost'] for r in results.values()]
        
        # Normalize metrics (lower is better)
        avg_recovery_time = np.mean(recovery_times)
        avg_recovery_cost = np.mean(recovery_costs)
        
        # Simple scoring (in production, use more sophisticated model)
        time_score = max(0, 100 - (avg_recovery_time / 10))  # Penalty for long recovery
        cost_score = max(0, 100 - (avg_recovery_cost / 1000000))  # Penalty for high cost
        
        return (time_score + cost_score) / 2


class SimulationService:
    """Main simulation service orchestrator"""
    
    def __init__(self):
        self.monte_carlo = MonteCarloEngine()
        self.bayesian = BayesianNetworkEngine()
        self.stress_test = StressTestEngine()
    
    async def run_simulation(self, request: SimulationRequest) -> SimulationResponse:
        """Run simulation based on request type"""
        try:
            simulation_id = str(uuid.uuid4())
            
            logger.info("Starting simulation", 
                       simulation_id=simulation_id,
                       type=request.method,
                       scenario_id=request.scenario_id)
            
            # Run appropriate simulation method
            if request.method == 'monte_carlo':
                results = self.monte_carlo.run_simulation(
                    request.monte_carlo_config, 
                    request.runs
                )
            elif request.method == 'bayesian_network':
                results = self.bayesian.build_network(request.bayesian_config)
            elif request.method == 'stress_test':
                results = self.stress_test.run_stress_test(request.stress_test_config)
            else:
                raise ValueError(f"Unknown simulation method: {request.method}")
            
            # Store simulation results
            await self._store_simulation_results(simulation_id, request, results)
            
            # Publish simulation completed event
            await messaging_manager.publish(
                "sim.run",
                json.dumps({
                    "event": "simulation_completed",
                    "simulation_id": simulation_id,
                    "scenario_id": request.scenario_id,
                    "method": request.method
                }).encode()
            )
            
            return SimulationResponse(
                id=simulation_id,
                scenario_id=request.scenario_id,
                method=request.method,
                runs=request.runs,
                status="completed",
                results=results,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Simulation failed", error=str(e))
            raise
    
    async def _store_simulation_results(self, simulation_id: str, request: SimulationRequest, results: Dict[str, Any]):
        """Store simulation results in database"""
        try:
            query = """
                INSERT INTO simulations (id, scenario_id, runs, seed, results, status, created_at, completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            
            now = datetime.utcnow()
            await db_manager.execute_query(
                query,
                simulation_id,
                request.scenario_id,
                request.runs,
                request.seed,
                json.dumps(results),
                "completed",
                now,
                now
            )
            
            logger.info("Simulation results stored", simulation_id=simulation_id)
            
        except Exception as e:
            logger.error("Failed to store simulation results", error=str(e))
            raise

"""Tests for simulation service"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.services.simulation_service import (
    SimulationService, MonteCarloEngine, BayesianNetworkEngine, StressTestEngine
)
from src.models.simulation import (
    SimulationRequest, MonteCarloConfig, BayesianNetworkConfig, StressTestConfig
)


class TestMonteCarloEngine:
    """Test Monte Carlo simulation engine"""
    
    def setup_method(self):
        self.engine = MonteCarloEngine(seed=42)
    
    def test_financial_impact_calculation(self):
        """Test financial scenario impact calculation"""
        params = {
            'market_drop_percent': 0.3,
            'duration_months': 6,
            'portfolio_value': 100000000
        }
        
        impact = self.engine._calculate_financial_impact(params)
        
        assert impact['total'] > 0
        assert impact['financial'] > impact['operational']
        assert impact['financial'] > impact['reputational']
        
        # Test that larger market drop increases impact
        params_high = {**params, 'market_drop_percent': 0.5}
        impact_high = self.engine._calculate_financial_impact(params_high)
        assert impact_high['total'] > impact['total']
    
    def test_cyber_impact_calculation(self):
        """Test cyber scenario impact calculation"""
        params = {
            'downtime_hours': 72,
            'systems_affected_count': 5,
            'hourly_revenue': 50000
        }
        
        impact = self.engine._calculate_cyber_impact(params)
        
        assert impact['total'] > 0
        assert impact['financial'] > 0
        assert impact['operational'] > 0
        assert impact['reputational'] > 0
        
        # Revenue loss should be proportional to downtime
        expected_revenue_loss = 72 * 50000
        assert impact['financial'] >= expected_revenue_loss
    
    def test_supply_chain_impact_calculation(self):
        """Test supply chain scenario impact calculation"""
        params = {
            'supplier_outage_duration': 14,
            'production_capacity_impact': 0.7,
            'daily_revenue': 1000000
        }
        
        impact = self.engine._calculate_supply_chain_impact(params)
        
        assert impact['total'] > 0
        assert impact['financial'] > 0
        
        # Production loss should be proportional to outage duration and impact
        expected_production_loss = 14 * 1000000 * 0.7
        assert impact['financial'] >= expected_production_loss
    
    def test_monte_carlo_simulation(self):
        """Test full Monte Carlo simulation"""
        config = MonteCarloConfig(
            scenario_type='financial',
            parameters={
                'market_drop_percent': {
                    'distribution': 'normal',
                    'mean': 0.2,
                    'std': 0.05
                },
                'portfolio_value': {
                    'distribution': 'uniform',
                    'low': 50000000,
                    'high': 150000000
                }
            }
        )
        
        results = self.engine.run_simulation(config, runs=1000)
        
        assert results['runs'] == 1000
        assert 'statistics' in results
        assert 'distribution' in results
        assert 'percentiles' in results
        
        # Check statistics
        stats = results['statistics']
        assert stats['mean'] > 0
        assert stats['std'] > 0
        assert stats['min'] >= 0
        assert stats['max'] > stats['mean']
        
        # Check percentiles
        percentiles = results['percentiles']
        assert percentiles['p50'] < percentiles['p95']
        assert percentiles['p95'] < percentiles['p99']
    
    def test_parameter_sampling(self):
        """Test parameter distribution sampling"""
        parameters = {
            'normal_param': {
                'distribution': 'normal',
                'mean': 100,
                'std': 10
            },
            'uniform_param': {
                'distribution': 'uniform',
                'low': 0,
                'high': 1
            },
            'lognormal_param': {
                'distribution': 'lognormal',
                'mean': 0,
                'sigma': 1
            }
        }
        
        sample = self.engine._sample_parameters(parameters)
        
        assert 'normal_param' in sample
        assert 'uniform_param' in sample
        assert 'lognormal_param' in sample
        
        # Uniform parameter should be in range
        assert 0 <= sample['uniform_param'] <= 1
        
        # Lognormal should be positive
        assert sample['lognormal_param'] > 0
    
    def test_statistics_calculation(self):
        """Test statistical measures calculation"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = self.engine._calculate_statistics(values)
        
        assert stats['mean'] == 5.5
        assert stats['median'] == 5.5
        assert stats['min'] == 1
        assert stats['max'] == 10
        assert stats['std'] > 0


class TestBayesianNetworkEngine:
    """Test Bayesian network engine"""
    
    def setup_method(self):
        self.engine = BayesianNetworkEngine()
    
    def test_network_construction(self):
        """Test Bayesian network construction"""
        config = BayesianNetworkConfig(
            nodes=[
                {'name': 'MarketCrash', 'properties': {'type': 'binary'}},
                {'name': 'PortfolioLoss', 'properties': {'type': 'continuous'}},
                {'name': 'LiquidityCrisis', 'properties': {'type': 'binary'}}
            ],
            edges=[
                {'source': 'MarketCrash', 'target': 'PortfolioLoss', 'strength': 0.8},
                {'source': 'PortfolioLoss', 'target': 'LiquidityCrisis', 'strength': 0.6}
            ],
            evidence={'MarketCrash': 0.3}
        )
        
        results = self.engine.build_network(config)
        
        assert 'network_structure' in results
        assert 'inference_results' in results
        assert 'network_metrics' in results
        
        # Check network structure
        structure = results['network_structure']
        assert structure['node_count'] == 3
        assert structure['edge_count'] == 2
        
        # Check inference results
        inference = results['inference_results']
        assert 'MarketCrash' in inference
        assert 'PortfolioLoss' in inference
        assert 'LiquidityCrisis' in inference
        
        # Evidence should be preserved
        assert inference['MarketCrash'] == 0.3
    
    def test_network_metrics(self):
        """Test network topology metrics"""
        # Create a simple network
        self.engine.network.add_node('A')
        self.engine.network.add_node('B')
        self.engine.network.add_node('C')
        self.engine.network.add_edge('A', 'B')
        self.engine.network.add_edge('B', 'C')
        
        metrics = self.engine._calculate_network_metrics()
        
        assert 'density' in metrics
        assert 'average_clustering' in metrics
        assert 'average_path_length' in metrics
        
        # Density should be between 0 and 1
        assert 0 <= metrics['density'] <= 1


class TestStressTestEngine:
    """Test stress testing engine"""
    
    def setup_method(self):
        self.engine = StressTestEngine()
    
    def test_single_stress_test(self):
        """Test single stress test scenario"""
        scenario_config = {
            'stress_level': 'severe',
            'parameters': {
                'base_impact': 1000000,
                'recovery_time_days': 30
            }
        }
        
        results = self.engine._run_single_stress_test(scenario_config)
        
        assert results['stress_level'] == 'severe'
        assert results['multiplier'] == 4.0  # Severe multiplier
        assert results['stressed_impact'] == 4000000  # 1M * 4.0
        assert results['recovery_time_days'] == 120  # 30 * 4.0
        assert results['total_cost'] > results['stressed_impact']
    
    def test_stress_test_levels(self):
        """Test different stress test levels"""
        base_config = {
            'parameters': {
                'base_impact': 1000000,
                'recovery_time_days': 30
            }
        }
        
        levels = ['mild', 'moderate', 'severe', 'extreme']
        expected_multipliers = [1.5, 2.5, 4.0, 6.0]
        
        for level, expected_mult in zip(levels, expected_multipliers):
            config = {**base_config, 'stress_level': level}
            results = self.engine._run_single_stress_test(config)
            
            assert results['multiplier'] == expected_mult
            assert results['stressed_impact'] == 1000000 * expected_mult
    
    def test_full_stress_test(self):
        """Test full stress test with multiple scenarios"""
        config = StressTestConfig(
            scenarios={
                'cyber_attack': {
                    'stress_level': 'severe',
                    'parameters': {'base_impact': 2000000, 'recovery_time_days': 14}
                },
                'market_crash': {
                    'stress_level': 'extreme',
                    'parameters': {'base_impact': 5000000, 'recovery_time_days': 60}
                }
            }
        )
        
        results = self.engine.run_stress_test(config)
        
        assert 'individual_scenarios' in results
        assert 'aggregate_results' in results
        assert 'stress_test_summary' in results
        
        # Check individual scenarios
        individual = results['individual_scenarios']
        assert 'cyber_attack' in individual
        assert 'market_crash' in individual
        
        # Check aggregate results
        aggregate = results['aggregate_results']
        assert aggregate['worst_case_impact'] > 0
        assert aggregate['total_portfolio_impact'] > 0
        assert aggregate['longest_recovery'] > 0
    
    def test_resilience_score_calculation(self):
        """Test resilience score calculation"""
        mock_results = {
            'scenario1': {
                'recovery_time_days': 30,
                'recovery_cost': 500000,
                'total_cost': 2000000
            },
            'scenario2': {
                'recovery_time_days': 60,
                'recovery_cost': 1000000,
                'total_cost': 4000000
            }
        }
        
        score = self.engine._calculate_resilience_score(mock_results)
        
        assert 0 <= score <= 100
        assert isinstance(score, float)


class TestSimulationService:
    """Test main simulation service"""
    
    @pytest.fixture
    def mock_db_manager(self):
        with patch('src.services.simulation_service.db_manager') as mock:
            mock.execute_query = AsyncMock()
            yield mock
    
    @pytest.fixture
    def mock_messaging(self):
        with patch('src.services.simulation_service.messaging_manager') as mock:
            mock.publish = AsyncMock()
            yield mock
    
    def setup_method(self):
        self.service = SimulationService()
    
    @pytest.mark.asyncio
    async def test_monte_carlo_simulation(self, mock_db_manager, mock_messaging):
        """Test Monte Carlo simulation through service"""
        request = SimulationRequest(
            scenario_id='test-scenario',
            method='monte_carlo',
            runs=1000,
            seed=42,
            monte_carlo_config=MonteCarloConfig(
                scenario_type='financial',
                parameters={
                    'market_drop_percent': {
                        'distribution': 'normal',
                        'mean': 0.2,
                        'std': 0.05
                    }
                }
            )
        )
        
        response = await self.service.run_simulation(request)
        
        assert response.id is not None
        assert response.scenario_id == 'test-scenario'
        assert response.method == 'monte_carlo'
        assert response.runs == 1000
        assert response.status == 'completed'
        assert response.results is not None
        
        # Check that database storage was called
        mock_db_manager.execute_query.assert_called_once()
        
        # Check that event was published
        mock_messaging.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bayesian_simulation(self, mock_db_manager, mock_messaging):
        """Test Bayesian network simulation"""
        request = SimulationRequest(
            scenario_id='test-scenario',
            method='bayesian_network',
            runs=1,
            bayesian_config=BayesianNetworkConfig(
                nodes=[{'name': 'TestNode', 'properties': {}}],
                edges=[],
                evidence={'TestNode': 0.5}
            )
        )
        
        response = await self.service.run_simulation(request)
        
        assert response.method == 'bayesian_network'
        assert response.status == 'completed'
        assert 'network_structure' in response.results
    
    @pytest.mark.asyncio
    async def test_stress_test_simulation(self, mock_db_manager, mock_messaging):
        """Test stress test simulation"""
        request = SimulationRequest(
            scenario_id='test-scenario',
            method='stress_test',
            runs=1,
            stress_test_config=StressTestConfig(
                scenarios={
                    'test_scenario': {
                        'stress_level': 'moderate',
                        'parameters': {'base_impact': 1000000}
                    }
                }
            )
        )
        
        response = await self.service.run_simulation(request)
        
        assert response.method == 'stress_test'
        assert response.status == 'completed'
        assert 'individual_scenarios' in response.results
    
    @pytest.mark.asyncio
    async def test_invalid_simulation_method(self, mock_db_manager, mock_messaging):
        """Test handling of invalid simulation method"""
        request = SimulationRequest(
            scenario_id='test-scenario',
            method='invalid_method',
            runs=1000
        )
        
        with pytest.raises(ValueError, match="Unknown simulation method"):
            await self.service.run_simulation(request)


# Golden dataset tests for historical scenarios
class TestGoldenDatasets:
    """Test simulations against historical scenarios"""
    
    def setup_method(self):
        self.engine = MonteCarloEngine(seed=42)
    
    def test_2008_financial_crisis(self):
        """Test 2008 financial crisis scenario"""
        # Historical parameters from 2008 crisis
        params = {
            'market_drop_percent': 0.57,  # S&P 500 peak-to-trough
            'duration_months': 17,        # Oct 2007 to Mar 2009
            'portfolio_value': 100000000,
            'credit_spread_increase': 0.06,
            'volatility_spike': 0.8
        }
        
        impact = self.engine._calculate_financial_impact(params)
        
        # Validate against historical ranges
        assert impact['total'] > 50000000  # Significant impact expected
        assert impact['financial'] > impact['operational']
        
        # Test with Monte Carlo
        config = MonteCarloConfig(
            scenario_type='financial',
            parameters={
                'market_drop_percent': {
                    'distribution': 'normal',
                    'mean': 0.57,
                    'std': 0.1
                }
            }
        )
        
        results = self.engine.run_simulation(config, runs=1000)
        
        # Results should show high impact with reasonable distribution
        assert results['statistics']['mean'] > 30000000
        assert results['percentiles']['p95'] > results['statistics']['mean']
    
    def test_2021_chip_shortage(self):
        """Test 2021 semiconductor shortage scenario"""
        params = {
            'supplier_outage_duration': 180,  # ~6 months average
            'production_capacity_impact': 0.4,  # 40% reduction
            'daily_revenue': 2000000,
            'alternative_suppliers_available': False,
            'inventory_buffer_days': 30
        }
        
        impact = self.engine._calculate_supply_chain_impact(params)
        
        # Validate supply chain specific impacts
        assert impact['total'] > 100000000  # Significant supply chain impact
        assert impact['financial'] > 0
        assert impact['operational'] > 0
    
    def test_wannacry_ransomware(self):
        """Test WannaCry ransomware scenario (2017)"""
        params = {
            'downtime_hours': 96,  # ~4 days average
            'systems_affected_count': 8,  # Multiple critical systems
            'hourly_revenue': 100000,
            'data_recovery_possible': False,  # Many couldn't recover
            'ransom_amount': 300,  # $300 in Bitcoin
            'reputation_impact_multiplier': 2.0
        }
        
        impact = self.engine._calculate_cyber_impact(params)
        
        # Validate cyber-specific impacts
        assert impact['total'] > 5000000  # Significant cyber impact
        assert impact['reputational'] > 0  # Reputation damage
        assert impact['operational'] > 0   # Operational disruption


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

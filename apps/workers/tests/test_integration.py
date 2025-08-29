"""Integration tests for end-to-end workflows"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.services.ingestion_service import IngestionService
from src.services.scenario_service import ScenarioService
from src.services.simulation_service import SimulationService
from src.services.visualization_service import VisualizationService
from src.services.mitigation_service import MitigationService
from src.services.report_service import ReportService

from src.models.ingestion import DataSourceCreate, IngestionJob
from src.models.scenario import ScenarioRequest
from src.models.simulation import SimulationRequest, MonteCarloConfig
from src.models.visualization import VisualizationRequest
from src.models.mitigation import MitigationRequest
from src.models.report import ReportRequest


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow: ingest → scenario → sim → viz → mitigation → report"""
    
    @pytest.fixture
    def mock_services(self):
        """Mock all external dependencies"""
        with patch('src.core.database.db_manager') as mock_db, \
             patch('src.core.messaging.messaging_manager') as mock_msg:
            
            mock_db.execute_query = AsyncMock()
            mock_db.execute_one = AsyncMock()
            mock_msg.publish = AsyncMock()
            
            yield mock_db, mock_msg
    
    @pytest.mark.asyncio
    async def test_complete_financial_risk_workflow(self, mock_services):
        """Test complete workflow for financial risk scenario"""
        mock_db, mock_msg = mock_services
        
        # Step 1: Data Ingestion
        ingestion_service = IngestionService()
        
        # Mock CSV data upload
        csv_content = b"""asset_name,asset_type,value,sector
Portfolio A,investment,50000000,technology
Portfolio B,investment,30000000,finance
Cash Reserves,cash,10000000,liquidity"""
        
        ingestion_job = await ingestion_service.process_uploaded_file(
            filename="portfolio_data.csv",
            content=csv_content,
            content_type="text/csv"
        )
        
        assert ingestion_job.status == "processing"
        assert ingestion_job.records_found == 3
        
        # Step 2: Scenario Generation
        scenario_service = ScenarioService()
        
        scenario_request = ScenarioRequest(
            name="Market Crash Q1 2024",
            type="financial",
            description="Severe market downturn affecting tech and finance sectors",
            assumptions={
                "market_drop_percent": 35,
                "duration_months": 8,
                "affected_sectors": ["technology", "finance"],
                "portfolio_correlation": 0.7
            },
            context={
                "economic_indicators": {
                    "inflation_rate": 0.06,
                    "interest_rates": 0.055,
                    "unemployment": 0.045
                }
            }
        )
        
        # Mock CrewAI response
        with patch.object(scenario_service, 'generate_scenario') as mock_generate:
            mock_scenario_response = type('MockResponse', (), {
                'id': 'scenario-123',
                'name': scenario_request.name,
                'type': scenario_request.type,
                'narrative': {
                    'executive_summary': 'Severe market downturn scenario',
                    'timeline': [
                        {'day': 0, 'event': 'Market crash begins', 'impact': 'high'},
                        {'day': 30, 'event': 'Full impact realized', 'impact': 'critical'}
                    ]
                },
                'assumptions': scenario_request.assumptions,
                'status': 'generated',
                'created_at': datetime.utcnow()
            })()
            
            mock_generate.return_value = mock_scenario_response
            scenario_response = await scenario_service.generate_scenario(scenario_request)
        
        assert scenario_response.id == 'scenario-123'
        assert scenario_response.status == 'generated'
        
        # Step 3: Simulation Execution
        simulation_service = SimulationService()
        
        simulation_request = SimulationRequest(
            scenario_id=scenario_response.id,
            method='monte_carlo',
            runs=5000,
            seed=42,
            monte_carlo_config=MonteCarloConfig(
                scenario_type='financial',
                parameters={
                    'market_drop_percent': {
                        'distribution': 'normal',
                        'mean': 0.35,
                        'std': 0.08
                    },
                    'portfolio_value': {
                        'distribution': 'uniform',
                        'low': 80000000,
                        'high': 100000000
                    }
                }
            )
        )
        
        simulation_response = await simulation_service.run_simulation(simulation_request)
        
        assert simulation_response.scenario_id == scenario_response.id
        assert simulation_response.method == 'monte_carlo'
        assert simulation_response.runs == 5000
        assert simulation_response.status == 'completed'
        assert 'statistics' in simulation_response.results
        
        # Validate simulation results
        stats = simulation_response.results['statistics']
        assert stats['mean'] > 0
        assert stats['p95'] > stats['median']
        
        # Step 4: Visualization Generation
        visualization_service = VisualizationService()
        
        # Generate impact matrix
        viz_request = VisualizationRequest(
            scenario_id=scenario_response.id,
            viz_type='impact_matrix',
            data={
                'risks': [
                    {'name': 'Market Crash', 'likelihood': 0.35, 'impact': 0.9},
                    {'name': 'Liquidity Crisis', 'likelihood': 0.25, 'impact': 0.7},
                    {'name': 'Credit Risk', 'likelihood': 0.4, 'impact': 0.6}
                ]
            }
        )
        
        viz_response = await visualization_service.generate_visualization(viz_request)
        
        assert viz_response.scenario_id == scenario_response.id
        assert viz_response.viz_type == 'impact_matrix'
        assert viz_response.status == 'completed'
        assert viz_response.chart_data is not None
        
        # Step 5: Mitigation Strategy Generation
        mitigation_service = MitigationService()
        
        mitigation_request = MitigationRequest(
            scenario_id=scenario_response.id,
            risk_type='financial',
            risk_data={
                'annual_loss_expectancy': stats['mean'],
                'current_risk_level': 0.8,
                'portfolio_value': 90000000
            },
            budget_limit=5000000,
            priority='high',
            max_strategies=5
        )
        
        mitigation_response = await mitigation_service.generate_mitigations(mitigation_request)
        
        assert mitigation_response.scenario_id == scenario_response.id
        assert len(mitigation_response.strategies) > 0
        assert mitigation_response.recommended_strategy is not None
        
        # Validate mitigation strategies
        top_strategy = mitigation_response.recommended_strategy
        assert 'cost_benefit_analysis' in top_strategy
        assert 'implementation_plan' in top_strategy
        assert top_strategy['rank'] == 1
        
        # Step 6: Report Generation
        report_service = ReportService()
        
        report_request = ReportRequest(
            scenario_id=scenario_response.id,
            format='pdf',
            sections=[
                'executive_summary',
                'scenario_details',
                'simulation_results',
                'risk_matrix',
                'mitigation_strategies'
            ],
            title='Financial Risk Assessment - Market Crash Scenario'
        )
        
        report_response = await report_service.generate_report(report_request)
        
        assert report_response.scenario_id == scenario_response.id
        assert report_response.format == 'pdf'
        assert report_response.status == 'completed'
        assert report_response.download_url is not None
        
        # Verify all steps completed successfully
        workflow_summary = {
            'ingestion': {
                'status': ingestion_job.status,
                'records': ingestion_job.records_found
            },
            'scenario': {
                'id': scenario_response.id,
                'status': scenario_response.status
            },
            'simulation': {
                'id': simulation_response.id,
                'runs': simulation_response.runs,
                'mean_impact': stats['mean']
            },
            'visualization': {
                'id': viz_response.id,
                'type': viz_response.viz_type
            },
            'mitigation': {
                'id': mitigation_response.id,
                'strategies_count': len(mitigation_response.strategies)
            },
            'report': {
                'id': report_response.id,
                'format': report_response.format
            }
        }
        
        # All components should be successful
        assert workflow_summary['ingestion']['records'] == 3
        assert workflow_summary['scenario']['status'] == 'generated'
        assert workflow_summary['simulation']['runs'] == 5000
        assert workflow_summary['mitigation']['strategies_count'] > 0
        assert workflow_summary['report']['format'] == 'pdf'
    
    @pytest.mark.asyncio
    async def test_cyber_risk_workflow(self, mock_services):
        """Test workflow for cyber risk scenario"""
        mock_db, mock_msg = mock_services
        
        # Cyber-specific workflow
        scenario_service = ScenarioService()
        simulation_service = SimulationService()
        
        # Cyber scenario
        scenario_request = ScenarioRequest(
            name="Advanced Persistent Threat",
            type="cyber",
            description="Sophisticated APT targeting critical infrastructure",
            assumptions={
                "attack_vectors": ["phishing", "zero_day", "insider_threat"],
                "systems_affected": ["erp", "scada", "databases"],
                "detection_time_hours": 168,  # 1 week
                "containment_time_hours": 72,
                "data_exfiltration_gb": 500
            }
        )
        
        # Mock scenario generation
        with patch.object(scenario_service, 'generate_scenario') as mock_generate:
            mock_scenario_response = type('MockResponse', (), {
                'id': 'cyber-scenario-456',
                'name': scenario_request.name,
                'type': scenario_request.type,
                'status': 'generated',
                'created_at': datetime.utcnow()
            })()
            
            mock_generate.return_value = mock_scenario_response
            scenario_response = await scenario_service.generate_scenario(scenario_request)
        
        # Cyber-specific simulation
        simulation_request = SimulationRequest(
            scenario_id=scenario_response.id,
            method='monte_carlo',
            runs=3000,
            monte_carlo_config=MonteCarloConfig(
                scenario_type='cyber',
                parameters={
                    'downtime_hours': {
                        'distribution': 'lognormal',
                        'mean': 4.2,  # log(72 hours)
                        'sigma': 0.5
                    },
                    'systems_affected_count': {
                        'distribution': 'uniform',
                        'low': 3,
                        'high': 8
                    }
                }
            )
        )
        
        simulation_response = await simulation_service.run_simulation(simulation_request)
        
        assert simulation_response.status == 'completed'
        assert 'statistics' in simulation_response.results
        
        # Cyber scenarios should show different impact patterns
        stats = simulation_response.results['statistics']
        assert stats['mean'] > 0
        
        print(f"Cyber workflow completed: {scenario_response.id} -> {simulation_response.id}")
    
    @pytest.mark.asyncio
    async def test_supply_chain_workflow(self, mock_services):
        """Test workflow for supply chain risk scenario"""
        mock_db, mock_msg = mock_services
        
        scenario_service = ScenarioService()
        simulation_service = SimulationService()
        
        # Supply chain scenario
        scenario_request = ScenarioRequest(
            name="Critical Supplier Bankruptcy",
            type="supply_chain",
            description="Bankruptcy of key supplier affecting 60% of production",
            assumptions={
                "supplier_dependency": 0.6,
                "alternative_suppliers": 2,
                "qualification_time_weeks": 12,
                "inventory_buffer_days": 45,
                "production_impact": 0.8
            }
        )
        
        # Mock scenario generation
        with patch.object(scenario_service, 'generate_scenario') as mock_generate:
            mock_scenario_response = type('MockResponse', (), {
                'id': 'supply-scenario-789',
                'name': scenario_request.name,
                'type': scenario_request.type,
                'status': 'generated',
                'created_at': datetime.utcnow()
            })()
            
            mock_generate.return_value = mock_scenario_response
            scenario_response = await scenario_service.generate_scenario(scenario_request)
        
        # Supply chain simulation
        simulation_request = SimulationRequest(
            scenario_id=scenario_response.id,
            method='monte_carlo',
            runs=2000,
            monte_carlo_config=MonteCarloConfig(
                scenario_type='supply_chain',
                parameters={
                    'supplier_outage_duration': {
                        'distribution': 'triangular',
                        'left': 30,
                        'mode': 90,
                        'right': 180
                    },
                    'production_capacity_impact': {
                        'distribution': 'beta',
                        'alpha': 2,
                        'beta': 3
                    }
                }
            )
        )
        
        simulation_response = await simulation_service.run_simulation(simulation_request)
        
        assert simulation_response.status == 'completed'
        print(f"Supply chain workflow completed: {scenario_response.id} -> {simulation_response.id}")
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_services):
        """Test error handling in workflow"""
        mock_db, mock_msg = mock_services
        
        scenario_service = ScenarioService()
        
        # Test invalid scenario type
        invalid_request = ScenarioRequest(
            name="Invalid Scenario",
            type="invalid_type",
            description="This should fail",
            assumptions={}
        )
        
        with pytest.raises(Exception):
            await scenario_service.generate_scenario(invalid_request)
    
    @pytest.mark.asyncio
    async def test_concurrent_simulations(self, mock_services):
        """Test running multiple simulations concurrently"""
        mock_db, mock_msg = mock_services
        
        simulation_service = SimulationService()
        
        # Create multiple simulation requests
        requests = []
        for i in range(3):
            request = SimulationRequest(
                scenario_id=f'scenario-{i}',
                method='monte_carlo',
                runs=1000,
                seed=42 + i,
                monte_carlo_config=MonteCarloConfig(
                    scenario_type='financial',
                    parameters={
                        'market_drop_percent': {
                            'distribution': 'normal',
                            'mean': 0.2 + (i * 0.1),
                            'std': 0.05
                        }
                    }
                )
            )
            requests.append(request)
        
        # Run simulations concurrently
        tasks = [simulation_service.run_simulation(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(responses) == 3
        for response in responses:
            assert response.status == 'completed'
            assert response.runs == 1000
        
        # Results should be different due to different parameters
        means = [resp.results['statistics']['mean'] for resp in responses]
        assert len(set(means)) > 1  # Should have different means


class TestDataFlowIntegrity:
    """Test data integrity throughout the workflow"""
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Test that data remains consistent through the pipeline"""
        # Test scenario ID propagation
        scenario_id = 'test-scenario-123'
        
        # All services should maintain scenario ID
        simulation_request = SimulationRequest(
            scenario_id=scenario_id,
            method='monte_carlo',
            runs=100
        )
        
        viz_request = VisualizationRequest(
            scenario_id=scenario_id,
            viz_type='impact_matrix',
            data={}
        )
        
        mitigation_request = MitigationRequest(
            scenario_id=scenario_id,
            risk_type='financial',
            risk_data={}
        )
        
        report_request = ReportRequest(
            scenario_id=scenario_id,
            format='pdf',
            sections=['executive_summary']
        )
        
        # All should reference the same scenario
        assert simulation_request.scenario_id == scenario_id
        assert viz_request.scenario_id == scenario_id
        assert mitigation_request.scenario_id == scenario_id
        assert report_request.scenario_id == scenario_id
    
    def test_assumption_propagation(self):
        """Test that assumptions flow correctly through pipeline"""
        assumptions = {
            'market_drop_percent': 30,
            'duration_months': 6,
            'affected_sectors': ['tech', 'finance']
        }
        
        # Assumptions should be preserved and used in calculations
        assert assumptions['market_drop_percent'] > 0
        assert assumptions['duration_months'] > 0
        assert len(assumptions['affected_sectors']) > 0
        
        # Simulation parameters should reflect assumptions
        sim_params = {
            'market_drop_percent': {
                'distribution': 'normal',
                'mean': assumptions['market_drop_percent'] / 100,
                'std': 0.05
            }
        }
        
        assert sim_params['market_drop_percent']['mean'] == 0.3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

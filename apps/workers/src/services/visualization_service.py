"""Visualization service for generating charts, matrices, and graphs"""

import uuid
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog
import base64
import io

from ..models.visualization import (
    VisualizationRequest, VisualizationResponse, ImpactMatrix,
    CausalGraph, SimulationChart, HeatmapConfig
)
from ..core.database import db_manager
from ..core.messaging import messaging_manager
from ..config import settings

logger = structlog.get_logger()


class ImpactMatrixGenerator:
    """Generate impact vs likelihood matrices"""
    
    def generate_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate impact matrix visualization"""
        try:
            # Extract risk data
            risks = data.get('risks', [])
            
            if not risks:
                # Generate sample data for demonstration
                risks = self._generate_sample_risks()
            
            # Create impact matrix
            fig = go.Figure()
            
            # Add risk points
            for risk in risks:
                fig.add_trace(go.Scatter(
                    x=[risk['likelihood']],
                    y=[risk['impact']],
                    mode='markers+text',
                    text=[risk['name']],
                    textposition="top center",
                    marker=dict(
                        size=risk.get('size', 20),
                        color=risk.get('color', 'blue'),
                        opacity=0.7
                    ),
                    name=risk['name']
                ))
            
            # Add risk zones
            self._add_risk_zones(fig)
            
            # Update layout
            fig.update_layout(
                title="Risk Impact vs Likelihood Matrix",
                xaxis_title="Likelihood",
                yaxis_title="Impact",
                xaxis=dict(range=[0, 1], tickformat='.0%'),
                yaxis=dict(range=[0, 1], tickformat='.0%'),
                showlegend=False,
                width=800,
                height=600
            )
            
            # Convert to JSON
            matrix_json = fig.to_json()
            
            # Generate summary statistics
            summary = self._calculate_matrix_summary(risks)
            
            return {
                'type': 'impact_matrix',
                'chart_data': matrix_json,
                'summary': summary,
                'risk_count': len(risks),
                'high_risk_count': len([r for r in risks if r['impact'] > 0.7 and r['likelihood'] > 0.5])
            }
            
        except Exception as e:
            logger.error("Impact matrix generation failed", error=str(e))
            raise
    
    def _generate_sample_risks(self) -> List[Dict[str, Any]]:
        """Generate sample risk data"""
        return [
            {'name': 'Cyber Attack', 'likelihood': 0.6, 'impact': 0.8, 'color': 'red', 'size': 25},
            {'name': 'Market Crash', 'likelihood': 0.2, 'impact': 0.9, 'color': 'orange', 'size': 30},
            {'name': 'Supplier Failure', 'likelihood': 0.4, 'impact': 0.6, 'color': 'yellow', 'size': 20},
            {'name': 'Regulatory Change', 'likelihood': 0.7, 'impact': 0.4, 'color': 'green', 'size': 15},
            {'name': 'Key Person Risk', 'likelihood': 0.3, 'impact': 0.5, 'color': 'blue', 'size': 18},
            {'name': 'Natural Disaster', 'likelihood': 0.1, 'impact': 0.7, 'color': 'purple', 'size': 22}
        ]
    
    def _add_risk_zones(self, fig):
        """Add risk zone backgrounds to matrix"""
        # High risk zone (top right)
        fig.add_shape(
            type="rect",
            x0=0.5, y0=0.7, x1=1.0, y1=1.0,
            fillcolor="red", opacity=0.1,
            layer="below", line_width=0
        )
        
        # Medium risk zones
        fig.add_shape(
            type="rect",
            x0=0.3, y0=0.5, x1=0.7, y1=0.8,
            fillcolor="orange", opacity=0.1,
            layer="below", line_width=0
        )
        
        # Low risk zone (bottom left)
        fig.add_shape(
            type="rect",
            x0=0.0, y0=0.0, x1=0.4, y1=0.4,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0
        )
    
    def _calculate_matrix_summary(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for risk matrix"""
        if not risks:
            return {}
        
        likelihoods = [r['likelihood'] for r in risks]
        impacts = [r['impact'] for r in risks]
        
        return {
            'average_likelihood': np.mean(likelihoods),
            'average_impact': np.mean(impacts),
            'risk_score': np.mean([l * i for l, i in zip(likelihoods, impacts)]),
            'highest_risk': max(risks, key=lambda r: r['likelihood'] * r['impact'])['name'],
            'risk_distribution': {
                'high': len([r for r in risks if r['likelihood'] * r['impact'] > 0.5]),
                'medium': len([r for r in risks if 0.2 < r['likelihood'] * r['impact'] <= 0.5]),
                'low': len([r for r in risks if r['likelihood'] * r['impact'] <= 0.2])
            }
        }


class CausalGraphGenerator:
    """Generate causal dependency graphs"""
    
    def generate_graph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate causal graph visualization"""
        try:
            # Extract dependencies
            dependencies = data.get('dependencies', [])
            
            if not dependencies:
                dependencies = self._generate_sample_dependencies()
            
            # Create network graph
            G = nx.DiGraph()
            
            # Add nodes and edges
            for dep in dependencies:
                G.add_edge(
                    dep['source'], 
                    dep['target'],
                    weight=dep.get('strength', 1.0),
                    delay=dep.get('delay', 0)
                )
            
            # Calculate layout
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Create plotly graph
            fig = self._create_network_plot(G, pos, dependencies)
            
            # Calculate network metrics
            metrics = self._calculate_network_metrics(G)
            
            return {
                'type': 'causal_graph',
                'chart_data': fig.to_json(),
                'network_metrics': metrics,
                'node_count': G.number_of_nodes(),
                'edge_count': G.number_of_edges(),
                'critical_paths': self._find_critical_paths(G)
            }
            
        except Exception as e:
            logger.error("Causal graph generation failed", error=str(e))
            raise
    
    def _generate_sample_dependencies(self) -> List[Dict[str, Any]]:
        """Generate sample dependency data"""
        return [
            {'source': 'Cyber Attack', 'target': 'System Downtime', 'strength': 0.9, 'delay': 1},
            {'source': 'System Downtime', 'target': 'Revenue Loss', 'strength': 0.8, 'delay': 2},
            {'source': 'System Downtime', 'target': 'Customer Impact', 'strength': 0.7, 'delay': 4},
            {'source': 'Customer Impact', 'target': 'Reputation Damage', 'strength': 0.6, 'delay': 24},
            {'source': 'Market Crash', 'target': 'Portfolio Loss', 'strength': 0.95, 'delay': 0},
            {'source': 'Portfolio Loss', 'target': 'Liquidity Crisis', 'strength': 0.5, 'delay': 12},
            {'source': 'Supplier Failure', 'target': 'Production Delay', 'strength': 0.8, 'delay': 8},
            {'source': 'Production Delay', 'target': 'Customer Impact', 'strength': 0.6, 'delay': 48},
            {'source': 'Liquidity Crisis', 'target': 'Credit Rating', 'strength': 0.7, 'delay': 168}
        ]
    
    def _create_network_plot(self, G: nx.DiGraph, pos: Dict, dependencies: List[Dict]) -> go.Figure:
        """Create network plot using plotly"""
        # Extract node and edge coordinates
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = list(G.nodes())
        
        # Create edges
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines',
            name='Dependencies'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=30,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            name='Events'
        ))
        
        # Update layout
        fig.update_layout(
            title="Causal Dependency Graph",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=800,
            height=600
        )
        
        return fig
    
    def _calculate_network_metrics(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Calculate network topology metrics"""
        try:
            return {
                'density': nx.density(G),
                'average_clustering': nx.average_clustering(G.to_undirected()),
                'number_of_components': nx.number_weakly_connected_components(G),
                'average_path_length': nx.average_shortest_path_length(G.to_undirected()) 
                    if nx.is_weakly_connected(G) else 0,
                'centrality_measures': {
                    'betweenness': dict(nx.betweenness_centrality(G)),
                    'closeness': dict(nx.closeness_centrality(G)),
                    'degree': dict(nx.degree_centrality(G))
                }
            }
        except Exception as e:
            logger.error("Network metrics calculation failed", error=str(e))
            return {}
    
    def _find_critical_paths(self, G: nx.DiGraph) -> List[List[str]]:
        """Find critical paths in the network"""
        try:
            # Find longest paths (simplified approach)
            critical_paths = []
            
            # Get source nodes (no predecessors)
            sources = [n for n in G.nodes() if G.in_degree(n) == 0]
            
            # Get sink nodes (no successors)
            sinks = [n for n in G.nodes() if G.out_degree(n) == 0]
            
            # Find paths from sources to sinks
            for source in sources:
                for sink in sinks:
                    try:
                        paths = list(nx.all_simple_paths(G, source, sink))
                        if paths:
                            # Add longest path
                            longest_path = max(paths, key=len)
                            if len(longest_path) > 2:  # Only include meaningful paths
                                critical_paths.append(longest_path)
                    except nx.NetworkXNoPath:
                        continue
            
            return critical_paths[:5]  # Return top 5 critical paths
            
        except Exception as e:
            logger.error("Critical path finding failed", error=str(e))
            return []


class SimulationChartGenerator:
    """Generate simulation result charts"""
    
    def generate_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simulation charts"""
        try:
            chart_type = data.get('chart_type', 'distribution')
            simulation_results = data.get('results', {})
            
            if chart_type == 'distribution':
                return self._generate_distribution_chart(simulation_results)
            elif chart_type == 'timeline':
                return self._generate_timeline_chart(simulation_results)
            elif chart_type == 'sensitivity':
                return self._generate_sensitivity_chart(simulation_results)
            elif chart_type == 'comparison':
                return self._generate_comparison_chart(simulation_results)
            else:
                raise ValueError(f"Unknown chart type: {chart_type}")
                
        except Exception as e:
            logger.error("Simulation chart generation failed", error=str(e))
            raise
    
    def _generate_distribution_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate distribution histogram"""
        distribution = results.get('distribution', [])
        
        if not distribution:
            # Generate sample distribution
            distribution = np.random.lognormal(13, 1, 10000).tolist()
        
        # Create histogram
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=distribution,
            nbinsx=50,
            name='Impact Distribution',
            marker_color='skyblue',
            opacity=0.7
        ))
        
        # Add percentile lines
        percentiles = [50, 75, 90, 95, 99]
        colors = ['green', 'yellow', 'orange', 'red', 'darkred']
        
        for p, color in zip(percentiles, colors):
            value = np.percentile(distribution, p)
            fig.add_vline(
                x=value,
                line_dash="dash",
                line_color=color,
                annotation_text=f"P{p}: ${value:,.0f}"
            )
        
        fig.update_layout(
            title="Monte Carlo Simulation Results - Impact Distribution",
            xaxis_title="Financial Impact ($)",
            yaxis_title="Frequency",
            width=800,
            height=500
        )
        
        # Calculate statistics
        stats = {
            'mean': np.mean(distribution),
            'median': np.median(distribution),
            'std': np.std(distribution),
            'percentiles': {f'p{p}': np.percentile(distribution, p) for p in percentiles}
        }
        
        return {
            'type': 'distribution_chart',
            'chart_data': fig.to_json(),
            'statistics': stats,
            'sample_size': len(distribution)
        }
    
    def _generate_timeline_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate timeline chart showing impact evolution"""
        # Generate sample timeline data
        days = list(range(0, 365, 30))
        impact_scenarios = {
            'Optimistic': [100, 80, 60, 40, 30, 20, 15, 10, 5, 2, 1, 0, 0],
            'Expected': [100, 90, 85, 75, 60, 45, 35, 25, 15, 10, 5, 2, 0],
            'Pessimistic': [100, 95, 92, 88, 80, 70, 60, 50, 40, 30, 20, 10, 5]
        }
        
        fig = go.Figure()
        
        colors = ['green', 'blue', 'red']
        for i, (scenario, values) in enumerate(impact_scenarios.items()):
            fig.add_trace(go.Scatter(
                x=days,
                y=values,
                mode='lines+markers',
                name=scenario,
                line=dict(color=colors[i], width=3)
            ))
        
        fig.update_layout(
            title="Risk Impact Timeline - Recovery Scenarios",
            xaxis_title="Days from Initial Event",
            yaxis_title="Impact Level (%)",
            width=800,
            height=500,
            yaxis=dict(range=[0, 105])
        )
        
        return {
            'type': 'timeline_chart',
            'chart_data': fig.to_json(),
            'scenarios': list(impact_scenarios.keys()),
            'duration_days': max(days)
        }
    
    def _generate_sensitivity_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sensitivity analysis chart"""
        # Generate sample sensitivity data
        parameters = ['Market Volatility', 'Recovery Time', 'System Redundancy', 
                     'Insurance Coverage', 'Response Speed']
        sensitivity_values = [0.8, 0.6, -0.4, -0.7, -0.5]
        
        fig = go.Figure()
        
        colors = ['red' if x > 0 else 'green' for x in sensitivity_values]
        
        fig.add_trace(go.Bar(
            x=parameters,
            y=sensitivity_values,
            marker_color=colors,
            name='Sensitivity'
        ))
        
        fig.update_layout(
            title="Parameter Sensitivity Analysis",
            xaxis_title="Parameters",
            yaxis_title="Impact on Total Risk",
            width=800,
            height=500
        )
        
        return {
            'type': 'sensitivity_chart',
            'chart_data': fig.to_json(),
            'most_sensitive': parameters[np.argmax(np.abs(sensitivity_values))],
            'sensitivity_scores': dict(zip(parameters, sensitivity_values))
        }
    
    def _generate_comparison_chart(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scenario comparison chart"""
        scenarios = ['Cyber Attack', 'Market Crash', 'Supply Chain', 'Pandemic']
        financial_impact = [2.5, 8.2, 3.1, 5.7]
        operational_impact = [6.8, 2.1, 7.3, 8.9]
        reputational_impact = [7.2, 4.5, 4.8, 3.2]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Financial Impact',
            x=scenarios,
            y=financial_impact,
            marker_color='red'
        ))
        
        fig.add_trace(go.Bar(
            name='Operational Impact',
            x=scenarios,
            y=operational_impact,
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            name='Reputational Impact',
            x=scenarios,
            y=reputational_impact,
            marker_color='orange'
        ))
        
        fig.update_layout(
            title="Scenario Impact Comparison",
            xaxis_title="Risk Scenarios",
            yaxis_title="Impact Score (1-10)",
            barmode='group',
            width=800,
            height=500
        )
        
        return {
            'type': 'comparison_chart',
            'chart_data': fig.to_json(),
            'scenarios': scenarios,
            'highest_financial': scenarios[np.argmax(financial_impact)],
            'highest_operational': scenarios[np.argmax(operational_impact)]
        }


class HeatmapGenerator:
    """Generate risk heatmaps"""
    
    def generate_heatmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk correlation heatmap"""
        try:
            # Generate sample correlation matrix
            risk_factors = ['Market Risk', 'Credit Risk', 'Operational Risk', 
                          'Liquidity Risk', 'Cyber Risk', 'Regulatory Risk']
            
            # Create correlation matrix
            np.random.seed(42)
            correlation_matrix = np.random.rand(len(risk_factors), len(risk_factors))
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            np.fill_diagonal(correlation_matrix, 1.0)
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=risk_factors,
                y=risk_factors,
                colorscale='RdYlBu_r',
                zmid=0,
                text=np.round(correlation_matrix, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Risk Factor Correlation Heatmap",
                width=600,
                height=600
            )
            
            return {
                'type': 'heatmap',
                'chart_data': fig.to_json(),
                'risk_factors': risk_factors,
                'highest_correlation': self._find_highest_correlation(correlation_matrix, risk_factors),
                'correlation_summary': self._summarize_correlations(correlation_matrix)
            }
            
        except Exception as e:
            logger.error("Heatmap generation failed", error=str(e))
            raise
    
    def _find_highest_correlation(self, matrix: np.ndarray, factors: List[str]) -> Dict[str, Any]:
        """Find highest correlation pair"""
        # Mask diagonal and upper triangle
        mask = np.triu(np.ones_like(matrix), k=1).astype(bool)
        masked_matrix = np.where(mask, matrix, -np.inf)
        
        # Find maximum
        max_idx = np.unravel_index(np.argmax(masked_matrix), masked_matrix.shape)
        
        return {
            'factor1': factors[max_idx[0]],
            'factor2': factors[max_idx[1]], 
            'correlation': float(matrix[max_idx])
        }
    
    def _summarize_correlations(self, matrix: np.ndarray) -> Dict[str, float]:
        """Summarize correlation statistics"""
        # Get upper triangle (excluding diagonal)
        upper_triangle = matrix[np.triu_indices_from(matrix, k=1)]
        
        return {
            'average_correlation': float(np.mean(upper_triangle)),
            'max_correlation': float(np.max(upper_triangle)),
            'min_correlation': float(np.min(upper_triangle)),
            'high_correlations_count': int(np.sum(upper_triangle > 0.7))
        }


class VisualizationService:
    """Main visualization service orchestrator"""
    
    def __init__(self):
        self.impact_matrix = ImpactMatrixGenerator()
        self.causal_graph = CausalGraphGenerator()
        self.sim_chart = SimulationChartGenerator()
        self.heatmap = HeatmapGenerator()
    
    async def generate_visualization(self, request: VisualizationRequest) -> VisualizationResponse:
        """Generate visualization based on request type"""
        try:
            viz_id = str(uuid.uuid4())
            
            logger.info("Starting visualization generation",
                       viz_id=viz_id,
                       type=request.viz_type,
                       scenario_id=request.scenario_id)
            
            # Generate appropriate visualization
            if request.viz_type == 'impact_matrix':
                result = self.impact_matrix.generate_matrix(request.data)
            elif request.viz_type == 'causal_graph':
                result = self.causal_graph.generate_graph(request.data)
            elif request.viz_type == 'simulation_chart':
                result = self.sim_chart.generate_chart(request.data)
            elif request.viz_type == 'heatmap':
                result = self.heatmap.generate_heatmap(request.data)
            else:
                raise ValueError(f"Unknown visualization type: {request.viz_type}")
            
            # Store visualization
            await self._store_visualization(viz_id, request, result)
            
            # Publish visualization completed event
            await messaging_manager.publish(
                "viz.make",
                json.dumps({
                    "event": "visualization_generated",
                    "viz_id": viz_id,
                    "scenario_id": request.scenario_id,
                    "type": request.viz_type
                }).encode()
            )
            
            return VisualizationResponse(
                id=viz_id,
                scenario_id=request.scenario_id,
                viz_type=request.viz_type,
                chart_data=result.get('chart_data'),
                metadata=result,
                status="completed",
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Visualization generation failed", error=str(e))
            raise
    
    async def _store_visualization(self, viz_id: str, request: VisualizationRequest, result: Dict[str, Any]):
        """Store visualization in database"""
        try:
            # In production, store in proper visualization table
            logger.info("Visualization generated and ready", 
                       viz_id=viz_id,
                       type=request.viz_type)
            
        except Exception as e:
            logger.error("Failed to store visualization", error=str(e))
            raise

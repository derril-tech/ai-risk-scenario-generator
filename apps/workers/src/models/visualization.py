"""Visualization models"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class VisualizationRequest(BaseModel):
    """Visualization request model"""
    scenario_id: str
    viz_type: str  # impact_matrix, causal_graph, simulation_chart, heatmap
    data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


class VisualizationResponse(BaseModel):
    """Visualization response model"""
    id: str
    scenario_id: str
    viz_type: str
    chart_data: Optional[str] = None  # JSON string of chart
    metadata: Dict[str, Any]
    status: str
    created_at: datetime


class ImpactMatrix(BaseModel):
    """Impact matrix configuration"""
    risks: List[Dict[str, Any]]
    x_axis: str = "likelihood"
    y_axis: str = "impact"
    color_scheme: str = "risk_zones"


class CausalGraph(BaseModel):
    """Causal graph configuration"""
    dependencies: List[Dict[str, Any]]
    layout: str = "spring"
    show_weights: bool = True


class SimulationChart(BaseModel):
    """Simulation chart configuration"""
    chart_type: str  # distribution, timeline, sensitivity, comparison
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]] = None


class HeatmapConfig(BaseModel):
    """Heatmap configuration"""
    matrix_data: List[List[float]]
    labels: List[str]
    color_scale: str = "RdYlBu_r"


class ChartStyle(BaseModel):
    """Chart styling configuration"""
    width: int = 800
    height: int = 600
    color_palette: List[str] = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    font_size: int = 12
    title_font_size: int = 16

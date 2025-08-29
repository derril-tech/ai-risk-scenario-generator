"""Scenario generation service using CrewAI"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI

from ..models.scenario import ScenarioRequest, ScenarioResponse, NarrativeSection
from ..core.database import db_manager
from ..core.messaging import messaging_manager
from ..config import settings

logger = structlog.get_logger()


class AssetQueryTool(BaseTool):
    """Tool for querying organizational assets"""
    
    name: str = "asset_query"
    description: str = "Query organizational assets by type, category, or value range"
    
    def _run(self, query: str) -> str:
        """Execute asset query"""
        try:
            # Mock asset data - in production, query from database
            assets = [
                {"name": "Primary Data Center", "type": "infrastructure", "value": 5000000},
                {"name": "Customer Database", "type": "data", "value": 2000000},
                {"name": "Trading System", "type": "application", "value": 3000000},
                {"name": "Supply Chain Network", "type": "process", "value": 10000000},
                {"name": "Brand Reputation", "type": "intangible", "value": 50000000}
            ]
            
            # Simple filtering based on query
            if "high value" in query.lower():
                assets = [a for a in assets if a["value"] > 1000000]
            elif "infrastructure" in query.lower():
                assets = [a for a in assets if a["type"] == "infrastructure"]
            elif "data" in query.lower():
                assets = [a for a in assets if a["type"] == "data"]
            
            return json.dumps(assets)
            
        except Exception as e:
            logger.error("Asset query failed", error=str(e))
            return "[]"


class ThreatIntelTool(BaseTool):
    """Tool for querying threat intelligence"""
    
    name: str = "threat_intel"
    description: str = "Query current threat landscape and attack patterns"
    
    def _run(self, threat_type: str) -> str:
        """Get threat intelligence"""
        try:
            # Mock threat intelligence - in production, integrate with threat feeds
            threats = {
                "cyber": [
                    {"name": "Ransomware", "likelihood": 0.3, "impact": "high"},
                    {"name": "Data Breach", "likelihood": 0.25, "impact": "high"},
                    {"name": "DDoS Attack", "likelihood": 0.4, "impact": "medium"}
                ],
                "financial": [
                    {"name": "Market Crash", "likelihood": 0.1, "impact": "critical"},
                    {"name": "Currency Devaluation", "likelihood": 0.2, "impact": "high"},
                    {"name": "Interest Rate Shock", "likelihood": 0.15, "impact": "high"}
                ],
                "supply_chain": [
                    {"name": "Supplier Bankruptcy", "likelihood": 0.05, "impact": "high"},
                    {"name": "Natural Disaster", "likelihood": 0.1, "impact": "critical"},
                    {"name": "Geopolitical Disruption", "likelihood": 0.2, "impact": "high"}
                ]
            }
            
            return json.dumps(threats.get(threat_type, []))
            
        except Exception as e:
            logger.error("Threat intel query failed", error=str(e))
            return "[]"


class ScenarioService:
    """Service for AI-driven scenario generation"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize CrewAI agents
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup CrewAI agents for scenario generation"""
        
        # Risk Analyst Agent
        self.risk_analyst = Agent(
            role="Senior Risk Analyst",
            goal="Analyze organizational vulnerabilities and threat landscapes",
            backstory="""You are a seasoned risk analyst with 15+ years of experience 
            in enterprise risk management. You specialize in identifying critical 
            vulnerabilities and understanding how threats can cascade across domains.""",
            tools=[AssetQueryTool(), ThreatIntelTool()],
            llm=self.llm,
            verbose=True
        )
        
        # Scenario Writer Agent
        self.scenario_writer = Agent(
            role="Risk Scenario Writer",
            goal="Create compelling, realistic risk scenarios with detailed narratives",
            backstory="""You are an expert storyteller who specializes in risk scenarios.
            You create vivid, realistic narratives that help executives understand 
            potential threats and their cascading impacts across the organization.""",
            llm=self.llm,
            verbose=True
        )
        
        # Quantitative Analyst Agent
        self.quant_analyst = Agent(
            role="Quantitative Risk Analyst", 
            goal="Define quantitative parameters and assumptions for risk scenarios",
            backstory="""You are a quantitative analyst with expertise in financial 
            modeling, Monte Carlo simulations, and statistical risk analysis. You 
            translate qualitative scenarios into quantifiable parameters.""",
            llm=self.llm,
            verbose=True
        )
    
    async def generate_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        """Generate AI-driven risk scenario"""
        try:
            scenario_id = str(uuid.uuid4())
            
            logger.info("Starting scenario generation", 
                       scenario_id=scenario_id, 
                       type=request.type,
                       name=request.name)
            
            # Create CrewAI tasks
            tasks = self._create_scenario_tasks(request)
            
            # Create and run crew
            crew = Crew(
                agents=[self.risk_analyst, self.scenario_writer, self.quant_analyst],
                tasks=tasks,
                verbose=True
            )
            
            # Execute scenario generation
            result = crew.kickoff()
            
            # Parse and structure the result
            narrative = self._parse_crew_result(result)
            
            # Store scenario in database
            await self._store_scenario(scenario_id, request, narrative)
            
            # Publish scenario generated event
            await messaging_manager.publish(
                "scenario.gen",
                json.dumps({
                    "event": "scenario_generated",
                    "scenario_id": scenario_id,
                    "type": request.type
                }).encode()
            )
            
            return ScenarioResponse(
                id=scenario_id,
                name=request.name,
                type=request.type,
                narrative=narrative,
                assumptions=request.assumptions,
                status="generated",
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Scenario generation failed", error=str(e))
            raise
    
    def _create_scenario_tasks(self, request: ScenarioRequest) -> List[Task]:
        """Create CrewAI tasks for scenario generation"""
        
        # Task 1: Risk Analysis
        risk_analysis_task = Task(
            description=f"""
            Analyze the risk landscape for a {request.type} scenario named "{request.name}".
            
            Context: {request.context or 'General enterprise environment'}
            Assumptions: {json.dumps(request.assumptions)}
            
            Your analysis should:
            1. Identify key organizational assets at risk
            2. Research current threat patterns for {request.type} risks
            3. Assess vulnerability points and attack vectors
            4. Determine potential cascading effects across domains
            
            Provide a structured analysis with specific asset names, threat likelihoods, 
            and vulnerability assessments.
            """,
            agent=self.risk_analyst,
            expected_output="Detailed risk analysis with assets, threats, and vulnerabilities"
        )
        
        # Task 2: Narrative Creation
        narrative_task = Task(
            description=f"""
            Based on the risk analysis, create a compelling narrative for the 
            {request.type} scenario "{request.name}".
            
            The narrative should include:
            1. Executive Summary (2-3 sentences)
            2. Detailed Timeline (Day 0 through recovery)
            3. Key Events and Triggers
            4. Cascading Impact Description
            5. Affected Stakeholders
            6. Business Impact Assessment
            
            Write in a professional tone suitable for executive briefings.
            Make it realistic and specific to the organization's context.
            """,
            agent=self.scenario_writer,
            expected_output="Complete scenario narrative with timeline and impact description"
        )
        
        # Task 3: Quantitative Parameters
        quant_task = Task(
            description=f"""
            Define quantitative parameters and assumptions for the scenario 
            "{request.name}" based on the risk analysis and narrative.
            
            Provide:
            1. Key Quantitative Drivers (with ranges and distributions)
            2. Financial Impact Parameters (direct and indirect costs)
            3. Operational Impact Metrics (downtime, capacity reduction)
            4. Recovery Time Estimates
            5. Probability Distributions for Monte Carlo simulation
            6. Correlation Factors between different impact areas
            
            Use realistic ranges based on industry benchmarks and historical data.
            """,
            agent=self.quant_analyst,
            expected_output="Structured quantitative parameters for simulation modeling"
        )
        
        return [risk_analysis_task, narrative_task, quant_task]
    
    def _parse_crew_result(self, result: str) -> Dict[str, Any]:
        """Parse CrewAI result into structured narrative"""
        try:
            # In a real implementation, you'd parse the structured output
            # For now, create a structured response based on the result
            
            return {
                "executive_summary": "AI-generated executive summary of the risk scenario",
                "timeline": [
                    {"day": 0, "event": "Initial trigger event occurs", "impact": "low"},
                    {"day": 1, "event": "First-order impacts manifest", "impact": "medium"},
                    {"day": 3, "event": "Cascading effects begin", "impact": "high"},
                    {"day": 7, "event": "Secondary systems affected", "impact": "high"},
                    {"day": 14, "event": "Recovery efforts initiated", "impact": "medium"},
                    {"day": 30, "event": "Full recovery achieved", "impact": "low"}
                ],
                "key_events": [
                    "Primary system failure",
                    "Backup system overload", 
                    "Customer impact escalation",
                    "Regulatory notification required"
                ],
                "affected_assets": [
                    {"name": "Primary Data Center", "impact_level": "critical"},
                    {"name": "Customer Database", "impact_level": "high"},
                    {"name": "Trading System", "impact_level": "medium"}
                ],
                "business_impact": {
                    "financial": {"min": 1000000, "max": 5000000, "currency": "USD"},
                    "operational": {"downtime_hours": 72, "capacity_reduction": 0.6},
                    "reputational": {"severity": "high", "recovery_months": 6}
                },
                "stakeholders": [
                    "Executive Leadership",
                    "IT Operations",
                    "Customer Service",
                    "Legal & Compliance",
                    "External Customers"
                ],
                "generated_content": result[:1000] + "..." if len(result) > 1000 else result
            }
            
        except Exception as e:
            logger.error("Failed to parse crew result", error=str(e))
            return {"error": "Failed to parse scenario generation result"}
    
    async def _store_scenario(self, scenario_id: str, request: ScenarioRequest, narrative: Dict[str, Any]):
        """Store generated scenario in database"""
        try:
            query = """
                INSERT INTO scenarios (id, name, description, type, status, assumptions, narrative, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """
            
            now = datetime.utcnow()
            await db_manager.execute_query(
                query,
                scenario_id,
                request.name,
                request.description,
                request.type,
                "generated",
                json.dumps(request.assumptions),
                json.dumps(narrative),
                now,
                now
            )
            
            logger.info("Scenario stored in database", scenario_id=scenario_id)
            
        except Exception as e:
            logger.error("Failed to store scenario", scenario_id=scenario_id, error=str(e))
            raise
    
    async def get_scenario_templates(self) -> List[Dict[str, Any]]:
        """Get available scenario templates"""
        return [
            {
                "id": "financial_market_crash",
                "name": "Market Crash Scenario",
                "type": "financial",
                "description": "Severe market downturn affecting portfolio values and liquidity",
                "default_assumptions": {
                    "market_drop_percent": 30,
                    "duration_months": 6,
                    "affected_sectors": ["technology", "finance", "retail"],
                    "liquidity_impact": 0.4,
                    "recovery_timeline": 18
                },
                "key_drivers": ["market_volatility", "investor_sentiment", "economic_indicators"]
            },
            {
                "id": "supply_chain_disruption",
                "name": "Supply Chain Disruption",
                "type": "supply_chain",
                "description": "Major supplier outage causing production delays and revenue loss",
                "default_assumptions": {
                    "supplier_outage_duration": 14,
                    "affected_products": ["product_a", "product_b"],
                    "alternative_suppliers_available": False,
                    "inventory_buffer_days": 7,
                    "production_capacity_impact": 0.7
                },
                "key_drivers": ["supplier_reliability", "inventory_levels", "alternative_sources"]
            },
            {
                "id": "cyber_ransomware",
                "name": "Ransomware Attack",
                "type": "cyber",
                "description": "Sophisticated ransomware attack encrypting critical business systems",
                "default_assumptions": {
                    "systems_affected": ["erp", "email", "file_servers", "databases"],
                    "downtime_hours": 72,
                    "data_recovery_possible": True,
                    "ransom_amount": 1000000,
                    "backup_integrity": 0.8
                },
                "key_drivers": ["system_vulnerabilities", "backup_effectiveness", "incident_response"]
            },
            {
                "id": "operational_pandemic",
                "name": "Pandemic Business Disruption",
                "type": "operational",
                "description": "Global pandemic affecting workforce availability and operations",
                "default_assumptions": {
                    "workforce_availability": 0.6,
                    "remote_work_capability": 0.8,
                    "duration_months": 12,
                    "customer_demand_change": -0.3,
                    "supply_chain_impact": 0.4
                },
                "key_drivers": ["workforce_flexibility", "digital_readiness", "customer_adaptation"]
            }
        ]

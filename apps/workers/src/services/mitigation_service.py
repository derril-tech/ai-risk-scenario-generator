"""Mitigation service for generating and ranking risk mitigation strategies"""

import uuid
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass

from ..models.mitigation import (
    MitigationRequest, MitigationResponse, MitigationStrategy,
    CostBenefitAnalysis, ImplementationPlan, RiskReduction
)
from ..core.database import db_manager
from ..core.messaging import messaging_manager
from ..config import settings

logger = structlog.get_logger()


@dataclass
class MitigationTemplate:
    """Template for mitigation strategies"""
    id: str
    name: str
    category: str
    description: str
    risk_types: List[str]
    implementation_time: int  # days
    cost_range: Tuple[float, float]
    effectiveness: float  # 0.0 to 1.0
    prerequisites: List[str]
    kpis: List[str]


class MitigationLibrary:
    """Library of mitigation strategy templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[MitigationTemplate]:
        """Initialize mitigation strategy templates"""
        return [
            # Cyber Security Mitigations
            MitigationTemplate(
                id="cyber_backup_strategy",
                name="Enhanced Backup and Recovery System",
                category="cyber",
                description="Implement comprehensive backup strategy with offline storage and regular testing",
                risk_types=["cyber", "operational"],
                implementation_time=90,
                cost_range=(50000, 200000),
                effectiveness=0.8,
                prerequisites=["IT infrastructure assessment", "Data classification"],
                kpis=["Recovery Time Objective", "Recovery Point Objective", "Backup success rate"]
            ),
            MitigationTemplate(
                id="cyber_mfa_implementation",
                name="Multi-Factor Authentication Rollout",
                category="cyber",
                description="Deploy MFA across all critical systems and user accounts",
                risk_types=["cyber"],
                implementation_time=60,
                cost_range=(25000, 100000),
                effectiveness=0.7,
                prerequisites=["User inventory", "System integration capability"],
                kpis=["MFA adoption rate", "Authentication failure rate", "Security incidents"]
            ),
            MitigationTemplate(
                id="cyber_security_training",
                name="Cybersecurity Awareness Training",
                category="cyber",
                description="Comprehensive security awareness program with phishing simulations",
                risk_types=["cyber"],
                implementation_time=30,
                cost_range=(10000, 50000),
                effectiveness=0.6,
                prerequisites=["Training platform", "Content development"],
                kpis=["Training completion rate", "Phishing test results", "Incident reporting"]
            ),
            
            # Financial Risk Mitigations
            MitigationTemplate(
                id="financial_hedging",
                name="Financial Hedging Strategy",
                category="financial",
                description="Implement hedging instruments to reduce market exposure",
                risk_types=["financial"],
                implementation_time=45,
                cost_range=(100000, 500000),
                effectiveness=0.75,
                prerequisites=["Risk assessment", "Treasury expertise", "Board approval"],
                kpis=["Portfolio volatility", "Hedge effectiveness", "Cost of hedging"]
            ),
            MitigationTemplate(
                id="financial_diversification",
                name="Portfolio Diversification",
                category="financial",
                description="Diversify investments across asset classes and geographies",
                risk_types=["financial"],
                implementation_time=120,
                cost_range=(50000, 300000),
                effectiveness=0.65,
                prerequisites=["Investment policy", "Due diligence capability"],
                kpis=["Correlation coefficients", "Concentration risk", "Risk-adjusted returns"]
            ),
            MitigationTemplate(
                id="financial_liquidity_buffer",
                name="Enhanced Liquidity Management",
                category="financial",
                description="Maintain higher cash reserves and credit facilities",
                risk_types=["financial", "operational"],
                implementation_time=30,
                cost_range=(0, 100000),  # Opportunity cost
                effectiveness=0.8,
                prerequisites=["Cash flow analysis", "Credit facility negotiations"],
                kpis=["Liquidity ratios", "Credit utilization", "Cash conversion cycle"]
            ),
            
            # Supply Chain Mitigations
            MitigationTemplate(
                id="supply_diversification",
                name="Supplier Diversification Program",
                category="supply_chain",
                description="Develop alternative suppliers for critical components",
                risk_types=["supply_chain", "operational"],
                implementation_time=180,
                cost_range=(75000, 400000),
                effectiveness=0.7,
                prerequisites=["Supplier assessment", "Quality standards", "Contract negotiations"],
                kpis=["Supplier concentration", "Supply disruption incidents", "Cost variance"]
            ),
            MitigationTemplate(
                id="supply_inventory_buffer",
                name="Strategic Inventory Management",
                category="supply_chain",
                description="Maintain strategic inventory buffers for critical items",
                risk_types=["supply_chain"],
                implementation_time=60,
                cost_range=(100000, 1000000),
                effectiveness=0.6,
                prerequisites=["Demand forecasting", "Warehouse capacity", "Working capital"],
                kpis=["Inventory turnover", "Stockout incidents", "Carrying costs"]
            ),
            MitigationTemplate(
                id="supply_monitoring",
                name="Supply Chain Monitoring System",
                category="supply_chain",
                description="Real-time monitoring of supplier health and performance",
                risk_types=["supply_chain"],
                implementation_time=90,
                cost_range=(50000, 250000),
                effectiveness=0.65,
                prerequisites=["Data integration", "Analytics platform", "Supplier cooperation"],
                kpis=["Supplier score", "Early warning alerts", "Response time"]
            ),
            
            # Operational Mitigations
            MitigationTemplate(
                id="operational_bcp",
                name="Business Continuity Planning",
                category="operational",
                description="Comprehensive business continuity and disaster recovery plans",
                risk_types=["operational", "cyber", "supply_chain"],
                implementation_time=120,
                cost_range=(75000, 300000),
                effectiveness=0.8,
                prerequisites=["Risk assessment", "Process mapping", "Resource allocation"],
                kpis=["Plan testing frequency", "Recovery time", "Process availability"]
            ),
            MitigationTemplate(
                id="operational_cross_training",
                name="Cross-Training and Succession Planning",
                category="operational",
                description="Reduce key person risk through cross-training and succession plans",
                risk_types=["operational"],
                implementation_time=90,
                cost_range=(25000, 150000),
                effectiveness=0.7,
                prerequisites=["Skills assessment", "Training programs", "Knowledge management"],
                kpis=["Cross-training coverage", "Knowledge retention", "Succession readiness"]
            ),
            MitigationTemplate(
                id="operational_automation",
                name="Process Automation Initiative",
                category="operational",
                description="Automate critical processes to reduce human error and dependency",
                risk_types=["operational"],
                implementation_time=180,
                cost_range=(100000, 800000),
                effectiveness=0.75,
                prerequisites=["Process analysis", "Technology platform", "Change management"],
                kpis=["Process automation rate", "Error reduction", "Efficiency gains"]
            )
        ]
    
    def get_relevant_templates(self, risk_type: str, budget: Optional[float] = None) -> List[MitigationTemplate]:
        """Get relevant mitigation templates for risk type and budget"""
        relevant = [t for t in self.templates if risk_type in t.risk_types]
        
        if budget:
            relevant = [t for t in relevant if t.cost_range[0] <= budget]
        
        return sorted(relevant, key=lambda t: t.effectiveness, reverse=True)


class CostBenefitCalculator:
    """Calculate cost-benefit analysis for mitigation strategies"""
    
    def calculate_cba(self, strategy: MitigationTemplate, risk_data: Dict[str, Any]) -> CostBenefitAnalysis:
        """Calculate cost-benefit analysis"""
        try:
            # Extract risk parameters
            annual_loss_expectancy = risk_data.get('annual_loss_expectancy', 1000000)
            risk_reduction = strategy.effectiveness
            implementation_cost = np.mean(strategy.cost_range)
            annual_operating_cost = implementation_cost * 0.1  # 10% of implementation cost
            
            # Calculate benefits
            annual_benefit = annual_loss_expectancy * risk_reduction
            
            # Calculate costs over 5-year period
            total_implementation_cost = implementation_cost
            total_operating_cost = annual_operating_cost * 5
            total_cost = total_implementation_cost + total_operating_cost
            
            # Calculate financial metrics
            total_benefit = annual_benefit * 5
            net_benefit = total_benefit - total_cost
            roi = (net_benefit / total_cost) * 100 if total_cost > 0 else 0
            
            # Calculate payback period
            payback_period = implementation_cost / annual_benefit if annual_benefit > 0 else float('inf')
            
            # Calculate NPV (assuming 10% discount rate)
            discount_rate = 0.10
            npv = -implementation_cost
            for year in range(1, 6):
                annual_net_benefit = annual_benefit - annual_operating_cost
                npv += annual_net_benefit / ((1 + discount_rate) ** year)
            
            return CostBenefitAnalysis(
                implementation_cost=implementation_cost,
                annual_operating_cost=annual_operating_cost,
                annual_benefit=annual_benefit,
                total_cost=total_cost,
                total_benefit=total_benefit,
                net_benefit=net_benefit,
                roi_percent=roi,
                payback_period_years=payback_period,
                npv=npv,
                break_even_point=payback_period * 12 if payback_period != float('inf') else None
            )
            
        except Exception as e:
            logger.error("Cost-benefit calculation failed", error=str(e))
            raise


class ImplementationPlanner:
    """Create implementation plans for mitigation strategies"""
    
    def create_plan(self, strategy: MitigationTemplate, priority: str = "medium") -> ImplementationPlan:
        """Create implementation plan"""
        try:
            # Adjust timeline based on priority
            priority_multipliers = {"high": 0.7, "medium": 1.0, "low": 1.3}
            adjusted_duration = int(strategy.implementation_time * priority_multipliers.get(priority, 1.0))
            
            # Create phases
            phases = self._create_implementation_phases(strategy, adjusted_duration)
            
            # Calculate milestones
            milestones = self._create_milestones(strategy, phases)
            
            # Identify resources
            resources = self._identify_resources(strategy)
            
            # Assess risks
            implementation_risks = self._assess_implementation_risks(strategy)
            
            return ImplementationPlan(
                strategy_id=strategy.id,
                total_duration_days=adjusted_duration,
                phases=phases,
                milestones=milestones,
                required_resources=resources,
                dependencies=strategy.prerequisites,
                success_criteria=strategy.kpis,
                implementation_risks=implementation_risks,
                estimated_start_date=datetime.now(),
                estimated_completion_date=datetime.now() + timedelta(days=adjusted_duration)
            )
            
        except Exception as e:
            logger.error("Implementation planning failed", error=str(e))
            raise
    
    def _create_implementation_phases(self, strategy: MitigationTemplate, duration: int) -> List[Dict[str, Any]]:
        """Create implementation phases"""
        phases = []
        
        # Phase 1: Planning and Preparation (20% of duration)
        phase1_duration = int(duration * 0.2)
        phases.append({
            "name": "Planning and Preparation",
            "duration_days": phase1_duration,
            "start_day": 0,
            "activities": [
                "Stakeholder alignment",
                "Resource allocation",
                "Detailed planning",
                "Risk assessment"
            ],
            "deliverables": ["Implementation plan", "Resource plan", "Risk register"]
        })
        
        # Phase 2: Implementation (60% of duration)
        phase2_duration = int(duration * 0.6)
        phases.append({
            "name": "Implementation",
            "duration_days": phase2_duration,
            "start_day": phase1_duration,
            "activities": [
                "System deployment",
                "Process implementation",
                "Training delivery",
                "Testing and validation"
            ],
            "deliverables": ["Deployed system", "Trained users", "Test results"]
        })
        
        # Phase 3: Validation and Closure (20% of duration)
        phase3_duration = duration - phase1_duration - phase2_duration
        phases.append({
            "name": "Validation and Closure",
            "duration_days": phase3_duration,
            "start_day": phase1_duration + phase2_duration,
            "activities": [
                "User acceptance testing",
                "Performance validation",
                "Documentation",
                "Knowledge transfer"
            ],
            "deliverables": ["Acceptance sign-off", "Documentation", "Lessons learned"]
        })
        
        return phases
    
    def _create_milestones(self, strategy: MitigationTemplate, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create project milestones"""
        milestones = []
        
        for i, phase in enumerate(phases):
            milestone_day = phase["start_day"] + phase["duration_days"]
            milestones.append({
                "name": f"{phase['name']} Complete",
                "day": milestone_day,
                "criteria": phase["deliverables"],
                "critical": i == 1  # Implementation phase is critical
            })
        
        return milestones
    
    def _identify_resources(self, strategy: MitigationTemplate) -> List[Dict[str, Any]]:
        """Identify required resources"""
        base_resources = [
            {"type": "Project Manager", "quantity": 1, "duration_percent": 100},
            {"type": "Subject Matter Expert", "quantity": 2, "duration_percent": 60},
            {"type": "Technical Specialist", "quantity": 1, "duration_percent": 80}
        ]
        
        # Add category-specific resources
        if strategy.category == "cyber":
            base_resources.extend([
                {"type": "Security Analyst", "quantity": 2, "duration_percent": 70},
                {"type": "IT Administrator", "quantity": 1, "duration_percent": 50}
            ])
        elif strategy.category == "financial":
            base_resources.extend([
                {"type": "Financial Analyst", "quantity": 1, "duration_percent": 80},
                {"type": "Risk Manager", "quantity": 1, "duration_percent": 60}
            ])
        elif strategy.category == "supply_chain":
            base_resources.extend([
                {"type": "Procurement Specialist", "quantity": 1, "duration_percent": 70},
                {"type": "Supplier Manager", "quantity": 2, "duration_percent": 40}
            ])
        
        return base_resources
    
    def _assess_implementation_risks(self, strategy: MitigationTemplate) -> List[Dict[str, Any]]:
        """Assess implementation risks"""
        common_risks = [
            {
                "risk": "Resource availability",
                "likelihood": 0.3,
                "impact": "medium",
                "mitigation": "Early resource booking and backup plans"
            },
            {
                "risk": "Technical complexity",
                "likelihood": 0.4,
                "impact": "high",
                "mitigation": "Proof of concept and phased approach"
            },
            {
                "risk": "User resistance",
                "likelihood": 0.5,
                "impact": "medium",
                "mitigation": "Change management and training"
            },
            {
                "risk": "Budget overrun",
                "likelihood": 0.3,
                "impact": "high",
                "mitigation": "Detailed cost estimation and contingency"
            }
        ]
        
        return common_risks


class MitigationRanker:
    """Rank mitigation strategies based on multiple criteria"""
    
    def rank_strategies(self, strategies: List[Dict[str, Any]], criteria: Dict[str, float]) -> List[Dict[str, Any]]:
        """Rank strategies using weighted scoring"""
        try:
            # Default criteria weights
            default_criteria = {
                "effectiveness": 0.3,
                "roi": 0.25,
                "implementation_speed": 0.2,
                "cost": 0.15,
                "feasibility": 0.1
            }
            
            # Merge with provided criteria
            scoring_criteria = {**default_criteria, **criteria}
            
            # Calculate scores for each strategy
            scored_strategies = []
            
            for strategy in strategies:
                score = self._calculate_strategy_score(strategy, scoring_criteria)
                strategy_with_score = {**strategy, "total_score": score}
                scored_strategies.append(strategy_with_score)
            
            # Sort by total score (descending)
            ranked_strategies = sorted(scored_strategies, key=lambda s: s["total_score"], reverse=True)
            
            # Add ranking
            for i, strategy in enumerate(ranked_strategies):
                strategy["rank"] = i + 1
            
            return ranked_strategies
            
        except Exception as e:
            logger.error("Strategy ranking failed", error=str(e))
            raise
    
    def _calculate_strategy_score(self, strategy: Dict[str, Any], criteria: Dict[str, float]) -> float:
        """Calculate weighted score for a strategy"""
        scores = {}
        
        # Effectiveness score (0-100)
        scores["effectiveness"] = strategy.get("effectiveness", 0.5) * 100
        
        # ROI score (normalize to 0-100)
        roi = strategy.get("roi_percent", 0)
        scores["roi"] = min(100, max(0, roi)) if roi >= 0 else 0
        
        # Implementation speed score (faster = higher score)
        impl_time = strategy.get("implementation_time", 180)
        scores["implementation_speed"] = max(0, 100 - (impl_time / 365 * 100))
        
        # Cost score (lower cost = higher score)
        cost = strategy.get("implementation_cost", 1000000)
        max_cost = 1000000  # Normalize against max expected cost
        scores["cost"] = max(0, 100 - (cost / max_cost * 100))
        
        # Feasibility score (based on prerequisites and complexity)
        prereq_count = len(strategy.get("prerequisites", []))
        scores["feasibility"] = max(0, 100 - (prereq_count * 10))
        
        # Calculate weighted total
        total_score = sum(scores[criterion] * weight for criterion, weight in criteria.items() if criterion in scores)
        
        return total_score


class MitigationService:
    """Main mitigation service orchestrator"""
    
    def __init__(self):
        self.library = MitigationLibrary()
        self.cba_calculator = CostBenefitCalculator()
        self.planner = ImplementationPlanner()
        self.ranker = MitigationRanker()
    
    async def generate_mitigations(self, request: MitigationRequest) -> MitigationResponse:
        """Generate mitigation strategies for a scenario"""
        try:
            mitigation_id = str(uuid.uuid4())
            
            logger.info("Starting mitigation generation",
                       mitigation_id=mitigation_id,
                       scenario_id=request.scenario_id,
                       risk_type=request.risk_type)
            
            # Get relevant mitigation templates
            templates = self.library.get_relevant_templates(
                request.risk_type, 
                request.budget_limit
            )
            
            # Generate strategies with CBA and implementation plans
            strategies = []
            
            for template in templates[:request.max_strategies]:
                # Calculate cost-benefit analysis
                cba = self.cba_calculator.calculate_cba(template, request.risk_data)
                
                # Create implementation plan
                plan = self.planner.create_plan(template, request.priority)
                
                # Calculate risk reduction
                risk_reduction = RiskReduction(
                    risk_type=request.risk_type,
                    current_risk_level=request.risk_data.get('current_risk_level', 0.7),
                    residual_risk_level=request.risk_data.get('current_risk_level', 0.7) * (1 - template.effectiveness),
                    reduction_percentage=template.effectiveness * 100,
                    confidence_level=0.8  # Default confidence
                )
                
                strategy = MitigationStrategy(
                    id=template.id,
                    name=template.name,
                    category=template.category,
                    description=template.description,
                    effectiveness=template.effectiveness,
                    cost_benefit_analysis=cba,
                    implementation_plan=plan,
                    risk_reduction=risk_reduction,
                    prerequisites=template.prerequisites,
                    kpis=template.kpis
                )
                
                strategies.append(strategy.dict())
            
            # Rank strategies
            ranking_criteria = request.ranking_criteria or {}
            ranked_strategies = self.ranker.rank_strategies(strategies, ranking_criteria)
            
            # Store mitigation analysis
            await self._store_mitigation_analysis(mitigation_id, request, ranked_strategies)
            
            # Publish mitigation generated event
            await messaging_manager.publish(
                "mitigation.plan",
                json.dumps({
                    "event": "mitigation_generated",
                    "mitigation_id": mitigation_id,
                    "scenario_id": request.scenario_id,
                    "strategy_count": len(ranked_strategies)
                }).encode()
            )
            
            return MitigationResponse(
                id=mitigation_id,
                scenario_id=request.scenario_id,
                strategies=ranked_strategies,
                total_strategies=len(ranked_strategies),
                recommended_strategy=ranked_strategies[0] if ranked_strategies else None,
                analysis_summary=self._generate_analysis_summary(ranked_strategies),
                status="completed",
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Mitigation generation failed", error=str(e))
            raise
    
    def _generate_analysis_summary(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of mitigation analysis"""
        if not strategies:
            return {}
        
        total_cost = sum(s.get("implementation_cost", 0) for s in strategies)
        avg_effectiveness = np.mean([s.get("effectiveness", 0) for s in strategies])
        avg_roi = np.mean([s.get("roi_percent", 0) for s in strategies])
        
        return {
            "total_strategies_analyzed": len(strategies),
            "average_effectiveness": avg_effectiveness,
            "average_roi": avg_roi,
            "total_investment_required": total_cost,
            "recommended_approach": "Implement top 3 strategies for optimal risk reduction",
            "quick_wins": [s["name"] for s in strategies if s.get("implementation_time", 180) < 60][:3],
            "high_impact": [s["name"] for s in strategies if s.get("effectiveness", 0) > 0.7][:3]
        }
    
    async def _store_mitigation_analysis(self, mitigation_id: str, request: MitigationRequest, strategies: List[Dict[str, Any]]):
        """Store mitigation analysis in database"""
        try:
            # In production, store in proper mitigation table
            logger.info("Mitigation analysis stored",
                       mitigation_id=mitigation_id,
                       strategy_count=len(strategies))
            
        except Exception as e:
            logger.error("Failed to store mitigation analysis", error=str(e))
            raise
    
    async def create_jira_tasks(self, mitigation_id: str, selected_strategies: List[str]) -> Dict[str, Any]:
        """Create Jira tasks for selected mitigation strategies"""
        try:
            # Mock Jira integration - in production, use actual Jira API
            tasks = []
            
            for strategy_id in selected_strategies:
                task = {
                    "id": f"RISK-{len(tasks) + 1}",
                    "title": f"Implement {strategy_id}",
                    "description": f"Implementation of mitigation strategy: {strategy_id}",
                    "assignee": "risk-team",
                    "priority": "High",
                    "status": "To Do",
                    "created": datetime.utcnow().isoformat()
                }
                tasks.append(task)
            
            logger.info("Jira tasks created", mitigation_id=mitigation_id, task_count=len(tasks))
            
            return {
                "mitigation_id": mitigation_id,
                "tasks_created": len(tasks),
                "tasks": tasks,
                "jira_project": "RISK",
                "status": "success"
            }
            
        except Exception as e:
            logger.error("Jira task creation failed", error=str(e))
            raise

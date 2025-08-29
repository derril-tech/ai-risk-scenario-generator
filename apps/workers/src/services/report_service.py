"""Advanced report generation service with PDF, JSON, and CSV export"""

import uuid
import json
import io
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ..models.report import (
    ReportRequest, ReportResponse, ReportSection, 
    ExecutiveSummary, RiskAssessment, ComplianceReport
)
from ..core.database import db_manager
from ..core.messaging import messaging_manager
from ..config import settings

logger = structlog.get_logger()


class PDFReportGenerator:
    """Generate PDF reports using ReportLab"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            
            # Build report content
            story = []
            
            # Title page
            story.extend(self._create_title_page(report_data))
            story.append(PageBreak())
            
            # Table of contents
            story.extend(self._create_table_of_contents(report_data))
            story.append(PageBreak())
            
            # Report sections
            sections = report_data.get('sections', [])
            
            for section in sections:
                if section == 'executive_summary':
                    story.extend(self._create_executive_summary(report_data))
                elif section == 'scenario_details':
                    story.extend(self._create_scenario_details(report_data))
                elif section == 'simulation_results':
                    story.extend(self._create_simulation_results(report_data))
                elif section == 'risk_matrix':
                    story.extend(self._create_risk_matrix(report_data))
                elif section == 'mitigation_strategies':
                    story.extend(self._create_mitigation_strategies(report_data))
                elif section == 'compliance_overview':
                    story.extend(self._create_compliance_overview(report_data))
                elif section == 'appendices':
                    story.extend(self._create_appendices(report_data))
                
                story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error("PDF generation failed", error=str(e))
            raise
    
    def _create_title_page(self, report_data: Dict[str, Any]) -> List:
        """Create title page"""
        story = []
        
        # Title
        title = report_data.get('title', 'Risk Assessment Report')
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        scenario_name = report_data.get('scenario_name', 'Risk Scenario Analysis')
        story.append(Paragraph(scenario_name, self.styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        metadata = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Scenario Type:', report_data.get('scenario_type', 'Multi-domain')],
            ['Analysis Period:', report_data.get('analysis_period', '12 months')],
            ['Confidence Level:', report_data.get('confidence_level', '95%')],
            ['Report Version:', report_data.get('version', '1.0')]
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = """
        <b>CONFIDENTIAL</b><br/>
        This report contains confidential and proprietary information. 
        Distribution is restricted to authorized personnel only.
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        return story
    
    def _create_table_of_contents(self, report_data: Dict[str, Any]) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        sections = report_data.get('sections', [])
        section_names = {
            'executive_summary': 'Executive Summary',
            'scenario_details': 'Scenario Details',
            'simulation_results': 'Simulation Results',
            'risk_matrix': 'Risk Assessment Matrix',
            'mitigation_strategies': 'Mitigation Strategies',
            'compliance_overview': 'Compliance Overview',
            'appendices': 'Appendices'
        }
        
        toc_data = []
        page_num = 3  # Starting page after title and TOC
        
        for section in sections:
            section_name = section_names.get(section, section.replace('_', ' ').title())
            toc_data.append([section_name, str(page_num)])
            page_num += 2  # Estimate 2 pages per section
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        
        story.append(toc_table)
        
        return story
    
    def _create_executive_summary(self, report_data: Dict[str, Any]) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key findings
        summary_text = report_data.get('executive_summary', {})
        
        # Risk overview
        story.append(Paragraph("<b>Risk Overview</b>", self.styles['Heading3']))
        risk_overview = summary_text.get('risk_overview', 
            "This analysis examines potential risk scenarios and their impact on organizational objectives.")
        story.append(Paragraph(risk_overview, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        story.append(Paragraph("<b>Key Risk Metrics</b>", self.styles['Heading3']))
        
        metrics_data = [
            ['Metric', 'Value', 'Risk Level'],
            ['Expected Annual Loss', '$2.5M', 'High'],
            ['Maximum Potential Loss', '$15.2M', 'Critical'],
            ['Recovery Time Estimate', '72 hours', 'Medium'],
            ['Mitigation Coverage', '65%', 'Medium']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("<b>Key Recommendations</b>", self.styles['Heading3']))
        recommendations = [
            "Implement enhanced backup and recovery systems",
            "Diversify supplier base to reduce concentration risk",
            "Establish crisis communication protocols",
            "Increase cybersecurity training frequency",
            "Review and update business continuity plans"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
        
        return story
    
    def _create_scenario_details(self, report_data: Dict[str, Any]) -> List:
        """Create scenario details section"""
        story = []
        
        story.append(Paragraph("Scenario Details", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        scenario = report_data.get('scenario', {})
        
        # Scenario description
        story.append(Paragraph("<b>Scenario Description</b>", self.styles['Heading3']))
        description = scenario.get('description', 'Detailed scenario description not available.')
        story.append(Paragraph(description, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Timeline
        story.append(Paragraph("<b>Event Timeline</b>", self.styles['Heading3']))
        timeline = scenario.get('timeline', [])
        
        if timeline:
            timeline_data = [['Day', 'Event', 'Impact Level']]
            for event in timeline[:10]:  # Limit to first 10 events
                timeline_data.append([
                    str(event.get('day', 0)),
                    event.get('event', ''),
                    event.get('impact', 'Unknown')
                ])
            
            timeline_table = Table(timeline_data, colWidths=[0.8*inch, 3.5*inch, 1.2*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(timeline_table)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Assumptions
        story.append(Paragraph("<b>Key Assumptions</b>", self.styles['Heading3']))
        assumptions = scenario.get('assumptions', {})
        
        for key, value in assumptions.items():
            assumption_text = f"<b>{key.replace('_', ' ').title()}:</b> {value}"
            story.append(Paragraph(assumption_text, self.styles['Normal']))
        
        return story
    
    def _create_simulation_results(self, report_data: Dict[str, Any]) -> List:
        """Create simulation results section"""
        story = []
        
        story.append(Paragraph("Simulation Results", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        simulation = report_data.get('simulation_results', {})
        
        # Statistics summary
        story.append(Paragraph("<b>Statistical Summary</b>", self.styles['Heading3']))
        
        stats = simulation.get('statistics', {})
        stats_data = [
            ['Statistic', 'Value'],
            ['Mean Impact', f"${stats.get('mean', 0):,.0f}"],
            ['Median Impact', f"${stats.get('median', 0):,.0f}"],
            ['Standard Deviation', f"${stats.get('std', 0):,.0f}"],
            ['95th Percentile', f"${stats.get('p95', 0):,.0f}"],
            ['99th Percentile', f"${stats.get('p99', 0):,.0f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk distribution chart (placeholder)
        story.append(Paragraph("<b>Risk Distribution Analysis</b>", self.styles['Heading3']))
        story.append(Paragraph(
            "The Monte Carlo simulation was run with 10,000 iterations to model the range of potential outcomes. "
            "The distribution shows the probability of different impact levels occurring.",
            self.styles['Normal']
        ))
        
        return story
    
    def _create_risk_matrix(self, report_data: Dict[str, Any]) -> List:
        """Create risk matrix section"""
        story = []
        
        story.append(Paragraph("Risk Assessment Matrix", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Risk categories
        story.append(Paragraph("<b>Risk Categories</b>", self.styles['Heading3']))
        
        risks = report_data.get('risks', [])
        if risks:
            risk_data = [['Risk', 'Likelihood', 'Impact', 'Risk Level']]
            
            for risk in risks[:10]:  # Limit to top 10 risks
                risk_level = self._calculate_risk_level(
                    risk.get('likelihood', 0.5), 
                    risk.get('impact', 0.5)
                )
                
                risk_data.append([
                    risk.get('name', 'Unknown Risk'),
                    f"{risk.get('likelihood', 0.5)*100:.0f}%",
                    f"{risk.get('impact', 0.5)*100:.0f}%",
                    risk_level
                ])
            
            risk_table = Table(risk_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(risk_table)
        
        return story
    
    def _create_mitigation_strategies(self, report_data: Dict[str, Any]) -> List:
        """Create mitigation strategies section"""
        story = []
        
        story.append(Paragraph("Mitigation Strategies", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        strategies = report_data.get('mitigation_strategies', [])
        
        for i, strategy in enumerate(strategies[:5], 1):  # Top 5 strategies
            story.append(Paragraph(f"<b>Strategy {i}: {strategy.get('name', 'Unknown Strategy')}</b>", 
                                 self.styles['Heading3']))
            
            # Strategy details
            details = [
                f"<b>Description:</b> {strategy.get('description', 'No description available')}",
                f"<b>Implementation Cost:</b> ${strategy.get('implementation_cost', 0):,.0f}",
                f"<b>Expected ROI:</b> {strategy.get('roi_percent', 0):.1f}%",
                f"<b>Implementation Time:</b> {strategy.get('implementation_time', 0)} days",
                f"<b>Risk Reduction:</b> {strategy.get('effectiveness', 0)*100:.0f}%"
            ]
            
            for detail in details:
                story.append(Paragraph(detail, self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_compliance_overview(self, report_data: Dict[str, Any]) -> List:
        """Create compliance overview section"""
        story = []
        
        story.append(Paragraph("Compliance Overview", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Regulatory frameworks
        story.append(Paragraph("<b>Regulatory Framework Alignment</b>", self.styles['Heading3']))
        
        frameworks = [
            "ISO 31000 - Risk Management Guidelines",
            "NIST Risk Management Framework",
            "COSO Enterprise Risk Management",
            "Basel III Capital Requirements",
            "SOX Section 404 - Internal Controls"
        ]
        
        for framework in frameworks:
            story.append(Paragraph(f"• {framework}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Compliance status
        story.append(Paragraph("<b>Compliance Status</b>", self.styles['Heading3']))
        story.append(Paragraph(
            "This risk assessment has been conducted in accordance with established "
            "risk management frameworks and regulatory requirements. All identified "
            "risks have been properly documented and assessed using quantitative methods.",
            self.styles['Normal']
        ))
        
        return story
    
    def _create_appendices(self, report_data: Dict[str, Any]) -> List:
        """Create appendices section"""
        story = []
        
        story.append(Paragraph("Appendices", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Methodology
        story.append(Paragraph("<b>Appendix A: Methodology</b>", self.styles['Heading3']))
        methodology_text = """
        This risk assessment was conducted using a combination of quantitative and qualitative methods:
        
        1. Monte Carlo simulation with 10,000 iterations
        2. Expert judgment and historical data analysis
        3. Scenario-based stress testing
        4. Cross-domain dependency modeling
        
        All simulations were performed using industry-standard risk modeling techniques
        and validated against historical loss data where available.
        """
        story.append(Paragraph(methodology_text, self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Data sources
        story.append(Paragraph("<b>Appendix B: Data Sources</b>", self.styles['Heading3']))
        data_sources = [
            "Internal financial systems and databases",
            "Historical loss event database",
            "Industry benchmark data",
            "Regulatory guidance and requirements",
            "Third-party risk intelligence feeds"
        ]
        
        for source in data_sources:
            story.append(Paragraph(f"• {source}", self.styles['Normal']))
        
        return story
    
    def _calculate_risk_level(self, likelihood: float, impact: float) -> str:
        """Calculate risk level based on likelihood and impact"""
        risk_score = likelihood * impact
        
        if risk_score >= 0.6:
            return "High"
        elif risk_score >= 0.3:
            return "Medium"
        else:
            return "Low"


class JSONReportGenerator:
    """Generate JSON format reports"""
    
    def generate_json(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        try:
            # Structure the report data
            json_report = {
                "report_metadata": {
                    "id": report_data.get('id', str(uuid.uuid4())),
                    "title": report_data.get('title', 'Risk Assessment Report'),
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": report_data.get('version', '1.0'),
                    "format": "json"
                },
                "scenario": report_data.get('scenario', {}),
                "simulation_results": report_data.get('simulation_results', {}),
                "risk_assessment": {
                    "risks": report_data.get('risks', []),
                    "risk_matrix": report_data.get('risk_matrix', {}),
                    "overall_risk_score": report_data.get('overall_risk_score', 0)
                },
                "mitigation_strategies": report_data.get('mitigation_strategies', []),
                "compliance": {
                    "frameworks": report_data.get('compliance_frameworks', []),
                    "status": report_data.get('compliance_status', 'compliant')
                },
                "executive_summary": report_data.get('executive_summary', {}),
                "appendices": {
                    "methodology": report_data.get('methodology', {}),
                    "data_sources": report_data.get('data_sources', []),
                    "assumptions": report_data.get('assumptions', {})
                }
            }
            
            return json.dumps(json_report, indent=2, default=str)
            
        except Exception as e:
            logger.error("JSON generation failed", error=str(e))
            raise


class CSVReportGenerator:
    """Generate CSV format reports"""
    
    def generate_csv(self, report_data: Dict[str, Any]) -> str:
        """Generate CSV report"""
        try:
            # Create multiple CSV sections
            csv_sections = []
            
            # Risk assessment CSV
            risks = report_data.get('risks', [])
            if risks:
                risk_df = pd.DataFrame(risks)
                csv_sections.append("Risk Assessment")
                csv_sections.append(risk_df.to_csv(index=False))
                csv_sections.append("")
            
            # Simulation results CSV
            simulation = report_data.get('simulation_results', {})
            if simulation.get('distribution'):
                sim_df = pd.DataFrame({
                    'Run': range(len(simulation['distribution'])),
                    'Impact': simulation['distribution']
                })
                csv_sections.append("Simulation Results")
                csv_sections.append(sim_df.to_csv(index=False))
                csv_sections.append("")
            
            # Mitigation strategies CSV
            strategies = report_data.get('mitigation_strategies', [])
            if strategies:
                strategy_df = pd.DataFrame(strategies)
                csv_sections.append("Mitigation Strategies")
                csv_sections.append(strategy_df.to_csv(index=False))
                csv_sections.append("")
            
            return "\n".join(csv_sections)
            
        except Exception as e:
            logger.error("CSV generation failed", error=str(e))
            raise


class ReportService:
    """Main report generation service"""
    
    def __init__(self):
        self.pdf_generator = PDFReportGenerator()
        self.json_generator = JSONReportGenerator()
        self.csv_generator = CSVReportGenerator()
    
    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """Generate report in requested format"""
        try:
            report_id = str(uuid.uuid4())
            
            logger.info("Starting report generation",
                       report_id=report_id,
                       scenario_id=request.scenario_id,
                       format=request.format)
            
            # Gather report data
            report_data = await self._gather_report_data(request)
            
            # Generate report in requested format
            if request.format == 'pdf':
                content = self.pdf_generator.generate_pdf(report_data)
                content_type = 'application/pdf'
                filename = f"risk-report-{report_id}.pdf"
            elif request.format == 'json':
                content = self.json_generator.generate_json(report_data).encode('utf-8')
                content_type = 'application/json'
                filename = f"risk-report-{report_id}.json"
            elif request.format == 'csv':
                content = self.csv_generator.generate_csv(report_data).encode('utf-8')
                content_type = 'text/csv'
                filename = f"risk-report-{report_id}.csv"
            else:
                raise ValueError(f"Unsupported format: {request.format}")
            
            # Store report
            file_path = await self._store_report_file(report_id, content, filename)
            
            # Store report metadata
            await self._store_report_metadata(report_id, request, file_path, len(content))
            
            # Publish report generated event
            await messaging_manager.publish(
                "export.make",
                json.dumps({
                    "event": "report_generated",
                    "report_id": report_id,
                    "scenario_id": request.scenario_id,
                    "format": request.format
                }).encode()
            )
            
            return ReportResponse(
                id=report_id,
                scenario_id=request.scenario_id,
                title=request.title or "Risk Assessment Report",
                format=request.format,
                sections=request.sections,
                status="completed",
                file_path=file_path,
                file_size=len(content),
                download_url=f"/api/v1/reports/{report_id}/download",
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            raise
    
    async def _gather_report_data(self, request: ReportRequest) -> Dict[str, Any]:
        """Gather all data needed for report generation"""
        try:
            # Get scenario data
            scenario_query = "SELECT * FROM scenarios WHERE id = $1"
            scenario = await db_manager.execute_one(scenario_query, request.scenario_id)
            
            # Get simulation results
            sim_query = "SELECT * FROM simulations WHERE scenario_id = $1 ORDER BY created_at DESC LIMIT 1"
            simulation = await db_manager.execute_one(sim_query, request.scenario_id)
            
            # Mock data for demonstration - in production, gather from actual sources
            report_data = {
                'id': str(uuid.uuid4()),
                'title': request.title or "Risk Assessment Report",
                'scenario_name': scenario['name'] if scenario else 'Unknown Scenario',
                'scenario_type': scenario['type'] if scenario else 'multi-domain',
                'analysis_period': '12 months',
                'confidence_level': '95%',
                'version': '1.0',
                'sections': request.sections,
                'scenario': {
                    'description': scenario['description'] if scenario else 'Scenario description not available',
                    'timeline': [
                        {'day': 0, 'event': 'Initial trigger event', 'impact': 'low'},
                        {'day': 1, 'event': 'First-order impacts', 'impact': 'medium'},
                        {'day': 7, 'event': 'Cascading effects', 'impact': 'high'},
                        {'day': 30, 'event': 'Full impact realized', 'impact': 'critical'}
                    ],
                    'assumptions': json.loads(scenario['assumptions']) if scenario and scenario['assumptions'] else {}
                },
                'simulation_results': {
                    'statistics': {
                        'mean': 2500000,
                        'median': 2000000,
                        'std': 1200000,
                        'p95': 4800000,
                        'p99': 7200000
                    },
                    'distribution': [float(x) for x in range(500000, 5000000, 50000)]  # Sample distribution
                },
                'risks': [
                    {'name': 'Cyber Attack', 'likelihood': 0.6, 'impact': 0.8},
                    {'name': 'Market Crash', 'likelihood': 0.2, 'impact': 0.9},
                    {'name': 'Supplier Failure', 'likelihood': 0.4, 'impact': 0.6},
                    {'name': 'Regulatory Change', 'likelihood': 0.7, 'impact': 0.4}
                ],
                'mitigation_strategies': [
                    {
                        'name': 'Enhanced Backup System',
                        'description': 'Implement comprehensive backup and recovery',
                        'implementation_cost': 150000,
                        'roi_percent': 250,
                        'implementation_time': 90,
                        'effectiveness': 0.8
                    },
                    {
                        'name': 'Supplier Diversification',
                        'description': 'Develop alternative supplier network',
                        'implementation_cost': 300000,
                        'roi_percent': 180,
                        'implementation_time': 180,
                        'effectiveness': 0.7
                    }
                ],
                'executive_summary': {
                    'risk_overview': 'Analysis identifies significant exposure to cyber and operational risks with potential annual losses exceeding $2.5M.',
                    'key_findings': ['High cyber risk exposure', 'Supplier concentration risk', 'Insufficient backup systems'],
                    'recommendations': ['Implement enhanced cybersecurity', 'Diversify supplier base', 'Upgrade backup systems']
                },
                'compliance_frameworks': ['ISO 31000', 'NIST RMF', 'COSO ERM'],
                'compliance_status': 'compliant'
            }
            
            return report_data
            
        except Exception as e:
            logger.error("Failed to gather report data", error=str(e))
            raise
    
    async def _store_report_file(self, report_id: str, content: bytes, filename: str) -> str:
        """Store report file (mock implementation)"""
        try:
            # In production, store in S3/MinIO or file system
            file_path = f"/reports/{filename}"
            
            logger.info("Report file stored", 
                       report_id=report_id,
                       filename=filename,
                       size=len(content))
            
            return file_path
            
        except Exception as e:
            logger.error("Failed to store report file", error=str(e))
            raise
    
    async def _store_report_metadata(self, report_id: str, request: ReportRequest, file_path: str, file_size: int):
        """Store report metadata in database"""
        try:
            query = """
                INSERT INTO reports (id, scenario_id, title, format, sections, status, file_path, file_size, created_at, completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """
            
            now = datetime.utcnow()
            await db_manager.execute_query(
                query,
                report_id,
                request.scenario_id,
                request.title or "Risk Assessment Report",
                request.format,
                json.dumps(request.sections),
                "completed",
                file_path,
                file_size,
                now,
                now
            )
            
            logger.info("Report metadata stored", report_id=report_id)
            
        except Exception as e:
            logger.error("Failed to store report metadata", error=str(e))
            raise
    
    async def get_report_file(self, report_id: str) -> bytes:
        """Get report file content"""
        try:
            # In production, retrieve from S3/MinIO or file system
            # For now, return mock PDF content
            return b"Mock PDF content for report " + report_id.encode()
            
        except Exception as e:
            logger.error("Failed to get report file", error=str(e))
            raise

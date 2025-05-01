from typing import List, Dict
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from ..core.models import RiskReport
import datetime as dt

class DocumentationAgent:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.risk_colors = {
            "unacceptable": colors.red,
            "high": colors.orange,
            "medium": colors.goldenrod,
            "low": colors.green
        }
        
    def _create_risk_summary(self, reports: List[RiskReport]) -> Dict:
        summary = {"unacceptable": 0, "high": 0, "medium": 0, "low": 0}
        for report in reports:
            summary[report.risk_level] += 1
        return summary
        
    def _draw_header(self, canvas, width, height):
        # Draw header background
        canvas.setFillColor(colors.lightgrey)
        canvas.rect(0, height-100, width, 100, fill=1, stroke=0)
        
        # Draw logo/title
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 28)
        canvas.drawString(40, height-50, "RegulAIte")
        canvas.setFont("Helvetica", 18)
        canvas.drawString(40, height-75, "EU AI Act Compliance Report")
        
        # Draw timestamp
        canvas.setFont("Helvetica", 11)
        timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        canvas.drawString(width-200, height-50, f"Generated: {timestamp}")
        
        # Draw horizontal line
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(2)
        canvas.line(0, height-100, width, height-100)
        
    def _draw_summary(self, canvas, width, height, summary):
        y = height - 140
        
        # Draw section title with background
        canvas.setFillColor(colors.lightgrey)
        canvas.rect(40, y-5, width-80, 30, fill=1, stroke=0)
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(50, y, "Risk Level Summary")
        y -= 40
        
        # Calculate total assets
        total_assets = sum(summary.values())
        
        for level, count in summary.items():
            if count > 0:
                # Draw risk level box with percentage bar
                canvas.setFillColor(colors.lightgrey)
                canvas.rect(40, y-20, width-80, 30, fill=1, stroke=0)
                
                # Draw colored risk indicator
                canvas.setFillColor(self.risk_colors[level])
                canvas.rect(50, y-15, 20, 20, fill=1)
                
                # Draw text
                canvas.setFillColor(colors.black)
                canvas.setFont("Helvetica-Bold", 12)
                canvas.drawString(80, y, f"{level.title()}")
                canvas.setFont("Helvetica", 12)
                percentage = (count / total_assets) * 100
                canvas.drawString(200, y, f"{count} {'assets' if count > 1 else 'asset'} ({percentage:.0f}%)")
                
                # Draw percentage bar background
                canvas.setFillColor(colors.white)
                canvas.rect(width-250, y-10, 150, 10, fill=1)
                
                # Draw percentage bar
                canvas.setFillColor(self.risk_colors[level])
                bar_width = (percentage / 100) * 150
                canvas.rect(width-250, y-10, bar_width, 10, fill=1)
                
                y -= 35
        
        return y - 20
        
    def _draw_details(self, canvas, width, start_y, reports):
        y = start_y
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(40, y, "Detailed Analysis")
        y -= 30
        
        for r in reports:
            if y < 120:  # Increased minimum space needed
                canvas.showPage()
                y = A4[1] - 40  # Use A4 height
            
            # Draw box background
            canvas.setFillColor(colors.lightgrey)
            canvas.rect(40, y-90, width-80, 100, fill=1, stroke=0)
            
            # Draw risk level indicator and header
            canvas.setFillColor(self.risk_colors[r.risk_level])
            canvas.rect(40, y-15, width-80, 25, fill=1, stroke=0)
            
            # Draw asset details in white on risk color background
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawString(50, y+2, r.asset_id)
            canvas.setFont("Helvetica", 11)
            canvas.drawString(width-200, y+2, f"Confidence: {int(r.confidence * 100)}%")
            
            # Draw content on light grey background
            y -= 30
            canvas.setFillColor(colors.black)
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(50, y, "Relevant Articles:")
            canvas.setFont("Helvetica", 11)
            articles_text = ', '.join(r.articles) if r.articles else "None specified"
            canvas.drawString(150, y, articles_text)
            
            # Draw suggestions
            y -= 20
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(50, y, "Suggestions:")
            canvas.setFont("Helvetica", 11)
            if r.suggestions:
                for suggestion in r.suggestions:
                    y -= 15
                    canvas.drawString(65, y, f"• {suggestion}")
            else:
                y -= 15
                canvas.drawString(65, y, "No specific suggestions")
            
            y -= 40  # Extra space between entries
            
    def generate(self, reports: List[RiskReport]) -> str:
        path = Path(f"compliance_{dt.datetime.utcnow().isoformat()}.pdf")
        c = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        
        # Generate summary data
        summary = self._create_risk_summary(reports)
        
        # Draw report components
        self._draw_header(c, width, height)
        y = self._draw_summary(c, width, height, summary)
        self._draw_details(c, width, y, reports)
        
        c.save()
        return str(path)
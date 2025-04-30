from typing import List
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from ..core.models import RiskReport
import datetime as dt

class DocumentationAgent:
    def generate(self,reports:List[RiskReport])->str:
        path = Path(f"compliance_{dt.datetime.utcnow().isoformat()}.pdf")
        c = canvas.Canvas(str(path), pagesize=A4)
        w,h = A4; y=h-40
        c.setFont("Helvetica-Bold",14); c.drawString(40,y,"RegulAIte - Compliance Report"); y-=30
        c.setFont("Helvetica",9)
        for r in reports:
            if y<60: c.showPage(); y=h-40
            c.setFillColor({"unacceptable":"red","high":"orange",
                            "medium":"goldenrod","low":"green"}[r.risk_level])
            c.drawString(40,y,f"{r.asset_id} : {r.risk_level.upper()}  [Art {', '.join(r.articles)}]"); y-=15
            c.setFillColor("black")
        c.save()
        return str(path)
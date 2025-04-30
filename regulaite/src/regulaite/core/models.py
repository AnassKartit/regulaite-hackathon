from pydantic import BaseModel, Field
from typing import List, Dict, Any


class Asset(BaseModel):
    asset_id: str
    type:     str                     # service | model
    location: str
    code_ref: str | None = None
    metadata: Dict[str, Any] = {}     # never None


class RiskReport(BaseModel):
    asset_id:   str
    # pydantic-v2 ⇒ use *pattern* instead of deprecated *regex*
    risk_level: str = Field(..., pattern="^(unacceptable|high|medium|low)$")
    articles:   List[str]
    confidence: float
    suggestions: List[str]
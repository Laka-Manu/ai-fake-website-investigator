# schemas.py
from typing import TypedDict, Optional
from pydantic import BaseModel, Field

# 1. Network Agent output format
class NetworkReport(BaseModel):
    domain_age_days: int = Field(description="Domain age in days")
    ssl_valid: bool = Field(description="Is SSL certificate valid")
    suspicious_flags: list[str] = Field(description="List of suspicious network findings")

# 2. Vision Agent output format
class VisionReport(BaseModel):
    fake_logo_detected: bool = Field(description="True if spoofed logo is found")
    brand_detected: Optional[str] = Field(description="Targeted brand name if any")
    visual_risk_notes: str = Field(description="Notes on visual analysis")

# 3. Decision Agent output format
class FinalDecision(BaseModel):
    risk_score: int = Field(description="Risk Score from 0 to 100")
    verdict: str = Field(description="Verdict: SAFE, SUSPICIOUS, or PHISHING")
    reasoning: str = Field(description="Reasoning behind the verdict")

# 4. LangGraph Shared State
class AgentState(TypedDict):
    url: str
    screenshot_path: str
    network_report: Optional[dict]
    vision_report: Optional[dict]
    final_decision: Optional[dict]
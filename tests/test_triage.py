import pytest
from healthcare_agent.mcp_tools.triage_tools import calculate_risk_score, RiskLevel

class TestTriageTools:
    def test_low_risk_calculation(self):
        symptoms = ["mild headache"]
        vitals = {"temperature": 36.5, "heart_rate": 75, "o2_saturation": 98}
        result = calculate_risk_score(symptoms, vitals)
        assert result["risk_level"] == RiskLevel.LOW.value
        assert result["risk_score"] < 30
    
    def test_critical_risk_calculation(self):
        symptoms = ["chest pain", "difficulty breathing"]
        vitals = {"temperature": 39.5, "heart_rate": 130, "o2_saturation": 90}
        result = calculate_risk_score(symptoms, vitals)
        assert result["risk_level"] == RiskLevel.CRITICAL.value
        assert result["risk_score"] >= 80
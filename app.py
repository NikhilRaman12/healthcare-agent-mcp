import gradio as gr
import logging
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import settings
    from healthcare_agent.context.sharp import SHARPContext
    from healthcare_agent.agent.workflow import PatientWorkflow
    from healthcare_agent.agent.state import PatientWorkflowState
    from healthcare_agent.output import route_to_output, log_workflow_completion
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in demo mode without full backend")
    settings = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_patient(patient_id, chief_complaint, symptoms_text, temperature, heart_rate, blood_pressure, o2_saturation):
    try:
        if settings is None:
            return "❌ Backend not properly configured. Please check deployment settings."
        
        symptoms = [s.strip() for s in symptoms_text.split(",") if s.strip()]
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        context = SHARPContext(
            patient_id=patient_id or "demo-patient-001",
            fhir_token=settings.fhir.token if settings else "",
            encounter_id=f"enc-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            org_id="demo-org-001",
            user_id="demo-user"
        )
        
        initial_state: PatientWorkflowState = {
            "patient_id": context.patient_id,
            "encounter_id": context.encounter_id,
            "org_id": context.org_id,
            "fhir_token": context.fhir_token,
            "chief_complaint": chief_complaint,
            "symptoms": symptoms,
            "symptom_duration": "unknown",
            "vital_signs": {
                "temperature": float(temperature) if temperature else 37.0,
                "heart_rate": int(heart_rate) if heart_rate else 75,
                "blood_pressure": blood_pressure or "120/80",
                "o2_saturation": float(o2_saturation) if o2_saturation else 98.0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        workflow = PatientWorkflow(context)
        final_state = workflow.execute(initial_state)
        routing_result = route_to_output(final_state)
        
        risk_level = final_state.get("risk_level", "unknown")
        risk_score = final_state.get("risk_score", 0)
        triage_priority = final_state.get("triage_priority", "routine")
        output_route = routing_result.get("destination", "physician-review")
        soap_note = final_state.get("soap_note", "N/A")
        safety_issues = final_state.get("safety_issues", [])
        risk_factors = final_state.get("risk_factors", [])
        
        status_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "moderate": "🟡",
            "low": "🟢",
            "unknown": "⚪"
        }
        
        result = f"""
## Assessment Results

**Risk Level:** {status_emoji.get(risk_level, '⚪')} {risk_level.upper()} (Score: {risk_score})

**Triage Priority:** {triage_priority.upper()}

**Output Route:** {output_route}

### Risk Factors
{chr(10).join(['- ' + rf for rf in risk_factors]) if risk_factors else 'None identified'}

### Safety Issues
{chr(10).join(['- ' + si for si in safety_issues]) if safety_issues else 'No safety issues detected'}

### SOAP Note
```
{soap_note}
```

### Routing Decision
- **Destination:** {routing_result.get('destination')}
- **Status:** {routing_result.get('status')}
- **Timestamp:** {routing_result.get('timestamp')}
"""
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing patient: {str(e)}", exc_info=True)
        return f"❌ Error: {str(e)}\n\nPlease check your inputs and try again."

with gr.Blocks(title="Healthcare Agent MCP Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏥 Healthcare Agent MCP
    
    **A production-ready healthcare agent built with FastMCP, LangGraph, and Claude 3.5 Sonnet**
    
    This demo showcases an intelligent healthcare workflow orchestration system that:
    - ✅ Performs patient intake and data collection
    - ✅ Conducts risk assessment and triage
    - ✅ Checks medication safety (drug interactions & allergies)
    - ✅ Generates SOAP notes automatically
    - ✅ Routes cases based on risk level
    
    Built for the **Agents Assemble Healthcare AI Hackathon** by Prompt Opinion
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Patient Information")
            patient_id = gr.Textbox(
                label="Patient ID",
                placeholder="e.g., pat-12345",
                value="demo-patient-001"
            )
            chief_complaint = gr.Textbox(
                label="Chief Complaint",
                placeholder="e.g., Fever and cough for 3 days",
                value="Fever and cough for 3 days"
            )
            symptoms_text = gr.Textbox(
                label="Symptoms (comma-separated)",
                placeholder="e.g., fever, cough, sore throat",
                value="fever, cough, sore throat"
            )
            
            gr.Markdown("### Vital Signs")
            with gr.Row():
                temperature = gr.Number(
                    label="Temperature (°C)",
                    value=38.5,
                    minimum=35.0,
                    maximum=42.0
                )
                heart_rate = gr.Number(
                    label="Heart Rate (bpm)",
                    value=95,
                    minimum=40,
                    maximum=200
                )
            
            with gr.Row():
                blood_pressure = gr.Textbox(
                    label="Blood Pressure",
                    value="120/80"
                )
                o2_saturation = gr.Number(
                    label="O2 Saturation (%)",
                    value=97.0,
                    minimum=70.0,
                    maximum=100.0
                )
            
            submit_btn = gr.Button("🚀 Process Patient", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### Assessment Results")
            output = gr.Markdown()
    
    submit_btn.click(
        fn=process_patient,
        inputs=[patient_id, chief_complaint, symptoms_text, temperature, heart_rate, blood_pressure, o2_saturation],
        outputs=output
    )
    
    gr.Markdown("""
    ---
    ### 🏗️ Architecture
    
    - **MCP Tools:** FHIR data retrieval, medication safety checks, triage scoring
    - **LangGraph Workflow:** Intake → Triage → Safety → Documentation → Routing
    - **SHARP Context:** FHIR R4 compliant patient context propagation
    - **Claude 3.5 Sonnet:** LLM backbone for clinical reasoning
    
    ### 📊 Features
    
    - **Risk Assessment:** Automated scoring based on symptoms and vitals
    - **Safety Checks:** Drug-drug interactions and allergy conflicts
    - **SOAP Notes:** Auto-generated clinical documentation
    - **Smart Routing:** Auto-complete, physician review, or escalation
    - **Audit Trail:** Complete logging for compliance
    
    ### 🔗 Links
    
    - [GitHub Repository](https://github.com/NikhilRaman12/healthcare-agent-mcp)
    - [Prompt Opinion Platform](https://promptopinion.com)
    - [Agents Assemble Hackathon](https://devpost.com)
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

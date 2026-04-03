from __future__ import annotations

import json
import os

import gradio as gr

from config import settings
from healthcare_agent.app import build_context, build_initial_state, run_patient_workflow
from healthcare_agent.demo_cases import get_demo_case, get_demo_cases
from healthcare_agent.presenters import format_result_json, format_result_summary


def run_demo_case(case_label: str):
    try:
        case = get_demo_case(case_label)
        context = build_context(
            patient_id=case["patient_id"],
            encounter_id=case["encounter_id"],
            org_id=case["org_id"],
            fhir_token=settings.fhir.token,
            user_id=case["user_id"],
        )
        initial_state = build_initial_state(
            context,
            chief_complaint=case["chief_complaint"],
            symptoms=case["symptoms"],
            symptom_duration=case["symptom_duration"],
            vital_signs=case["vital_signs"],
        )
        result = run_patient_workflow(context, initial_state)
        return format_result_summary(result), format_result_json(result)
    except Exception as exc:
        error_payload = {"error": str(exc), "case_label": case_label}
        return f"Workflow failed: {exc}", json.dumps(error_payload, indent=2, ensure_ascii=False)


def build_demo() -> gr.Blocks:
    cases = get_demo_cases()
    labels = [case["label"] for case in cases]
    with gr.Blocks(title="Healthcare Agent Gradio Demo") as demo:
        gr.Markdown("# Healthcare Agent Demo")
        gr.Markdown("Pick one of the configured patient IDs and run the workflow.")
        case_selector = gr.Dropdown(choices=labels, value=labels[0], label="Demo Patient")
        run_button = gr.Button("Run Workflow", variant="primary")
        summary = gr.Textbox(label="Summary", lines=12)
        raw_json = gr.Textbox(label="Raw JSON", lines=20)
        run_button.click(fn=run_demo_case, inputs=case_selector, outputs=[summary, raw_json])
    return demo


demo = build_demo()


if __name__ == "__main__":
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0").strip() or "0.0.0.0"
    configured_port = os.getenv("GRADIO_SERVER_PORT", "").strip()
    server_port = int(configured_port) if configured_port else None
    configured_share = os.getenv("GRADIO_SHARE", "false").strip().lower()
    share = configured_share in {"1", "true", "yes", "on"}
    demo.launch(server_name=server_name, server_port=server_port, inbrowser=False, share=share, show_error=True)

<<<<<<< HEAD
# healthcare-agent-mcp
Modular, production-ready healthcare agent with FastMCP, LangGraph, and FHIR R4
=======
# Healthcare Agent MCP

A compact healthcare workflow service with three interfaces:

- FastAPI for HTTP integration
- Gradio for local demo and review
- FastMCP for tool-based interoperability

The workflow gathers patient context, performs simple triage and medication safety checks, generates a SOAP note, and routes the case for automation, review, or escalation.

## Features

- Modular workflow nodes for intake, triage, safety, documentation, and routing
- Reusable application layer shared by API, MCP, CLI, and Gradio entrypoints
- Demo-safe fallback behavior when live FHIR calls are unavailable
- Audit logging for workflow completion events
- Config-driven runtime behavior through environment variables

## Repository Layout

```text
healthcare_agent/
  agent/          Workflow graph, nodes, and shared state
  context/        Request context and context-safe serialization
  external/       FHIR client integration
  mcp_tools/      Reusable clinical helper logic
  output/         Routing and audit logging
  api.py          FastAPI app
  gradio_app.py   Gradio demo UI
  main.py         CLI entrypoint
  server.py       FastMCP server entrypoint
tests/            Workflow and routing tests
config.py         Environment-backed application settings
```

## Clone And Install

```powershell
git clone https://github.com/NikhilRaman12/healthcare-agent-mcp.git
cd healthcare-agent-mcp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a local `.env` from `.env.example` and provide only the values you need for your environment.

Core variables:

- `FHIR_URL`
- `FHIR_TOKEN`
- `LLM_API_KEY` or `ANTHROPIC_API_KEY`
- `DATABASE_URL`
- `LOG_LEVEL`
- `ENVIRONMENT`

Demo variables are available for local development, but production deployments should supply real configuration through environment variables or a managed secret store.

## Run Locally

Run the CLI workflow:

```powershell
venv\Scripts\python -m healthcare_agent.main
```

Run the API:

```powershell
venv\Scripts\python -m uvicorn healthcare_agent.api:app --host 0.0.0.0 --port 8000
```

Run the MCP server:

```powershell
venv\Scripts\python -m healthcare_agent.server
```

Run the Gradio UI:

```powershell
venv\Scripts\python -m healthcare_agent.gradio_app
```

Optional Gradio environment variables:

```powershell
$env:GRADIO_SERVER_NAME="0.0.0.0"
$env:GRADIO_SERVER_PORT="7860"
$env:GRADIO_SHARE="true"
venv\Scripts\python -m healthcare_agent.gradio_app
```

Gradio share links are temporary public tunnels. They are useful for short demos but should not be treated as permanent hosting.

## Docker

Build:

```powershell
docker build -t healthcare-agent-mcp .
```

Run the API container:

```powershell
docker run --env-file .env -p 8000:8000 healthcare-agent-mcp
```

## Testing

```powershell
venv\Scripts\python -m pytest
```

## Security Notes

- `.env`, local logs, `.gradio/`, and the local SQLite database are ignored by git
- FHIR tokens are redacted from serialized context and returned workflow results
- Use demo or synthetic patient data for shared demos unless you have an approved secure hosting setup
- For production use, store secrets in a managed secret service and terminate public traffic behind a proper deployment platform

## Production Readiness Notes

This repository is intentionally simple, but the structure is reusable:

- keep HTTP, MCP, and UI layers thin
- centralize workflow execution in `healthcare_agent/app.py`
- treat external service credentials as environment-provided secrets
- prefer managed deployment targets over temporary share links for public access

For production rollout, add stronger auth, structured observability, deployment automation, and a secure secret manager integration.
>>>>>>> 9248024c8b7ac2e7416829f3f6b924ed050636dd

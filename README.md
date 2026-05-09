# Healthcare Agent MCP

A **production-ready, modular healthcare agent** built with:
- **FastMCP** for Model Context Protocol (tool management)
- **LangGraph** for workflow orchestration
- **Claude 3.5 Sonnet** for LLM backbone
- **FHIR R4** for standardized healthcare data

## 🏗️ Architecture

### Workflow Nodes

1. **Intake Node** - Patient data collection and FHIR record retrieval
2. **Triage Node** - Risk assessment and priority determination
3. **Safety Node** - Medication safety checks (DDI & allergies)
4. **Documentation Node** - Automated SOAP note generation
5. **Router Node** - Intelligent case routing

### MCP Tools

- **FHIR Tools** - Patient data retrieval from FHIR servers
- **Triage Tools** - Risk scoring and priority calculation
- **Medication Tools** - Drug interaction and allergy checking

### SHARP Context

- Patient ID propagation
- FHIR token management
- Encounter and organization tracking
- Timestamp and metadata handling

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
FHIR_URL=https://hapi.fhir.org/baseR4
ANTHROPIC_API_KEY=your-api-key-here
```

### Run the Agent

```bash
# Windows
set PYTHONPATH=%CD%
python healthcare_agent\main.py

# Linux/Mac
export PYTHONPATH=$(pwd)
python healthcare_agent/main.py
```

### Run Gradio Demo

```bash
python app.py
```

## 📁 Project Structure

```
healthcare-agent-mcp/
├── app.py                          # Gradio demo interface
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── healthcare_agent/
│   ├── main.py                    # Main execution script
│   ├── agent/
│   │   ├── state.py              # Workflow state definition
│   │   ├── workflow.py           # Workflow orchestration
│   │   └── nodes/                # Workflow nodes
│   │       ├── intake.py
│   │       ├── triage.py
│   │       ├── safety.py
│   │       ├── doc.py
│   │       └── router.py
│   ├── context/
│   │   └── sharp.py              # SHARP context implementation
│   ├── external/
│   │   └── fhir_client.py        # FHIR client
│   ├── mcp_tools/
│   │   ├── fhir_tools.py         # FHIR MCP tools
│   │   ├── medication_tools.py   # Medication safety tools
│   │   └── triage_tools.py       # Triage tools
│   └── output/
│       ├── routing.py            # Output routing
│       └── audit.py              # Audit logging
└── tests/                         # Test suite
```

## 🎯 Features

- ✅ **Risk Assessment:** Automated scoring based on symptoms and vitals
- ✅ **Safety Checks:** Drug-drug interactions and allergy conflicts
- ✅ **SOAP Notes:** Auto-generated clinical documentation
- ✅ **Smart Routing:** Auto-complete, physician review, or escalation
- ✅ **Audit Trail:** Complete logging for compliance
- ✅ **FHIR R4 Compliant:** Standardized healthcare data exchange
- ✅ **MCP Integration:** Modular tool architecture
- ✅ **A2A Compatible:** Agent-to-agent communication ready

## 🏆 Hackathon Submission

Built for the **Agents Assemble: The Healthcare AI Endgame Challenge** by Prompt Opinion.

### Key Highlights

- **Standards-Based:** MCP, A2A, FHIR R4, SHARP
- **Production-Ready:** Error handling, logging, audit trails
- **Modular:** Easy to extend with new tools and nodes
- **Real-World:** Solves actual healthcare pain points

## 🔗 Links

- **Live Demo:** [Hugging Face Spaces](https://huggingface.co/spaces/NikhilRaman1203/healthcare-mcp-agent)
- **Hackathon:** [Agents Assemble](https://devpost.com)
- **Platform:** [Prompt Opinion](https://promptopinion.com)

## 📝 License

MIT License

## ⚠️ Disclaimer

This is a demonstration system for the hackathon. Not intended for actual clinical use without proper validation, regulatory approval, and clinical oversight.
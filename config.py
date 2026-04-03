from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


def _read_env_file(env_path: str = ".env") -> dict[str, str]:
    path = Path(env_path)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


ENV_VALUES = _read_env_file()


def _get_env(name: str, default, cast=str, aliases: tuple[str, ...] = ()):
    raw_value = os.getenv(name, ENV_VALUES.get(name))
    if raw_value in (None, ""):
        for alias in aliases:
            raw_value = os.getenv(alias, ENV_VALUES.get(alias))
            if raw_value not in (None, ""):
                break
    if raw_value in (None, ""):
        return default
    if cast is bool:
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}
    return cast(raw_value)


@dataclass
class FHIRSettings:
    url: str = field(default_factory=lambda: _get_env("FHIR_URL", "https://hapi.fhir.org/baseR4"))
    token: str = field(default_factory=lambda: _get_env("FHIR_TOKEN", ""))
    timeout: int = field(default_factory=lambda: _get_env("FHIR_TIMEOUT", 30, int))


@dataclass
class EHRSettings:
    api_url: str = field(default_factory=lambda: _get_env("EHR_API_URL", ""))
    api_key: str = field(default_factory=lambda: _get_env("EHR_API_KEY", ""))


@dataclass
class RxNormSettings:
    api_url: str = field(default_factory=lambda: _get_env("RXNORM_API_URL", "https://rxnav.nlm.nih.gov/REST"))
    timeout: int = field(default_factory=lambda: _get_env("RXNORM_TIMEOUT", 15, int))


@dataclass
class OpinionPlatformSettings:
    url: str = field(default_factory=lambda: _get_env("OPINION_PLATFORM_URL", ""))
    key: str = field(default_factory=lambda: _get_env("OPINION_PLATFORM_KEY", ""))


@dataclass
class LLMSettings:
    api_key: str = field(default_factory=lambda: _get_env("LLM_API_KEY", "", aliases=("ANTHROPIC_API_KEY",)))
    model_name: str = field(
        default_factory=lambda: _get_env(
            "LLM_MODEL_NAME",
            "claude-3-5-sonnet-20241022",
            aliases=("MODEL_NAME",),
        )
    )
    max_tokens: int = field(default_factory=lambda: _get_env("LLM_MAX_TOKENS", 4096, int))
    temperature: float = field(default_factory=lambda: _get_env("LLM_TEMPERATURE", 0.7, float))


@dataclass
class DatabaseSettings:
    url: str = field(default_factory=lambda: _get_env("DATABASE_URL", "sqlite:///./healthcare_agent.db"))
    echo: bool = field(default_factory=lambda: _get_env("DATABASE_ECHO", False, bool))
    pool_size: int = field(default_factory=lambda: _get_env("DATABASE_POOL_SIZE", 5, int))
    max_overflow: int = field(default_factory=lambda: _get_env("DATABASE_MAX_OVERFLOW", 10, int))


@dataclass
class AgentSettings:
    max_workflow_steps: int = field(default_factory=lambda: _get_env("MAX_WORKFLOW_STEPS", 10, int))
    workflow_timeout: int = field(default_factory=lambda: _get_env("WORKFLOW_TIMEOUT", 300, int))
    checkpoint_interval: int = field(default_factory=lambda: _get_env("CHECKPOINT_INTERVAL", 5, int))
    enable_auto_complete: bool = field(default_factory=lambda: _get_env("ENABLE_AUTO_COMPLETE", True, bool))
    auto_complete_threshold: float = field(default_factory=lambda: _get_env("AUTO_COMPLETE_THRESHOLD", 0.8, float))
    enable_human_review: bool = field(default_factory=lambda: _get_env("ENABLE_HUMAN_REVIEW", True, bool))
    enable_audit_logging: bool = field(default_factory=lambda: _get_env("ENABLE_AUDIT_LOGGING", True, bool))
    demo_patient_id: str = field(default_factory=lambda: _get_env("DEMO_PATIENT_ID", "pat-12345"))
    demo_encounter_id: str = field(default_factory=lambda: _get_env("DEMO_ENCOUNTER_ID", "enc-67890"))
    demo_org_id: str = field(default_factory=lambda: _get_env("DEMO_ORG_ID", "org-99999"))
    demo_user_id: str = field(default_factory=lambda: _get_env("DEMO_USER_ID", "dr-smith"))
    demo_chief_complaint: str = field(
        default_factory=lambda: _get_env("DEMO_CHIEF_COMPLAINT", "Fever and cough for 3 days")
    )
    demo_symptoms: str = field(default_factory=lambda: _get_env("DEMO_SYMPTOMS", "fever,cough,sore throat"))
    demo_symptom_duration: str = field(default_factory=lambda: _get_env("DEMO_SYMPTOM_DURATION", "3 days"))
    demo_temperature: float = field(default_factory=lambda: _get_env("DEMO_TEMPERATURE", 38.5, float))
    demo_heart_rate: int = field(default_factory=lambda: _get_env("DEMO_HEART_RATE", 95, int))
    demo_blood_pressure: str = field(default_factory=lambda: _get_env("DEMO_BLOOD_PRESSURE", "120/80"))
    demo_o2_saturation: float = field(default_factory=lambda: _get_env("DEMO_O2_SATURATION", 97.0, float))
    demo_patient_ids: str = field(
        default_factory=lambda: _get_env(
            "DEMO_PATIENT_IDS",
            "90250303,90252386,90254981,90255893,90256829",
        )
    )


@dataclass
class Settings:
    environment: str = field(default_factory=lambda: _get_env("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: _get_env("DEBUG", True, bool))
    log_level: str = field(default_factory=lambda: _get_env("LOG_LEVEL", "INFO"))
    log_file: str = field(default_factory=lambda: _get_env("LOG_FILE", "logs/healthcare_agent.log"))
    secret_key: str = field(default_factory=lambda: _get_env("SECRET_KEY", ""))
    fhir: FHIRSettings = field(default_factory=FHIRSettings)
    ehr: EHRSettings = field(default_factory=EHRSettings)
    rxnorm: RxNormSettings = field(default_factory=RxNormSettings)
    opinion_platform: OpinionPlatformSettings = field(default_factory=OpinionPlatformSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    agent: AgentSettings = field(default_factory=AgentSettings)

    def __post_init__(self) -> None:
        if not self.secret_key and self.environment == "development":
            self.secret_key = "dev-secret-key-insecure"


settings = Settings()
logger.info("Loaded settings for environment: %s", settings.environment)

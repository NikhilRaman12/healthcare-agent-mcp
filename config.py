from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import logging

logger = logging.getLogger(__name__)

class FHIRSettings(BaseSettings):
    url: str = Field(default="https://hapi.fhir.org/baseR4")
    token: str = Field(default="")
    timeout: int = Field(default=30)
    class Config:
        env_prefix = "FHIR_"
        extra = "ignore"

class EHRSettings(BaseSettings):
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    class Config:
        env_prefix = "EHR_"
        extra = "ignore"

class RxNormSettings(BaseSettings):
    api_url: str = Field(default="https://rxnav.nlm.nih.gov/REST")
    timeout: int = Field(default=15)
    class Config:
        env_prefix = "RXNORM_"
        extra = "ignore"

class OpinionPlatformSettings(BaseSettings):
    url: str = Field(default="")
    key: str = Field(default="")
    class Config:
        env_prefix = "OPINION_PLATFORM_"
        extra = "ignore"

class LLMSettings(BaseSettings):
    api_key: str = Field(default="")
    model_name: str = Field(default="claude-3-5-sonnet-20241022")
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.7)
    class Config:
        env_prefix = "ANTHROPIC_"
        extra = "ignore"

class DatabaseSettings(BaseSettings):
    url: str = Field(default="sqlite:///./healthcare_agent.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    class Config:
        env_prefix = "DATABASE_"
        extra = "ignore"

class AgentSettings(BaseSettings):
    max_workflow_steps: int = Field(default=10)
    workflow_timeout: int = Field(default=300)
    checkpoint_interval: int = Field(default=5)
    enable_auto_complete: bool = Field(default=True)
    auto_complete_threshold: float = Field(default=0.8)
    enable_human_review: bool = Field(default=True)
    enable_audit_logging: bool = Field(default=True)
    class Config:
        env_prefix = ""
        extra = "ignore"

class Settings(BaseSettings):
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/healthcare_agent.log")
    secret_key: str = Field(default="")
    fhir: FHIRSettings = FHIRSettings()
    ehr: EHRSettings = EHRSettings()
    rxnorm: RxNormSettings = RxNormSettings()
    opinion_platform: OpinionPlatformSettings = OpinionPlatformSettings()
    llm: LLMSettings = LLMSettings()
    database: DatabaseSettings = DatabaseSettings()
    agent: AgentSettings = AgentSettings()
    
    @validator("debug", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, v):
        if not v and cls.__fields__["environment"].default == "development":
            return "dev-secret-key-insecure"
        return v
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
logger.info(f"Loaded settings for environment: {settings.environment}")
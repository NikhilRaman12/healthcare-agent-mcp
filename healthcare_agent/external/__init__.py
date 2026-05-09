"""External integrations (FHIR, EHR, RxNorm, Opinion Platform)"""
from .fhir_client import fhir_client, FHIRClient
__all__ = ["fhir_client", "FHIRClient"]
"""
app/config.py

Centralized settings loaded from environment variables.
Defaults work out-of-the-box with NO external LLM.
"""

import os


class Settings:
    USE_LLM: bool = os.getenv("USE_LLM", "false").lower() == "true"
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    
    # Amounts at/above this are treated as high value for severity/escalation.
    HIGH_VALUE_THRESHOLD: float = float(os.getenv("HIGH_VALUE_THRESHOLD", "10000"))
    
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))


settings = Settings()

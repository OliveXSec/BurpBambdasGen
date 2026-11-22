"""Application settings using environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

        # Model settings
        self.model_name = os.getenv("MODEL_NAME", "claude-opus-5-5")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

        # Paths
        self.knowledge_base_path = Path(os.getenv(
            "KNOWLEDGE_BASE_PATH",
            "data/knowledge_base"
        ))
        self.data_dir = Path(os.getenv("DATA_DIR", "data"))

        # Retrieval settings
        self.n_examples = int(os.getenv("N_EXAMPLES", "3"))
        self.n_docs = int(os.getenv("N_DOCS", "5"))

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()

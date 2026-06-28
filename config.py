"""
Configuration file for the Actian → MuleSoft RAG project.
Loads environment variables and exposes them throughout the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# --------------------------------------------------
# MongoDB Configuration
# --------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ragdb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")
INDEX_NAME = os.getenv("INDEX_NAME", "default")

# --------------------------------------------------
# Embedding Configuration
# --------------------------------------------------

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface").lower()
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# --------------------------------------------------
# LLM Configuration
# --------------------------------------------------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    "o3-mini",
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --------------------------------------------------
# Validation
# --------------------------------------------------

missing = []

if not MONGO_URI:
    missing.append("MONGO_URI")

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    missing.append("OPENAI_API_KEY")

if LLM_PROVIDER in {"google", "gemini"} and not GEMINI_API_KEY:
    missing.append("GEMINI_API_KEY")

if missing:
    raise EnvironmentError(
        f"Missing environment variables: {', '.join(missing)}.\n"
        "Please create a .env file before running the project."
    )

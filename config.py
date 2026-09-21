"""
Configuration module for StudyCraft AI Student Utility Application.
Centralizes constants, default model settings, and input constraints.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# App Metadata
APP_NAME = "StudyCraft AI"
APP_TAGLINE = "Smart AI-Powered Study Assistant for Students"
APP_VERSION = "1.0.0"

# LLM Configuration Defaults
DEFAULT_MODEL = "gemini-1.5-flash"
AVAILABLE_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

# Task-Specific Temperature Tunings
TEMPERATURE_SETTINGS = {
    "summarizer": 0.3,
    "quiz": 0.2,
    "improver": 0.3,
    "explainer": 0.6,
}

# Input Validation Constraints
MIN_INPUT_CHARS = 15
MAX_INPUT_CHARS = 12000
MAX_WORD_RECOMMENDED = 2500

# Default API Key from environment if set
GEMINI_API_KEY_ENV = os.getenv("GEMINI_API_KEY", "")
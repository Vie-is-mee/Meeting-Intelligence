"""Load local configuration without exposing secrets or overriding the environment."""
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_local_config():
    load_dotenv(PROJECT_ROOT / '.env', override=False)

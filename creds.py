"""Loads secrets from cred.env (next to this file) or the environment, so no token lives in the code."""

import os
from pathlib import Path

_FILE = Path(__file__).parent / "cred.env"


def cred(name: str, default: str = "") -> str:
    if os.environ.get(name):
        return os.environ[name]
    if _FILE.exists():
        for line in _FILE.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == name:
                return value.strip().strip('"').strip("'")
    return default

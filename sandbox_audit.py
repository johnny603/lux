import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def audit_path() -> str:
    return os.getenv(
        "LUX_SANDBOX_AUDIT_LOG",
        os.path.expanduser("~/.lux/sandbox-audit.jsonl"),
    )


def record_execution(event: Dict[str, Any], path: Optional[str] = None) -> None:
    """Append one privacy-conscious sandbox event without exposing submitted source."""
    target = path or audit_path()
    directory = os.path.dirname(target)
    if directory:
        os.makedirs(directory, exist_ok=True)
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")

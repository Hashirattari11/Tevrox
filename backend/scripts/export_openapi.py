import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "openapi-export-secret-at-least-thirty-two-chars")
from app.main import app

destination = Path(__file__).resolve().parents[2] / "docs" / "api" / "openapi.json"
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"Wrote {destination}")

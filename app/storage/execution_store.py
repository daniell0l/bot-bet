import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.getenv("DATA_DIR", "data")
FILE_PATH = os.path.join(DATA_DIR, "executions.json")

RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "3"))

def save_execution(result: dict):
    data = []

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append({
        **result,
        "saved_at": datetime.now().isoformat()
    })

    keep_from_date = (datetime.now() - timedelta(days=RETENTION_DAYS - 1)).date()
    def _keep(entry):
        try:
            sa = datetime.fromisoformat(entry.get("saved_at"))
            return sa.date() >= keep_from_date
        except Exception:
            return False

    data = [x for x in data if _keep(x)]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

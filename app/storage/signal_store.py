import json
import os
from datetime import date, datetime, timedelta

DATA_DIR = os.getenv("DATA_DIR", "data")
STORAGE_DIR = DATA_DIR
STORAGE_PATH = os.path.join(STORAGE_DIR, "signals.json")

RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "3"))

def _default_data():
    return {
        "signals": []
    }

def _load_data():
    if not os.path.exists(STORAGE_PATH):
        return _default_data()

    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            data = _default_data()
            _save_data(data)
            return data

def _save_data(data):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_signal(signal: dict):
    data = _load_data()

    s = {**signal}
    if "date" not in s:
        s["date"] = str(date.today())

    data["signals"].append(s)

    keep_from = date.today() - timedelta(days=RETENTION_DAYS - 1)
    def _keep(sig):
        try:
            sig_date = datetime.strptime(sig.get("date", ""), "%Y-%m-%d").date()
            return sig_date >= keep_from
        except Exception:
            return False

    data["signals"] = [x for x in data.get("signals", []) if _keep(x)]

    _save_data(data)

def load_signals() -> list:
    data = _load_data()

    today = str(date.today())
    return [s for s in data.get("signals", []) if s.get("date") == today]

def update_signal_time(old_time: str, color: str, number: int, new_time: str) -> bool:
    data = _load_data()
    today = str(date.today())
    
    for signal in data.get("signals", []):
        if (signal.get("color") == color and 
            signal.get("number") == number and 
            signal.get("date") == today and
            signal.get("time") == old_time):
            
            signal["time"] = new_time
            _save_data(data)
            return True
    
    return False

def remove_signal(time: str, color: str, number: int) -> bool:
    data = _load_data()
    today = str(date.today())
    
    original_count = len(data.get("signals", []))
    
    data["signals"] = [
        s for s in data.get("signals", [])
        if not (s.get("time") == time and 
                s.get("color") == color and 
                s.get("number") == number and 
                s.get("date") == today)
    ]
    
    if len(data.get("signals", [])) < original_count:
        _save_data(data)
        return True
    
    return False

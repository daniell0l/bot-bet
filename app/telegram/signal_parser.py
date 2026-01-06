import re
from datetime import datetime

SIGNAL_REGEX = re.compile(
    r"(?P<time>\d{2}:\d{2})\s*"
    r"entrar\s+na\s*(?P<color>PRETA|VERMELHA).*?"
    r"\((?P<number>\d+)\)",
    re.IGNORECASE | re.DOTALL
)

def parse_signals(text: str):
    signals = []

    for match in SIGNAL_REGEX.finditer(text):
        signals.append({
            "time": match.group("time"),
            "color": match.group("color").upper(),
            "number": int(match.group("number")),
            "raw": match.group(0),
            "received_at": datetime.now().isoformat()
        })

    return signals

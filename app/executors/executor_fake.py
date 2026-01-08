import random
import uuid
from datetime import datetime

from app.core.strategy import MartingaleStrategy
from app.storage.execution_store import save_execution

COLORS = ["PRETA", "VERMELHA"]

def get_fake_result():
    return random.choice(COLORS)

def fake_place_bet(value: int, color: str):
    print(f" Apostando {value} na {color}")

async def execute_signal(signal: dict):
    signal_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()

    print(f"\n EXECUTANDO SINAL FAKE [{signal_id}] {signal['time']} | {signal['color']}")

    strategy = MartingaleStrategy(
        base_bet=5,
        max_losses=3,
        wait_between_spins=None
    )

    result = await strategy.run(
        signal=signal,
        get_result=get_fake_result,
        place_bet=fake_place_bet
    )

    payload = {
        "signal_id": signal_id,
        "signal_time": signal["time"],
        "color": signal["color"],
        "status": result["status"],
        "attempts": result["attempts"],
        "last_bet": result["last_bet"],
        "started_at": start_time.isoformat(),
        "finished_at": datetime.now().isoformat(),
        "executor": "fake"
    }

    save_execution(payload)

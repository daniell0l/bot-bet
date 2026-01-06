import uuid
from datetime import datetime

from app.core.strategy import MartingaleStrategy
from app.storage.execution_store import save_execution


class PlaywrightExecutor:
    def __init__(self, page):
        self.page = page 
    async def get_result(self) -> str:
        raise NotImplementedError("Implementar leitura do resultado")

    async def place_bet(self, value: int, color: str):
        raise NotImplementedError("Implementar aposta")

    async def execute_signal(self, signal):
        signal_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()

        print(f"\n🎯 EXECUTANDO SINAL REAL [{signal_id}] {signal['time']} | {signal['color']}")

        strategy = MartingaleStrategy(
            base_bet=5,
            max_losses=3,
            wait_between_spins=2
        )

        result = await strategy.run(
            signal=signal,
            get_result=self.get_result,
            place_bet=self.place_bet
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
            "executor": "playwright"
        }

        save_execution(payload)

import uuid
from datetime import datetime
from app.core.strategy import MartingaleStrategy
from app.extractors.double_result_extractor import DoubleResultExtractor
from app.storage.execution_store import save_execution


class PlaywrightSimulatorExecutor:
    def __init__(self, page):
        self.extractor = DoubleResultExtractor(page)

    async def execute_signal(self, signal: dict):
        signal_id = str(uuid.uuid4())[:8]
        signal["id"] = signal_id

        signal_time = datetime.strptime(signal["time"], "%H:%M").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )

        strategy = MartingaleStrategy()

        async def get_result():
            return await self.extractor.wait_valid_result(signal_time)

        result = await strategy.run(signal, get_result)

        save_execution({
            "signal_id": signal_id,
            "status": result["status"],
            "attempts": result["attempts"]
        })

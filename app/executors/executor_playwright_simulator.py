import uuid
from datetime import datetime
from app.core.strategy import MartingaleStrategy
from app.core.bank_manager import can_operate, register_result, get_status, get_base_bet, get_window_status, is_within_operation_window
from app.extractors.double_result_extractor import DoubleResultExtractor
from app.storage.execution_store import save_execution


class PlaywrightSimulatorExecutor:
    def __init__(self, page):
        self.extractor = DoubleResultExtractor(page)

    async def execute_signal(self, signal: dict):
        signal_time_str = signal["time"]
        
        if not is_within_operation_window(signal_time_str):
            window = get_window_status()
            print(f"\n⏸️  FORA DA JANELA DE OPERAÇÃO")
            print(f"   Janela de hoje: {window['window_name']}")
            print(f"   Sinal {signal_time_str} está fora do horário permitido.")
            print(f"   Sinal ignorado.\n")
            
            signal_id = str(uuid.uuid4())[:8]
            save_execution({
                "signal_id": signal_id,
                "status": "cancelled",
                "attempts": 0
            })
            register_result("cancelled")
            return
        
        if not can_operate(signal_time_str):
            status = get_status()
            print(f"\n🏆 META DIÁRIA ATINGIDA!")
            print(f"   Lucro do dia: R$ {status['today']['profit']:.2f}")
            print(f"   Operações pausadas até amanhã.")
            print(f"   Sinal {signal_time_str} ignorado.\n")
            return
        
        signal_id = str(uuid.uuid4())[:8]
        signal["id"] = signal_id

        signal_time = datetime.strptime(signal_time_str, "%H:%M").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )

        base_bet = get_base_bet()
        strategy = MartingaleStrategy(base_bet=base_bet)

        async def get_result():
            return await self.extractor.wait_valid_result(signal_time)

        result = await strategy.run(signal, get_result)

        bank_result = register_result(result["status"], result["attempts"])
        
        if result["status"] == "win":
            print(f"💰 Lucro do dia: R$ {bank_result['profit']:.2f}")
            if bank_result["goal_reached"]:
                print(f"🏆 META DIÁRIA ATINGIDA! Operações pausadas.")
        elif result["status"] == "loss":
            print(f"💸 Lucro do dia: R$ {bank_result['profit']:.2f}")

        save_execution({
            "signal_id": signal_id,
            "status": result["status"],
            "attempts": result["attempts"]
        })

from datetime import datetime
import uuid
from app.core.strategy import MartingaleStrategy
from app.core.bank_manager import (
    can_operate,
    get_base_bet,
    get_status,
    register_result,
    is_within_operation_window,
    get_window_status
)
from app.extractors.double_result_extractor import DoubleResultExtractor
from app.storage.execution_store import save_execution

class PlaywrightExecutor:
    def __init__(self, page):
        self.page = page
        self.extractor = DoubleResultExtractor(page)

    async def select_color(self, color: str):
        selector = f'[data-color="{color.lower()}"]'
        await self.page.wait_for_selector(selector, timeout=5000)
        await self.page.click(selector)

    async def fill_bet_value(self, value: float):
        await self.page.wait_for_selector('#sum', timeout=5000)
        await self.page.click('#sum')
        await self.page.keyboard.press('Control+A')
        await self.page.keyboard.press('Backspace')
        await self.page.keyboard.type(f"{value:.2f}")

    async def confirm_bet(self):
        await self.page.wait_for_selector('button.confirm-bet', timeout=5000)
        await self.page.click('button.confirm-bet')

    async def place_bet(self, color: str, value: float):
        print(f"[Playwright] Iniciando aposta: cor={color}, valor={value}", flush=True)
        try:
            color_map = {
                "vermelha": "red",
                "preta": "black",
                "branco": "white",
                "red": "red",
                "black": "black",
                "white": "white"
            }
            site_color = color_map.get(color.lower(), color.lower())

            await self.page.click(f'div.label.{site_color}')
            print(f"[Playwright] Selecionando cor: {site_color}", flush=True)

            await self.page.fill('input#sum', '')
            await self.page.fill('input#sum', str(value))
            print(f"[Playwright] Preenchendo valor: {value}", flush=True)

            await self.page.click('button.confirm-bet')
            print(f"[Playwright] Clicando em apostar", flush=True)

            print(f"[Playwright] Aposta realizada!", flush=True)
        except Exception as e:
            print(f"[Playwright] Erro ao fazer aposta: {e}", flush=True)
            raise

    async def execute_signal(self, signal: dict):
        signal_time_str = signal["time"]

        if not is_within_operation_window(signal_time_str):
            window = get_window_status()
            print(f"\n⏸️ FORA DA JANELA DE OPERAÇÃO")
            print(f"   Janela: {window['window_name']}")
            print(f"   Sinal {signal_time_str} ignorado.\n")

            signal_id =  str(uuid.uuid4())[:8]
            save_execution({
                "signal_id": signal_id,
                "status": "cancelled",
                "attempts": 0
            })
            register_result("cancelled")
            return

        if not can_operate(signal_time_str):
            status = get_status()
            print(f"\n🏆 META DIÁRIA ATINGIDA")
            print(f"   Lucro do dia: R$ {status['today']['profit']:.2f}")
            print(f"   Operações pausadas até amanhã.")
            print(f"   Sinal {signal_time_str} ignorado.\n")
            return

        signal.setdefault("id", f"{signal_time_str}-{signal['color']}")

        signal_time = datetime.strptime(signal_time_str, "%H:%M").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )

        base_bet = get_base_bet()
        strategy = MartingaleStrategy(self, base_bet=base_bet)

        async def get_result():
            return await self.extractor.wait_valid_result(signal_time)

        result = await strategy.run(signal, get_result)

        bank = register_result(
            result["status"],
            result["attempts"]
        )

        if result["status"] == "win":
            print(f"💰 Lucro do dia: R$ {bank['profit']:.2f}")
        elif result["status"] == "loss":
            print(f"💸 Lucro do dia: R$ {bank['profit']:.2f}")

        save_execution({
            "signal_id": signal["id"],
            "status": result["status"],
            "attempts": result["attempts"]
        })

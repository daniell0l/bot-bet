class MartingaleStrategy:
    def __init__(self, base_bet=5, max_losses=3):
        self.base_bet = base_bet
        self.max_losses = max_losses

    async def run(self, signal, get_result):
        sep = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        print(f"\n{sep}")
        print(f"🎯 SINAL {signal['time']} | {signal['color']}")
        print(f"🆔 {signal['id']}")
        print(f"{sep}")
        print("👀 Observação")

        data = await get_result()

        d = data["discarded"]
        print(f"⏭️ Rodada descartada: {d['number']} | {d['color']}")

        v = data["valid"]
        print(f"🎲 Observação válida: {v['number']} | {v['color']}")

        if v["color"] == signal["color"]:
            print("\n❌ Cor bateu na observação → CANCELADO")
            print(sep)
            return {"status": "cancelled", "attempts": 0}

        bet = self.base_bet

        for i in range(1, self.max_losses + 1):
            print(f"\n💰 Entrada {i}º → {bet}=R$ {signal['color']}")
            r = (await get_result())["valid"]
            print(f"🎲 Resultado: {r['color']} - Nº {r['number']}")

            if r["color"] == signal["color"]:
                print("\n🎉 WIN")
                print(sep)
                return {"status": "win", "attempts": i}

            bet *= 2

        print("\n❌ STOP LOSS")
        print(sep)
        return {"status": "loss", "attempts": self.max_losses}

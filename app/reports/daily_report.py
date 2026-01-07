import json
import os
from datetime import datetime, date
from collections import defaultdict

DATA_DIR = os.getenv("DATA_DIR", "data")
EXECUTIONS_PATH = os.path.join(DATA_DIR, "executions.json")

BET_TABLE = {
    1: {"bet": 5, "profit": 5},
    2: {"bet": 10, "profit": 5},
    3: {"bet": 20, "profit": 5},
}

TOTAL_LOSS = 35


def load_executions() -> list:
    """Carrega todas as execuções do arquivo."""
    if not os.path.exists(EXECUTIONS_PATH):
        return []
    
    with open(EXECUTIONS_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_executions_by_date(target_date: date = None) -> list:
    """Retorna execuções de uma data específica (padrão: hoje)."""
    if target_date is None:
        target_date = date.today()
    
    executions = load_executions()
    
    return [
        e for e in executions
        if datetime.fromisoformat(e["saved_at"]).date() == target_date
    ]


def calculate_profit(execution: dict) -> float:
    """Calcula o lucro/prejuízo de uma execução."""
    status = execution.get("status")
    attempts = execution.get("attempts", 0)
    
    if status == "cancelled":
        return 0.0
    
    if status == "win":
        return BET_TABLE.get(attempts, {"profit": 0})["profit"]
    
    if status == "loss":
        return -TOTAL_LOSS
    
    return 0.0


def generate_daily_report(target_date: date = None) -> dict:
    """Gera relatório completo de um dia."""
    if target_date is None:
        target_date = date.today()
    
    executions = get_executions_by_date(target_date)
    
    stats = {
        "date": str(target_date),
        "total": len(executions),
        "win": 0,
        "loss": 0,
        "cancelled": 0,
        "profit": 0.0,
        "win_by_attempt": {1: 0, 2: 0, 3: 0},
        "executions": []
    }
    
    for e in executions:
        status = e.get("status")
        attempts = e.get("attempts", 0)
        profit = calculate_profit(e)
        
        if status == "win":
            stats["win"] += 1
            if attempts in stats["win_by_attempt"]:
                stats["win_by_attempt"][attempts] += 1
        elif status == "loss":
            stats["loss"] += 1
        elif status == "cancelled":
            stats["cancelled"] += 1
        
        stats["profit"] += profit
        stats["executions"].append({
            "signal_id": e.get("signal_id"),
            "status": status,
            "attempts": attempts,
            "profit": profit,
            "time": e.get("saved_at")
        })
    
    played = stats["win"] + stats["loss"]
    stats["win_rate"] = (stats["win"] / played * 100) if played > 0 else 0.0
    
    return stats


def print_daily_report(target_date: date = None):
    """Imprime relatório formatado no console."""
    report = generate_daily_report(target_date)
    
    sep = "━" * 40
    
    print(f"\n{sep}")
    print(f"📊 RELATÓRIO DIÁRIO - {report['date']}")
    print(sep)
    
    print(f"\n📈 RESUMO GERAL")
    print(f"   Total de sinais: {report['total']}")
    print(f"   ✅ WIN: {report['win']}")
    print(f"   ❌ LOSS: {report['loss']}")
    print(f"   ⏭️  CANCELADOS: {report['cancelled']}")
    
    print(f"\n🎯 TAXA DE ACERTO")
    played = report['win'] + report['loss']
    print(f"   Apostas realizadas: {played}")
    print(f"   Taxa de acerto: {report['win_rate']:.1f}%")
    
    print(f"\n🎲 WINS POR TENTATIVA")
    for attempt, count in report['win_by_attempt'].items():
        emoji = "🥇" if attempt == 1 else "🥈" if attempt == 2 else "🥉"
        print(f"   {emoji} {attempt}ª entrada: {count}")
    
    print(f"\n💰 RESULTADO FINANCEIRO")
    profit = report['profit']
    if profit > 0:
        print(f"   🟢 LUCRO: +R$ {profit:.2f}")
    elif profit < 0:
        print(f"   🔴 PREJUÍZO: -R$ {abs(profit):.2f}")
    else:
        print(f"   ⚪ NEUTRO: R$ 0,00")
    
    print(f"\n{sep}\n")
    
    return report


def print_summary_all_days():
    """Imprime resumo de todos os dias disponíveis."""
    executions = load_executions()
    
    if not executions:
        print("Nenhuma execução encontrada.")
        return
    
    by_date = defaultdict(list)
    for e in executions:
        d = datetime.fromisoformat(e["saved_at"]).date()
        by_date[d].append(e)
    
    sep = "━" * 50
    print(f"\n{sep}")
    print(f"📊 RESUMO GERAL - TODOS OS DIAS")
    print(sep)
    
    total_profit = 0.0
    total_win = 0
    total_loss = 0
    total_cancelled = 0
    
    for d in sorted(by_date.keys()):
        report = generate_daily_report(d)
        total_profit += report['profit']
        total_win += report['win']
        total_loss += report['loss']
        total_cancelled += report['cancelled']
        
        profit_str = f"+R$ {report['profit']:.2f}" if report['profit'] >= 0 else f"-R$ {abs(report['profit']):.2f}"
        emoji = "🟢" if report['profit'] > 0 else "🔴" if report['profit'] < 0 else "⚪"
        
        print(f"\n📅 {d} | {emoji} {profit_str}")
        print(f"   WIN: {report['win']} | LOSS: {report['loss']} | CANCEL: {report['cancelled']} | Taxa: {report['win_rate']:.1f}%")
    
    print(f"\n{sep}")
    print(f"📊 TOTAL ACUMULADO")
    
    total_played = total_win + total_loss
    win_rate = (total_win / total_played * 100) if total_played > 0 else 0
    
    print(f"   Sinais: {total_win + total_loss + total_cancelled} | Apostas: {total_played}")
    print(f"   WIN: {total_win} | LOSS: {total_loss} | CANCEL: {total_cancelled}")
    print(f"   Taxa de acerto: {win_rate:.1f}%")
    
    if total_profit > 0:
        print(f"   🟢 LUCRO TOTAL: +R$ {total_profit:.2f}")
    elif total_profit < 0:
        print(f"   🔴 PREJUÍZO TOTAL: -R$ {abs(total_profit):.2f}")
    else:
        print(f"   ⚪ NEUTRO: R$ 0,00")
    
    print(f"{sep}\n")


if __name__ == "__main__":
    print_daily_report()
    print_summary_all_days()

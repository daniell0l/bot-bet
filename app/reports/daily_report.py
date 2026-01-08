from datetime import datetime, date
from collections import defaultdict
from app.storage.database import get_db

BET_TABLE = {
    1: {"bet": 5, "profit": 5},
    2: {"bet": 10, "profit": 5},
    3: {"bet": 20, "profit": 5},
}

TOTAL_LOSS = 35

def load_executions() -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, status, attempts, saved_at
            FROM executions
            ORDER BY saved_at
        """)
        
        return [dict(row) for row in cursor.fetchall()]

def get_executions_by_date(target_date: date = None) -> list:
    if target_date is None:
        target_date = date.today()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, status, attempts, saved_at
            FROM executions
            WHERE DATE(saved_at) = ?
            ORDER BY saved_at
        """, (str(target_date),))
        
        return [dict(row) for row in cursor.fetchall()]

def calculate_profit(execution: dict) -> float:
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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT DATE(saved_at) as exec_date
            FROM executions
            ORDER BY exec_date
        """)
        dates = [row["exec_date"] for row in cursor.fetchall()]
    
    if not dates:
        print("Nenhuma execução encontrada.")
        return
    
    sep = "━" * 50
    print(f"\n{sep}")
    print(f"📊 RESUMO GERAL - TODOS OS DIAS")
    print(sep)
    
    total_profit = 0.0
    total_win = 0
    total_loss = 0
    total_cancelled = 0
    
    for d in dates:
        target_date = datetime.strptime(d, "%Y-%m-%d").date()
        report = generate_daily_report(target_date)
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

import os
from datetime import date, datetime, time
from app.storage.database import get_db

INITIAL_BANK = float(os.getenv("BANK_INITIAL", "100"))
DAILY_GOAL_PERCENT = float(os.getenv("BANK_DAILY_GOAL_PERCENT", "20"))
BET_PERCENT = float(os.getenv("BANK_BET_PERCENT", "5"))

OPERATION_WINDOWS = {
    "odd": {"start": time(7, 0), "end": time(11, 0), "name": "Manhã (07:00-11:00)"},
    "even": {"start": time(20, 0), "end": time(23, 0), "name": "Noite (20:00-23:00)"}
}

def _get_bank_config() -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bank_config WHERE id = 1")
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                INSERT INTO bank_config (id, initial_bank, current_bank, daily_goal_percent, bet_percent)
                VALUES (1, ?, ?, ?, ?)
            """, (INITIAL_BANK, INITIAL_BANK, DAILY_GOAL_PERCENT, BET_PERCENT))
            
            return {
                "initial_bank": INITIAL_BANK,
                "current_bank": INITIAL_BANK,
                "daily_goal_percent": DAILY_GOAL_PERCENT,
                "bet_percent": BET_PERCENT
            }
        
        return {
            "initial_bank": row["initial_bank"],
            "current_bank": row["current_bank"],
            "daily_goal_percent": row["daily_goal_percent"],
            "bet_percent": row["bet_percent"]
        }

def _update_bank_config(current_bank: float = None, initial_bank: float = None):
    config = _get_bank_config()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bank_config 
            SET current_bank = ?, initial_bank = ?
            WHERE id = 1
        """, (
            current_bank if current_bank is not None else config["current_bank"],
            initial_bank if initial_bank is not None else config["initial_bank"]
        ))

def _get_today_key() -> str:
    return str(date.today())

def _get_today_stats() -> dict:
    today = _get_today_key()
    config = _get_bank_config()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (today,))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                INSERT INTO daily_stats (date, start_bank, profit, wins, losses, cancelled, goal_reached)
                VALUES (?, ?, 0, 0, 0, 0, 0)
            """, (today, config["current_bank"]))
            
            return {
                "date": today,
                "start_bank": config["current_bank"],
                "profit": 0.0,
                "wins": 0,
                "losses": 0,
                "cancelled": 0,
                "goal_reached": False,
                "goal_reached_at": None
            }
        
        return {
            "date": row["date"],
            "start_bank": row["start_bank"],
            "profit": row["profit"],
            "wins": row["wins"],
            "losses": row["losses"],
            "cancelled": row["cancelled"],
            "goal_reached": bool(row["goal_reached"]),
            "goal_reached_at": row["goal_reached_at"]
        }

def _update_today_stats(profit: float = None, wins: int = None, losses: int = None, 
                        cancelled: int = None, goal_reached: bool = None, goal_reached_at: str = None):
    today = _get_today_key()
    current = _get_today_stats()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE daily_stats 
            SET profit = ?, wins = ?, losses = ?, cancelled = ?, goal_reached = ?, goal_reached_at = ?
            WHERE date = ?
        """, (
            profit if profit is not None else current["profit"],
            wins if wins is not None else current["wins"],
            losses if losses is not None else current["losses"],
            cancelled if cancelled is not None else current["cancelled"],
            1 if (goal_reached if goal_reached is not None else current["goal_reached"]) else 0,
            goal_reached_at if goal_reached_at is not None else current["goal_reached_at"],
            today
        ))

def get_base_bet() -> float:
    config = _get_bank_config()
    return round(config["current_bank"] * (config["bet_percent"] / 100), 2)

def get_daily_goal() -> float:
    config = _get_bank_config()
    return round(config["current_bank"] * (config["daily_goal_percent"] / 100), 2)

def is_daily_goal_reached() -> bool:
    today_stats = _get_today_stats()
    return today_stats["goal_reached"]

def get_today_window() -> dict:
    today = date.today()
    day = today.day
    
    if day % 2 == 1:
        return {**OPERATION_WINDOWS["odd"], "type": "odd", "day": day}
    else:
        return {**OPERATION_WINDOWS["even"], "type": "even", "day": day}

def is_within_operation_window(signal_time_str: str = None) -> bool:
    window = get_today_window()
    
    if signal_time_str:
        check_time = datetime.strptime(signal_time_str, "%H:%M").time()
    else:
        check_time = datetime.now().time()
    
    return window["start"] <= check_time <= window["end"]

def can_operate(signal_time: str = None) -> bool:
    if is_daily_goal_reached():
        return False
    
    if not is_within_operation_window(signal_time):
        return False
    
    return True

def get_window_status() -> dict:
    window = get_today_window()
    now = datetime.now().time()
    is_active = window["start"] <= now <= window["end"]
    
    return {
        "window_name": window["name"],
        "window_type": "Dia Ímpar (Manhã)" if window["type"] == "odd" else "Dia Par (Noite)",
        "start": window["start"].strftime("%H:%M"),
        "end": window["end"].strftime("%H:%M"),
        "day": window["day"],
        "is_active": is_active,
        "current_time": now.strftime("%H:%M")
    }

def register_result(status: str, attempts: int = 0):
    config = _get_bank_config()
    today_stats = _get_today_stats()
    base_bet = config["current_bank"] * (config["bet_percent"] / 100)
    new_profit = today_stats["profit"]
    new_wins = today_stats["wins"]
    new_losses = today_stats["losses"]
    new_cancelled = today_stats["cancelled"]
    new_bank = config["current_bank"]
    goal_reached = today_stats["goal_reached"]
    goal_reached_at = today_stats["goal_reached_at"]
    
    if status == "win":
        profit = base_bet
        new_wins += 1
        new_profit += profit
        new_bank += profit
        
    elif status == "loss":
        loss = base_bet * 7 
        new_losses += 1
        new_profit -= loss
        new_bank -= loss
        
    elif status == "cancelled":
        new_cancelled += 1
    
    _update_bank_config(current_bank=new_bank)
    
    daily_goal = new_bank * (config["daily_goal_percent"] / 100)
    if new_profit >= daily_goal and not goal_reached:
        goal_reached = True
        goal_reached_at = datetime.now().isoformat()
    
    _update_today_stats(
        profit=new_profit,
        wins=new_wins,
        losses=new_losses,
        cancelled=new_cancelled,
        goal_reached=goal_reached,
        goal_reached_at=goal_reached_at
    )
    
    return {
        "profit": new_profit,
        "goal_reached": goal_reached,
        "current_bank": new_bank
    }

def get_status() -> dict:
    config = _get_bank_config()
    today_stats = _get_today_stats()
    base_bet = get_base_bet()
    daily_goal = get_daily_goal()
    window_status = get_window_status()
    
    return {
        "current_bank": config["current_bank"],
        "initial_bank": config["initial_bank"],
        "base_bet": base_bet,
        "bet_percent": config["bet_percent"],
        "daily_goal": daily_goal,
        "daily_goal_percent": config["daily_goal_percent"],
        "operation_window": window_status,
        "today": {
            "date": _get_today_key(),
            "profit": today_stats["profit"],
            "wins": today_stats["wins"],
            "losses": today_stats["losses"],
            "cancelled": today_stats["cancelled"],
            "goal_reached": today_stats["goal_reached"],
            "goal_reached_at": today_stats["goal_reached_at"],
            "remaining": max(0, daily_goal - today_stats["profit"])
        }
    }

def reset_bank(new_value: float = None):
    new_bank = new_value or INITIAL_BANK
    _update_bank_config(current_bank=new_bank, initial_bank=new_bank)

def print_status():
    status = get_status()
    window = status['operation_window']
    
    sep = "━" * 40
    print(f"\n{sep}")
    print(f"💰 STATUS DA BANCA")
    print(sep)
    
    print(f"\n📊 CAPITAL")
    print(f"   Banca atual: R$ {status['current_bank']:.2f}")
    print(f"   Aposta base: R$ {status['base_bet']:.2f} ({status['bet_percent']}%)")
    
    print(f"\n🕐 JANELA DE OPERAÇÃO (Dia {window['day']})")
    print(f"   Tipo: {window['window_type']}")
    print(f"   Horário: {window['start']} às {window['end']}")
    print(f"   Hora atual: {window['current_time']}")
    if window['is_active']:
        print(f"   ✅ JANELA ATIVA - Operando!")
    else:
        print(f"   ⏸️  FORA DA JANELA - Aguardando...")
    
    print(f"\n🎯 META DIÁRIA ({status['today']['date']})")
    print(f"   Meta: R$ {status['daily_goal']:.2f} ({status['daily_goal_percent']}%)")
    print(f"   Lucro atual: R$ {status['today']['profit']:.2f}")
    print(f"   Faltam: R$ {status['today']['remaining']:.2f}")
    
    if status['today']['goal_reached']:
        print(f"\n   🏆 META ATINGIDA! Operações pausadas.")
        print(f"   ⏰ Atingida às: {status['today']['goal_reached_at'][:19]}")
    
    print(f"\n📈 OPERAÇÕES DE HOJE")
    print(f"   ✅ Wins: {status['today']['wins']}")
    print(f"   ❌ Losses: {status['today']['losses']}")
    print(f"   ⏭️  Cancelados: {status['today']['cancelled']}")
    
    print(f"\n{sep}\n")

def get_monthly_report(year: int = None, month: int = None) -> dict:
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    
    config = _get_bank_config()
    month_prefix = f"{year}-{month:02d}"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM daily_stats 
            WHERE date LIKE ?
            ORDER BY date
        """, (f"{month_prefix}%",))
        
        rows = cursor.fetchall()
    
    total_profit = 0.0
    total_wins = 0
    total_losses = 0
    total_cancelled = 0
    goals_reached = 0
    days_operated = len(rows)
    daily_details = []
    
    for row in rows:
        total_profit += row["profit"] or 0
        total_wins += row["wins"] or 0
        total_losses += row["losses"] or 0
        total_cancelled += row["cancelled"] or 0
        if row["goal_reached"]:
            goals_reached += 1
        
        daily_details.append({
            "date": row["date"],
            "profit": row["profit"] or 0,
            "wins": row["wins"] or 0,
            "losses": row["losses"] or 0,
            "cancelled": row["cancelled"] or 0,
            "goal_reached": bool(row["goal_reached"])
        })
    
    total_played = total_wins + total_losses
    win_rate = (total_wins / total_played * 100) if total_played > 0 else 0
    
    return {
        "year": year,
        "month": month,
        "month_name": datetime(year, month, 1).strftime("%B %Y"),
        "days_operated": days_operated,
        "goals_reached": goals_reached,
        "total_profit": total_profit,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "total_cancelled": total_cancelled,
        "total_played": total_played,
        "win_rate": win_rate,
        "daily_details": daily_details,
        "current_bank": config["current_bank"],
        "initial_bank": config["initial_bank"]
    }

def print_monthly_report(year: int = None, month: int = None):
    report = get_monthly_report(year, month)
    
    sep = "━" * 50
    
    print(f"\n{sep}")
    print(f"📅 RELATÓRIO MENSAL - {report['month_name'].upper()}")
    print(sep)
    
    print(f"\n📊 RESUMO DO MÊS")
    print(f"   Dias operados: {report['days_operated']}")
    print(f"   Metas atingidas: {report['goals_reached']}/{report['days_operated']}")
    
    print(f"\n🎯 OPERAÇÕES")
    print(f"   Total apostas: {report['total_played']}")
    print(f"   ✅ Wins: {report['total_wins']}")
    print(f"   ❌ Losses: {report['total_losses']}")
    print(f"   ⏭️  Cancelados: {report['total_cancelled']}")
    print(f"   Taxa de acerto: {report['win_rate']:.1f}%")
    
    print(f"\n💰 RESULTADO FINANCEIRO")
    if report['total_profit'] > 0:
        print(f"   🟢 LUCRO DO MÊS: +R$ {report['total_profit']:.2f}")
    elif report['total_profit'] < 0:
        print(f"   🔴 PREJUÍZO DO MÊS: -R$ {abs(report['total_profit']):.2f}")
    else:
        print(f"   ⚪ NEUTRO: R$ 0,00")
    
    print(f"\n   Banca inicial: R$ {report['initial_bank']:.2f}")
    print(f"   Banca atual: R$ {report['current_bank']:.2f}")
    
    growth = ((report['current_bank'] - report['initial_bank']) / report['initial_bank']) * 100
    if growth > 0:
        print(f"   📈 Crescimento: +{growth:.1f}%")
    elif growth < 0:
        print(f"   📉 Queda: {growth:.1f}%")
    
    print(f"\n{sep}")
    print(f"📆 DETALHAMENTO DIÁRIO")
    print(sep)
    
    for day in report['daily_details']:
        emoji = "🟢" if day['profit'] > 0 else "🔴" if day['profit'] < 0 else "⚪"
        goal_emoji = "🏆" if day['goal_reached'] else "  "
        profit_str = f"+R$ {day['profit']:.2f}" if day['profit'] >= 0 else f"-R$ {abs(day['profit']):.2f}"
        
        print(f"\n{goal_emoji} {day['date']} | {emoji} {profit_str}")
        print(f"      W: {day['wins']} | L: {day['losses']} | C: {day['cancelled']}")
    
    print(f"\n{sep}\n")

if __name__ == "__main__":
    print_status()

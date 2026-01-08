import json
import os
from datetime import datetime
from app.storage.database import get_db, init_database

DATA_DIR = os.getenv("DATA_DIR", "data")

def migrate_executions():
    json_path = os.path.join(DATA_DIR, "executions.json")
    
    if not os.path.exists(json_path):
        print("❌ Arquivo executions.json não encontrado")
        return 0
    
    with open(json_path, "r", encoding="utf-8") as f:
        executions = json.load(f)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM executions")
        
        for ex in executions:
            cursor.execute("""
                INSERT INTO executions (signal_id, status, attempts, saved_at)
                VALUES (?, ?, ?, ?)
            """, (
                ex.get("signal_id"),
                ex.get("status"),
                ex.get("attempts", 0),
                ex.get("saved_at")
            ))
    
    print(f"✅ Migradas {len(executions)} execuções")
    return len(executions)


def migrate_signals():
    json_path = os.path.join(DATA_DIR, "signals.json")
    
    if not os.path.exists(json_path):
        print("❌ Arquivo signals.json não encontrado")
        return 0
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    signals = data.get("signals", [])
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM signals")
        
        for sig in signals:
            cursor.execute("""
                INSERT INTO signals (signal_id, message_id, signal_index, time, color, number, date, cancelled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sig.get("id"),
                sig.get("message_id"),
                sig.get("index"),
                sig.get("time"),
                sig.get("color"),
                sig.get("number"),
                sig.get("date"),
                1 if sig.get("cancelled") else 0
            ))
    
    print(f"✅ Migrados {len(signals)} sinais")
    return len(signals)


def migrate_bank():
    json_path = os.path.join(DATA_DIR, "bank.json")
    
    if not os.path.exists(json_path):
        print("❌ Arquivo bank.json não encontrado")
        return False
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM bank_config")
        cursor.execute("""
            INSERT INTO bank_config (id, initial_bank, current_bank, daily_goal_percent, bet_percent)
            VALUES (1, ?, ?, ?, ?)
        """, (
            data.get("initial_bank", 100),
            data.get("current_bank", 100),
            data.get("daily_goal_percent", 20),
            data.get("bet_percent", 5)
        ))
        
        cursor.execute("DELETE FROM daily_stats")
        daily_stats = data.get("daily_stats", {})
        
        for date_key, stats in daily_stats.items():
            cursor.execute("""
                INSERT INTO daily_stats (date, start_bank, profit, wins, losses, cancelled, goal_reached, goal_reached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date_key,
                stats.get("start_bank", 0),
                stats.get("profit", 0),
                stats.get("wins", 0),
                stats.get("losses", 0),
                stats.get("cancelled", 0),
                1 if stats.get("goal_reached") else 0,
                stats.get("goal_reached_at")
            ))
    
    print(f"✅ Migrada configuração da banca")
    print(f"✅ Migradas {len(daily_stats)} estatísticas diárias")
    return True

def backup_json_files():
    """Cria backup dos arquivos JSON"""
    import shutil
    
    backup_dir = os.path.join(DATA_DIR, "backup_json")
    os.makedirs(backup_dir, exist_ok=True)
    
    files = ["executions.json", "signals.json", "bank.json"]
    
    for f in files:
        src = os.path.join(DATA_DIR, f)
        if os.path.exists(src):
            dst = os.path.join(backup_dir, f)
            shutil.copy2(src, dst)
            print(f"📦 Backup: {f} -> backup_json/{f}")

def main():
    print("\n" + "=" * 50)
    print("🔄 MIGRAÇÃO JSON → SQLite")
    print("=" * 50)
    
    init_database()
    
    print("\n📦 Criando backup dos arquivos JSON...")
    backup_json_files()
    
    print("\n🔄 Migrando dados...")
    migrate_executions()
    migrate_signals()
    migrate_bank()
    
    print("\n" + "=" * 50)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print("\nOs arquivos JSON originais estão em: data/backup_json/")
    print("Você pode deletá-los após verificar que tudo funciona.\n")


if __name__ == "__main__":
    main()

from datetime import date
from app.storage.database import get_db


def add_signal(signal: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        
        signal_date = signal.get("date", str(date.today()))
        
        cursor.execute("""
            INSERT INTO signals (signal_id, message_id, signal_index, time, color, number, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            signal.get("id"),
            signal.get("message_id"),
            signal.get("index"),
            signal["time"],
            signal["color"],
            signal["number"],
            signal_date
        ))


def load_signals() -> list:
    today = str(date.today())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, message_id, signal_index, time, color, number, date
            FROM signals 
            WHERE date = ? AND cancelled = 0
        """, (today,))
        
        rows = cursor.fetchall()
        return [
            {
                "id": row["signal_id"],
                "message_id": row["message_id"],
                "index": row["signal_index"],
                "time": row["time"],
                "color": row["color"],
                "number": row["number"],
                "date": row["date"]
            }
            for row in rows
        ]


def update_signal_time(old_time: str, color: str, number: int, new_time: str) -> bool:
    today = str(date.today())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET time = ?
            WHERE time = ? AND color = ? AND number = ? AND date = ? AND cancelled = 0
        """, (new_time, old_time, color, number, today))
        
        return cursor.rowcount > 0


def remove_signal(time: str, color: str, number: int) -> bool:
    today = str(date.today())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET cancelled = 1
            WHERE time = ? AND color = ? AND number = ? AND date = ? AND cancelled = 0
        """, (time, color, number, today))
        
        return cursor.rowcount > 0


def cancel_signal_by_message(message_id: int, signal_index: int) -> dict | None:
    today = str(date.today())
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT time, color, number 
            FROM signals 
            WHERE message_id = ? AND signal_index = ? AND date = ? AND cancelled = 0
        """, (message_id, signal_index, today))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        signal_data = {
            "time": row["time"],
            "color": row["color"],
            "number": row["number"]
        }
        
        cursor.execute("""
            UPDATE signals 
            SET cancelled = 1
            WHERE message_id = ? AND signal_index = ? AND date = ?
        """, (message_id, signal_index, today))
        
        return signal_data


def get_signal_by_message(message_id: int, signal_index: int) -> dict | None:
    today = str(date.today())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, message_id, signal_index, time, color, number, date, cancelled
            FROM signals 
            WHERE message_id = ? AND signal_index = ? AND date = ?
        """, (message_id, signal_index, today))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "id": row["signal_id"],
            "message_id": row["message_id"],
            "index": row["signal_index"],
            "time": row["time"],
            "color": row["color"],
            "number": row["number"],
            "date": row["date"],
            "cancelled": bool(row["cancelled"])
        }

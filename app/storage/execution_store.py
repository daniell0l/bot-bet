from datetime import datetime
from app.storage.database import get_db


def save_execution(result: dict):
    """Salva o resultado de uma execução"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO executions (signal_id, status, attempts, saved_at)
            VALUES (?, ?, ?, ?)
        """, (
            result.get("signal_id"),
            result["status"],
            result.get("attempts", 0),
            datetime.now().isoformat()
        ))


def load_executions() -> list:
    """Carrega todas as execuções"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, status, attempts, saved_at
            FROM executions
            ORDER BY saved_at DESC
        """)
        
        rows = cursor.fetchall()
        return [
            {
                "signal_id": row["signal_id"],
                "status": row["status"],
                "attempts": row["attempts"],
                "saved_at": row["saved_at"]
            }
            for row in rows
        ]


def load_executions_by_date(target_date: str) -> list:
    """Carrega execuções de uma data específica"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT signal_id, status, attempts, saved_at
            FROM executions
            WHERE DATE(saved_at) = ?
            ORDER BY saved_at
        """, (target_date,))
        
        rows = cursor.fetchall()
        return [
            {
                "signal_id": row["signal_id"],
                "status": row["status"],
                "attempts": row["attempts"],
                "saved_at": row["saved_at"]
            }
            for row in rows
        ]


def get_executions_summary(target_date: str = None) -> dict:
    """Retorna resumo das execuções (wins, losses, cancelled)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if target_date:
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(attempts) as total_attempts
                FROM executions
                WHERE DATE(saved_at) = ?
                GROUP BY status
            """, (target_date,))
        else:
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(attempts) as total_attempts
                FROM executions
                GROUP BY status
            """)
        
        rows = cursor.fetchall()
        
        summary = {"win": 0, "loss": 0, "cancelled": 0, "total_attempts": 0}
        for row in rows:
            summary[row["status"]] = row["count"]
            if row["status"] in ["win", "loss"]:
                summary["total_attempts"] += row["total_attempts"] or 0
        
        return summary


def get_executions_by_hour(target_date: str = None) -> list:
    """Retorna execuções agrupadas por hora para análise"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if target_date:
            cursor.execute("""
                SELECT 
                    CAST(strftime('%H', saved_at) AS INTEGER) as hour,
                    status,
                    COUNT(*) as count,
                    AVG(attempts) as avg_attempts
                FROM executions
                WHERE DATE(saved_at) = ?
                GROUP BY hour, status
                ORDER BY hour
            """, (target_date,))
        else:
            cursor.execute("""
                SELECT 
                    CAST(strftime('%H', saved_at) AS INTEGER) as hour,
                    status,
                    COUNT(*) as count,
                    AVG(attempts) as avg_attempts
                FROM executions
                GROUP BY hour, status
                ORDER BY hour
            """)
        
        return [dict(row) for row in cursor.fetchall()]

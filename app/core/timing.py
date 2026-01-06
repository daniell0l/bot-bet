import random

def next_spin_delay() -> float:
    """
    Delay médio entre giros da roleta (em segundos)
    Baseado no histórico real (~16–18s)
    """
    return random.uniform(16.5, 18.5)

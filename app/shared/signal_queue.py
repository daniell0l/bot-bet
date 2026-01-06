import asyncio

# Fila global para sinais que chegam após o bot iniciar (para o scheduler processar)
signal_queue = asyncio.Queue()

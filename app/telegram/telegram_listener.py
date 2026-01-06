import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

from app.telegram.signal_parser import parse_signals
from app.storage.signal_store import add_signal, load_signals, remove_signal
from app.shared.signal_queue import signal_queue
from app.scheduler.scheduler import cancel_scheduled_signal

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")

client = TelegramClient(session_name, api_id, api_hash)


def _safe_print(*args):
    try:
        print(*args)
    except UnicodeEncodeError:
        print(*[str(a).encode("ascii", "replace").decode() for a in args])


def _is_target_chat(chat):
    titles = os.getenv("SIGNAL_CHAT_TITLES", "").split(",")
    ids = os.getenv("SIGNAL_CHAT_IDS", "").split(",")

    return (
        any(t.strip() and t.strip() in (chat.title or "") for t in titles) or
        any(str(chat.id) == cid.strip() for cid in ids)
    )


@client.on(events.MessageEdited)
async def on_edited(event):
    chat = await event.get_chat()
    if not _is_target_chat(chat):
        return

    message_id = event.message.id
    new_signals = parse_signals(event.raw_text or "")
    stored = load_signals()

    # Filtra apenas sinais que vieram desta mensagem específica
    old_signals_from_msg = [s for s in stored if s.get("message_id") == message_id]
    
    if not old_signals_from_msg:
        return

    # Cria dicionário dos novos sinais por índice (posição na mensagem)
    new_by_index = {s["index"]: s for s in new_signals}

    for old in old_signals_from_msg:
        old_index = old.get("index")
        
        if old_index is not None and old_index in new_by_index:
            new = new_by_index[old_index]
            
            # Se o sinal na mesma posição teve horário, cor ou número alterados
            if (old["time"] != new["time"] or 
                old["color"] != new["color"] or 
                old["number"] != new["number"]):
                
                removed = remove_signal(old["time"], old["color"], old["number"])
                if removed:
                    cancel_scheduled_signal(old)

                    _safe_print(
                        f"✏️ SINAL EDITADO → ENTRADA CANCELADA | "
                        f"{old['time']} {old['color']} ({old['number']}) → {new['time']} {new['color']} ({new['number']})"
                    )


@client.on(events.NewMessage)
async def handler(event):
    chat = await event.get_chat()
    if not _is_target_chat(chat):
        return

    message = event.raw_text or ""
    message_id = event.message.id
    signals = parse_signals(message)

    if not signals:
        return

    print(f"\n📩 NOVA MENSAGEM DETECTADA ({chat.title})")
    print("────────────────────────────")

    for signal in signals:
        # Adiciona o message_id para rastrear edições
        signal["message_id"] = message_id
        add_signal(signal)

        print("✅ SINAL SALVO")
        print(f"🕒 Horário: {signal['time']}")
        print(f"🎯 Cor: {signal['color']}")
        print(f"🔢 Número: {signal['number']}")
        print("────────────────────────────")

        await signal_queue.put(signal)


async def start_bot():
    _safe_print("🤖 Telegram conectado")
    await client.start()
    await client.run_until_disconnected()

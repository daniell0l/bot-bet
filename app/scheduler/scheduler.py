import asyncio
from datetime import datetime
from app.executors.executor_playwright_simulator import PlaywrightSimulatorExecutor

scheduled_tasks: dict[tuple, asyncio.Task] = {}


def build_key(signal: dict) -> tuple:
    return (signal["time"], signal["color"], signal["number"])


def cancel_scheduled_signal(signal: dict):
    key = build_key(signal)
    task = scheduled_tasks.pop(key, None)

    if task and not task.done():
        task.cancel()


async def schedule_signal(signal: dict, executor):
    key = build_key(signal)

    now = datetime.now()
    signal_time = datetime.strptime(signal["time"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )

    if signal_time <= now:
        return

    try:
        await asyncio.sleep((signal_time - now).total_seconds())
        await executor.execute_signal(signal)
    except asyncio.CancelledError:
        pass
    finally:
        scheduled_tasks.pop(key, None)


async def start_scheduler(page):
    from app.shared.signal_queue import signal_queue
    from app.storage.signal_store import load_signals

    executor = PlaywrightSimulatorExecutor(page)

    for signal in load_signals():
        key = build_key(signal)
        scheduled_tasks[key] = asyncio.create_task(
            schedule_signal(signal, executor)
        )

    while True:
        signal = await signal_queue.get()
        key = build_key(signal)

        if key not in scheduled_tasks:
            scheduled_tasks[key] = asyncio.create_task(
                schedule_signal(signal, executor)
            )

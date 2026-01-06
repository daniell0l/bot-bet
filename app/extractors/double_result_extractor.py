import asyncio
from datetime import datetime


class DoubleResultExtractor:
    def __init__(self, page):
        self.page = page
        self.last_hash = None

    async def _next_result(self):
        while True:
            item = await self.page.query_selector(".history-items .item:first-child")
            if not item:
                await asyncio.sleep(0.2)
                continue

            html = await item.inner_html()
            h = hash(html)
            if h == self.last_hash:
                await asyncio.sleep(0.2)
                continue

            self.last_hash = h
            cls = (await item.get_attribute("class") or "").lower()

            color = (
                "PRETA" if "black" in cls else
                "VERMELHA" if "red" in cls else
                "BRANCO" if "white" in cls else None
            )
            if not color:
                continue

            number = int(await (await item.query_selector(".inside")).inner_text())
            return {"number": number, "color": color}

    async def wait_valid_result(self, signal_time: datetime):
        if datetime.now() < signal_time:
            await asyncio.sleep((signal_time - datetime.now()).total_seconds())

        self.last_hash = None
        discarded = await self._next_result()
        valid = await self._next_result()

        return {
            "discarded": discarded,
            "valid": valid
        }

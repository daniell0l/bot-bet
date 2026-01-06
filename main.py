import asyncio
from playwright.async_api import async_playwright
from app.telegram.telegram_listener import start_bot
from app.scheduler.scheduler import start_scheduler

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://goflecha.com/double")

        print("🌐 Página do Double carregada")

        await asyncio.gather(
            start_bot(),
            start_scheduler(page)
        )

if __name__ == "__main__":
    asyncio.run(main())

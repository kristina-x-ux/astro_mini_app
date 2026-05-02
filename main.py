import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌙 Открыть астроприложение",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )

    await message.answer(
        "✨ Добро пожаловать!\n\n"
        "Нажмите кнопку ниже, чтобы получить анализ.",
        reply_markup=keyboard
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/free-analysis")
async def free_analysis(request: Request):
    data = await request.json()

    name = data.get("name", "Гость")

    text = f"""
✨ Астрологический анализ {name}

Вы человек с глубокой внутренней природой и сильной интуицией.

Вы умеете чувствовать людей и видеть скрытые процессы.

Но при этом внутри есть противоречие:
желание стабильности и тяга к переменам.

Это делает вас сильной, но иногда перегруженной.

🔥 Ваш потенциал — в осознанности и глубине.
"""

    return JSONResponse({"analysis": text})


@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.on_event("startup")
async def startup():
    await bot.set_webhook(f"{WEBAPP_URL}/webhook")

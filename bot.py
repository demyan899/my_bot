from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv  # <-- добавил
load_dotenv()  # Загружаем переменные из .env

API_TOKEN = os.getenv("API_TOKEN")


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

GOALS_FILE = "goals.json"

def load_goals():
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_goals(data):
    with open(GOALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("👋 Привет! Отправь свои цели на месяц с помощью команды /цели")

@dp.message_handler(commands=['цели'])
async def cmd_goals(message: types.Message):
    await message.reply("✍️ Введи список целей на месяц, по одной цели в строке")

@dp.message_handler(lambda msg: msg.text and not msg.text.startswith("/"))
async def handle_text(message: types.Message):
    user_id = str(message.from_user.id)
    goals = load_goals()
    goals[user_id] = message.text.strip().split("\n")
    save_goals(goals)
    await message.reply("✅ Цели сохранены! Я буду напоминать тебе их каждый день в 9:00.")

async def send_daily_tasks():
    now = datetime.now().strftime("%d.%m.%Y")
    goals = load_goals()
    for user_id, user_goals in goals.items():
        text = f"📅 Задачи на {now}:\n\n"
        text += "\n".join(f"✅ {goal}" for goal in user_goals)
        try:
            await bot.send_message(int(user_id), text)
        except:
            pass

async def main():
    # Запуск планировщика
    scheduler.add_job(send_daily_tasks, trigger='cron', hour=9, minute=0)
    scheduler.start()

    # Запуск бота
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())

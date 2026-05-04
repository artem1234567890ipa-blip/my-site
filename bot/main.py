"""
ChemLab Bot — Telegram бот для платформы chemlab.
Функции: регистрация, выдача кода, антиспам, защита от флуда.
"""
import asyncio
import os
import random
import string
import time
import httpx
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

BOT_TOKEN     = os.getenv("BOT_TOKEN")
ADMIN_ID      = int(os.getenv("ADMIN_ID", "0"))
SUPABASE_URL  = os.getenv("SUPABASE_URL")
SUPABASE_KEY  = os.getenv("SUPABASE_SECRET_KEY")

bot     = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp      = Dispatcher(storage=storage)
router  = Router()
dp.include_router(router)

# ─── Защита от флуда ──────────────────────────────────────────────
RATE_LIMIT: dict[int, list[float]] = {}  # user_id -> list of timestamps
MAX_MESSAGES = 5     # максимум сообщений
TIME_WINDOW  = 60    # за 60 секунд
BLOCKED: set[int] = set()

def is_rate_limited(user_id: int) -> bool:
    now = time.time()
    if user_id in BLOCKED:
        return True
    history = RATE_LIMIT.get(user_id, [])
    history = [t for t in history if now - t < TIME_WINDOW]
    history.append(now)
    RATE_LIMIT[user_id] = history
    if len(history) > MAX_MESSAGES:
        BLOCKED.add(user_id)
        return True
    return False

# ─── Supabase helpers ─────────────────────────────────────────────
HEADERS = lambda: {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

async def get_existing_code(telegram_id: int) -> str | None:
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(
                f"{SUPABASE_URL}/rest/v1/registrations"
                f"?telegram_id=eq.{telegram_id}&select=access_code",
                headers=HEADERS()
            )
            d = r.json()
            return d[0]["access_code"] if d else None
        except Exception as e:
            print(f"[get_existing_code] {e}")
            return None

async def save_registration(telegram_id: int, username: str, full_name: str, code: str) -> bool:
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.post(
                f"{SUPABASE_URL}/rest/v1/registrations",
                json={"telegram_id": telegram_id, "username": username or "",
                      "full_name": full_name, "access_code": code},
                headers=HEADERS()
            )
            return r.status_code in (200, 201)
        except Exception as e:
            print(f"[save_registration] {e}")
            return False

def generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

# ─── FSM ──────────────────────────────────────────────────────────
class Reg(StatesGroup):
    waiting_name = State()

# ─── Handlers ─────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    uid = message.from_user.id

    if is_rate_limited(uid):
        await message.answer("⏳ Слишком много запросов. Подождите минуту.")
        return

    existing = await get_existing_code(uid)
    if existing:
        await message.answer(
            f"👋 С возвращением!\n\n"
            f"Ваш код доступа:\n\n"
            f"<code>{existing}</code>\n\n"
            f"Введите его на сайте для входа в лабораторию.",
            parse_mode="HTML"
        )
        return

    args = command.args
    if args == "register":
        await state.set_state(Reg.waiting_name)
        await message.answer(
            "🧪 Добро пожаловать в <b>ChemLab</b>!\n\n"
            "Введите ваше имя и фамилию для регистрации:",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "👋 Привет! Я бот платформы <b>ChemLab</b>.\n\n"
            "🔬 Химия и биология — интерактивная база знаний.\n\n"
            "Используй /register для получения кода доступа\n"
            "или перейди на сайт и нажми кнопку регистрации.",
            parse_mode="HTML"
        )

@router.message(F.text == "/register")
async def cmd_register(message: Message, state: FSMContext):
    uid = message.from_user.id

    if is_rate_limited(uid):
        await message.answer("⏳ Слишком много запросов. Подождите минуту.")
        return

    existing = await get_existing_code(uid)
    if existing:
        await message.answer(
            f"✅ Вы уже зарегистрированы!\n\nВаш код:\n\n<code>{existing}</code>",
            parse_mode="HTML"
        )
        return

    await state.set_state(Reg.waiting_name)
    await message.answer("Введите ваше имя и фамилию:")

@router.message(Reg.waiting_name)
async def process_name(message: Message, state: FSMContext):
    uid  = message.from_user.id
    name = message.text.strip()

    if is_rate_limited(uid):
        await state.clear()
        await message.answer("⏳ Слишком много запросов. Попробуйте через минуту.")
        return

    if len(name) < 2:
        await message.answer("Введите корректное имя (минимум 2 символа):")
        return

    if len(name) > 60:
        await message.answer("Имя слишком длинное. Введите имя и фамилию:")
        return

    code    = generate_code()
    uname   = message.from_user.username or ""
    success = await save_registration(uid, uname, name, code)
    await state.clear()

    if success:
        if ADMIN_ID:
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"🆕 Новая регистрация!\n"
                    f"👤 {name}\n"
                    f"📱 @{uname or 'нет'} (ID: {uid})\n"
                    f"🔑 Код: {code}"
                )
            except Exception:
                pass

        await message.answer(
            f"✅ Регистрация успешна, <b>{name}</b>!\n\n"
            f"Ваш персональный код доступа:\n\n"
            f"<code>{code}</code>\n\n"
            f"📌 Введите этот код на сайте ChemLab для доступа к лаборатории.\n"
            f"🔒 Сохраните код — он нужен при каждом входе.\n\n"
            f"Используйте /code чтобы получить код снова.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка сохранения. Попробуйте позже командой /register."
        )

@router.message(F.text == "/code")
async def cmd_code(message: Message):
    if is_rate_limited(message.from_user.id):
        await message.answer("⏳ Подождите минуту.")
        return
    code = await get_existing_code(message.from_user.id)
    if code:
        await message.answer(
            f"🔑 Ваш код доступа:\n\n<code>{code}</code>\n\nВведите его на сайте ChemLab.",
            parse_mode="HTML"
        )
    else:
        await message.answer("Вы ещё не зарегистрированы. Используйте /register.")

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "<b>ChemLab Bot 🧪</b>\n\n"
        "/start — начало работы\n"
        "/register — зарегистрироваться и получить код\n"
        "/code — показать ваш код доступа\n"
        "/help — помощь\n\n"
        "После получения кода введите его на сайте для доступа к лаборатории.",
        parse_mode="HTML"
    )

@router.message(F.text == "/status")
async def cmd_status(message: Message):
    """Проверка статуса бота (только для администратора)."""
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"✅ Бот работает\n"
        f"🚫 Заблокировано: {len(BLOCKED)} пользователей\n"
        f"📊 Rate limit записей: {len(RATE_LIMIT)}"
    )

@router.message()
async def catch_all(message: Message):
    """Отвечает на любое другое сообщение."""
    if is_rate_limited(message.from_user.id):
        return
    await message.answer(
        "Используйте /register для получения кода доступа\nили /help для помощи."
    )

# ─── Main ─────────────────────────────────────────────────────────
async def main():
    print("ChemLab Bot started ✅")
    print(f"Admin ID: {ADMIN_ID}")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

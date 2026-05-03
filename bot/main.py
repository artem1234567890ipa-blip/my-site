import asyncio
import os
import random
import string
import httpx
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


class Registration(StatesGroup):
    waiting_name = State()


def generate_code() -> str:
    """Generate a unique 6-digit numeric access code."""
    return ''.join(random.choices(string.digits, k=6))


async def save_to_supabase(telegram_id: int, username: str, full_name: str, code: str) -> bool:
    """Save user registration to Supabase."""
    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "telegram_id": telegram_id,
        "username": username or "",
        "full_name": full_name,
        "access_code": code,
        "verified": False
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{SUPABASE_URL}/rest/v1/registrations",
                json=payload,
                headers=headers,
                timeout=10
            )
            return r.status_code in (200, 201)
        except Exception as e:
            print(f"Supabase error: {e}")
            return False


async def get_existing_code(telegram_id: int) -> str | None:
    """Check if user already has a code."""
    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/registrations?telegram_id=eq.{telegram_id}&select=access_code",
                headers=headers,
                timeout=10
            )
            data = r.json()
            if data and len(data) > 0:
                return data[0]["access_code"]
        except Exception:
            pass
    return None


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    args = command.args

    # Check if user already registered
    existing = await get_existing_code(message.from_user.id)
    if existing:
        await message.answer(
            f"С возвращением! Ваш код доступа:\n\n"
            f"<code>{existing}</code>\n\n"
            f"Введите его на сайте ChemLab для входа в лабораторию.",
            parse_mode="HTML"
        )
        return

    if args == "register":
        await state.set_state(Registration.waiting_name)
        await message.answer(
            "Добро пожаловать в <b>ChemLab</b>!\n\n"
            "Для регистрации введите ваше имя и фамилию:",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Привет! Я бот платформы <b>ChemLab</b> — мир химии.\n\n"
            "Для регистрации перейдите на сайт и нажмите кнопку регистрации, "
            "или введите команду /register.",
            parse_mode="HTML"
        )


@router.message(F.text == "/register")
async def cmd_register(message: Message, state: FSMContext):
    existing = await get_existing_code(message.from_user.id)
    if existing:
        await message.answer(
            f"Вы уже зарегистрированы! Ваш код:\n\n<code>{existing}</code>",
            parse_mode="HTML"
        )
        return
    await state.set_state(Registration.waiting_name)
    await message.answer("Введите ваше имя и фамилию:")


@router.message(Registration.waiting_name)
async def process_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name) < 2:
        await message.answer("Введите корректное имя (минимум 2 символа):")
        return

    # Generate code and save
    code = generate_code()
    username = message.from_user.username or ""
    saved = await save_to_supabase(message.from_user.id, username, full_name, code)

    await state.clear()

    if saved:
        # Notify admin
        if ADMIN_ID:
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"Новая регистрация!\n"
                    f"Имя: {full_name}\n"
                    f"TG: @{username or 'нет'}\n"
                    f"ID: {message.from_user.id}\n"
                    f"Код: {code}"
                )
            except Exception:
                pass

        await message.answer(
            f"Регистрация прошла успешно, <b>{full_name}</b>!\n\n"
            f"Ваш персональный код доступа:\n\n"
            f"<code>{code}</code>\n\n"
            f"Введите этот код на сайте ChemLab, чтобы войти в лабораторию.\n\n"
            f"Сохраните код — он понадобится при следующем входе.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Произошла ошибка при сохранении. Попробуйте позже или обратитесь к администратору."
        )


@router.message(F.text == "/code")
async def cmd_code(message: Message):
    """Show user's existing code."""
    code = await get_existing_code(message.from_user.id)
    if code:
        await message.answer(
            f"Ваш код доступа:\n\n<code>{code}</code>",
            parse_mode="HTML"
        )
    else:
        await message.answer("Вы ещё не зарегистрированы. Используйте /register.")


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "<b>ChemLab Bot</b>\n\n"
        "/register — зарегистрироваться и получить код\n"
        "/code — показать ваш код доступа\n"
        "/help — помощь\n\n"
        "После регистрации введите код на сайте ChemLab.",
        parse_mode="HTML"
    )


async def main():
    print("ChemLab Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

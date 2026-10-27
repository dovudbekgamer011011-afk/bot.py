# ============================================================
# M Y S T I C D R O P — To'liq professional bot (Render uchun)
# ============================================================
import asyncio
import random
import logging
import json
import os
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
    InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ==========================================
# ⚠️ MAXFIY SOZLAMALAR (.env)
# ==========================================
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN or ADMIN_ID == 0:
    print("❌ XATOLIK: .env faylida BOT_TOKEN yoki ADMIN_ID topilmadi!")
    exit()
# ==========================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

CONFIG_FILE = "config.json"
USERS_FILE = "users.json"
PROMO_FILE = "promos.json"
TASKS_FILE = "tasks.json"

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"{filename} yuklashda xato: {e}")
            return default
    return default

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"{filename} saqlashda xato: {e}")

app_config = load_json(CONFIG_FILE, {"channels": []})
users_db = load_json(USERS_FILE, {})
promos_db = load_json(PROMO_FILE, {
    "promo15119287": 50,
    "abdulaziz1122": 50,
    "print(\"hello world\")": 100,
    "D15119287": 100
})
tasks_db = load_json(TASKS_FILE, [
    {"id": "task_1", "name": "📢 Kanalga a'zo bo'lish", "reward": 2, "type": "channel", "link": "@mystic_drop_uz"}
])

# ==========================================
# TO'LIQ TILLAR (UZ, RU, EN)
# ==========================================
TEXTS = {
    "uz": {
        "welcome": "✦ <b>M Y S T I C D R O P</b> ✦\n\n🕊 <b>Xush kelibsiz, {name}!</b>\n\n<i>Davom etish uchun quyidagi tugmani bosing:</i>",
        "enter": "✦ Portalga Kirish ✦",
        "status_name": "Ism", "status_bal": "Balans", "status_ref": "Referallar",
        "choose": "Quyidagi xizmatlardan birini tanlang:",
        "drop_menu": "⭐ <b>STARS DROP MARKAZI</b> ⭐\n\nO'yinlarni tanlang:",
        "daily_ok": "✅ Kunlik bonus olindi! +1 Stars.",
        "daily_no": "⏳ Siz bugungi bonusni allaqachon olgansiz.",
        "ref_link": "🔗 Sizning havolangiz:\n<code>{link}</code>",
        "gift_no": "❌ Kamida {price} Stars kerak. Sizda: {bal}.",
        "lang_choose": "🌐 <b>Tilni tanlang:</b>",
        "lang_set": "✅ Til o'zgartirildi!",
        "btn_stars": "⭐ Stars", "btn_prem": "💎 Premium", "btn_gift": "🎁 Sovg'alar",
        "btn_bal": "💳 Balans", "btn_ref": "👥 Referal (+2)", "btn_hist": "🕰 Faollik Tarixi",
        "btn_help": "❔ Yordam", "btn_lang": "🌐 Tilni o'zgartirish",
        "btn_daily": "📅 Kunlik Bonus (+1)",
        "btn_tasks": "📋 Vazifalar (Tasklar)",
        "btn_darts": "🎯 Nayza", "btn_dice": "🎲 Kubik", "btn_bowl": "🎳 Bouling",
        "btn_basket": "🏀 Basketbol", "btn_slot": "🎰 Slot", "btn_mines": "💣 Mina O'yini",
        "btn_ladder": "🪜 Narvon O'yini",
        "back": "⬅️ Orqaga", "play_again": "🎮 Yana o'ynash"
    },
    "ru": {
        "welcome": "✦ <b>M Y S T I C D R O P</b> ✦\n\n🕊 <b>Добро пожаловать, {name}!</b>\n\n<i>Нажмите кнопку ниже, чтобы продолжить:</i>",
        "enter": "✦ Войти в Портал ✦",
        "status_name": "Имя", "status_bal": "Баланс", "status_ref": "Рефералы",
        "choose": "Выберите одну из услуг:",
        "drop_menu": "⭐ <b>ЦЕНТР STARS DROP</b> ⭐\n\nВыберите игру:",
        "daily_ok": "✅ Ежедневный бонус получен! +1 Stars.",
        "daily_no": "⏳ Вы уже получили бонус сегодня.",
        "ref_link": "🔗 Ваша ссылка:\n<code>{link}</code>",
        "gift_no": "❌ Нужно минимум {price} Stars. У вас: {bal}.",
        "lang_choose": "🌐 <b>Выберите язык:</b>",
        "lang_set": "✅ Язык изменен!",
        "btn_stars": "⭐ Stars", "btn_prem": "💎 Премиум", "btn_gift": "🎁 Подарки",
        "btn_bal": "💳 Баланс", "btn_ref": "👥 Реферал (+2)", "btn_hist": "🕰 История",
        "btn_help": "❔ Помощь", "btn_lang": "🌐 Язык",
        "btn_daily": "📅 Бонус (+1)",
        "btn_tasks": "📋 Задания",
        "btn_darts": "🎯 Дартс", "btn_dice": "🎲 Кубик", "btn_bowl": "🎳 Боулинг",
        "btn_basket": "🏀 Баскетбол", "btn_slot": "🎰 Слот", "btn_mines": "💣 Мины",
        "btn_ladder": "🪜 Лестница",
        "back": "⬅️ Назад", "play_again": "🎮 Играть снова"
    },
    "en": {
        "welcome": "✦ <b>M Y S T I C D R O P</b> ✦\n\n🕊 <b>Welcome, {name}!</b>\n\n<i>Click the button below to continue:</i>",
        "enter": "✦ Enter Portal ✦",
        "status_name": "Name", "status_bal": "Balance", "status_ref": "Referrals",
        "choose": "Choose one of the services:",
        "drop_menu": "⭐ <b>STARS DROP CENTER</b> ⭐\n\nChoose a game:",
        "daily_ok": "✅ Daily bonus received! +1 Stars.",
        "daily_no": "⏳ You already received today's bonus.",
        "ref_link": "🔗 Your link:\n<code>{link}</code>",
        "gift_no": "❌ Need at least {price} Stars. You have: {bal}.",
        "lang_choose": "🌐 <b>Choose language:</b>",
        "lang_set": "✅ Language changed!",
        "btn_stars": "⭐ Stars", "btn_prem": "💎 Premium", "btn_gift": "🎁 Gifts",
        "btn_bal": "💳 Balance", "btn_ref": "👥 Referral (+2)", "btn_hist": "🕰 History",
        "btn_help": "❔ Help", "btn_lang": "🌐 Language",
        "btn_daily": "📅 Daily Bonus (+1)",
        "btn_tasks": "📋 Tasks",
        "btn_darts": "🎯 Darts", "btn_dice": "🎲 Dice", "btn_bowl": "🎳 Bowling",
        "btn_basket": "🏀 Basketball", "btn_slot": "🎰 Slot", "btn_mines": "💣 Mines",
        "btn_ladder": "🪜 Ladder",
        "back": "⬅️ Back", "play_again": "🎮 Play Again"
    }
}

def t(user_id, key, **kwargs):
    user = get_user(user_id)
    lang = user.get("lang", "uz")
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, "")
    if kwargs:
        return text.format(**kwargs)
    return text

class GameStates(StatesGroup):
    waiting_for_bet = State()
    waiting_for_mines_count = State()
    playing_mines = State()
    playing_ladder = State()

class AdminStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_link = State()
    waiting_for_promo_name = State()
    waiting_for_promo_amount = State()
    waiting_for_task_name = State()
    waiting_for_task_reward = State()
    waiting_for_task_link = State()

class PromoState(StatesGroup):
    waiting_for_promo = State()

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users_db:
        users_db[user_id] = {}
    defaults = {
        "username": "Foydalanuvchi", "balance": 0.0, "referals": 0,
        "last_daily": None, "history": [], "lang": "uz",
        "win_streak": 0, "used_promo": [], "caught_cheating": False,
        "total_wagered": 0.0, "total_won": 0.0, "completed_tasks": [],
        "first_step_cashout_count": 0, "total_played": 0, "loss_streak": 0
    }
    for k, v in defaults.items():
        users_db[user_id].setdefault(k, v)
    return users_db[user_id]

def get_status_text(user_id):
    user = get_user(user_id)
    balance_text = "∞ (Cheksiz)" if user_id == ADMIN_ID else f"{user['balance']:.2f} Stars"
    return (
        f"✧ <b>PROFIL</b> ✧\n"
        f"◈ <b>{t(user_id, 'status_name')}:</b> <code>@{user['username']}</code>\n"
        f"◈ <b>{t(user_id, 'status_bal')}:</b> <code>{balance_text}</code>\n"
        f"◈ <b>{t(user_id, 'status_ref')}:</b> <code>{user['referals']} ta</code>\n"
        f"✧──────────────────✧\n\n"
    )

def get_main_keyboard(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t(user_id, "btn_stars")), KeyboardButton(text=t(user_id, "btn_prem")), KeyboardButton(text=t(user_id, "btn_gift")))
    builder.row(KeyboardButton(text=t(user_id, "btn_bal")), KeyboardButton(text=t(user_id, "btn_ref")), KeyboardButton(text=t(user_id, "btn_hist")))
    builder.row(KeyboardButton(text=t(user_id, "btn_help")), KeyboardButton(text=t(user_id, "btn_lang")))
    return builder.as_markup(resize_keyboard=True)

# ============================================================
# 🎯 MATEMATIK YADRO VA ALGORITM
# ============================================================
STREAK_2_CHANCE = 0.30
FIRST_STEP_TRAP_THRESHOLD = 3
FIRST_STEP_TRAP_PROB = 0.99
BIG_BET_PERCENT = 0.70
BIG_BET_ABS = 10.0
CONSOLATION_LOSS_STREAK = 4
CONSOLATION_PROB = 0.75

def dynamic_house_edge(user, bet_amount, is_game=True):
    if not is_game:
        return 0.05
    edge = 0.05
    total_played = user.get("total_played", 0)
    if total_played < 10:
        edge = 0.02
    elif total_played >= 50:
        edge = 0.08

    balance = user.get("balance", 0.0)
    if balance > 0 and bet_amount >= balance * BIG_BET_PERCENT:
        edge += 0.40 * min(1.0, bet_amount / balance)
    if bet_amount > BIG_BET_ABS:
        edge += 0.15
    return max(0.02, min(0.50, edge))

def is_big_bet(user, bet_amount):
    balance = user.get("balance", 0.0)
    if balance > 0 and bet_amount >= balance * BIG_BET_PERCENT:
        return True
    if bet_amount > BIG_BET_ABS:
        return True
    return False

def apply_streak_penalty(user, base_win_chance):
    if user.get("win_streak", 0) >= 2:
        return base_win_chance * STREAK_2_CHANCE
    return base_win_chance

def should_trigger_cashout_trap(user):
    return user.get("first_step_cashout_count", 0) >= FIRST_STEP_TRAP_THRESHOLD - 1

def reset_cashout_trap(user):
    user["first_step_cashout_count"] = 0

def increment_cashout_trap(user):
    user["first_step_cashout_count"] = user.get("first_step_cashout_count", 0) + 1

def is_consolation_time(user):
    return user.get("loss_streak", 0) >= CONSOLATION_LOSS_STREAK

def update_after_win(user, winnings, bet_amount):
    user["win_streak"] = user.get("win_streak", 0) + 1
    user["loss_streak"] = 0
    user["total_won"] = round(user.get("total_won", 0.0) + winnings, 2)
    user["total_wagered"] = round(user.get("total_wagered", 0.0) + bet_amount, 2)
    user["total_played"] = user.get("total_played", 0) + 1

def update_after_loss(user, bet_amount):
    user["win_streak"] = 0
    user["loss_streak"] = user.get("loss_streak", 0) + 1
    user["total_wagered"] = round(user.get("total_wagered", 0.0) + bet_amount, 2)
    user["total_played"] = user.get("total_played", 0) + 1

# ==========================================
# MAJBURIY KANALLAR
# ==========================================
def normalize_channel_link(link):
    if not link:
        return ""
    link = link.strip()
    if link.startswith("http"):
        return link
    if link.startswith("@"):
        return "https://t.me/" + link[1:]
    if re.fullmatch(r"-?\d+", link):
        return link
    return "https://t.me/" + link

async def check_subscriptions(user_id):
    channels = app_config.get("channels", [])
    not_joined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except Exception as e:
            logging.warning(f"Kanal tekshirishda xato ({ch.get('id')}): {e}")
            continue
    return not_joined

def get_subscription_keyboard(not_joined):
    kb = []
    for ch in not_joined:
        url = normalize_channel_link(ch.get("link") or ch.get("id"))
        name = ch.get("name") or ch.get("id")
        if url.startswith("http"):
            kb.append([InlineKeyboardButton(text=f"📢 {name}", url=url)])
        else:
            kb.append([InlineKeyboardButton(text=f"📢 {name} (yopiq)", callback_data="subs_private")])
    kb.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def require_subscription(event, user_id):
    not_joined = await check_subscriptions(user_id)
    if not_joined:
        text = "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:</b>"
        kb = get_subscription_keyboard(not_joined)
        if isinstance(event, types.CallbackQuery):
            try:
                await event.message.edit_text(text, reply_markup=kb)
            except Exception:
                await event.message.answer(text, reply_markup=kb)
        else:
            await event.answer(text, reply_markup=kb)
        return False
    return True

@dp.callback_query(F.data == "subs_private")
async def subs_private(callback: types.CallbackQuery):
    await callback.answer("Bu yopiq kanal — admin bilan bog'laning.", show_alert=True)

@dp.callback_query(F.data == "check_subs")
async def check_subs_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = await check_subscriptions(user_id)
    if not_joined:
        return await callback.answer("❌ Siz hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        t(user_id, "welcome", name=get_user(user_id)['username']),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "enter"), callback_data="enter_system")]])
    )
    await callback.answer("✅ Rahmat!")

# ==========================================
# START VA ADMIN PANEL
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    user["username"] = message.from_user.username or "Foydalanuvchi"

    args = message.text.split()
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if (ref_id != user_id and user["referals"] == 0
                    and user["balance"] == 0 and str(ref_id) in users_db):
                get_user(ref_id)["balance"] = round(get_user(ref_id)["balance"] + 2.0, 2)
                get_user(ref_id)["referals"] += 1
                save_json(USERS_FILE, users_db)
                try:
                    await bot.send_message(ref_id, "🎉 Referal qo'shildi! +2 Stars")
                except Exception:
                    pass
        except ValueError:
            pass

    save_json(USERS_FILE, users_db)

    not_joined = await check_subscriptions(user_id)
    if not_joined:
        await message.answer(
            "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:</b>",
            reply_markup=get_subscription_keyboard(not_joined)
        )
        return

    await message.answer(
        t(user_id, "welcome", name=user['username']),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "enter"), callback_data="enter_system")]])
    )

@dp.callback_query(F.data == "enter_system")
async def enter_system(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not await require_subscription(callback, user_id):
        return
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_status_text(user_id) + t(user_id, "choose"),
        reply_markup=get_main_keyboard(user_id)
    )

@dp.message(Command("admin"))
async def cmd_admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz!")
    await state.clear()

    try:
        star_balance = await bot.get_my_star_balance()
        real_stars = star_balance.amount
    except Exception:
        real_stars = "Xatolik"

    text = "👑 <b>Admin Panel</b>\n\n"
    text += f"💳 <b>Botning Real Stars Balansi:</b> <code>{real_stars}</code>\n\n"
    text += "👥 <b>Foydalanuvchilar:</b>\n"

    kb = []
    count = 0
    for uid, udata in users_db.items():
        if count >= 20:
            text += "<i>... va boshqalar</i>\n"
            break
        text += f"◈ @{udata.get('username', '?')} (ID: <code>{uid}</code>) — {udata.get('balance', 0):.2f} Stars\n"
        kb.append([InlineKeyboardButton(text=f"👤 @{udata.get('username', '?')} ({udata.get('balance', 0):.2f}⭐)", callback_data=f"admin_view_{uid}")])
        count += 1

    kb.append([InlineKeyboardButton(text="🎟 Promo Kodlar", callback_data="admin_promo_menu")])
    kb.append([InlineKeyboardButton(text="📋 Tasklar", callback_data="admin_tasks_menu")])
    kb.append([InlineKeyboardButton(text="🧪 Kanallarni Tekshirish", callback_data="admin_test_channels")])
    kb.append([InlineKeyboardButton(text="➕ Kanal Qo'shish", callback_data="admin_add_channel")])
    kb.append([InlineKeyboardButton(text="🗑 Kanal O'chirish", callback_data="admin_del_channel_list")])

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("admin_view_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_view_user(callback: types.CallbackQuery):
    target_id = callback.data.split("_")[-1]
    if target_id not in users_db:
        return await callback.answer("Foydalanuvchi topilmadi!", show_alert=True)
    user = users_db[target_id]
    stats_text = (
        f"👤 <b>Foydalanuvchi Statistikasi</b>\n\n"
        f"◈ <b>ID:</b> <code>{target_id}</code>\n"
        f"◈ <b>Username:</b> <code>@{user.get('username', '?')}</code>\n"
        f"◈ <b>Balans:</b> <code>{user.get('balance', 0):.2f} Stars</code>\n"
        f"◈ <b>Referallar:</b> <code>{user.get('referals', 0)} ta</code>\n"
        f"◈ <b>Til:</b> <code>{user.get('lang', 'uz')}</code>\n"
        f"◈ <b>Win streak:</b> <code>{user.get('win_streak', 0)}</code>\n"
        f"◈ <b>Loss streak:</b> <code>{user.get('loss_streak', 0)}</code>\n"
        f"◈ <b>1-qadam cashout:</b> <code>{user.get('first_step_cashout_count', 0)}</code>\n"
        f"◈ <b>Shubhali:</b> <code>{user.get('caught_cheating', False)}</code>\n\n"
        f"📊 <b>O'yin Statistikasi:</b>\n"
        f"◈ <b>Jami tikilgan:</b> <code>{user.get('total_wagered', 0.0):.2f} Stars</code>\n"
        f"◈ <b>Jami yutilgan:</b> <code>{user.get('total_won', 0.0):.2f} Stars</code>\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ Balansni 0 ga tushirish", callback_data=f"admin_zero_{target_id}")],
        [InlineKeyboardButton(text="🔄 Trap counter ni reset qilish", callback_data=f"admin_reset_trap_{target_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]
    ])
    await callback.message.edit_text(stats_text, reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_zero_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_zero_balance(callback: types.CallbackQuery):
    target_id = callback.data.split("_")[-1]
    if target_id in users_db:
        users_db[target_id]["balance"] = 0.0
        users_db[target_id]["caught_cheating"] = True
        save_json(USERS_FILE, users_db)
        await callback.message.edit_text(
            f"✅ <code>@{users_db[target_id].get('username', '?')}</code> balansi 0 ga tushirildi."
        )
    else:
        await callback.answer("Topilmadi!", show_alert=True)

@dp.callback_query(F.data.startswith("admin_reset_trap_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_reset_trap(callback: types.CallbackQuery):
    target_id = callback.data.split("_")[-1]
    if target_id in users_db:
        users_db[target_id]["first_step_cashout_count"] = 0
        users_db[target_id]["win_streak"] = 0
        users_db[target_id]["loss_streak"] = 0
        save_json(USERS_FILE, users_db)
        await callback.message.edit_text("✅ Trap counter reset qilindi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]]))
    else:
        await callback.answer("Topilmadi!", show_alert=True)

@dp.callback_query(F.data == "admin_back", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_back(callback: types.CallbackQuery):
    await callback.message.delete()
    fake_msg = callback.message
    fake_msg.from_user = callback.from_user
    await cmd_admin_panel(fake_msg, None)
    await callback.answer()

# ==========================================
# KANALLAR BOSHQARUVI
# ==========================================
@dp.callback_query(F.data == "admin_add_channel", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_add_channel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 <b>1-qadam: Kanal ID sini kiriting</b>\n\n"
        "Ommaviy: <code>@kanal_username</code>\n"
        "Yopiq: <code>-1001234567890</code>"
    )
    await state.set_state(AdminStates.waiting_for_channel_id)

@dp.message(AdminStates.waiting_for_channel_id, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_channel_id(message: types.Message, state: FSMContext):
    channel_id = message.text.strip()
    try:
        chat = await bot.get_chat(chat_id=channel_id)
        await state.update_data(channel_id=channel_id, channel_name=chat.title)
        await message.answer(f"✅ Kanal topildi: <b>{chat.title}</b>\n\n🔗 <b>2-qadam: Kanal havolasini kiriting</b>")
        await state.set_state(AdminStates.waiting_for_channel_link)
    except Exception as e:
        await message.answer(f"❌ <b>Xatolik!</b> Kanal topilmadi.\n\nSabab: {e}")
        await state.clear()

@dp.message(AdminStates.waiting_for_channel_link, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_channel_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channels = app_config.get("channels", [])
    channels.append({
        "id": data.get("channel_id"),
        "link": message.text.strip(),
        "name": data.get("channel_name") or data.get("channel_id")
    })
    app_config["channels"] = channels
    save_json(CONFIG_FILE, app_config)
    await state.clear()
    await message.answer("✅ Kanal qo'shildi!", reply_markup=get_main_keyboard(message.from_user.id))

@dp.callback_query(F.data == "admin_test_channels", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_test_channels(callback: types.CallbackQuery):
    channels = app_config.get("channels", [])
    report = "🧪 <b>Kanallar holati:</b>\n\n"
    if not channels:
        report += "<i>Kanallar yo'q.</i>"
    for ch in channels:
        try:
            chat = await bot.get_chat(chat_id=ch['id'])
            report += f"✅ {ch.get('name', ch['id'])} — OK ({chat.title})\n"
        except Exception as e:
            report += f"❌ {ch.get('name', ch['id'])} — Xato: {e}\n"
    await callback.message.answer(report)

@dp.callback_query(F.data == "admin_del_channel_list", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_channel_list(callback: types.CallbackQuery):
    channels = app_config.get("channels", [])
    if not channels:
        return await callback.answer("Kanallar yo'q!", show_alert=True)
    kb = []
    for idx, ch in enumerate(channels):
        kb.append([InlineKeyboardButton(text=f"❌ {ch.get('name', ch['id'])}", callback_data=f"admin_del_channel_{idx}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")])
    await callback.message.edit_text("🗑 <b>Qaysi kanalni o'chirmoqchisiz?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("admin_del_channel_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_channel(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[-1])
    channels = app_config.get("channels", [])
    if 0 <= idx < len(channels):
        removed = channels.pop(idx)
        app_config["channels"] = channels
        save_json(CONFIG_FILE, app_config)
        await callback.message.edit_text(
            f"✅ <code>{removed.get('name', removed['id'])}</code> o'chirildi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]])
        )
    else:
        await callback.answer("Topilmadi!", show_alert=True)

# ==========================================
# PROMO KODLAR BOSHQARUVI
# ==========================================
@dp.callback_query(F.data == "admin_promo_menu", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_promo_menu(callback: types.CallbackQuery):
    text = "🎟 <b>Promo Kodlar</b>\n\n<b>Mavjud:</b>\n"
    for code, amount in promos_db.items():
        text += f"◈ <code>{code}</code> — {amount} Stars\n"
    kb = [
        [InlineKeyboardButton(text="➕ Yangi Promo", callback_data="admin_add_promo")],
        [InlineKeyboardButton(text="🗑 Promoni O'chirish", callback_data="admin_del_promo_list")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "admin_add_promo", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_add_promo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🎟 <b>Yangi Promo Kod</b>\n\nPromo kod nomini kiriting:")
    await state.set_state(AdminStates.waiting_for_promo_name)

@dp.message(AdminStates.waiting_for_promo_name, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_promo_name(message: types.Message, state: FSMContext):
    await state.update_data(promo_name=message.text.strip())
    await message.answer("💰 Bu promo qancha Stars bersin? (Faqat raqam):")
    await state.set_state(AdminStates.waiting_for_promo_amount)

@dp.message(AdminStates.waiting_for_promo_amount, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_promo_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Faqat raqam kiriting.")
    data = await state.get_data()
    promo_name = data.get("promo_name")
    amount = int(message.text)
    promos_db[promo_name] = amount
    save_json(PROMO_FILE, promos_db)
    await state.clear()
    await message.answer(f"✅ Promo yaratildi: <code>{promo_name}</code> — <b>{amount} Stars</b>")

@dp.callback_query(F.data == "admin_del_promo_list", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_promo_list(callback: types.CallbackQuery):
    kb = []
    for code in promos_db.keys():
        kb.append([InlineKeyboardButton(text=f"❌ {code}", callback_data=f"admin_del_promo_{code}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_promo_menu")])
    await callback.message.edit_text("🗑 <b>Qaysi promo kodni o'chirmoqchisiz?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("admin_del_promo_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_promo(callback: types.CallbackQuery):
    code_to_del = callback.data[len("admin_del_promo_"):]
    if code_to_del in promos_db:
        del promos_db[code_to_del]
        save_json(PROMO_FILE, promos_db)
        await callback.message.edit_text(
            f"✅ <code>{code_to_del}</code> o'chirildi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_promo_menu")]])
        )
    else:
        await callback.answer("Topilmadi!", show_alert=True)

# ==========================================
# TASKLAR BOSHQARUVI (ADMIN)
# ==========================================
@dp.callback_query(F.data == "admin_tasks_menu", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_tasks_menu(callback: types.CallbackQuery):
    text = "📋 <b>Tasklar</b>\n\n<b>Mavjud:</b>\n"
    if not tasks_db:
        text += "<i>Hozircha yo'q.</i>\n"
    else:
        for task in tasks_db:
            text += f"◈ {task['name']} — {task['reward']} Stars ({task['link']})\n"
    kb = [
        [InlineKeyboardButton(text="➕ Yangi Task", callback_data="admin_add_task")],
        [InlineKeyboardButton(text="🗑 Taskni O'chirish", callback_data="admin_del_task_list")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "admin_add_task", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_add_task(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📋 <b>Yangi Task</b>\n\nVazifa nomini kiriting:")
    await state.set_state(AdminStates.waiting_for_task_name)

@dp.message(AdminStates.waiting_for_task_name, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text.strip())
    await message.answer("💰 Bu vazifa uchun qancha Stars? (Faqat raqam):")
    await state.set_state(AdminStates.waiting_for_task_reward)

@dp.message(AdminStates.waiting_for_task_reward, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_task_reward(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Faqat raqam kiriting.")
    await state.update_data(task_reward=int(message.text))
    await message.answer("🔗 Kanal havolasini kiriting:\n(<code>@kanal</code> yoki <code>https://t.me/kanal</code>)")
    await state.set_state(AdminStates.waiting_for_task_link)

@dp.message(AdminStates.waiting_for_task_link, F.func(lambda m: m.from_user.id == ADMIN_ID))
async def process_task_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    link_raw = message.text.strip()

    chat_id = None
    if re.fullmatch(r"-?\d+", link_raw):
        chat_id = link_raw
    elif link_raw.startswith("@"):
        chat_id = link_raw
    else:
        m = re.search(r"t\.me/([A-Za-z0-9_]+)", link_raw)
        if m:
            chat_id = "@" + m.group(1)

    if not chat_id:
        return await message.answer("❌ Havolani tushunmadim. <code>@username</code> yoki <code>https://t.me/username</code>.")

    try:
        chat = await bot.get_chat(chat_id=chat_id)
        chat_title = chat.title
    except Exception as e:
        return await message.answer(f"❌ Kanal topilmadi yoki bot admin emas.\nSabab: {e}")

    task_id = f"task_{len(tasks_db) + 1}_{int(datetime.now().timestamp())}"
    new_task = {
        "id": task_id,
        "name": data.get("task_name"),
        "reward": data.get("task_reward"),
        "type": "channel",
        "link": chat_id,
        "chat_title": chat_title
    }
    tasks_db.append(new_task)
    save_json(TASKS_FILE, tasks_db)
    await state.clear()
    await message.answer(
        f"✅ Task yaratildi!\n\n"
        f"Nomi: {new_task['name']}\n"
        f"Mukofot: {new_task['reward']} Stars\n"
        f"Kanal: {chat_title} (<code>{chat_id}</code>)"
    )

@dp.callback_query(F.data == "admin_del_task_list", F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_task_list(callback: types.CallbackQuery):
    kb = []
    for task in tasks_db:
        kb.append([InlineKeyboardButton(text=f"❌ {task['name']}", callback_data=f"admin_del_task_{task['id']}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_tasks_menu")])
    await callback.message.edit_text("🗑 <b>Qaysi taskni o'chirmoqchisiz?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("admin_del_task_"), F.func(lambda m: m.from_user.id == ADMIN_ID))
async def admin_del_task(callback: types.CallbackQuery):
    global tasks_db
    task_id = callback.data[len("admin_del_task_"):]
    tasks_db = [tt for tt in tasks_db if tt['id'] != task_id]
    save_json(TASKS_FILE, tasks_db)
    await callback.message.edit_text(
        "✅ Task o'chirildi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_tasks_menu")]])
    )

# ==========================================
# O'YINLAR MENYUSI
# ==========================================
@dp.message(F.text.in_([TEXTS["uz"]["btn_stars"], TEXTS["ru"]["btn_stars"], TEXTS["en"]["btn_stars"]]))
async def stars_drop_menu(message: types.Message):
    user_id = message.from_user.id
    if not await require_subscription(message, user_id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(user_id, "btn_daily"), callback_data="drop_daily")],
        [InlineKeyboardButton(text=t(user_id, "btn_tasks"), callback_data="show_tasks")],
        [InlineKeyboardButton(text=t(user_id, "btn_darts"), callback_data="play_darts"), InlineKeyboardButton(text=t(user_id, "btn_dice"), callback_data="play_dice")],
        [InlineKeyboardButton(text=t(user_id, "btn_bowl"), callback_data="play_bowling"), InlineKeyboardButton(text=t(user_id, "btn_basket"), callback_data="play_basket")],
        [InlineKeyboardButton(text=t(user_id, "btn_slot"), callback_data="play_slot"), InlineKeyboardButton(text=t(user_id, "btn_mines"), callback_data="start_mines")],
        [InlineKeyboardButton(text=t(user_id, "btn_ladder"), callback_data="start_ladder")]
    ])
    await message.answer(get_status_text(user_id) + t(user_id, "drop_menu"), reply_markup=kb)

@dp.callback_query(F.data == "back_to_stars")
async def back_to_stars(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(user_id, "btn_daily"), callback_data="drop_daily")],
        [InlineKeyboardButton(text=t(user_id, "btn_tasks"), callback_data="show_tasks")],
        [InlineKeyboardButton(text=t(user_id, "btn_darts"), callback_data="play_darts"), InlineKeyboardButton(text=t(user_id, "btn_dice"), callback_data="play_dice")],
        [InlineKeyboardButton(text=t(user_id, "btn_bowl"), callback_data="play_bowling"), InlineKeyboardButton(text=t(user_id, "btn_basket"), callback_data="play_basket")],
        [InlineKeyboardButton(text=t(user_id, "btn_slot"), callback_data="play_slot"), InlineKeyboardButton(text=t(user_id, "btn_mines"), callback_data="start_mines")],
        [InlineKeyboardButton(text=t(user_id, "btn_ladder"), callback_data="start_ladder")]
    ])
    try:
        await callback.message.edit_text(get_status_text(user_id) + t(user_id, "drop_menu"), reply_markup=kb)
    except Exception:
        await callback.message.answer(get_status_text(user_id) + t(user_id, "drop_menu"), reply_markup=kb)

# ==========================================
# TASKLAR — FOYDALANUVCHI
# ==========================================
@dp.callback_query(F.data == "show_tasks")
async def show_tasks(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not tasks_db:
        return await callback.answer("Hozircha vazifalar yo'q.", show_alert=True)

    kb = []
    for task in tasks_db:
        if task['id'] in user.get("completed_tasks", []):
            kb.append([InlineKeyboardButton(text=f"✅ {task['name']} (Bajarildi)", callback_data="task_done")])
        else:
            kb.append([InlineKeyboardButton(text=f"{task['name']} (+{task['reward']}⭐)", callback_data=f"task_info_{task['id']}")])

    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_stars")])

    try:
        await callback.message.edit_text(
            get_status_text(user_id) + "📋 <b>Mavjud Vazifalar</b>\n\nQuyidagi vazifalarni bajarib, Stars ishlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
    except Exception:
        await callback.message.answer(
            get_status_text(user_id) + "📋 <b>Mavjud Vazifalar</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )

@dp.callback_query(F.data.startswith("task_info_"))
async def task_info(callback: types.CallbackQuery):
    task_id = callback.data[len("task_info_"):]
    task = next((tt for tt in tasks_db if tt['id'] == task_id), None)
    
    if not task:
        return await callback.answer("Task topilmadi!", show_alert=True)

    link = task['link']
    if link.startswith("@") or link.startswith("-"):
        channel_link = f"https://t.me/{link.replace('@', '')}" if link.startswith("@") else "https://t.me/c/"
    else:
        channel_link = link

    kb = []
    if channel_link.startswith("https://t.me/"):
        kb.append([InlineKeyboardButton(text="📢 Kanalga o'tish", url=channel_link)])
    
    kb.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data=f"do_task_{task_id}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="show_tasks")])

    await callback.message.edit_text(
        get_status_text(callback.from_user.id) + 
        f"📋 <b>Vazifa:</b> {task['name']}\n"
        f"💰 <b>Mukofot:</b> +{task['reward']} Stars\n\n"
        f"<i>Avval kanalga a'zo bo'ling, so'ngra 'Tekshirish' tugmasini bosing.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(F.data.startswith("do_task_"))
async def do_task(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    task_id = callback.data[len("do_task_"):]

    task = next((tt for tt in tasks_db if tt['id'] == task_id), None)
    if not task:
        return await callback.answer("Task topilmadi!", show_alert=True)

    if task_id in user.get("completed_tasks", []):
        return await callback.answer("Siz bu vazifani allaqachon bajargansiz!", show_alert=True)

    chat_id = task['link']
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in ["left", "kicked"]:
            raise Exception("Siz kanalga a'zo emassiz")
    except Exception as e:
        error_text = str(e).lower()
        if "member list is inaccessible" in error_text or "not enough rights" in error_text or "chat not found" in error_text:
            await bot.send_message(
                ADMIN_ID, 
                f"⚠️ <b>Diqqat!</b> Task tekshirishda xato:\n"
                f"Kanal: <code>{chat_id}</code>\n"
                f"Xato: <code>{e}</code>\n\n"
                f"<i>Iltimos, botni kanaldan chiqarib, qayta qo'shing va unga 'Foydalanuvchilarni boshqarish' huquqini bering. Yoki kanalni @username orqali qayta qo'shing.</i>"
            )
            pass
        else:
            return await callback.answer("❌ Siz hali kanalga a'zo bo'lmadingiz. Kanalga o'tib, a'zo bo'ling va qayta tekshiring.", show_alert=True)

    user["balance"] = round(user["balance"] + task['reward'], 2)
    user.setdefault("completed_tasks", []).append(task_id)
    user["history"].append(f"Task: {task['name']} (+{task['reward']} Stars)")
    save_json(USERS_FILE, users_db)

    await callback.answer(f"✅ Vazifa bajarildi! +{task['reward']} Stars", show_alert=True)
    await show_tasks(callback)

@dp.callback_query(F.data == "task_done")
async def task_done(callback: types.CallbackQuery):
    await callback.answer("Siz bu vazifani allaqachon bajargansiz!", show_alert=True)

# ==========================================
# KUNLIK BONUS
# ==========================================
@dp.callback_query(F.data == "drop_daily")
async def drop_daily(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id == ADMIN_ID:
        return await callback.answer("Admin, sizga shart emas!", show_alert=True)

    user = get_user(user_id)
    today = datetime.now().date().isoformat()

    if user.get("last_daily") == today:
        return await callback.answer(t(user_id, "daily_no"), show_alert=True)

    user["balance"] = round(user["balance"] + 1.0, 2)
    user["last_daily"] = today
    save_json(USERS_FILE, users_db)
    await callback.answer(t(user_id, "daily_ok"), show_alert=True)

# ============================================================
# 🪜 NARVON O'YINI
# ============================================================
LADDER_MULTIPLIERS = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
WIN_CHANCES = {0: 0.70, 1: 0.60, 2: 0.50, 3: 0.40, 4: 0.35, 5: 0.25, 6: 0.15, 7: 0.05, 8: 0.01}

@dp.callback_query(F.data == "start_ladder")
async def ask_bet_ladder(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not await require_subscription(callback, user_id):
        return
    await state.update_data(game_type="ladder")
    await state.set_state(GameStates.waiting_for_bet)
    await callback.message.edit_text(get_status_text(user_id) + "🪜 <b>NARVON O'YINI</b>\n\nQancha Stars tikmoqchisiz? (Faqat raqam yuboring, masalan 5 yoki 5.5):")

@dp.callback_query(GameStates.playing_ladder, F.data.startswith("ladder_click_"))
async def ladder_click(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get('step', 0)
    bet_amount = data.get('bet', 5.0)
    clicked_indices = data.get('clicked_indices', [])
    rows_mines = data.get('rows_mines', [])
    user_id = callback.from_user.id
    user = get_user(user_id)

    clicked_index = int(callback.data.split("_")[-1])

    if step == 0 and should_trigger_cashout_trap(user):
        is_win = random.random() >= FIRST_STEP_TRAP_PROB
        reset_cashout_trap(user)
    else:
        loss_streak = user.get("loss_streak", 0)
        if loss_streak >= 2 and step < 2:
            win_chance = 0.95 
        else:
            base_chance = WIN_CHANCES.get(step, 0.01)
            win_chance = apply_streak_penalty(user, base_chance)
            if is_consolation_time(user):
                win_chance = max(win_chance, CONSOLATION_PROB)
        is_win = random.random() < win_chance

    if not is_win:
        await state.clear()
        if user_id != ADMIN_ID:
            update_after_loss(user, bet_amount)
        save_json(USERS_FILE, users_db)

        kb = []
        for i in range(len(LADDER_MULTIPLIERS) - 1, -1, -1):
            row_buttons = []
            for j in range(6):
                if i == step and j == clicked_index:
                    row_buttons.append(InlineKeyboardButton(text="💥", callback_data="ladder_ignore"))
                elif i > step and j in rows_mines[i]:
                    row_buttons.append(InlineKeyboardButton(text="💣", callback_data="ladder_ignore"))
                elif i < step and j == clicked_indices[i]:
                    row_buttons.append(InlineKeyboardButton(text="🪙", callback_data="ladder_ignore"))
                else:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
            kb.append(row_buttons)

        kb.append([InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="start_ladder")])

        await callback.message.edit_text(
            get_status_text(user_id) +
            f"💥 <b>PORTLADINGIZ!</b>\n\n"
            f"Siz <b>{step + 1}-qatorda</b> minaga urildingiz va <b>{bet_amount:.2f} Stars</b> yutqazdingiz.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        return

    clicked_indices.append(clicked_index)
    step += 1
    await state.update_data(step=step, clicked_indices=clicked_indices)

    if step >= len(LADDER_MULTIPLIERS):
        current_multiplier = LADDER_MULTIPLIERS[-1]
        winnings = round(bet_amount * current_multiplier, 2)
        if user_id != ADMIN_ID:
            user["balance"] = round(user["balance"] + winnings, 2)
            update_after_win(user, winnings, bet_amount)
            save_json(USERS_FILE, users_db)
        await state.clear()

        kb = []
        for i in range(len(LADDER_MULTIPLIERS) - 1, -1, -1):
            row_buttons = []
            for j in range(6):
                if i < len(clicked_indices) and j == clicked_indices[i]:
                    row_buttons.append(InlineKeyboardButton(text="🪙", callback_data="ladder_ignore"))
                else:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
            kb.append(row_buttons)
        kb.append([InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="start_ladder")])

        await callback.message.edit_text(
            get_status_text(user_id) +
            f"🏆 <b>G'ALABA!</b>\n\n"
            f"Siz barcha qatorlardan o'tdingiz! Koeffitsiyent: <b>{current_multiplier}x</b>.\n"
            f"Balansingizga <b>+{winnings:.2f} Stars</b> qo'shildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        return

    current_multiplier = LADDER_MULTIPLIERS[step - 1]
    potential_win = round(bet_amount * current_multiplier, 2)

    kb = []
    for i in range(len(LADDER_MULTIPLIERS) - 1, -1, -1):
        row_buttons = []
        for j in range(6):
            if i < step - 1:
                if j == clicked_indices[i]:
                    row_buttons.append(InlineKeyboardButton(text="🪙", callback_data="ladder_ignore"))
                else:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
            elif i == step - 1:
                if j == clicked_index:
                    row_buttons.append(InlineKeyboardButton(text="🪙", callback_data="ladder_ignore"))
                elif j in rows_mines[i]:
                    row_buttons.append(InlineKeyboardButton(text="💣", callback_data="ladder_ignore"))
                else:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
            elif i == step:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data=f"ladder_click_{j}"))
            else:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
        kb.append(row_buttons)

    if step > 0:
        kb.append([InlineKeyboardButton(text=f"💰 Yechib olish ({potential_win:.2f} Stars)", callback_data="ladder_cashout")])
    kb.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="ladder_cancel")])

    await callback.message.edit_text(
        get_status_text(user_id) +
        f"🪜 <b>NARVON O'YINI</b>\n\n"
        f"Stavka: <b>{bet_amount:.2f} Stars</b>\n"
        f"O'tilgan qatorlar: <b>{step}/{len(LADDER_MULTIPLIERS)}</b>\n"
        f"Koeffitsiyent: <b>{current_multiplier}x</b>\n\n"
        f"Keyingi qatordan joy tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(GameStates.playing_ladder, F.data == "ladder_cashout")
async def ladder_cashout(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get('step', 0)
    bet_amount = data.get('bet', 5.0)
    clicked_indices = data.get('clicked_indices', [])
    user_id = callback.from_user.id
    user = get_user(user_id)

    if step == 0:
        return await callback.answer("Siz hali birorta qatordan o'tmadingiz!", show_alert=True)

    current_multiplier = LADDER_MULTIPLIERS[step - 1]
    winnings = round(bet_amount * current_multiplier, 2)

    if user_id != ADMIN_ID:
        if step == 1:
            increment_cashout_trap(user)
        else:
            reset_cashout_trap(user)
        user["balance"] = round(user["balance"] + winnings, 2)
        update_after_win(user, winnings, bet_amount)
        save_json(USERS_FILE, users_db)

    await state.clear()

    kb = []
    for i in range(len(LADDER_MULTIPLIERS) - 1, -1, -1):
        row_buttons = []
        for j in range(6):
            if i < len(clicked_indices) and j == clicked_indices[i]:
                row_buttons.append(InlineKeyboardButton(text="🪙", callback_data="ladder_ignore"))
            else:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
        kb.append(row_buttons)
    kb.append([InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="start_ladder")])

    await callback.message.edit_text(
        get_status_text(user_id) +
        f"💰 <b>PUL YECHIB OLINDI!</b>\n\n"
        f"Siz <b>{current_multiplier}x</b> koeffitsiyent bilan <b>{winnings:.2f} Stars</b> yutib oldingiz!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(GameStates.playing_ladder, F.data == "ladder_cancel")
async def ladder_cancel(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bet_amount = data.get('bet', 0.0)
    user_id = callback.from_user.id
    user = get_user(user_id)
    await state.clear()
    if user_id != ADMIN_ID:
        update_after_loss(user, bet_amount)
        save_json(USERS_FILE, users_db)
    await callback.message.edit_text(
        get_status_text(user_id) + "❌ O'yin bekor qilindi. Stavka yutqazildi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "back"), callback_data="back_to_stars")]])
    )

@dp.callback_query(F.data == "ladder_ignore")
async def ladder_ignore(callback: types.CallbackQuery):
    await callback.answer()

# ============================================================
# 💣 MINA O'YINI
# ============================================================
@dp.callback_query(F.data == "start_mines")
async def ask_bet_mines(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not await require_subscription(callback, user_id):
        return
    await state.update_data(game_type="mines")
    await state.set_state(GameStates.waiting_for_bet)
    await callback.message.edit_text(get_status_text(user_id) + "💣 <b>MINA O'YINI</b>\n\nQancha Stars tikmoqchisiz? (Faqat raqam yuboring, masalan 5 yoki 5.5):")

@dp.message(GameStates.waiting_for_mines_count)
async def process_mines_count(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not message.text.isdigit():
        await state.clear()
        return await message.answer(
            get_status_text(user_id) + "❌ O'yin bekor qilindi.",
            reply_markup=get_main_keyboard(user_id)
        )

    mines_count = int(message.text)
    if mines_count < 3 or mines_count > 9:
        return await message.answer("❌ Mina soni 3 dan 9 gacha bo'lishi kerak.")

    data = await state.get_data()
    bet_amount = data.get('bet', 5.0)
    user = get_user(user_id)

    if user_id != ADMIN_ID:
        user["balance"] = round(user["balance"] - bet_amount, 2)
        save_json(USERS_FILE, users_db)

    total_cells = 16
    mines = random.sample(range(total_cells), mines_count)

    await state.update_data(mines=mines, opened=[], total_cells=total_cells, mines_count=mines_count, bet=bet_amount)
    await state.set_state(GameStates.playing_mines)

    kb = []
    for i in range(0, total_cells, 4):
        row = []
        for j in range(4):
            cell_id = i + j
            row.append(InlineKeyboardButton(text="🔒", callback_data=f"mine_click_{cell_id}"))
        kb.append(row)

    await message.answer(
        get_status_text(user_id) +
        f"💣 <b>MINA O'YINI BOSHLANDI</b>\n\n"
        f"Stavka: <b>{bet_amount:.2f} Stars</b>\n"
        f"Minalar: <b>{mines_count} ta</b>\n\n"
        f"Qulfni ochish uchun katakni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

def calculate_multiplier(opened_count, mines_count):
    if opened_count == 0:
        return 1.00
    elif opened_count == 1:
        return 1.1
    elif opened_count == 2:
        return 1.3
    elif opened_count == 3:
        return 1.5
    else:
        return round(1.5 + (opened_count - 3) * 0.2, 2)

@dp.callback_query(GameStates.playing_mines, F.data.startswith("mine_click_"))
async def click_mine_cell(callback: types.CallbackQuery, state: FSMContext):
    cell_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    mines = data['mines']
    opened = data['opened']
    total_cells = data['total_cells']
    mines_count = data['mines_count']
    bet_amount = data.get('bet', 5.0)
    user_id = callback.from_user.id
    user = get_user(user_id)

    if cell_id in opened:
        return await callback.answer("Bu katak allaqachon ochilgan!")

    current_multiplier = calculate_multiplier(len(opened), mines_count)

    if len(opened) == 0 and should_trigger_cashout_trap(user):
        forced_hit = random.random() < FIRST_STEP_TRAP_PROB
        reset_cashout_trap(user)
    else:
        loss_streak = user.get("loss_streak", 0)
        if loss_streak >= 2 and len(opened) < 2:
            adjusted_win_prob = 0.95
        else:
            natural_win_prob = 1 - (mines_count / max(1, total_cells - len(opened)))
            adjusted_win_prob = apply_streak_penalty(user, natural_win_prob)
            if is_consolation_time(user):
                adjusted_win_prob = max(adjusted_win_prob, CONSOLATION_PROB)
                
        adjusted_mine_prob = 1 - adjusted_win_prob
        forced_hit = random.random() < adjusted_mine_prob

    if cell_id in mines or forced_hit:
        opened.append(cell_id)
        await state.clear()

        kb = []
        for i in range(0, total_cells, 4):
            row = []
            for j in range(4):
                c_id = i + j
                if c_id in mines or c_id == cell_id:
                    row.append(InlineKeyboardButton(text="💥", callback_data="mines_ignore"))
                else:
                    row.append(InlineKeyboardButton(text="💎", callback_data="mines_ignore"))
            kb.append(row)

        kb.append([InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="start_mines")])

        if user_id != ADMIN_ID:
            update_after_loss(user, bet_amount)
        save_json(USERS_FILE, users_db)

        await callback.message.edit_text(
            get_status_text(user_id) +
            f"💥 <b>PORTLADINGIZ!</b>\n\n"
            f"Siz minaga urildingiz va <b>{bet_amount:.2f} Stars</b> yutqazdingiz.\n"
            f"Koeffitsiyent: <b>{current_multiplier:.2f}x</b> edi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        return

    opened.append(cell_id)
    new_multiplier = calculate_multiplier(len(opened), mines_count)
    await state.update_data(opened=opened)

    kb = []
    for i in range(0, total_cells, 4):
        row = []
        for j in range(4):
            c_id = i + j
            if c_id in opened:
                row.append(InlineKeyboardButton(text="💎", callback_data="mines_ignore"))
            else:
                row.append(InlineKeyboardButton(text="🔒", callback_data=f"mine_click_{c_id}"))
        kb.append(row)

    potential_win = round(bet_amount * new_multiplier, 2)
    kb.append([InlineKeyboardButton(text=f"💰 Yechib olish ({potential_win:.2f} Stars)", callback_data="cashout_mines")])
    kb.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="cancel_mines")])

    await callback.message.edit_text(
        get_status_text(user_id) +
        f"💣 <b>MINA O'YINI</b>\n\n"
        f"Ochilgan kataklar: <b>{len(opened)} ta</b>\n"
        f"Joriy koeffitsiyent: <b>{new_multiplier:.2f}x</b>\n"
        f"Yutishingiz mumkin: <b>{potential_win:.2f} Stars</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(GameStates.playing_mines, F.data == "cashout_mines")
async def cashout_mines(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_cells = data['total_cells']
    mines = data['mines']
    mines_count = data['mines_count']
    opened = data['opened']
    bet_amount = data.get('bet', 5.0)
    user_id = callback.from_user.id
    user = get_user(user_id)

    multiplier = calculate_multiplier(len(opened), mines_count)
    winnings = round(bet_amount * multiplier, 2)

    if user_id != ADMIN_ID:
        if len(opened) == 1:
            increment_cashout_trap(user)
        else:
            reset_cashout_trap(user)
        user["balance"] = round(user["balance"] + winnings, 2)
        update_after_win(user, winnings, bet_amount)

    await state.clear()
    kb = []
    for i in range(0, total_cells, 4):
        row = []
        for j in range(4):
            c_id = i + j
            row.append(InlineKeyboardButton(text="💥" if c_id in mines else "💎", callback_data="mines_ignore"))
        kb.append(row)

    kb.append([InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="start_mines")])
    save_json(USERS_FILE, users_db)

    await callback.message.edit_text(
        get_status_text(user_id) +
        f"💰 <b>PUL YECHIB OLINDI!</b>\n\nSiz <b>{multiplier:.2f}x</b> koeffitsiyent bilan <b>{winnings:.2f} Stars</b> yutib oldingiz!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(GameStates.playing_mines, F.data == "cancel_mines")
async def cancel_mines(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bet_amount = data.get('bet', 0.0)
    user_id = callback.from_user.id
    user = get_user(user_id)
    await state.clear()
    if user_id != ADMIN_ID:
        update_after_loss(user, bet_amount)
        save_json(USERS_FILE, users_db)
    await callback.message.edit_text(
        get_status_text(user_id) + "❌ O'yin bekor qilindi. Stavka yutqazildi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "back"), callback_data="back_to_stars")]])
    )

@dp.callback_query(F.data == "mines_ignore")
async def mines_ignore(callback: types.CallbackQuery):
    await callback.answer()

# ==========================================
# ANIMATSION O'YINLAR
# ==========================================
@dp.callback_query(F.data.startswith("play_"))
async def ask_bet_anim_game(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not await require_subscription(callback, user_id):
        return
    game_type = callback.data.split("_")[1]
    await state.update_data(game_type=game_type)
    await state.set_state(GameStates.waiting_for_bet)
    await callback.message.edit_text(get_status_text(user_id) + f"🎮 <b>O'YIN: {game_type.upper()}</b>\n\nQancha Stars tikmoqchisiz? (Faqat raqam yuboring, masalan 5 yoki 5.5):")

# ============================================================
# 🎲 STAVKANI QABUL QILISH (ARRA TISHLI MODEL)
# ============================================================
@dp.message(GameStates.waiting_for_bet)
async def process_bet(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)

    try:
        bet_amount = float(message.text.replace(',', '.'))
    except ValueError:
        await state.clear()
        return await message.answer(
            get_status_text(user_id) + "❌ O'yin bekor qilindi. Faqat raqam kiriting.",
            reply_markup=get_main_keyboard(user_id)
        )

    if bet_amount < 0.1:
        return await message.answer("❌ Stavka kamida 0.1 Stars.")

    if user_id != ADMIN_ID and user["balance"] < bet_amount:
        await state.clear()
        return await message.answer(
            f"❌ Balansingizda yetarli Stars yo'q. Sizda: {user['balance']:.2f} Stars.",
            reply_markup=get_main_keyboard(user_id)
        )

    data = await state.get_data()
    game_type = data.get('game_type')

    if game_type == "ladder":
        if user_id != ADMIN_ID:
            user["balance"] = round(user["balance"] - bet_amount, 2)
            save_json(USERS_FILE, users_db)

        rows_mines = []
        for _ in range(len(LADDER_MULTIPLIERS)):
            mines = random.sample(range(6), 3)
            rows_mines.append(mines)

        await state.update_data(bet=bet_amount, step=0, clicked_indices=[], rows_mines=rows_mines)
        await state.set_state(GameStates.playing_ladder)

        kb = []
        for i in range(len(LADDER_MULTIPLIERS) - 1, -1, -1):
            row_buttons = []
            for j in range(6):
                if i == 0:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data=f"ladder_click_{j}"))
                else:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ladder_ignore"))
            kb.append(row_buttons)
        kb.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="ladder_cancel")])

        await message.answer(
            get_status_text(user_id) +
            f"🪜 <b>NARVON O'YINI BOSHLANDI</b>\n\n"
            f"Stavka: <b>{bet_amount:.2f} Stars</b>\n"
            f"O'tilgan qatorlar: <b>0/{len(LADDER_MULTIPLIERS)}</b>\n"
            f"Joriy koeffitsiyent: <b>1.00x</b>\n\n"
            f"Birinchi qatordan joy tanlang (6 ta katakdan 3 tasi mina):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        return

    if game_type == "mines":
        await state.update_data(bet=bet_amount)
        await state.set_state(GameStates.waiting_for_mines_count)
        return await message.answer(get_status_text(user_id) + f"💣 <b>MINA O'YINI</b>\n\nStavka: <b>{bet_amount:.2f} Stars</b>\n\nNechta mina qo'yishni xohlaysiz? (3 dan 9 gacha):")

    if user_id != ADMIN_ID:
        user["balance"] = round(user["balance"] - bet_amount, 2)
        save_json(USERS_FILE, users_db)

    dice_emoji = {"darts": "🎯", "dice": "🎲", "bowling": "🎳",
                  "basket": "🏀", "slot": "🎰"}.get(game_type, "🎲")
    await state.clear()

    loss_streak = user.get("loss_streak", 0)
    
    if loss_streak >= 2:
        is_win = True
    elif user.get("total_played", 0) < 3:
        is_win = random.random() < 0.70
    elif bet_amount > 10.0:
        is_win = random.random() < 0.20
    elif is_big_bet(user, bet_amount):
        is_win = random.random() < 0.15
    else:
        is_win = random.random() < 0.30

    forced_value = None
    if game_type in ["darts", "dice", "bowling"]:
        if is_win:
            if loss_streak >= 2:
                win_type = random.choice([1.2, 1.3, 1.5])
                if win_type == 1.2: forced_value = 4
                elif win_type == 1.3: forced_value = 4
                else: forced_value = 5
            else:
                forced_value = 6 if random.random() < 0.5 else 5
        else:
            forced_value = random.choice([1, 2, 3])
            
    elif game_type == "basket":
        if is_win:
            if loss_streak >= 2:
                win_type = random.choice([1.2, 1.3, 1.5])
                if win_type in [1.2, 1.3]: forced_value = 3
                else: forced_value = 4
            else:
                forced_value = 5 if random.random() < 0.5 else 4
        else:
            forced_value = random.choice([1, 2])
            
    elif game_type == "slot":
        if is_win:
            forced_value = 64 if random.random() < 0.5 else 22 
        else:
            forced_value = random.choice([1, 22, 43, 12, 13]) 

    try:
        msg = await message.answer_dice(emoji=dice_emoji, value=forced_value)
    except Exception:
        msg = await message.answer_dice(emoji=dice_emoji)

    await asyncio.sleep(3.5)
    result = msg.dice.value

    if game_type in ["darts", "dice", "bowling"]:
        is_win_real = result in [4, 5, 6]
        if result == 6: multiplier = 2.0
        elif result == 5: multiplier = 1.5
        elif result == 4: 
            multiplier = 1.3 if loss_streak >= 2 and random.random() < 0.5 else 1.2
        else: multiplier = 0.0
            
    elif game_type == "basket":
        is_win_real = result in [3, 4, 5]
        if result == 5: multiplier = 2.0
        elif result == 4: multiplier = 1.5
        elif result == 3:
            multiplier = 1.3 if loss_streak >= 2 and random.random() < 0.5 else 1.2
        else: multiplier = 0.0
            
    elif game_type == "slot":
        is_win_real = result in [1, 64, 22, 43]
        multiplier = 2.0 if result in [1, 64] else (1.5 if result in [22, 43] else 0.0)
    else:
        is_win_real = False
        multiplier = 0.0

    if multiplier > 0:
        winnings = round(bet_amount * multiplier, 2)
        if user_id != ADMIN_ID:
            user["balance"] = round(user["balance"] + winnings, 2)
            update_after_win(user, winnings, bet_amount)
            save_json(USERS_FILE, users_db)
        status_msg = (
            f"🎉 <b>YUTDINGIZ!</b> Ball: {result}. "
            f"Koeffitsiyent: <b>{multiplier}x</b>.\n"
            f"Balansingizga <b>+{winnings:.2f} Stars</b> qo'shildi."
        )
    else:
        if user_id != ADMIN_ID:
            update_after_loss(user, bet_amount)
            save_json(USERS_FILE, users_db)
        status_msg = (
            f"😔 <b>YUTQAZDINGIZ!</b> Ball: {result}. "
            f"Koeffitsiyent: <b>0x</b>.\n<b>-{bet_amount:.2f} Stars</b>."
        )

    admin_msg = "\n\n👑 <i>Admin rejimi</i>" if user_id == ADMIN_ID else ""
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "play_again"), callback_data="back_to_stars")]])
    await message.answer(get_status_text(user_id) + status_msg + admin_msg, reply_markup=kb)

# ==========================================
# PREMIUM
# ==========================================
@dp.message(F.text.in_([TEXTS["uz"]["btn_prem"], TEXTS["ru"]["btn_prem"], TEXTS["en"]["btn_prem"]]))
async def premium_menu(message: types.Message):
    user_id = message.from_user.id
    if not await require_subscription(message, user_id):
        return
    user = get_user(user_id)
    premium_price = 300
    text = (
        f"💎 <b>Premium Obuna</b>\n\n"
        f"Sizga <b>1 oylik Premium</b> obunasini taklif qilamiz:\n\n"
        f"◈ O'yinlarda <b>2x ko'proq</b> yutish imkoniyati.\n"
        f"◈ Kunlik bonusdan <b>2x ko'proq</b> Stars.\n"
        f"◈ Maxsus 'Premium' statusi.\n"
        f"◈ Sovg'alarni <b>10% chegirma</b> bilan.\n\n"
        f"💰 <b>Narxi:</b> {premium_price} Stars / 1 oy\n"
        f"💳 <b>Sizning balansingiz:</b> {user['balance']:.2f} Stars"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Sotib olish ({premium_price} Stars)", callback_data=f"buy_prem_{premium_price}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_stars")]
    ])
    await message.answer(get_status_text(user_id) + text, reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_prem_"))
async def process_premium_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    price = int(callback.data.split("_")[-1])

    if user_id != ADMIN_ID and user["balance"] < price:
        return await callback.answer(f"❌ Balansingizda yetarli Stars yo'q. Sizda: {user['balance']:.2f} Stars.", show_alert=True)

    if user_id != ADMIN_ID:
        user["balance"] = round(user["balance"] - price, 2)
        save_json(USERS_FILE, users_db)

    await callback.message.edit_text(
        get_status_text(user_id) +
        f"✅ <b>Tabriklaymiz!</b>\n\n"
        f"Siz <b>1 oylik Premium</b> obunasini sotib oldingiz!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎮 O'yinlarga qaytish", callback_data="back_to_stars")]])
    )
    await bot.send_message(
        ADMIN_ID,
        f"💎 **Yangi Premium Xarid!**\n\n"
        f"Foydalanuvchi: @{user['username']}\n"
        f"To'lov: Bot ichidagi balans\n"
        f"Miqdor: {price} Stars\n"
        f"Qolgan balans: {user['balance']:.2f} Stars"
    )
    await callback.answer("Premium muvaffaqiyatli sotib olindi!")

# ==========================================
# TO'LOV TIZIMLARI (FAQAT STARS)
# ==========================================
@dp.message(F.text.in_([TEXTS["uz"]["btn_bal"], TEXTS["ru"]["btn_bal"], TEXTS["en"]["btn_bal"]]))
async def show_balance_and_deposit(message: types.Message):
    user_id = message.from_user.id
    if not await require_subscription(message, user_id):
        return
    user = get_user(user_id)
    bal = "∞ (Cheksiz)" if user_id == ADMIN_ID else f"{user['balance']:.2f} Stars"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Balansni to'ldirish (Stars)", callback_data="dep_stars")]
    ])
    await message.answer(get_status_text(user_id) + f"💳 {t(user_id, 'status_bal')}: <b>{bal}</b>", reply_markup=kb)

@dp.callback_query(F.data == "dep_stars")
async def deposit_stars_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 5 Stars", callback_data="buy_stars_5"), InlineKeyboardButton(text="⭐ 10 Stars", callback_data="buy_stars_10")],
        [InlineKeyboardButton(text="⭐ 15 Stars", callback_data="buy_stars_15"), InlineKeyboardButton(text="⭐ 25 Stars", callback_data="buy_stars_25")],
        [InlineKeyboardButton(text="⭐ 50 Stars", callback_data="buy_stars_50"), InlineKeyboardButton(text="⭐ 75 Stars", callback_data="buy_stars_75")],
        [InlineKeyboardButton(text="⭐ 100 Stars", callback_data="buy_stars_100")]
    ])
    await callback.message.edit_text("⭐ <b>Telegram Stars orqali to'ldirish</b>\n\nMiqdorni tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_stars_"))
async def process_stars_payment(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[-1])
    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title="Balansni to'ldirish",
            description=f"Telegram Stars orqali {amount} Stars",
            payload=f"stars_deposit_{callback.from_user.id}_{amount}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} Stars", amount=amount)]
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ To'lov oynasini ochishda xatolik.", show_alert=True)
        await bot.send_message(ADMIN_ID, f"🚨 To'lov xatosi: {e}")

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    payment_info = message.successful_payment
    amount = payment_info.total_amount
    user_id = message.from_user.id
    user = get_user(user_id)

    user["balance"] = round(user["balance"] + amount, 2)
    user["history"].append(f"Depozit (Stars): +{amount}")
    save_json(USERS_FILE, users_db)

    await message.answer(
        f"✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
        f"Balansingizga <b>+{amount} Stars</b> qo'shildi.\n"
        f"Joriy balans: <b>{user['balance']:.2f} Stars</b>",
        reply_markup=get_main_keyboard(user_id)
    )
    await bot.send_message(ADMIN_ID, f"💰 **Yangi Depozit!**\n\nFoydalanuvchi: @{user['username']}\nMiqdor: {amount} Stars")

# ==========================================
# SOVG'ALAR
# ==========================================
@dp.message(F.text.in_([TEXTS["uz"]["btn_gift"], TEXTS["ru"]["btn_gift"], TEXTS["en"]["btn_gift"]]))
async def gifts_menu(message: types.Message):
    user_id = message.from_user.id
    if not await require_subscription(message, user_id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Heart (16 Stars)", callback_data="gift_heart"), InlineKeyboardButton(text="🧸 Teddy Bear (16 Stars)", callback_data="gift_teddy")],
        [InlineKeyboardButton(text="🌹 Bouquet (51 Stars)", callback_data="gift_bouquet"), InlineKeyboardButton(text="🚀 Rocket (51 Stars)", callback_data="gift_rocket")],
        [InlineKeyboardButton(text="🎂 Cake (51 Stars)", callback_data="gift_cake"), InlineKeyboardButton(text="🏆 Trophy (101 Stars)", callback_data="gift_trophy")]
    ])
    await message.answer(get_status_text(user_id) + "🎁 <b>Mystic Gifts Do'koni</b>\n\nSovg'ani tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("gift_"))
async def buy_gift(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    gifts_data = {
        "gift_heart": {"name": "Heart (Yurakcha)", "price": 16},
        "gift_teddy": {"name": "Teddy Bear (Ayiqcha)", "price": 16},
        "gift_bouquet": {"name": "Bouquet (Gullar)", "price": 51},
        "gift_rocket": {"name": "Rocket (Raketa)", "price": 51},
        "gift_cake": {"name": "Cake (Tort)", "price": 51},
        "gift_trophy": {"name": "Trophy (Kubok)", "price": 101}
    }
    gift = gifts_data.get(callback.data)
    if not gift:
        return

    price = gift["price"]
    gift_name = gift["name"]

    if user_id == ADMIN_ID or user["balance"] >= price:
        if user_id != ADMIN_ID:
            user["balance"] = round(user["balance"] - price, 2)
            save_json(USERS_FILE, users_db)
        await callback.message.edit_text(get_status_text(user_id) + f"✅ <b>{gift_name}</b> xarid qilindi! Admin tez orada taqdim etadi.")
        await bot.send_message(ADMIN_ID, f"🚨 **Yangi Sovg'a Xaridi!**\n\nFoydalanuvchi: @{user['username']}\nSovg'a: {gift_name}\nNarxi: {price} Stars")
    else:
        await callback.answer(t(user_id, "gift_no", price=price, bal=user['balance']), show_alert=True)

# ==========================================
# PROMO KOD
# ==========================================
@dp.message(Command("promo"))
async def cmd_promo(message: types.Message, state: FSMContext):
    await message.answer("🎁 <b>Promo Kod</b>\n\nPromo kodni kiriting:")
    await state.set_state(PromoState.waiting_for_promo)

@dp.message(PromoState.waiting_for_promo)
async def process_promo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    code = message.text.strip()

    if code in promos_db:
        if code in user.get("used_promo", []):
            await message.answer("❌ Siz allaqachon bu promo-koddan foydalangansiz!")
            await state.clear()
            return
        amount = promos_db[code]
        user["balance"] = round(user["balance"] + amount, 2)
        user.setdefault("used_promo", []).append(code)
        user["history"].append(f"Promo kod ({code}): +{amount} Stars")
        save_json(USERS_FILE, users_db)
        await message.answer(f"✅ <b>Tabriklaymiz!</b>\n\n+{amount} Stars qo'shildi!", reply_markup=get_main_keyboard(user_id))
    else:
        await message.answer("❌ <b>Xato!</b> Bunday promo kod mavjud emas.")
    await state.clear()

# ==========================================
# QOLGAN FUNKSIYALAR
# ==========================================
@dp.message(F.text.in_([TEXTS["uz"]["btn_hist"], TEXTS["ru"]["btn_hist"], TEXTS["en"]["btn_hist"]]))
async def show_history(message: types.Message):
    user = get_user(message.from_user.id)
    history = "\n".join(user["history"][-5:]) if user["history"] else "Bo'sh."
    await message.answer(get_status_text(message.from_user.id) + f"🕰 Tarix:\n\n{history}")

@dp.message(F.text.in_([TEXTS["uz"]["btn_ref"], TEXTS["ru"]["btn_ref"], TEXTS["en"]["btn_ref"]]))
async def referal_info(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    await message.answer(get_status_text(message.from_user.id) + t(message.from_user.id, "ref_link", link=ref_link))

@dp.message(F.text.in_([TEXTS["uz"]["btn_help"], TEXTS["ru"]["btn_help"], TEXTS["en"]["btn_help"]]))
async def help_menu(message: types.Message):
    help_text = (
        f"❔ <b>Yordam Markazi</b>\n\n"
        f"✦ <b>M Y S T I C D R O P</b> — o'yin va imkoniyatlar makoningiz.\n\n"
        f"<b>💳 Balans:</b>\n"
        f"◈ Telegram Stars orqali to'ldiring.\n"
        f"◈ Kunlik bonus: +1 Stars.\n"
        f"◈ Tasklarni bajaring: qo'shimcha Stars.\n"
        f"◈ Do'stlarni taklif qiling: +2 Stars.\n\n"
        f"<b>🎮 O'yinlar:</b>\n"
        f"◈ Mina: minalarni topmasdan kataklarni oching.\n"
        f"◈ Narvon: 12 qatordan o'ting.\n"
        f"◈ Nayza/Kubik/Bouling/Basket/Slot: omadni sinang.\n\n"
        f"<b>🛡 Xavfsizlik:</b>\n"
        f"◈ Barcha natijalar RNG asosida.\n"
        f"◈ Firibgarlik aniqlansa — balans 0 ga tushiriladi.\n\n"
        f"<b>📞 Aloqa:</b> @admin_username"
    )
    await message.answer(help_text)

@dp.message(F.text.in_([TEXTS["uz"]["btn_lang"], TEXTS["ru"]["btn_lang"], TEXTS["en"]["btn_lang"]]))
async def lang_menu(message: types.Message):
    await message.answer(t(message.from_user.id, "lang_choose"), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ]))

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    get_user(callback.from_user.id)["lang"] = lang
    save_json(USERS_FILE, users_db)
    await callback.message.delete()
    await callback.message.answer(t(callback.from_user.id, "lang_set"), reply_markup=get_main_keyboard(callback.from_user.id))

# ==========================================
# RENDER UCHUN VEB-SERVER VA PING
# ==========================================
async def web_handler(request):
    return web.Response(text="Bot is running!")

async def keep_alive():
    """Har 10 daqiqada Adminga xabar yuborib, botni uyg'oq tutadi."""
    while True:
        await asyncio.sleep(600)  # 600 sekund = 10 daqiqa
        try:
            await bot.send_message(ADMIN_ID, "♻️ Bot uyg'oq (Render auto-ping).")
        except Exception as e:
            print(f"Ping xatosi: {e}")

# ==========================================
# ISHGA TUSHIRISH
# ==========================================
async def main():
    print("Bot ishga tushdi...")
    
    # 1. Avto-ping vazifasini ishga tushirish
    asyncio.create_task(keep_alive())
    
    # 2. Render talab qiladigan kichik veb-serverni yaratish
    app = web.Application()
    app.router.add_get("/", web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Veb-server {port}-portda ishga tushdi...")

    # 3. Botni polling rejimida ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")

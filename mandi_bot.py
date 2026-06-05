"""
🍋 MANDI BOOK TELEGRAM BOT
==========================
Install: pip install python-telegram-bot==20.7
Run: python mandi_bot.py
"""

import os
import json
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# ── CONFIG ──────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN", "YAHAN_APNA_TOKEN_DAALO")
DATA_FILE = "mandi_data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── DATA HELPERS ─────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"aawak": [], "bikri": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def now_str():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

# ── CONVERSATION STATES ──────────────────────────────────

# Aawak states
(
    AW_TRUCK, AW_DRIVER, AW_FROM,
    AW_FRUIT, AW_VARIETY, AW_PER_BOX, AW_TOTAL_BOX,
    AW_KISAN_COUNT, AW_KISAN_NAAM, AW_KISAN_PETI,
    AW_HAMALI, AW_ARHAT, AW_CONFIRM
) = range(13)

# Bikri states
(
    BK_KISAN, BK_FRUIT, BK_BUYER,
    BK_BOXES, BK_PER_BOX, BK_RATE, BK_CONFIRM
) = range(13, 20)

# ── MAIN MENU ────────────────────────────────────────────
def main_menu_kb():
    return ReplyKeyboardMarkup(
        [["🚛 Maal Aaya (Aawak)", "💰 Maal Bika (Bikri)"],
         ["📋 Aaj ki Report", "📊 Kisan Hisaab"]],
        resize_keyboard=True
    )

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍋 *Mandi Book Bot mein aapka swagat hai!*\n\n"
        "Niche se option chuniye:",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

# ════════════════════════════════════════════════════════
#  AAWAK FLOW
# ════════════════════════════════════════════════════════

async def aawak_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    ctx.user_data["aawak"] = {}
    await update.message.reply_text(
        "🚛 *Naya Truck Entry*\n\n"
        "📝 *Step 1/7*\n"
        "Truck ka number batao:\n_(jaise: HR55AB1234)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return AW_TRUCK

async def aw_truck(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["aawak"]["truck_no"] = update.message.text.upper().strip()
    await update.message.reply_text(
        "👤 *Step 2/7*\n"
        "Driver ka naam batao:",
        parse_mode="Markdown"
    )
    return AW_DRIVER

async def aw_driver(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["aawak"]["driver"] = update.message.text.strip()
    # Quick location buttons
    kb = ReplyKeyboardMarkup(
        [["Nagpur", "Ratnagiri"], ["Lucknow", "Varanasi"],
         ["Delhi", "Mumbai"], ["Aur jagah..."]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "📍 *Step 3/7*\n"
        "Truck kahan se aaya? (button ya khud likho)",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return AW_FROM

async def aw_from(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["aawak"]["from_place"] = update.message.text.strip()
    # Fruit quick buttons
    kb = ReplyKeyboardMarkup(
        [["🥭 Aam", "🍌 Kela"], ["🍎 Seb", "🍇 Angoor"],
         ["🍊 Santra", "🍈 Tarbooz"], ["Dusra Phal..."]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "🍎 *Step 4/7*\n"
        "Kaun sa maal aaya?",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return AW_FRUIT

async def aw_fruit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    fruit = update.message.text.replace("🥭 ", "").replace("🍌 ", "").replace("🍎 ", "") \
                              .replace("🍇 ", "").replace("🍊 ", "").replace("🍈 ", "").strip()
    ctx.user_data["aawak"]["fruit"] = fruit
    await update.message.reply_text(
        "🌿 Variety / Kisam batao:\n_(jaise: Alphonso, Dussehri, Langra — ya Skip likhो)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["Skip"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return AW_VARIETY

async def aw_variety(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    v = update.message.text.strip()
    ctx.user_data["aawak"]["variety"] = "" if v.lower() == "skip" else v
    await update.message.reply_text(
        "📦 Ek peti mein kitna maal hai? _(kg mein)_\n"
        "_(jaise: 10, 15, 20)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["10", "12", "15"], ["20", "25", "30"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return AW_PER_BOX

async def aw_per_box(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["aawak"]["per_box_kg"] = float(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Sirf number daalo jaise: 10"); return AW_PER_BOX
    await update.message.reply_text(
        "📦 *Step 5/7*\n"
        "Total kitni petiyan aayi?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return AW_TOTAL_BOX

async def aw_total_box(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        boxes = int(update.message.text.strip())
        ctx.user_data["aawak"]["total_boxes"] = boxes
        per = ctx.user_data["aawak"]["per_box_kg"]
        ctx.user_data["aawak"]["total_wt"] = boxes * per
    except:
        await update.message.reply_text("❌ Sirf number daalo jaise: 200"); return AW_TOTAL_BOX

    await update.message.reply_text(
        f"✅ Total wajan: *{ctx.user_data['aawak']['total_wt']} kg*\n\n"
        f"👨‍🌾 *Step 6/7 — Kisanon ki jankari*\n"
        f"Is truck mein kitne logon ka maal hai?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["1", "2", "3"], ["4", "5", "6+"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return AW_KISAN_COUNT

async def aw_kisan_count(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        n = int(update.message.text.strip().replace("6+", "6"))
        ctx.user_data["aawak"]["kisan_total"] = n
        ctx.user_data["aawak"]["kisans"] = []
        ctx.user_data["aawak"]["kisan_idx"] = 0
    except:
        await update.message.reply_text("❌ Sirf number daalo"); return AW_KISAN_COUNT

    await update.message.reply_text(
        f"👨‍🌾 Kisan 1 ka naam batao:",
        reply_markup=ReplyKeyboardRemove()
    )
    return AW_KISAN_NAAM

async def aw_kisan_naam(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    idx = ctx.user_data["aawak"]["kisan_idx"]
    ctx.user_data["aawak"][f"_kisan_naam_{idx}"] = update.message.text.strip()
    await update.message.reply_text(
        f"📦 {update.message.text.strip()} ki kitni petiyan hain?"
    )
    return AW_KISAN_PETI

async def aw_kisan_peti(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        peti = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Sirf number daalo"); return AW_KISAN_PETI

    idx = ctx.user_data["aawak"]["kisan_idx"]
    naam = ctx.user_data["aawak"][f"_kisan_naam_{idx}"]
    ctx.user_data["aawak"]["kisans"].append({"naam": naam, "peti": peti})
    ctx.user_data["aawak"]["kisan_idx"] += 1

    total = ctx.user_data["aawak"]["kisan_total"]
    next_idx = ctx.user_data["aawak"]["kisan_idx"]

    if next_idx < total:
        await update.message.reply_text(
            f"👨‍🌾 Kisan {next_idx + 1} ka naam batao:"
        )
        return AW_KISAN_NAAM
    else:
        # All kisans done → ask charges
        await update.message.reply_text(
            "💰 *Step 7/7 — Charges*\n\n"
            "Hamali kitna hai? _(₹ per peti)_\n"
            "_(0 daalo agar nahi hai)_",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["0", "5", "10"], ["15", "20", "25"]],
                resize_keyboard=True, one_time_keyboard=True
            )
        )
        return AW_HAMALI

async def aw_hamali(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["aawak"]["hamali_rate"] = float(update.message.text.strip())
    except:
        ctx.user_data["aawak"]["hamali_rate"] = 0

    await update.message.reply_text(
        "📊 Arhat / Commission kitna % hai?\n_(jaise: 6, 7, 8 — ya 0)_",
        reply_markup=ReplyKeyboardMarkup(
            [["0", "6", "7"], ["8", "10", "12"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return AW_ARHAT

async def aw_arhat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["aawak"]["arhat_pct"] = float(update.message.text.strip())
    except:
        ctx.user_data["aawak"]["arhat_pct"] = 0

    # Build summary
    a = ctx.user_data["aawak"]
    kisans_text = "\n".join([f"  • {k['naam']} — {k['peti']} peti" for k in a["kisans"]])
    summary = (
        f"📋 *Entry ka Summary — Confirm Karo*\n\n"
        f"🚛 Truck: `{a['truck_no']}`\n"
        f"🧑 Driver: {a['driver']}\n"
        f"📍 Kahan se: {a['from_place']}\n"
        f"🍎 Maal: {a['fruit']} {a.get('variety','')}\n"
        f"📦 {a['total_boxes']} peti × {a['per_box_kg']}kg = *{a['total_wt']} kg*\n\n"
        f"👨‍🌾 *Kisaan:*\n{kisans_text}\n\n"
        f"💰 Hamali: ₹{a['hamali_rate']}/peti\n"
        f"📊 Arhat: {a['arhat_pct']}%\n\n"
        f"Sahi hai?"
    )
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Haan, Save Karo", "❌ Nahi, Dobara"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return AW_CONFIRM

async def aw_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if "Haan" in update.message.text:
        a = ctx.user_data["aawak"]
        a["date"] = now_str()
        a["type"] = "aawak"
        a["id"] = int(datetime.now().timestamp())

        data = load_data()
        data["aawak"].append(a)
        save_data(data)

        await update.message.reply_text(
            f"✅ *Entry Save Ho Gayi!*\n\n"
            f"🚛 {a['truck_no']} — {a['fruit']}\n"
            f"{a['total_boxes']} peti / {a['total_wt']} kg\n"
            f"📅 {a['date']}",
            parse_mode="Markdown",
            reply_markup=main_menu_kb()
        )
    else:
        await update.message.reply_text(
            "🔄 Theek hai, dobara shuru karte hain...",
            reply_markup=main_menu_kb()
        )
    ctx.user_data.clear()
    return ConversationHandler.END

# ════════════════════════════════════════════════════════
#  BIKRI FLOW
# ════════════════════════════════════════════════════════

async def bikri_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    ctx.user_data["bikri"] = {}

    # Show recent kisans as buttons
    data = load_data()
    kisans = list({k["naam"] for e in data["aawak"] for k in e.get("kisans", [])})
    kisans = kisans[:6]  # Max 6 buttons

    if kisans:
        rows = [kisans[i:i+2] for i in range(0, len(kisans), 2)]
        kb = ReplyKeyboardMarkup(rows + [["Naya naam..."]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "💰 *Bikri Entry*\n\n"
            "👨‍🌾 Kiska maal bika? (ya naam likho)",
            parse_mode="Markdown",
            reply_markup=kb
        )
    else:
        await update.message.reply_text(
            "💰 *Bikri Entry*\n\n"
            "👨‍🌾 Kisan ka naam batao:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    return BK_KISAN

async def bk_kisan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["bikri"]["kisan"] = update.message.text.strip()
    await update.message.reply_text(
        "🍎 Kaun sa maal bika?",
        reply_markup=ReplyKeyboardRemove()
    )
    return BK_FRUIT

async def bk_fruit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["bikri"]["fruit"] = update.message.text.strip()
    await update.message.reply_text("🛒 Kharidaar / Vyapari ka naam?")
    return BK_BUYER

async def bk_buyer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["bikri"]["buyer"] = update.message.text.strip()
    await update.message.reply_text(
        "📦 Kitni peti biki?",
        reply_markup=ReplyKeyboardRemove()
    )
    return BK_BOXES

async def bk_boxes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["bikri"]["boxes"] = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Sirf number daalo"); return BK_BOXES
    await update.message.reply_text(
        "⚖️ Ek peti mein kitna kg?",
        reply_markup=ReplyKeyboardMarkup(
            [["10", "12", "15"], ["20", "25", "30"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return BK_PER_BOX

async def bk_per_box(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["bikri"]["per_box"] = float(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Sirf number daalo"); return BK_PER_BOX
    await update.message.reply_text(
        "💵 Rate kya tha? _(₹ per kg)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return BK_RATE

async def bk_rate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        rate = float(update.message.text.strip())
        ctx.user_data["bikri"]["rate"] = rate
        b = ctx.user_data["bikri"]
        total_wt = b["boxes"] * b["per_box"]
        total_amt = total_wt * rate
        b["total_wt"] = total_wt
        b["total_amt"] = total_amt
    except:
        await update.message.reply_text("❌ Sirf number daalo"); return BK_RATE

    b = ctx.user_data["bikri"]

    # Find arhat from aawak entry for this kisan
    data = load_data()
    aawak = next((e for e in reversed(data["aawak"])
                  if any(k["naam"] == b["kisan"] for k in e.get("kisans", []))), None)

    arhat_amt = 0
    hamali_amt = 0
    net = b["total_amt"]

    if aawak:
        arhat_amt = round((aawak.get("arhat_pct", 0) / 100) * b["total_amt"], 2)
        hamali_amt = aawak.get("hamali_rate", 0) * b["boxes"]
        net = b["total_amt"] - arhat_amt - hamali_amt

    b["arhat_amt"] = arhat_amt
    b["hamali_amt"] = hamali_amt
    b["net_payment"] = net

    summary = (
        f"🧾 *Bikri ka Hisaab — Confirm Karo*\n\n"
        f"👨‍🌾 Kisan: {b['kisan']}\n"
        f"🍎 Maal: {b['fruit']}\n"
        f"🛒 Kharidaar: {b['buyer']}\n"
        f"📦 {b['boxes']} peti × {b['per_box']}kg = {b['total_wt']}kg\n"
        f"💵 Rate: ₹{rate}/kg\n\n"
        f"💰 Kul Bikri: ₹{b['total_amt']:,.0f}\n"
        f"➖ Arhat: ₹{arhat_amt:,.0f}\n"
        f"➖ Hamali: ₹{hamali_amt:,.0f}\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ *Net Payment: ₹{net:,.0f}*\n\n"
        f"Sahi hai?"
    )
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Haan, Save Karo", "❌ Nahi, Dobara"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return BK_CONFIRM

async def bk_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if "Haan" in update.message.text:
        b = ctx.user_data["bikri"]
        b["date"] = now_str()
        b["type"] = "bikri"
        b["id"] = int(datetime.now().timestamp())

        data = load_data()
        data["bikri"].append(b)
        save_data(data)

        await update.message.reply_text(
            f"✅ *Bikri Save Ho Gayi!*\n\n"
            f"👨‍🌾 {b['kisan']} → 🛒 {b['buyer']}\n"
            f"💵 Net: ₹{b['net_payment']:,.0f}\n"
            f"📅 {b['date']}",
            parse_mode="Markdown",
            reply_markup=main_menu_kb()
        )
    else:
        await update.message.reply_text("🔄 Dobara shuru karte hain...", reply_markup=main_menu_kb())

    ctx.user_data.clear()
    return ConversationHandler.END

# ════════════════════════════════════════════════════════
#  REPORT
# ════════════════════════════════════════════════════════

async def report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today = datetime.now().strftime("%d %b %Y")

    aaj_aawak = [e for e in data["aawak"] if today in e.get("date", "")]
    aaj_bikri = [e for e in data["bikri"] if today in e.get("date", "")]

    total_bikri_amt = sum(e.get("total_amt", 0) for e in aaj_bikri)

    text = f"📊 *Aaj ki Report — {today}*\n\n"
    text += f"🚛 Trucks aaye: {len(aaj_aawak)}\n"
    text += f"💰 Bikri entries: {len(aaj_bikri)}\n"
    text += f"💵 Kul Bikri: ₹{total_bikri_amt:,.0f}\n\n"

    if aaj_aawak:
        text += "🚛 *Aawak:*\n"
        for e in aaj_aawak:
            text += f"  • {e['truck_no']} — {e['fruit']} {e['total_boxes']}peti/{e['total_wt']}kg\n"

    if aaj_bikri:
        text += "\n💰 *Bikri:*\n"
        for e in aaj_bikri:
            text += f"  • {e['kisan']} → {e['buyer']}: ₹{e.get('net_payment',0):,.0f}\n"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

async def kisan_hisaab(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["bikri"]:
        await update.message.reply_text("Abhi koi bikri entry nahi hai.", reply_markup=main_menu_kb())
        return

    hisaab = {}
    for e in data["bikri"]:
        k = e.get("kisan", "?")
        if k not in hisaab:
            hisaab[k] = {"bikri": 0, "net": 0}
        hisaab[k]["bikri"] += e.get("total_amt", 0)
        hisaab[k]["net"] += e.get("net_payment", 0)

    text = "📊 *Kisan-wise Hisaab*\n\n"
    for naam, h in hisaab.items():
        text += f"👨‍🌾 *{naam}*\n  💰 Bikri: ₹{h['bikri']:,.0f} | Net: ₹{h['net']:,.0f}\n\n"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("❌ Cancel ho gaya.", reply_markup=main_menu_kb())
    return ConversationHandler.END

# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════

def main():
    app = Application.builder().token(TOKEN).build()

    # Aawak conversation
    aawak_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("🚛 Maal Aaya"), aawak_start),
            CommandHandler("aawak", aawak_start),
        ],
        states={
            AW_TRUCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_truck)],
            AW_DRIVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_driver)],
            AW_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_from)],
            AW_FRUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_fruit)],
            AW_VARIETY: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_variety)],
            AW_PER_BOX: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_per_box)],
            AW_TOTAL_BOX: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_total_box)],
            AW_KISAN_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_kisan_count)],
            AW_KISAN_NAAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_kisan_naam)],
            AW_KISAN_PETI: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_kisan_peti)],
            AW_HAMALI: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_hamali)],
            AW_ARHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_arhat)],
            AW_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, aw_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Bikri conversation
    bikri_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("💰 Maal Bika"), bikri_start),
            CommandHandler("bikri", bikri_start),
        ],
        states={
            BK_KISAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_kisan)],
            BK_FRUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_fruit)],
            BK_BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_buyer)],
            BK_BOXES: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_boxes)],
            BK_PER_BOX: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_per_box)],
            BK_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_rate)],
            BK_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, bk_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(aawak_handler)
    app.add_handler(bikri_handler)
    app.add_handler(MessageHandler(filters.Regex("📋 Aaj ki Report"), report))
    app.add_handler(MessageHandler(filters.Regex("📊 Kisan Hisaab"), kisan_hisaab))

    print("🍋 Mandi Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()

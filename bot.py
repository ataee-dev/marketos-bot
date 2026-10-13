import os
import json
import random
import time
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ─────────── تنظیمات ───────────
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
STATE_FILE = Path('last_state.json')

BASE_URL = "https://raw.githubusercontent.com/ataee-dev/marketos/main/data"

SOURCES = {
    "latest":   f"{BASE_URL}/latest.json",
    "domestic": f"{BASE_URL}/cars/domestic.json",
    "dubai":    f"{BASE_URL}/cars/dubai.json",
}

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

# ─────────── گروه‌بندی نمادها ───────────
GROUPS = {
    "gold": {
        "title": "🥇 طلا و سکه",
        "symbols": {
            "geram18": "گرم ۱۸ عیار",
            "geram24": "گرم ۲۴ عیار",
            "mesghal": "مثقال",
            "sekeb": "سکه بهار",
            "sekee": "سکه امامی",
            "nim": "نیم سکه",
            "rob": "ربع سکه",
            "ons": "انس جهانی",
        },
    },
    "forex": {
        "title": "💵 ارز",
        "symbols": {
            "price_dollar_rl": "دلار آزاد",
            "price_dollar_dt": "دلار دولتی",
            "price_eur": "یورو",
            "price_gbp": "پوند",
            "price_aed": "درهم امارات",
            "price_cny": "یوان چین",
            "price_try": "لیر ترکیه",
            "price_jpy": "یِن ژاپن",
            "price_chf": "فرانک سوئیس",
            "price_sar": "ریال سعودی",
            "price_kwd": "دینار کویت",
            "price_cad": "دلار کانادا",
        },
    },
    "crypto": {
        "title": "⚡️ ارز دیجیتال",
        "symbols": {
            "crypto-bitcoin": "بیت‌کوین",
            "crypto-ethereum": "اتریوم",
            "crypto-tether": "تتر",
            "crypto-binance-coin": "BNB",
            "crypto-solana": "سولانا",
            "crypto-ripple": "ریپل",
            "crypto-cardano": "کاردانو",
            "crypto-dogecoin": "دوج‌کوین",
            "crypto-litecoin": "لایت‌کوین",
            "crypto-polkadot": "پولکادات",
            "crypto-tron": "ترون",
            "crypto-chainlink": "چین‌لینک",
        },
    },
    "commodity": {
        "title": "🛢 کالا و انرژی",
        "symbols": {
            "oil_brent": "نفت برنت",
            "oil_opec": "نفت اوپک",
            "energy_natural_gas": "گاز طبیعی",
            "silver": "نقره (انس)",
            "silver_999": "نقره ۹۹۹",
            "platinum": "پلاتین",
            "palladium": "پالادیوم",
            "copper": "مس",
            "aluminium": "آلومینیوم",
            "commodity_us_wheat": "گندم",
            "commodity_corn": "ذرت",
            "commodity_us_coffee_c": "قهوه",
        },
    },
}

# ─────────── متن‌های متغیر ───────────
QUOTES = [
    "«طلا همیشه درخشنده است، حتی در تاریکی.»",
    "«بازار، آینه‌ی ترس و طمع آدم‌هاست.»",
    "«هر عددی که می‌بینی، پشتش یک تصمیم انسانیه.»",
    "«اقتصاد، علم اعداد نیست؛ علم انتخاب‌هاست.»",
    "«ثبات، گران‌ترین کالای بازار امروزه.»",
    "«در بازار، صبر بیشتر از پول ارزش داره.»",
    "«بازار امروز، بازار فردا را می‌سازد.»",
    "«قیمت‌ها دروغ نمی‌گویند، فقط دیر جواب می‌دهند.»",
]

INTROS_GOLD = [
    "✍️ <b>طلا در یک نگاه</b>",
    "🥇 <b>بازار طلا و سکه</b>",
    "✨ <b>درخشش امروز طلا</b>",
    "🌟 <b>طلای امروز، در یک قاب</b>",
]

INTROS_FOREX = [
    "💵 <b>بازار ارز</b>",
    "📊 <b>نگاهی به بازار ارز</b>",
    "🔔 <b>ارز — چه خبر؟</b>",
    "💱 <b>نبض بازار ارز</b>",
]

INTROS_CRYPTO = [
    "⚡️ <b>بازار کریپتوکارنسی</b>",
    "🪙 <b>دنیای ارز دیجیتال</b>",
    "🔮 <b>کریپتو در یک نگاه</b>",
    "💎 <b>ارز دیجیتال — امروز</b>",
]

INTROS_COMMODITY = [
    "🛢 <b>کالا، انرژی و فلزات</b>",
    "⚙️ <b>بازار جهانی کالا</b>",
    "🏭 <b>انرژی و مواد پایه</b>",
    "🌾 <b>کالاهای اساسی امروز</b>",
]

INTROS_DOMESTIC = [
    "🚗 <b>بازار خودروهای داخلی</b>",
    "🏎 <b>خودروهای داخلی امروز</b>",
    "🔧 <b>قیمت‌های خودرو داخلی</b>",
]

INTROS_DUBAI = [
    "🚙 <b>خودروهای وارداتی دبی</b>",
    "✨ <b>بازار لوکس دبی</b>",
    "🌍 <b>خودروهای دبی — امروز</b>",
]

CLOSINGS = [
    "🌐 marketos.ir",
    "📱 marketos.ir | همه‌چیز یه‌جا",
    "🔗 برای جزئیات بیشتر: marketos.ir",
    "💡 اطلاعات کامل: marketos.ir",
    "📌 بازار زنده: marketos.ir",
]


# ─────────── توابع کمکی ───────────
def fa_digits(text):
    """تبدیل اعداد لاتین به فارسی"""
    en = '0123456789'
    fa = '۰۱۲۳۴۵۶۷۸۹'
    return str(text).translate(str.maketrans(en, fa))


def now_tehran():
    return datetime.now(TEHRAN_TZ)


def fetch_json(url):
    r = requests.get(url, timeout=25)
    r.raise_for_status()
    return r.json()


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_state(data):
    STATE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


def fmt_price(value):
    """فرمت قیمت"""
    if value is None:
        return "—"
    if isinstance(value, float):
        if abs(value) < 10:
            return f"{value:,.4f}"
        elif abs(value) < 1000:
            return f"{value:,.2f}"
        return f"{value:,.0f}"
    return f"{value:,}"


def fmt_change(dp):
    """فرمت درصد تغییر"""
    if dp is None or dp == 0:
        return ""
    if dp > 0:
        return f"🟢 {dp:.2f}٪"
    return f"🔴 {abs(dp):.2f}٪"


# ─────────── ارسال به تلگرام ───────────
def send_message(text, reply_markup=None, disable_notification=False):
    """ارسال یک پیام به کانال"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    if disable_notification:
        payload['disable_notification'] = True

    try:
        r = requests.post(url, json=payload, timeout=25)
        if r.ok:
            print(f"   ✅ ارسال شد ({len(text)} کاراکتر)")
            return True
        else:
            print(f"   ❌ خطا {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ استثنا: {e}")
        return False


def send_long(text, reply_markup=None):
    """اگه پیام بلند بود، تکه‌تکه بفرست"""
    MAX = 3800
    if len(text) <= MAX:
        send_message(text, reply_markup)
        return

    parts = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX:
            parts.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        parts.append(current)

    for i, part in enumerate(parts):
        markup = reply_markup if i == len(parts) - 1 else None
        send_message(part, markup)
        time.sleep(1)


def make_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🌐 سایت", "url": "https://ataee-dev.github.io/marketos/"},
                {"text": "📊 نمودارها", "url": "https://ataee-dev.github.io/marketos/#charts"},
            ]
        ]
    }


# ─────────── ساخت پیام‌ها ───────────
def build_gold_message(data, is_daily=True):
    """🥇 طلا و سکه — با نقل قول"""
    if not data or 'data' not in data:
        return None

    items = data['data']
    quote = random.choice(QUOTES)
    intro = random.choice(INTROS_GOLD)
    closing = random.choice(CLOSINGS)

    lines = [f"<blockquote>{quote}</blockquote>", ""]
    lines.append(intro)

    if is_daily:
        now = now_tehran()
        lines.append(f"📅 {fa_digits(now.strftime('%Y/%m/%d'))}")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━")
    lines.append("")

    for key in ["geram18", "geram24", "mesghal", "sekeb", "sekee", "nim", "rob"]:
        if key in items and items[key].get('p') is not None:
            label = GROUPS['gold']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            lines.append(f"• <b>{label}</b>  ›  <code>{price}</code>")

    if "ons" in items and items["ons"].get('p'):
        ons = items["ons"]
        price = fa_digits(fmt_price(ons['p']))
        change = fmt_change(ons.get('dp', 0))
        lines.append("")
        lines.append("🌍 <b>انس جهانی</b>")
        lines.append(f"<code>{price}</code> دلار  {change}")

    lines.append("")
    lines.append(closing)

    return "\n".join(lines)


def build_forex_message(data, is_daily=True):
    """💵 ارز"""
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_FOREX)
    closing = random.choice(CLOSINGS)

    dollar = items.get("price_dollar_rl", {}).get('p', 0)
    dollar_str = fa_digits(fmt_price(dollar))

    opener = random.choice([
        f"📌 امروز دلار آزاد روی <code>{dollar_str}</code> تومان ایستاد.",
        f"💵 دلار امروز <code>{dollar_str}</code> تومان معامله شد.",
        f"🔹 بازار ارز با دلار <code>{dollar_str}</code> تومانی.",
        f"📊 دلار آزاد: <code>{dollar_str}</code> تومان",
    ])

    lines = [intro, "", opener, ""]
    lines.append("━━━━━━━━━━━━━━")
    lines.append("")

    main_currencies = ["price_dollar_rl", "price_dollar_dt", "price_eur", "price_gbp"]
    regional = ["price_aed", "price_try", "price_sar", "price_kwd"]
    others = ["price_cny", "price_jpy", "price_chf", "price_cad"]

    lines.append("<b>ارزهای اصلی</b>")
    for key in main_currencies:
        if key in items and items[key].get('p'):
            label = GROUPS['forex']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  <code>{price}</code>"
            if change:
                line += f"  {change}"
            lines.append(line)

    lines.append("")
    lines.append("<b>ارزهای منطقه‌ای</b>")
    for key in regional:
        if key in items and items[key].get('p'):
            label = GROUPS['forex']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            lines.append(f"▪️ {label}  ›  <code>{price}</code>")

    lines.append("")
    lines.append("<b>سایر ارزها</b>")
    for key in others:
        if key in items and items[key].get('p'):
            label = GROUPS['forex']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            lines.append(f"▪️ {label}  ›  <code>{price}</code>")

    lines.append("")
    lines.append(closing)

    return "\n".join(lines)


def build_crypto_message(data, is_daily=True):
    """⚡️ کریپتو"""
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_CRYPTO)
    closing = random.choice(CLOSINGS)
    now = now_tehran()

    lines = [intro]
    lines.append(f"🕐 {fa_digits(now.strftime('%H:%M'))}")
    lines.append("")

    for key in ["crypto-bitcoin", "crypto-ethereum"]:
        if key in items and items[key].get('p'):
            item = items[key]
            symbol = "₿" if "bitcoin" in key else "Ξ"
            label = GROUPS['crypto']['symbols'][key]
            price = fa_digits(fmt_price(item['p']))
            change = fmt_change(item.get('dp', 0))

            lines.append("┌─────────────────┐")
            lines.append(f"│  {symbol}  <b>{label}</b>")
            lines.append(f"│  <code>{price}</code> دلار")
            if change:
                lines.append(f"│  {change}")
            lines.append("└─────────────────┘")
            lines.append("")

    lines.append("━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("<b>سایر ارزها</b>")

    others = [k for k in GROUPS['crypto']['symbols']
              if k not in ("crypto-bitcoin", "crypto-ethereum")]
    for key in others:
        if key in items and items[key].get('p'):
            label = GROUPS['crypto']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  <code>{price}</code>"
            if change:
                line += f"  {change}"
            lines.append(line)

    lines.append("")
    lines.append(closing)

    return "\n".join(lines)


def build_commodity_message(data, is_daily=True):
    """🛢 کالا"""
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_COMMODITY)
    closing = random.choice(CLOSINGS)

    lines = [intro, ""]
    lines.append("<blockquote>بازار جهانی امروز شاهد نوسانات مختلفی بود.</blockquote>")
    lines.append("")

    # انرژی
    lines.append("<b>انرژی</b>")
    for key in ["oil_brent", "oil_opec", "energy_natural_gas"]:
        if key in items and items[key].get('p'):
            label = GROUPS['commodity']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  <code>{price}</code>"
            if change:
                line += f"  {change}"
            lines.append(line)

    # فلزات گرانبها
    lines.append("")
    lines.append("<b>فلزات گرانبها</b>")
    for key in ["silver", "silver_999", "platinum", "palladium"]:
        if key in items and items[key].get('p'):
            label = GROUPS['commodity']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  <code>{price}</code>"
            if change:
                line += f"  {change}"
            lines.append(line)

    # فلزات پایه
    lines.append("")
    lines.append("<b>فلزات پایه</b>")
    for key in ["copper", "aluminium"]:
        if key in items and items[key].get('p'):
            label = GROUPS['commodity']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            lines.append(f"▪️ {label}  ›  <code>{price}</code>")

    # کشاورزی
    lines.append("")
    lines.append("<b>محصولات کشاورزی</b>")
    for key in ["commodity_us_wheat", "commodity_corn", "commodity_us_coffee_c"]:
        if key in items and items[key].get('p'):
            label = GROUPS['commodity']['symbols'][key]
            price = fa_digits(fmt_price(items[key]['p']))
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  <code>{price}</code>"
            if change:
                line += f"  {change}"
            lines.append(line)

    lines.append("")
    lines.append(closing)

    return "\n".join(lines)


def build_domestic_message(data, max_items=15):
    """🚗 خودروهای داخلی"""
    if not data or 'items' not in data:
        return None

    items = [i for i in data['items']
             if i.get('status') == 'available' and i.get('priceMarket')]

    if not items:
        return None

    items.sort(key=lambda x: abs(x.get('change') or 0), reverse=True)
    items = items[:max_items]

    intro = random.choice(INTROS_DOMESTIC)
    closing = random.choice(CLOSINGS)
    quote = random.choice(QUOTES)

    lines = [intro, ""]
    lines.append(f"<blockquote>{quote}</blockquote>")
    lines.append("")

    # گروه‌بندی بر اساس category
    by_category = {}
    for item in items:
        cat = item.get('category', 'سایر')
        by_category.setdefault(cat, []).append(item)

    for cat, cat_items in by_category.items():
        lines.append(f"<b>{cat}</b>")
        for item in cat_items:
            name = item.get('name', '—')
            price = item['priceMarket'] / 1_000_000
            change = item.get('change') or 0

            line = f"▪️ {name}  ›  <code>{fa_digits(f'{price:,.0f}')} م.ت</code>"

            if change and change != 0:
                change_m = change / 1_000_000
                if change > 0:
                    line += f"  🟢 +{fa_digits(f'{change_m:,.0f}')}م"
                else:
                    line += f"  🔴 {fa_digits(f'{change_m:,.0f}')}م"
            lines.append(line)
        lines.append("")

    lines.append("💰 <i>قیمت‌ها به میلیون تومان</i>")
    lines.append(closing)

    return "\n".join(lines)


def build_dubai_message(data, max_items=20):
    """🚙 خودروهای دبی"""
    if not data or 'items' not in data:
        return None

    items = [i for i in data['items'] if i.get('change')]

    if not items:
        return None

    items.sort(key=lambda x: x.get('change') or 0, reverse=True)
    items = items[:max_items]

    intro = random.choice(INTROS_DUBAI)
    closing = random.choice(CLOSINGS)

    lines = [intro, ""]
    lines.append("<blockquote>✨ برندهای لوکس، دست‌چین‌شده از بازار دبی</blockquote>")
    lines.append("")

    # گروه‌بندی بر اساس برند
    by_brand = {}
    for item in items:
        brand = item.get('category', 'سایر')
        by_brand.setdefault(brand, []).append(item)

    for brand, brand_items in by_brand.items():
        lines.append(f"<b>◾️ {brand}</b>")
        for item in brand_items:
            name = item.get('name', '—')
            variant = item.get('rawPriceFactory', '')
            price = item.get('change', 0)

            display = name
            if variant and variant not in ('...', 'base', ''):
                display = f"{name} ({variant})"

            lines.append(
                f"▪️ {display}  ›  <code>{fa_digits(f'{price:,}')} درهم</code>"
            )
        lines.append("")

    lines.append(closing)

    return "\n".join(lines)


# ─────────── پیام‌های ساعتی (فقط تغییرات) ───────────
def build_hourly_updates(all_data, last_data):
    """پیام‌های ساعتی — فقط تغییرات"""
    messages = []
    now = now_tehran()

    if not last_data:
        return []

    new_latest = (all_data.get('latest') or {}).get('data', {})
    old_latest = (last_data.get('latest') or {}).get('data', {})

    # ۱. طلا
    gold_changes = []
    for key in GROUPS['gold']['symbols']:
        if key in new_latest and key in old_latest:
            old_p = old_latest[key].get('p')
            new_p = new_latest[key].get('p')
            if old_p != new_p:
                label = GROUPS['gold']['symbols'][key]
                price = fa_digits(fmt_price(new_p))
                dp = new_latest[key].get('dp', 0)
                arrow = "🟢 ↑" if dp > 0 else "🔴 ↓"
                chg = f"{arrow} {abs(dp):.2f}٪" if dp else ""
                gold_changes.append(
                    f"• <b>{label}</b>  ›  <code>{price}</code>  {chg}"
                )

    if gold_changes:
        intro = random.choice(["✍️ <b>طلا در یک ساعت گذشته</b>",
                               "🥇 <b>تحرکات بازار طلا</b>",
                               "⚡️ <b>طلا — جدیدترین‌ها</b>"])
        msg = f"{intro}\n🕐 {fa_digits(now.strftime('%H:%M'))}\n\n"
        msg += "\n".join(gold_changes)
        msg += f"\n\n{random.choice(CLOSINGS)}"
        messages.append(msg)

    # ۲. ارز
    forex_changes = []
    for key in GROUPS['forex']['symbols']:
        if key in new_latest and key in old_latest:
            old_p = old_latest[key].get('p')
            new_p = new_latest[key].get('p')
            if old_p != new_p:
                label = GROUPS['forex']['symbols'][key]
                price = fa_digits(fmt_price(new_p))
                dp = new_latest[key].get('dp', 0)
                arrow = "🟢 ↑" if dp > 0 else "🔴 ↓"
                chg = f"{arrow} {abs(dp):.2f}٪" if dp else ""
                forex_changes.append(
                    f"• <b>{label}</b>  ›  <code>{price}</code>  {chg}"
                )

    if forex_changes:
        intro = random.choice(["💵 <b>ارز — چه خبر؟</b>",
                               "📊 <b>بازار ارز در یک نگاه</b>",
                               "🔔 <b>ارز: تغییرات مهم</b>"])
        msg = f"{intro}\n🕐 {fa_digits(now.strftime('%H:%M'))}\n\n"
        msg += "\n".join(forex_changes)
        msg += f"\n\n{random.choice(CLOSINGS)}"
        messages.append(msg)

    # ۳. کریپتو
    crypto_changes = []
    for key in GROUPS['crypto']['symbols']:
        if key in new_latest and key in old_latest:
            old_p = old_latest[key].get('p')
            new_p = new_latest[key].get('p')
            if old_p != new_p:
                label = GROUPS['crypto']['symbols'][key]
                price = fa_digits(fmt_price(new_p))
                dp = new_latest[key].get('dp', 0)
                arrow = "🟢 ↑" if dp > 0 else "🔴 ↓"
                chg = f"{arrow} {abs(dp):.2f}٪" if dp else ""
                crypto_changes.append(
                    f"• <b>{label}</b>  ›  <code>{price}</code>  {chg}"
                )

    if crypto_changes:
        intro = random.choice(["⚡️ <b>کریپتو در یه ساعت اخیر</b>",
                               "🪙 <b>تحرکات بازار دیجیتال</b>",
                               "🔮 <b>کریپتو — جدیدترین‌ها</b>"])
        msg = f"{intro}\n🕐 {fa_digits(now.strftime('%H:%M'))}\n\n"
        msg += "\n".join(crypto_changes)
        msg += f"\n\n{random.choice(CLOSINGS)}"
        messages.append(msg)

    # ۴. خودروهای داخلی
    domestic_changes = []
    new_domestic = (all_data.get('domestic') or {}).get('items', [])
    old_domestic_map = {
        i.get('id', '') + str(i.get('rawPriceFactory', '')): i
        for i in (last_data.get('domestic') or {}).get('items', [])
    }

    for item in new_domestic:
        key = item.get('id', '') + str(item.get('rawPriceFactory', ''))
        old = old_domestic_map.get(key)
        if old and old.get('priceMarket') != item.get('priceMarket'):
            name = item.get('name', '—')
            price = item['priceMarket'] / 1_000_000
            change = item.get('change') or 0
            arrow = "🟢" if change > 0 else "🔴"
            domestic_changes.append(
                f"▪️ <b>{name}</b>  ›  <code>{fa_digits(f'{price:,.0f}')} م.ت</code>  {arrow}"
            )

    if domestic_changes:
        intro = random.choice(["🚗 <b>خودروهای داخلی — چه تغییری کردن؟</b>",
                               "🏎 <b>بازار خودرو داخلی</b>"])
        msg = f"{intro}\n🕐 {fa_digits(now.strftime('%H:%M'))}\n\n"
        msg += "\n".join(domestic_changes[:10])
        msg += f"\n\n{random.choice(CLOSINGS)}"
        messages.append(msg)

    # ۵. خودروهای دبی
    dubai_changes = []
    new_dubai = (all_data.get('dubai') or {}).get('items', [])
    old_dubai_map = {
        i.get('id', '') + str(i.get('rawPriceFactory', '')): i
        for i in (last_data.get('dubai') or {}).get('items', [])
    }

    for item in new_dubai:
        key = item.get('id', '') + str(item.get('rawPriceFactory', ''))
        old = old_dubai_map.get(key)
        if old and old.get('change') != item.get('change'):
            name = item.get('name', '—')
            price = item.get('change', 0)
            dubai_changes.append(
                f"▪️ <b>{name}</b>  ›  <code>{fa_digits(f'{price:,}')} درهم</code>"
            )

    if dubai_changes:
        intro = random.choice(["🚙 <b>خودروهای دبی — به‌روزرسانی</b>",
                               "✨ <b>بازار لوکس دبی</b>"])
        msg = f"{intro}\n🕐 {fa_digits(now.strftime('%H:%M'))}\n\n"
        msg += "\n".join(dubai_changes[:8])
        msg += f"\n\n{random.choice(CLOSINGS)}"
        messages.append(msg)

    return messages


# ─────────── منطق اصلی ───────────
def main():
    now = now_tehran()
    is_daily = (now.hour == 0)

    print(f"🕐 {now.strftime('%Y-%m-%d %H:%M')} تهران")
    print(f"📋 حالت: {'روزانه' if is_daily else 'ساعتی'}")

    # دریافت دیتا
    all_data = {}
    for name, url in SOURCES.items():
        try:
            all_data[name] = fetch_json(url)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_data[name] = None

    last = load_state()

    # ارسال
    if is_daily:
        print("\n📤 ارسال گزارش روزانه...")
        messages = [
            ("طلا", build_gold_message(all_data.get('latest'), is_daily=True)),
            ("ارز", build_forex_message(all_data.get('latest'), is_daily=True)),
            ("کریپتو", build_crypto_message(all_data.get('latest'), is_daily=True)),
            ("کالا", build_commodity_message(all_data.get('latest'), is_daily=True)),
            ("خودرو داخلی", build_domestic_message(all_data.get('domestic'))),
            ("خودرو دبی", build_dubai_message(all_data.get('dubai'))),
        ]

        for i, (name, msg) in enumerate(messages):
            if msg:
                print(f"\n📨 پیام {i+1}: {name}")
                keyboard = make_keyboard() if i == len(messages) - 1 else None
                send_long(msg, keyboard)
                time.sleep(2)

    else:
        hourly = build_hourly_updates(all_data, last)

        if not hourly:
            print("⏭️ بدون تغییر، ارسال نشد")
            return

        print(f"\n📤 ارسال {len(hourly)} پیام ساعتی...")
        for i, msg in enumerate(hourly):
            print(f"\n📨 پیام {i+1}")
            keyboard = make_keyboard() if i == len(hourly) - 1 else None
            send_long(msg, keyboard)
            time.sleep(2)

    # ذخیره state
    save_state(all_data)
    print("\n✅ تمام شد")


if __name__ == '__main__':
    main()
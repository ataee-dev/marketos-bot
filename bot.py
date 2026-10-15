import os
import json
import random
import time
import requests
import jdatetime
from pathlib import Path
from datetime import timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

# ─────────── تنظیمات ───────────
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
IMAGE_FILE = Path('marketos_table.png')
ASSETS_DIR = Path('assets')
CONTENT_DIR = Path('content')

BASE_URL = "https://raw.githubusercontent.com/ataee-dev/marketos/main/data"
SOURCES = {
    "latest":   f"{BASE_URL}/latest.json",
    "domestic": f"{BASE_URL}/cars/domestic.json",
}

CHANNEL_NAME = "قیمتو"
CHANNEL_USERNAME = "@gheimatoo"
CHANNEL_URL = "https://t.me/gheimatoo"
SITE_URL = "https://ataee-dev.github.io/marketos/index.html"
SITE_DISPLAY = "ataee-dev.github.io/marketos"
GITHUB_URL = "https://github.com/ataee-dev/marketos"

# ۱۰ نماد پرکاربرد برای پیام پین
TOP_KEYS = [
    "price_dollar_rl", "geram18", "sekeb", "sekee", "price_eur",
    "crypto-bitcoin", "mesghal", "ons", "crypto-ethereum", "price_gbp"
]

# ─────────── نمادها ───────────
SYMBOLS = {
    "sekeb": ("سکه بهار آزادی", "toman", "azadi.webp"),
    "sekee": ("سکه امامی", "toman", "emami.webp"),
    "nim": ("نیم سکه", "toman", "coin.webp"),
    "rob": ("ربع سکه", "toman", "coin.webp"),
    "gerami": ("سکه گرمی", "toman", "gerami.webp"),
    "geram18": ("طلای ۱۸ عیار", "toman", "gold.webp"),
    "geram24": ("طلای ۲۴ عیار", "toman", "gold.webp"),
    "mesghal": ("مثقال طلا", "toman", "gold.webp"),
    "ons": ("انس جهانی طلا", "dollar", "gold.webp"),
    "price_dollar_rl": ("دلار آمریکا", "toman", "usd.webp"),
    "price_dollar_dt": ("دلار دولتی", "toman", "usd.webp"),
    "price_eur": ("یورو", "toman", "eur.webp"),
    "price_gbp": ("پوند", "toman", "gbp.webp"),
    "price_aed": ("درهم امارات", "toman", "aed.webp"),
    "price_cad": ("دلار کانادا", "toman", "cad.webp"),
    "price_cny": ("یوان چین", "toman", "cny.webp"),
    "price_try": ("لیر ترکیه", "toman", "try.webp"),
    "price_jpy": ("ین ژاپن", "toman", "jpy.webp"),
    "price_chf": ("فرانک سوئیس", "toman", "chf.webp"),
    "price_sar": ("ریال سعودی", "toman", "sar.webp"),
    "price_kwd": ("دینار کویت", "toman", "kwd.webp"),
    "crypto-bitcoin": ("بیت‌کوین", "dollar", "btc.webp"),
    "crypto-ethereum": ("اتریوم", "dollar", "eth.webp"),
    "crypto-tether": ("تتر", "dollar", "usdt.webp"),
    "crypto-binance-coin": ("BNB", "dollar", "bnb.webp"),
    "crypto-solana": ("سولانا", "dollar", "sol.webp"),
    "crypto-ripple": ("ریپل", "dollar", "xrp.webp"),
    "crypto-dogecoin": ("دوج‌کوین", "dollar", "doge.webp"),
    "crypto-litecoin": ("لایت‌کوین", "dollar", "ltc.webp"),
    "crypto-polkadot": ("پولکادات", "dollar", "dot.webp"),
    "oil_brent": ("نفت برنت", "dollar", "brent.webp"),
    "oil": ("نفت WTI", "dollar", "oill.webp"),
    "energy_natural_gas": ("گاز طبیعی", "dollar", "gas.webp"),
    "silver": ("نقره (انس)", "dollar", "silver.webp"),
    "platinum": ("پلاتین", "dollar", "platinum.webp"),
    "palladium": ("پالادیوم", "dollar", "palladium.webp"),
    "copper": ("مس", "dollar", "copper.webp"),
    "aluminium": ("آلومینیوم", "dollar", "aluminium.webp"),
    "commodity_us_wheat": ("گندم", "dollar", "wheat.webp"),
    "commodity_corn": ("ذرت", "dollar", "corn.webp"),
    "commodity_us_coffee_c": ("قهوه", "dollar", "coffee.webp"),
    "commodity_us_sugar_no11": ("شکر", "dollar", "sugar.webp"),
}

# ─────────── متن‌های متغیر ───────────
INTROS_GOLD = ["🌟 <b>طلا و سکه امروز</b>", "✨ <b>درخشش بازار طلا</b>",
               "🥇 <b>بازار طلا و سکه</b>", "💫 <b>نبض بازار طلا</b>"]
INTROS_FOREX = ["💵 <b>بازار ارز امروز</b>", "📊 <b>نگاهی به بازار ارز</b>",
                "💱 <b>نبض بازار ارز</b>", "🌐 <b>ارز در یک نگاه</b>"]
INTROS_CRYPTO = ["⚡️ <b>بازار ارز دیجیتال</b>", "🪙 <b>دنیای کریپتو</b>",
                 "💎 <b>کریپتو امروز</b>", "🔮 <b>ارز دیجیتال در یک نگاه</b>"]
INTROS_COMMODITY = ["🛢 <b>کالا و انرژی</b>", "🏭 <b>بازار جهانی کالا</b>",
                    "⚙️ <b>انرژی و فلزات</b>", "🌾 <b>کالاهای اساسی</b>"]
INTROS_CARS = ["🚗 <b>بازار خودروهای داخلی</b>", "🏎 <b>خودروهای داخلی امروز</b>",
               "🔧 <b>قیمت خودروهای داخلی</b>", "🛣 <b>بازار خودرو در یک نگاه</b>"]

# ─────────── توابع کمکی ───────────
def fa_digits(text):
    return str(text).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))

def now_tehran():
    return jdatetime.datetime.now()

def get_jalali_str():
    now = now_tehran()
    wd = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
    m = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
         "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
    return f"{wd[now.weekday()]} {now.day} {m[now.month-1]} {now.year} — {now.hour:02d}:{now.minute:02d}"

def fetch_json(url):
    r = requests.get(url, timeout=25)
    r.raise_for_status()
    return r.json()

def load_content(filename):
    p = CONTENT_DIR / filename
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        # quotes.json لیست رشته‌ست، بقیه لیست دیکشنری
        if data and isinstance(data[0], str):
            return [{"text": t} for t in data]
        return data
    except Exception as e:
        print(f"⚠️ {filename}: {e}")
        return []

def pick_content(filename):
    items = load_content(filename)
    if not items:
        return None
    return random.choice(items)

def fmt_price(value, unit="toman"):
    if value is None:
        return "—"
    if isinstance(value, float):
        if abs(value) < 1:
            num = f"{value:,.6f}"
        elif abs(value) < 100:
            num = f"{value:,.2f}"
        else:
            num = f"{value:,.0f}"
    else:
        num = f"{value:,}"
    num = fa_digits(num)
    if unit == "toman":
        return f"{num} تومان"
    elif unit == "dollar":
        return f"{num} دلار"
    return num

def build_header():
    return (
        f"<b>🥇 {CHANNEL_NAME}</b> | {CHANNEL_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

def build_footer():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <a href='{SITE_URL}'>{SITE_DISPLAY}</a>"
    )

def make_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🌐 سایت قیمتو", "url": SITE_URL}],
            [
                {"text": "📊 گیت‌هاب", "url": GITHUB_URL},
                {"text": "📢 کانال", "url": CHANNEL_URL},
            ],
        ]
    }

# ─────────── ارسال ───────────
def send_message(text, reply_markup=None, disable_notification=False):
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
        else:
            print(f"   ❌ {r.status_code}: {r.text[:200]}")
        return r
    except Exception as e:
        print(f"   ❌ {e}")
        return None

def send_photo(photo_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHANNEL_ID,
                'caption': caption[:1024],
                'parse_mode': 'HTML',
            }
            r = requests.post(url, files=files, data=data, timeout=30)
            if r.ok:
                print(f"   ✅ تصویر ارسال شد")
            else:
                print(f"   ❌ تصویر: {r.text[:200]}")
            return r
    except Exception as e:
        print(f"   ❌ {e}")
        return None

def pin_message(message_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage"
    try:
        r = requests.post(url, json={
            'chat_id': CHANNEL_ID,
            'message_id': message_id,
            'disable_notification': True
        }, timeout=20)
        if r.ok:
            print(f"   📌 سنجاق شد")
        return r
    except Exception as e:
        print(f"   ❌ {e}")
        return None

# ─────────── تصویر جدول ───────────
def generate_table_image(data):
    W, H = 900, 900
    img = Image.new('RGB', (W, H), '#0F172A')
    draw = ImageDraw.Draw(img)

    fb = ASSETS_DIR / "IRANSansWeb_Bold.ttf"
    fr = ASSETS_DIR / "IRANSansWeb.ttf"

    try:
        f_title = ImageFont.truetype(str(fb), 32)
        f_row = ImageFont.truetype(str(fr), 22)
        f_small = ImageFont.truetype(str(fr), 16)
        f_price = ImageFont.truetype(str(fb), 22)
    except Exception:
        f_title = f_row = f_small = f_price = ImageFont.load_default()

    lp = ASSETS_DIR / "logo.png"
    if lp.exists():
        try:
            lg = Image.open(lp).convert("RGBA")
            lg.thumbnail((70, 70))
            img.paste(lg, (30, 20), lg)
        except Exception:
            pass

    draw.text((W-40, 25), "قیمتو", fill="#FFD700", font=f_title, anchor="ra")
    draw.text((W-40, 65), "@gheimatoo", fill="#94A3B8", font=f_small, anchor="ra")
    draw.line([(30, 105), (W-30, 105)], fill="#334155", width=2)
    draw.text((W//2, 130), get_jalali_str(), fill="#CBD5E1", font=f_small, anchor="mm")

    y = 165
    latest = data.get('latest', {}).get('data', {})

    for i, key in enumerate(TOP_KEYS):
        if key not in SYMBOLS or key not in latest:
            continue
        label, unit, logo_file = SYMBOLS[key]
        price = latest[key].get('p')
        if price is None:
            continue

        bg = "#1E293B" if i % 2 == 0 else "#0F172A"
        draw.rectangle([(30, y), (W-30, y+58)], fill=bg)

        lpath = ASSETS_DIR / logo_file
        if lpath.exists():
            try:
                ic = Image.open(lpath).convert("RGBA")
                ic.thumbnail((40, 40))
                img.paste(ic, (W-90, y+9), ic)
            except Exception:
                pass

        draw.text((W-110, y+17), label, fill="#F1F5F9", font=f_row, anchor="ra")
        draw.text((60, y+17), fmt_price(price, unit), fill="#10B981", font=f_price, anchor="la")

        y += 62

    draw.line([(30, H-55), (W-30, H-55)], fill="#334155", width=2)
    draw.text((W//2, H-32), "gheimatoo.ir  |  @gheimatoo", fill="#64748B", font=f_small, anchor="mm")

    img.save(IMAGE_FILE, "PNG")
    return IMAGE_FILE

# ─────────── پیام پین (لیست پرکاربرد) ───────────
def build_pinned_message(data):
    items = data.get('data', {})
    lines = [
        build_header(),
        "",
        "📌 <b>لیست پرکاربردهای بازار</b>",
        f"🕐 {get_jalali_str()}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    for key in TOP_KEYS:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            price = fmt_price(items[key]['p'], unit)
            dp = items[key].get('dp', 0)
            chg = ""
            if dp and dp != 0:
                chg = f"  {'🔺' if dp > 0 else '🔻'} {fa_digits(f'{abs(dp):.2f}')}٪"
            lines.append(f"▪️ <b>{label}</b>")
            lines.append(f"   <code>{price}</code>{chg}")
            lines.append("")

    lines += ["", build_footer()]
    return "\n".join(lines)

# ─────────── پیام‌های گزارش قیمت ───────────
def build_gold_message(data):
    items = data.get('data', {})
    lines = [build_header(), "", random.choice(INTROS_GOLD), f"🕐 {get_jalali_str()}", ""]

    for key, label in [("price_dollar_rl", "💰 دلار آمریکا فروش"),
                       ("price_dollar_dt", "💵 دلار آمریکا خرید"),
                       ("price_eur", "💶 یورو"),
                       ("price_cad", "🇨🇦 دلار کانادا"),
                       ("price_aed", "🇦🇪 درهم امارات")]:
        if key in items and items[key].get('p'):
            lines.append(f"{label}  <b>{fmt_price(items[key]['p'])}</b>")
            lines.append("")

    lines += ["━━━━━━━━━━━━━━━━━━━━━━", ""]
    for key, label in [("sekee", "🪙 سکه امامی"), ("sekeb", "🪙 سکه بهار آزادی"),
                       ("nim", "🪙 نیم سکه"), ("rob", "🪙 ربع سکه"),
                       ("gerami", "🪙 سکه گرمی")]:
        if key in items and items[key].get('p'):
            lines.append(f"{label}  <b>{fmt_price(items[key]['p'])}</b>")
            lines.append("")

    lines += ["━━━━━━━━━━━━━━━━━━━━━━", ""]
    for key, label in [("geram18", "✨ طلای ۱۸ عیار"), ("geram24", "✨ طلای ۲۴ عیار"),
                       ("mesghal", "⚜️ مثقال طلا")]:
        if key in items and items[key].get('p'):
            lines.append(f"{label}  <b>{fmt_price(items[key]['p'])}</b>")
            lines.append("")

    if "ons" in items and items["ons"].get('p'):
        lines.append(f"🌍 انس جهانی  <b>{fmt_price(items['ons']['p'], 'dollar')}</b>")

    lines += ["", build_footer(), "", "#نرخ_ارز #قیمتو"]
    return "\n".join(lines)


def build_forex_message(data):
    items = data.get('data', {})
    lines = [build_header(), "", random.choice(INTROS_FOREX), f"🕐 {get_jalali_str()}", ""]

    for key in ["price_dollar_rl", "price_dollar_dt", "price_eur", "price_gbp",
                "price_aed", "price_cad", "price_cny", "price_try",
                "price_jpy", "price_chf", "price_sar", "price_kwd"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            price = fmt_price(items[key]['p'], unit)
            dp = items[key].get('dp', 0)
            chg = ""
            if dp and dp != 0:
                chg = f"  {'🔺' if dp > 0 else '🔻'} {fa_digits(f'{abs(dp):.2f}')}٪"
            lines.append(f"▪️ {label}  ›  <b>{price}</b>{chg}")

    lines += ["", build_footer()]
    return "\n".join(lines)


def build_crypto_message(data):
    items = data.get('data', {})
    lines = [build_header(), "", random.choice(INTROS_CRYPTO), f"🕐 {get_jalali_str()}", ""]

    for key in ["crypto-bitcoin", "crypto-ethereum", "crypto-tether",
                "crypto-binance-coin", "crypto-solana", "crypto-ripple",
                "crypto-dogecoin", "crypto-litecoin", "crypto-polkadot"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            price = fmt_price(items[key]['p'], unit)
            dp = items[key].get('dp', 0)
            chg = ""
            if dp and dp != 0:
                chg = f"  {'🔺' if dp > 0 else '🔻'} {fa_digits(f'{abs(dp):.2f}')}٪"
            lines.append(f"▪️ {label}  ›  <b>{price}</b>{chg}")

    lines += ["", build_footer()]
    return "\n".join(lines)


def build_commodity_message(data):
    items = data.get('data', {})
    lines = [build_header(), "", random.choice(INTROS_COMMODITY), f"🕐 {get_jalali_str()}", ""]

    lines.append("<b>⛽ انرژی</b>")
    for key in ["oil_brent", "oil", "energy_natural_gas"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            price = fmt_price(items[key]['p'], unit)
            dp = items[key].get('dp', 0)
            chg = ""
            if dp and dp != 0:
                chg = f"  {'🔺' if dp > 0 else '🔻'} {fa_digits(f'{abs(dp):.2f}')}٪"
            lines.append(f"▪️ {label}  ›  <b>{price}</b>{chg}")

    lines.append("")
    lines.append("<b>💎 فلزات گرانبها</b>")
    for key in ["silver", "platinum", "palladium"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            price = fmt_price(items[key]['p'], unit)
            dp = items[key].get('dp', 0)
            chg = ""
            if dp and dp != 0:
                chg = f"  {'🔺' if dp > 0 else '🔻'} {fa_digits(f'{abs(dp):.2f}')}٪"
            lines.append(f"▪️ {label}  ›  <b>{price}</b>{chg}")

    lines.append("")
    lines.append("<b>🔩 فلزات پایه</b>")
    for key in ["copper", "aluminium"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            lines.append(f"▪️ {label}  ›  <b>{fmt_price(items[key]['p'], unit)}</b>")

    lines.append("")
    lines.append("<b>🌾 محصولات کشاورزی</b>")
    for key in ["commodity_us_wheat", "commodity_corn",
                "commodity_us_coffee_c", "commodity_us_sugar_no11"]:
        if key in items and items[key].get('p') and key in SYMBOLS:
            label, unit, _ = SYMBOLS[key]
            lines.append(f"▪️ {label}  ›  <b>{fmt_price(items[key]['p'], unit)}</b>")

    lines += ["", build_footer()]
    return "\n".join(lines)


def build_cars_message(data, max_items=15):
    if not data or 'items' not in data:
        return None
    items = [i for i in data['items']
             if i.get('status') == 'available' and i.get('priceMarket')]
    if not items:
        return None
    items.sort(key=lambda x: abs(x.get('change') or 0), reverse=True)
    items = items[:max_items]

    lines = [build_header(), "", random.choice(INTROS_CARS), f"🕐 {get_jalali_str()}", ""]

    by_cat = {}
    for item in items:
        cat = item.get('category', 'سایر')
        by_cat.setdefault(cat, []).append(item)

    for cat, cat_items in by_cat.items():
        lines.append(f"<b>🏭 {cat}</b>")
        for item in cat_items:
            name = item.get('name', '—')
            price_m = item['priceMarket'] / 1_000_000
            change = item.get('change') or 0
            line = f"▪️ {name}  ›  <b>{fa_digits(f'{price_m:,.0f}')} م.ت</b>"
            if change and change != 0:
                change_m = change / 1_000_000
                arrow = "🔺" if change > 0 else "🔻"
                line += f"  {arrow} {fa_digits(f'{abs(change_m):,.0f}')}م"
            lines.append(line)
        lines.append("")

    lines.append("💰 <i>قیمت‌ها به میلیون تومان</i>")
    lines.append(build_footer())
    return "\n".join(lines)


# ─────────── پیام‌های محتوایی ───────────
def build_content_did_you_know():
    item = pick_content('did_you_know.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "💡 <b>دانستنی</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#دانستنی #قیمتو"
    )


def build_content_market_fact():
    item = pick_content('market_facts.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "📊 <b>واقعیت بازار</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#بازار #قیمتو"
    )


def build_content_tip():
    item = pick_content('tips.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "💡 <b>نکته‌ی آموزشی</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#آموزش #قیمتو"
    )


def build_content_quote():
    item = pick_content('quotes.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "💭 <b>جمله‌ی روز</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#جمله_روز #قیمتو"
    )


def build_content_bubble():
    item = pick_content('bubble_analysis.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "🫧 <b>تحلیل حباب</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#حباب #قیمتو"
    )


def build_content_comparison():
    item = pick_content('comparisons.json')
    if not item:
        return None
    return (
        f"{build_header()}\n"
        "\n"
        "⚖️ <b>مقایسه‌ی بازارها</b>\n"
        "\n"
        f"<blockquote>{item['text']}</blockquote>\n"
        "\n"
        f"{build_footer()}\n"
        "\n"
        "#مقایسه #قیمتو"
    )


# ─────────── منطق اصلی ───────────
def main():
    print(f"🕐 {get_jalali_str()}")

    all_data = {}
    for name, url in SOURCES.items():
        try:
            all_data[name] = fetch_json(url)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_data[name] = None

    latest = all_data.get('latest')
    if not latest:
        print("❌ دیتای latest دریافت نشد")
        return

    now = now_tehran()

    # ─── ابتدای روز: گزارش کامل + پیام پین + تصویر ───
    if now.hour == 0:
        print("\n📌 حالت: گزارش روزانه + سنجاق")

        # ۱. پیام پین (لیست پرکاربرد)
        print("\n📨 پیام ۱: لیست پرکاربرد (سنجاق)")
        pin_msg = build_pinned_message(latest)
        resp = send_message(pin_msg)
        if resp and resp.ok:
            try:
                msg_id = resp.json().get('result', {}).get('message_id')
                if msg_id:
                    pin_message(msg_id)
            except Exception:
                pass
        time.sleep(3)

        # ۲. تصویر جدول
        print("\n🖼️ تصویر جدول")
        try:
            img = generate_table_image(all_data)
            if img:
                send_photo(img, f"📊 <b>جدول نمادهای پرکاربرد</b>\n\n🌐 {SITE_DISPLAY}")
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(3)

        # ۳. طلا
        print("\n📨 پیام ۳: طلا و سکه")
        send_message(build_gold_message(latest))
        time.sleep(2)

        # ۴. ارز
        print("\n📨 پیام ۴: ارز")
        send_message(build_forex_message(latest))
        time.sleep(2)

        # ۵. کریپتو
        print("\n📨 پیام ۵: کریپتو")
        send_message(build_crypto_message(latest))
        time.sleep(2)

        # ۶. کالا
        print("\n📨 پیام ۶: کالا")
        send_message(build_commodity_message(latest))
        time.sleep(2)

        # ۷. خودرو
        if all_data.get('domestic'):
            print("\n📨 پیام ۷: خودرو")
            cars = build_cars_message(all_data['domestic'])
            if cars:
                send_message(cars)
            time.sleep(2)

        # ۸. محتوای آموزشی روزانه
        print("\n📨 پیام ۸: محتوای روزانه")
        content_builders = [
            build_content_did_you_know,
            build_content_tip,
            build_content_quote,
            build_content_bubble,
            build_content_comparison,
            build_content_market_fact,
        ]
        content_msg = random.choice(content_builders)()
        if content_msg:
            send_message(content_msg, make_keyboard())

    # ─── ساعات دیگر: ترکیب قیمت + محتوا ───
    else:
        # تصمیم‌گیری: قیمت یا محتوا؟
        # ۶۰٪ قیمت، ۴۰٪ محتوا (به‌صورت تصادفی)

        if random.random() < 0.6:
            # گزارش قیمت
            price_builders = [
                ("طلا", build_gold_message),
                ("ارز", build_forex_message),
                ("کریپتو", build_crypto_message),
                ("کالا", build_commodity_message),
            ]
            name, builder = random.choice(price_builders)
            print(f"\n📨 گزارش قیمت: {name}")
            send_message(builder(latest), make_keyboard())
        else:
            # محتوای آموزشی
            content_builders = [
                ("دانستنی", build_content_did_you_know),
                ("نکته", build_content_tip),
                ("جمله", build_content_quote),
                ("حباب", build_content_bubble),
                ("مقایسه", build_content_comparison),
                ("واقعیت", build_content_market_fact),
            ]
            name, builder = random.choice(content_builders)
            print(f"\n📨 محتوا: {name}")
            msg = builder()
            if msg:
                send_message(msg, make_keyboard())

    print("\n✅ تمام شد")


if __name__ == '__main__':
    main()
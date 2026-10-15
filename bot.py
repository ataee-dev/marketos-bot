import os
import json
import random
import time
import requests
import jdatetime
from pathlib import Path
from datetime import timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# ─────────── تنظیمات ───────────
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
STATE_FILE = Path('last_state.json')
IMAGE_FILE = Path('marketos_table.png')
ASSETS_DIR = Path('assets')

BASE_URL = "https://raw.githubusercontent.com/ataee-dev/marketos/main/data"
SOURCES = {
    "latest":   f"{BASE_URL}/latest.json",
    "domestic": f"{BASE_URL}/cars/domestic.json",
}

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

CHANNEL_NAME = "قیمتو"
CHANNEL_USERNAME = "@gheimatoo"
CHANNEL_URL = "https://t.me/gheimatoo"
SITE_URL = "gheimatoo.ir"
NAVASAN_URL = "https://www.navasan.net"


# ─────────── تعریف نمادها ───────────
SYMBOLS = {
    "gold": {
        "title": "🥇 طلا و سکه",
        "items": {
            "sekeb": ("سکه بهار آزادی", "toman", "azadi.webp"),
            "sekee": ("سکه امامی", "toman", "emami.webp"),
            "nim": ("نیم سکه", "toman", "coin.webp"),
            "rob": ("ربع سکه", "toman", "coin.webp"),
            "gerami": ("سکه گرمی", "toman", "gerami.webp"),
            "geram18": ("طلای ۱۸ عیار", "toman", "gold.webp"),
            "geram24": ("طلای ۲۴ عیار", "toman", "gold.webp"),
            "mesghal": ("مثقال طلا", "toman", "gold.webp"),
            "ons": ("انس جهانی", "dollar", "gold.webp"),
        },
    },
    "forex": {
        "title": "💵 ارز",
        "items": {
            "price_dollar_rl": ("دلار آمریکا", "toman", "usd.webp"),
            "price_dollar_dt": ("دلار دولتی", "toman", "usd.webp"),
            "price_eur": ("یورو", "toman", "eur.webp"),
            "price_gbp": ("پوند", "toman", "gbp.webp"),
            "price_aed": ("درهم امارات", "toman", "aed.webp"),
            "price_cad": ("دلار کانادا", "toman", "cad.webp"),
            "price_cny": ("یوان چین", "toman", "cny.webp"),
            "price_try": ("لیر ترکیه", "toman", "try.webp"),
            "price_jpy": ("یِن ژاپن", "toman", "jpy.webp"),
            "price_chf": ("فرانک سوئیس", "toman", "chf.webp"),
            "price_sar": ("ریال سعودی", "toman", "sar.webp"),
            "price_kwd": ("دینار کویت", "toman", "kwd.webp"),
        },
    },
    "crypto": {
        "title": "🪙 ارز دیجیتال",
        "items": {
            "crypto-bitcoin": ("بیت‌کوین", "dollar", "btc.webp"),
            "crypto-ethereum": ("اتریوم", "dollar", "eth.webp"),
            "crypto-tether": ("تتر", "dollar", "usdt.webp"),
            "crypto-binance-coin": ("BNB", "dollar", "bnb.webp"),
            "crypto-solana": ("سولانا", "dollar", "sol.webp"),
            "crypto-ripple": ("ریپل", "dollar", "xrp.webp"),
            "crypto-dogecoin": ("دوج‌کوین", "dollar", "doge.webp"),
            "crypto-litecoin": ("لایت‌کوین", "dollar", "ltc.webp"),
            "crypto-polkadot": ("پولکادات", "dollar", "dot.webp"),
        },
    },
    "commodity": {
        "title": "🛢 کالا و انرژی",
        "items": {
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
        },
    },
}

# ۱۰ نماد پرکاربرد برای تصویر
TOP_10_KEYS = [
    "price_dollar_rl",
    "price_eur",
    "price_gbp",
    "price_aed",
    "geram18",
    "sekeb",
    "sekee",
    "nim",
    "rob",
    "crypto-bitcoin",
]


# ─────────── متن‌های متغیر ───────────
QUOTES = [
    "«بازار، آینه‌ی ترس و طمع آدم‌هاست.»",
    "«هر عددی که می‌بینی، پشتش یک تصمیم انسانیه.»",
    "«اقتصاد، علم اعداد نیست؛ علم انتخاب‌هاست.»",
    "«طلا همیشه درخشنده است، حتی در تاریکی.»",
]

INTROS_GOLD = [
    "🌟 <b>طلا و سکه امروز</b>",
    "✨ <b>درخشش بازار طلا</b>",
    "🥇 <b>بازار طلا و سکه</b>",
]

INTROS_FOREX = [
    "💵 <b>بازار ارز امروز</b>",
    "📊 <b>نگاهی به بازار ارز</b>",
    "💱 <b>نبض بازار ارز</b>",
]

INTROS_CRYPTO = [
    "⚡️ <b>بازار ارز دیجیتال</b>",
    "🪙 <b>دنیای کریپتو</b>",
    "💎 <b>کریپتو امروز</b>",
]

INTROS_COMMODITY = [
    "🛢 <b>کالا و انرژی</b>",
    "🏭 <b>بازار جهانی کالا</b>",
    "⚙️ <b>انرژی و فلزات</b>",
]

INTROS_CARS = [
    "🚗 <b>بازار خودروهای داخلی</b>",
    "🏎 <b>خودروهای داخلی امروز</b>",
]

CLOSINGS = [
    f"🌐 {SITE_URL}",
    f"🔗 {SITE_URL} | @gheimatoo",
]


# ─────────── توابع کمکی ───────────
def fa_digits(text):
    return str(text).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))


def fa_text(text):
    """تبدیل متن فارسی به فرمت قابل نمایش در PIL"""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)


def now_tehran():
    return jdatetime.datetime.now(locale=jdatetime.FA_LOCALE)


def get_jalali_str():
    now = now_tehran()
    return now.strftime("%A %d %B %Y ساعت %H:%M")


def fetch_json(url):
    r = requests.get(url, timeout=25)
    r.raise_for_status()
    return r.json()


def fmt_price(value, unit="toman"):
    """فرمت قیمت با اعداد کامل و فارسی"""
    if value is None:
        return "—"
    
    if isinstance(value, float):
        if abs(value) < 1:
            num_str = f"{value:,.6f}"
        elif abs(value) < 100:
            num_str = f"{value:,.2f}"
        else:
            num_str = f"{value:,.0f}"
    else:
        num_str = f"{value:,}"
    
    num_str = fa_digits(num_str)
    
    if unit == "toman":
        return f"{num_str} تومان"
    elif unit == "dollar":
        return f"{num_str} دلار"
    elif unit == "dirham":
        return f"{num_str} درهم"
    return num_str


def get_logo_path(filename):
    if not filename:
        return None
    p = ASSETS_DIR / filename
    return p if p.exists() else None


# ─────────── ساخت تصویر جدول ───────────
def generate_table_image(data):
    """ساخت تصویر جدول با لوگوها"""
    
    W, H = 900, 780
    img = Image.new('RGB', (W, H), '#0F172A')
    draw = ImageDraw.Draw(img)
    
    # فونت‌های IRANSans
    font_bold = ASSETS_DIR / "IRANSansWeb_Bold.ttf"
    font_reg = ASSETS_DIR / "IRANSansWeb.ttf"
    
    try:
        if font_bold.exists() and font_reg.exists():
            font_title = ImageFont.truetype(str(font_bold), 32)
            font_row = ImageFont.truetype(str(font_reg), 22)
            font_small = ImageFont.truetype(str(font_reg), 16)
            font_price = ImageFont.truetype(str(font_bold), 22)
        else:
            font_title = ImageFont.load_default()
            font_row = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_price = ImageFont.load_default()
    except Exception as e:
        print(f"⚠️ فونت لود نشد: {e}")
        font_title = ImageFont.load_default()
        font_row = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_price = ImageFont.load_default()
    
    # ─── هدر با لوگوی قیمتو ───
    logo_path = ASSETS_DIR / "logo.png"
    header_y = 20
    
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((70, 70))
            img.paste(logo, (30, header_y), logo)
        except Exception as e:
            print(f"⚠️ لوگو لود نشد: {e}")
    
    # عنوان
    draw.text((W - 40, header_y + 5), fa_text("قیمتو"), 
              fill="#FFD700", font=font_title, anchor="ra")
    draw.text((W - 40, header_y + 45), fa_text("@gheimatoo"), 
              fill="#94A3B8", font=font_small, anchor="ra")
    
    # خط جداکننده
    draw.line([(30, 105), (W-30, 105)], fill="#334155", width=2)
    
    # ─── تاریخ و ساعت ───
    now_str = get_jalali_str()
    draw.text((W//2, 130), fa_text(now_str), 
              fill="#CBD5E1", font=font_small, anchor="mm")
    
    # ─── جدول ───
    y_pos = 165
    latest_data = data.get('latest', {}).get('data', {})
    
    for i, key in enumerate(TOP_10_KEYS):
        label, unit, logo_file = None, "toman", None
        for grp in SYMBOLS.values():
            if key in grp['items']:
                label, unit, logo_file = grp['items'][key]
                break
        
        if not label or key not in latest_data:
            continue
        
        item = latest_data[key]
        price = item.get('p')
        if price is None:
            continue
        
        # رنگ ردیف متناوب
        row_bg = "#1E293B" if i % 2 == 0 else "#0F172A"
        draw.rectangle([(30, y_pos), (W-30, y_pos+58)], fill=row_bg)
        
        # لوگو سمت راست
        logo_path = get_logo_path(logo_file)
        if logo_path:
            try:
                ic = Image.open(logo_path).convert("RGBA")
                ic.thumbnail((40, 40))
                img.paste(ic, (W - 90, y_pos + 9), ic)
            except Exception:
                pass
        
        # نام نماد (راست‌چین)
        draw.text((W - 110, y_pos + 17), fa_text(label), 
                  fill="#F1F5F9", font=font_row, anchor="ra")
        
        # قیمت (چپ‌چین)
        price_str = fmt_price(price, unit)
        draw.text((60, y_pos + 17), fa_text(price_str), 
                  fill="#10B981", font=font_price, anchor="la")
        
        y_pos += 62
    
    # ─── فوتر ───
    draw.line([(30, H-55), (W-30, H-55)], fill="#334155", width=2)
    draw.text((W//2, H-32), fa_text(f"🌐 {SITE_URL}  |  @gheimatoo"), 
              fill="#64748B", font=font_small, anchor="mm")
    
    img.save(IMAGE_FILE, "PNG")
    print(f"✅ تصویر ساخته شد: {IMAGE_FILE}")
    return IMAGE_FILE


# ─────────── ارسال به تلگرام ───────────
def send_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    try:
        r = requests.post(url, json=payload, timeout=25)
        if r.ok:
            print(f"   ✅ ارسال شد ({len(text)} کاراکتر)")
        else:
            print(f"   ❌ خطا {r.status_code}: {r.text[:200]}")
        return r
    except Exception as e:
        print(f"   ❌ استثنا: {e}")
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
                print(f"   ❌ خطای تصویر: {r.text[:200]}")
            return r
    except Exception as e:
        print(f"   ❌ استثنا: {e}")
        return None


def pin_message(message_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage"
    payload = {
        'chat_id': CHANNEL_ID,
        'message_id': message_id,
        'disable_notification': True
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.ok:
            print(f"   📌 سنجاق شد")
        return r
    except Exception as e:
        print(f"   ❌ خطای سنجاق: {e}")
        return None


def make_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🌐 gheimatoo.ir", "url": f"https://{SITE_URL}"},
                {"text": "📊 navasan.net", "url": NAVASAN_URL},
            ]
        ]
    }


# ─────────── پیام طلا و سکه ───────────
def build_gold_message(data):
    items = data.get('data', {})
    now_str = get_jalali_str()
    intro = random.choice(INTROS_GOLD)
    
    lines = [
        f"🥇 <b>{CHANNEL_NAME}</b> | {CHANNEL_USERNAME}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        intro,
        f"🕐 {now_str}",
        "",
    ]
    
    # دلار آمریکا فروش
    if "price_dollar_rl" in items and items["price_dollar_rl"].get('p'):
        lines.append(f" 💵 دلار آمریکا فروش 🔴 : {fmt_price(items['price_dollar_rl']['p'])}")
        lines.append("")
    
    # دلار آمریکا خرید (dolati)
    if "price_dollar_dt" in items and items["price_dollar_dt"].get('p'):
        lines.append(f" 💵 دلار آمریکا خرید 🔵 : {fmt_price(items['price_dollar_dt']['p'])}")
        lines.append("")
    
    # یورو
    if "price_eur" in items and items["price_eur"].get('p'):
        lines.append(f" 💶 یورو فروش : {fmt_price(items['price_eur']['p'])}")
        lines.append("")
    
    # دلار کانادا
    if "price_cad" in items and items["price_cad"].get('p'):
        lines.append(f" دلار کانادا فروش 🇨🇦 : {fmt_price(items['price_cad']['p'])}")
        lines.append("")
    
    # درهم امارات
    if "price_aed" in items and items["price_aed"].get('p'):
        lines.append(f" درهم امارات 🇦🇪 : {fmt_price(items['price_aed']['p'])}")
        lines.append("")
    
    # سکه امامی
    if "sekee" in items and items["sekee"].get('p'):
        lines.append(f" سکه امامی ✴️ : {fmt_price(items['sekee']['p'])}")
        lines.append("")
    
    # سکه بهار
    if "sekeb" in items and items["sekeb"].get('p'):
        lines.append(f" سکه بهار آزادی ✴️ : {fmt_price(items['sekeb']['p'])}")
        lines.append("")
    
    # نیم سکه
    if "nim" in items and items["nim"].get('p'):
        lines.append(f" نیم سکه ✴️ : {fmt_price(items['nim']['p'])}")
        lines.append("")
    
    # ربع سکه
    if "rob" in items and items["rob"].get('p'):
        lines.append(f" ربع سکه ✴️ : {fmt_price(items['rob']['p'])}")
        lines.append("")
    
    # سکه گرمی
    if "gerami" in items and items["gerami"].get('p'):
        lines.append(f" سکه گرمی ✴️ : {fmt_price(items['gerami']['p'])}")
        lines.append("")
    
    # طلای ۱۸ عیار
    if "geram18" in items and items["geram18"].get('p'):
        lines.append(f" طلای ۱۸ عیار هر گرم ✴️ : {fmt_price(items['geram18']['p'])}")
        lines.append("")
    
    # مثقال
    if "mesghal" in items and items["mesghal"].get('p'):
        lines.append(f" مثقال طلای آبشده ✴️ : {fmt_price(items['mesghal']['p'])}")
        lines.append("")
    
    # لینک و هشتگ
    lines.append("")
    lines.append(f"🌐 {SITE_URL}")
    lines.append("")
    lines.append(f"#نرخ_ارز 🕐 {now_str}")
    
    return "\n".join(lines)


# ─────────── پیام ارز ───────────
def build_forex_message(data):
    items = data.get('data', {})
    now_str = get_jalali_str()
    intro = random.choice(INTROS_FOREX)
    quote = random.choice(QUOTES)
    closing = random.choice(CLOSINGS)
    
    lines = [
        f"💵 <b>{CHANNEL_NAME}</b> | {CHANNEL_USERNAME}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        intro,
        f"🕐 {now_str}",
        "",
        f"<blockquote>{quote}</blockquote>",
        "",
    ]
    
    for key in ["price_dollar_rl", "price_dollar_dt", "price_eur", "price_gbp",
                "price_aed", "price_cad", "price_cny", "price_try",
                "price_jpy", "price_chf", "price_sar", "price_kwd"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['forex']['items'].get(key, (None, None, None))
            if label:
                lines.append(f"▪️ {label}  ›  <b>{fmt_price(items[key]['p'], unit)}</b>")
    
    lines.append("")
    lines.append(closing)
    
    return "\n".join(lines)


# ─────────── پیام کریپتو ───────────
def build_crypto_message(data):
    items = data.get('data', {})
    now_str = get_jalali_str()
    intro = random.choice(INTROS_CRYPTO)
    closing = random.choice(CLOSINGS)
    
    lines = [
        f"⚡️ <b>{CHANNEL_NAME}</b> | {CHANNEL_USERNAME}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        intro,
        f"🕐 {now_str}",
        "",
    ]
    
    for key in ["crypto-bitcoin", "crypto-ethereum", "crypto-tether",
                "crypto-binance-coin", "crypto-solana", "crypto-ripple",
                "crypto-dogecoin", "crypto-litecoin", "crypto-polkadot"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['crypto']['items'].get(key, (None, None, None))
            if label:
                price = fmt_price(items[key]['p'], unit)
                dp = items[key].get('dp', 0)
                change = ""
                if dp and dp != 0:
                    arrow = "🔺" if dp > 0 else "🔻"
                    change = f"  {arrow} {fa_digits(f'{abs(dp):.2f}')}٪"
                lines.append(f"▪️ {label}  ›  <b>{price}</b>{change}")
    
    lines.append("")
    lines.append(closing)
    
    return "\n".join(lines)


# ─────────── پیام کالا ───────────
def build_commodity_message(data):
    items = data.get('data', {})
    now_str = get_jalali_str()
    intro = random.choice(INTROS_COMMODITY)
    quote = random.choice(QUOTES)
    closing = random.choice(CLOSINGS)
    
    lines = [
        f"🛢 <b>{CHANNEL_NAME}</b> | {CHANNEL_USERNAME}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        intro,
        f"🕐 {now_str}",
        "",
        f"<blockquote>{quote}</blockquote>",
        "",
    ]
    
    # انرژی
    lines.append("<b>انرژی</b>")
    for key in ["oil_brent", "oil", "energy_natural_gas"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['commodity']['items'].get(key, (None, None, None))
            if label:
                price = fmt_price(items[key]['p'], unit)
                dp = items[key].get('dp', 0)
                change = ""
                if dp and dp != 0:
                    arrow = "🔺" if dp > 0 else "🔻"
                    change = f"  {arrow} {fa_digits(f'{abs(dp):.2f}')}٪"
                lines.append(f"▪️ {label}  ›  <b>{price}</b>{change}")
    
    # فلزات گرانبها
    lines.append("")
    lines.append("<b>فلزات گرانبها</b>")
    for key in ["silver", "platinum", "palladium"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['commodity']['items'].get(key, (None, None, None))
            if label:
                price = fmt_price(items[key]['p'], unit)
                dp = items[key].get('dp', 0)
                change = ""
                if dp and dp != 0:
                    arrow = "🔺" if dp > 0 else "🔻"
                    change = f"  {arrow} {fa_digits(f'{abs(dp):.2f}')}٪"
                lines.append(f"▪️ {label}  ›  <b>{price}</b>{change}")
    
    # فلزات پایه
    lines.append("")
    lines.append("<b>فلزات پایه</b>")
    for key in ["copper", "aluminium"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['commodity']['items'].get(key, (None, None, None))
            if label:
                price = fmt_price(items[key]['p'], unit)
                lines.append(f"▪️ {label}  ›  <b>{price}</b>")
    
    # کشاورزی
    lines.append("")
    lines.append("<b>محصولات کشاورزی</b>")
    for key in ["commodity_us_wheat", "commodity_corn", 
                "commodity_us_coffee_c", "commodity_us_sugar_no11"]:
        if key in items and items[key].get('p'):
            label, unit, _ = SYMBOLS['commodity']['items'].get(key, (None, None, None))
            if label:
                price = fmt_price(items[key]['p'], unit)
                lines.append(f"▪️ {label}  ›  <b>{price}</b>")
    
    lines.append("")
    lines.append(closing)
    
    return "\n".join(lines)


# ─────────── پیام خودرو ───────────
def build_cars_message(data, max_items=15):
    if not data or 'items' not in data:
        return None
    
    items = [i for i in data['items']
             if i.get('status') == 'available' and i.get('priceMarket')]
    
    if not items:
        return None
    
    items.sort(key=lambda x: abs(x.get('change') or 0), reverse=True)
    items = items[:max_items]
    
    now_str = get_jalali_str()
    intro = random.choice(INTROS_CARS)
    closing = random.choice(CLOSINGS)
    
    lines = [
        f"🚗 <b>{CHANNEL_NAME}</b> | {CHANNEL_USERNAME}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        intro,
        f"🕐 {now_str}",
        "",
    ]
    
    by_cat = {}
    for item in items:
        cat = item.get('category', 'سایر')
        by_cat.setdefault(cat, []).append(item)
    
    for cat, cat_items in by_cat.items():
        lines.append(f"<b>{cat}</b>")
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
    lines.append(closing)
    
    return "\n".join(lines)


# ─────────── منطق اصلی ───────────
def main():
    print(f"🕐 {get_jalali_str()}")
    
    # دریافت دیتا
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
    
    # ─── ۱. پیام طلا و سکه (و سنجاق) ───
    print("\n📨 پیام ۱: طلا و سکه")
    gold_msg = build_gold_message(latest)
    resp = send_message(gold_msg, make_keyboard())
    if resp and resp.ok:
        try:
            msg_id = resp.json().get('result', {}).get('message_id')
            if msg_id:
                pin_message(msg_id)
        except Exception:
            pass
    
    time.sleep(3)
    
    # ─── ۲. تصویر جدول ───
    print("\n🖼️ ساخت تصویر جدول...")
    try:
        img_path = generate_table_image(all_data)
        if img_path:
            caption = f"📊 <b>۱۰ نماد پرکاربرد بازار</b>\n\n🌐 {SITE_URL}"
            send_photo(img_path, caption)
    except Exception as e:
        print(f"❌ خطا در تصویر: {e}")
    
    time.sleep(3)
    
    # ─── ۳. پیام ارز ───
    print("\n📨 پیام ۲: ارز")
    forex_msg = build_forex_message(latest)
    send_message(forex_msg)
    
    time.sleep(2)
    
    # ─── ۴. پیام کریپتو ───
    print("\n📨 پیام ۳: کریپتو")
    crypto_msg = build_crypto_message(latest)
    send_message(crypto_msg)
    
    time.sleep(2)
    
    # ─── ۵. پیام کالا ───
    print("\n📨 پیام ۴: کالا")
    commodity_msg = build_commodity_message(latest)
    send_message(commodity_msg)
    
    time.sleep(2)
    
    # ─── ۶. پیام خودرو ───
    if all_data.get('domestic'):
        print("\n📨 پیام ۵: خودرو")
        cars_msg = build_cars_message(all_data['domestic'])
        if cars_msg:
            send_message(cars_msg)
    
    print("\n✅ تمام شد")


if __name__ == '__main__':
    main()
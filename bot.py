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
}

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

CHANNEL_NAME = "قیمتو"
CHANNEL_USERNAME = "@gheimatoo"
CHANNEL_URL = "https://t.me/gheimatoo"

# ─────────── گروه‌بندی نمادها ───────────
GROUPS = {
    "gold": {
        "title": "🥇 طلا و سکه",
        "symbols": {
            "geram18": ("گرم ۱۸ عیار", "toman"),
            "geram24": ("گرم ۲۴ عیار", "toman"),
            "mesghal": ("مثقال", "toman"),
            "sekeb": ("سکه بهار", "toman"),
            "sekee": ("سکه امامی", "toman"),
            "nim": ("نیم سکه", "toman"),
            "rob": ("ربع سکه", "toman"),
            "ons": ("انس جهانی", "dollar"),
        },
    },
    "forex": {
        "title": "💵 ارز",
        "symbols": {
            "price_dollar_rl": ("دلار آزاد", "toman"),
            "price_dollar_dt": ("دلار دولتی", "toman"),
            "price_eur": ("یورو", "toman"),
            "price_gbp": ("پوند", "toman"),
            "price_aed": ("درهم امارات", "toman"),
            "price_cny": ("یوان چین", "toman"),
            "price_try": ("لیر ترکیه", "toman"),
            "price_jpy": ("یِن ژاپن", "toman"),
            "price_chf": ("فرانک سوئیس", "toman"),
            "price_sar": ("ریال سعودی", "toman"),
            "price_kwd": ("دینار کویت", "toman"),
        },
    },
    "crypto": {
        "title": "🪙 ارز دیجیتال",
        "symbols": {
            "crypto-bitcoin": ("بیت‌کوین", "dollar"),
            "crypto-ethereum": ("اتریوم", "dollar"),
            "crypto-tether": ("تتر", "dollar"),
            "crypto-binance-coin": ("BNB", "dollar"),
            "crypto-solana": ("سولانا", "dollar"),
            "crypto-ripple": ("ریپل", "dollar"),
            "crypto-cardano": ("کاردانو", "dollar"),
            "crypto-dogecoin": ("دوج‌کوین", "dollar"),
            "crypto-litecoin": ("لایت‌کوین", "dollar"),
            "crypto-polkadot": ("پولکادات", "dollar"),
            "crypto-tron": ("ترون", "dollar"),
            "crypto-chainlink": ("چین‌لینک", "dollar"),
        },
    },
    "commodity": {
        "title": "🛢 کالا و انرژی",
        "symbols": {
            "oil_brent": ("نفت برنت", "dollar"),
            "energy_natural_gas": ("گاز طبیعی", "dollar"),
            "silver": ("نقره (انس)", "dollar"),
            "silver_999": ("نقره ۹۹۹", "toman"),
            "platinum": ("پلاتین", "dollar"),
            "palladium": ("پالادیوم", "dollar"),
            "copper": ("مس", "dollar"),
            "aluminium": ("آلومینیوم", "dollar"),
            "commodity_us_wheat": ("گندم", "dollar"),
            "commodity_corn": ("ذرت", "dollar"),
            "commodity_us_coffee_c": ("قهوه", "dollar"),
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
]

INTROS_GOLD = [
    "✨ <b>طلا و سکه امروز</b>",
    "🥇 <b>بازار طلا و سکه</b>",
    "🌟 <b>درخشش طلا در بازار</b>",
]

INTROS_FOREX = [
    "💵 <b>بازار ارز</b>",
    "📊 <b>نگاهی به بازار ارز</b>",
    "💱 <b>نبض بازار ارز</b>",
]

INTROS_CRYPTO = [
    "⚡️ <b>بازار ارز دیجیتال</b>",
    "🪙 <b>دنیای کریپتو</b>",
    "💎 <b>ارز دیجیتال امروز</b>",
]

INTROS_COMMODITY = [
    "🛢 <b>کالا و انرژی</b>",
    "🏭 <b>بازار جهانی کالا</b>",
    "⚙️ <b>انرژی و فلزات</b>",
]

INTROS_DOMESTIC = [
    "🚗 <b>بازار خودروهای داخلی</b>",
    "🏎 <b>خودروهای داخلی امروز</b>",
    "🔧 <b>قیمت خودروهای داخلی</b>",
]


# ─────────── توابع کمکی ───────────
def fa_digits(text):
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


def fmt_num(value, decimals=0):
    """فرمت عدد با کاما و تعداد اعشار مشخص"""
    if value is None:
        return "—"
    try:
        if decimals == 0:
            return f"{int(round(value)):,}"
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def fmt_price(value, unit="toman"):
    """فرمت قیمت با واحد"""
    if value is None:
        return "—"
    
    # اگه عدد خیلی کوچیکه (کریپتو)، اعشار بیشتری نشون بده
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
    elif unit == "dirham":
        return f"{num} درهم"
    return num


def fmt_change(dp):
    """فرمت درصد تغییر"""
    if dp is None or dp == 0:
        return ""
    arrow = "🔺" if dp > 0 else "🔻"
    return f"{arrow} {fa_digits(f'{abs(dp):.2f}')}٪"


def fmt_change_m(change):
    """فرمت تغییر مبلغ به میلیون تومان"""
    if change is None or change == 0:
        return ""
    change_m = change / 1_000_000
    arrow = "🔺" if change > 0 else "🔻"
    return f"{arrow} {fa_digits(f'{abs(change_m):,.0f}')}م"


def short_name(name, max_len=35):
    """کوتاه کردن نام‌های طولانی"""
    if not name:
        return "—"
    if len(name) <= max_len:
        return name
    return name[:max_len-3] + "..."


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
            return True
        else:
            print(f"   ❌ خطا {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ استثنا: {e}")
        return False


def send_long(text, reply_markup=None):
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
            [{"text": "🌐 قیمتو", "url": CHANNEL_URL}]
        ]
    }


# ─────────── هدر و فوتر ───────────
def build_header(icon, title, is_daily=True):
    now = now_tehran()
    lines = [
        f"<b>{icon} {CHANNEL_NAME}</b>  |  <a href='{CHANNEL_URL}'>{CHANNEL_USERNAME}</a>",
        "━━━━━━━━━━━━━━━━━",
        "",
    ]
    if is_daily:
        lines.append(f"{title}")
        lines.append(f"📅 {fa_digits(now.strftime('%Y/%m/%d'))} — {fa_digits(now.strftime('%H:%M'))}")
    else:
        lines.append(f"{title}")
        lines.append(f"🕐 {fa_digits(now.strftime('%H:%M'))}")
    lines.append("")
    return "\n".join(lines)


def build_footer():
    return f"\n🌐 <a href='{CHANNEL_URL}'>قیمتو</a>  |  {CHANNEL_USERNAME}"


# ─────────── ساخت پیام‌ها ───────────
def build_gold_message(data, is_daily=True):
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_GOLD)
    
    lines = [build_header("🥇", intro, is_daily)]
    
    # طلا و سکه
    for key in ["geram18", "geram24", "mesghal", "sekeb", "sekee", "nim", "rob"]:
        if key in items and items[key].get('p') is not None:
            label, unit = GROUPS['gold']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            lines.append(f"▪️ {label}  ›  <b>{price}</b>")
    
    # انس جهانی
    if "ons" in items and items["ons"].get('p'):
        ons = items["ons"]
        price = fmt_price(ons['p'], "dollar")
        change = fmt_change(ons.get('dp', 0))
        lines.append("")
        lines.append(f"🌍 <b>انس جهانی طلا</b>")
        line = f"   {price}"
        if change:
            line += f"   {change}"
        lines.append(line)
    
    lines.append(build_footer())
    return "\n".join(lines)


def build_forex_message(data, is_daily=True):
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_FOREX)
    
    dollar = items.get("price_dollar_rl", {}).get('p', 0)
    dollar_str = fmt_price(dollar, "toman")
    
    lines = [build_header("💵", intro, is_daily)]
    lines.append(f"📌 دلار آزاد امروز: <b>{dollar_str}</b>")
    lines.append("")
    
    # ارزهای اصلی
    lines.append("<b>ارزهای اصلی</b>")
    for key in ["price_dollar_rl", "price_dollar_dt", "price_eur", "price_gbp"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['forex']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  {price}"
            if change:
                line += f"  {change}"
            lines.append(line)
    
    # ارزهای منطقه‌ای
    lines.append("")
    lines.append("<b>ارزهای منطقه‌ای</b>")
    for key in ["price_aed", "price_try", "price_sar", "price_kwd"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['forex']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            lines.append(f"▪️ {label}  ›  {price}")
    
    # سایر
    lines.append("")
    lines.append("<b>سایر ارزها</b>")
    for key in ["price_cny", "price_jpy", "price_chf"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['forex']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            lines.append(f"▪️ {label}  ›  {price}")
    
    lines.append(build_footer())
    return "\n".join(lines)


def build_crypto_message(data, is_daily=True):
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_CRYPTO)
    
    lines = [build_header("⚡️", intro, is_daily)]
    
    # BTC و ETH برجسته
    for key, symbol in [("crypto-bitcoin", "₿"), ("crypto-ethereum", "Ξ")]:
        if key in items and items[key].get('p'):
            item = items[key]
            label, unit = GROUPS['crypto']['symbols'][key]
            price = fmt_price(item['p'], unit)
            change = fmt_change(item.get('dp', 0))
            lines.append(f"{symbol} <b>{label}</b>  ›  {price}")
            if change:
                lines.append(f"    {change}")
            lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("<b>سایر ارزها</b>")
    
    others = [k for k in GROUPS['crypto']['symbols'] 
              if k not in ("crypto-bitcoin", "crypto-ethereum")]
    for key in others:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['crypto']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  {price}"
            if change:
                line += f"  {change}"
            lines.append(line)
    
    lines.append(build_footer())
    return "\n".join(lines)


def build_commodity_message(data, is_daily=True):
    if not data or 'data' not in data:
        return None

    items = data['data']
    intro = random.choice(INTROS_COMMODITY)
    
    lines = [build_header("🛢", intro, is_daily)]
    
    # انرژی
    lines.append("<b>انرژی</b>")
    for key in ["oil_brent", "energy_natural_gas"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['commodity']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  {price}"
            if change:
                line += f"  {change}"
            lines.append(line)
    
    # فلزات گرانبها
    lines.append("")
    lines.append("<b>فلزات گرانبها</b>")
    for key in ["silver", "silver_999", "platinum", "palladium"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['commodity']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  {price}"
            if change:
                line += f"  {change}"
            lines.append(line)
    
    # فلزات پایه
    lines.append("")
    lines.append("<b>فلزات پایه</b>")
    for key in ["copper", "aluminium"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['commodity']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            lines.append(f"▪️ {label}  ›  {price}")
    
    # کشاورزی
    lines.append("")
    lines.append("<b>محصولات کشاورزی</b>")
    for key in ["commodity_us_wheat", "commodity_corn", "commodity_us_coffee_c"]:
        if key in items and items[key].get('p'):
            label, unit = GROUPS['commodity']['symbols'][key]
            price = fmt_price(items[key]['p'], unit)
            change = fmt_change(items[key].get('dp', 0))
            line = f"▪️ {label}  ›  {price}"
            if change:
                line += f"  {change}"
            lines.append(line)
    
    lines.append(build_footer())
    return "\n".join(lines)


def build_domestic_message(data, max_items=15):
    if not data or 'items' not in data:
        return None

    items = [i for i in data['items']
             if i.get('status') == 'available' and i.get('priceMarket')]

    if not items:
        return None

    items.sort(key=lambda x: abs(x.get('change') or 0), reverse=True)
    items = items[:max_items]

    intro = random.choice(INTROS_DOMESTIC)
    lines = [build_header("🚗", intro, is_daily=True)]

    # گروه‌بندی بر اساس category
    by_category = {}
    for item in items:
        cat = item.get('category', 'سایر')
        by_category.setdefault(cat, []).append(item)

    for cat, cat_items in by_category.items():
        lines.append(f"<b>{cat}</b>")
        for item in cat_items:
            name = short_name(item.get('name', '—'), 38)
            price_m = item['priceMarket'] / 1_000_000
            change = item.get('change') or 0

            line = f"▪️ {name}  ›  <b>{fa_digits(f'{price_m:,.0f}')} م.ت</b>"

            if change and change != 0:
                line += f"  {fmt_change_m(change)}"
            lines.append(line)
        lines.append("")

    lines.append("💰 <i>قیمت‌ها به میلیون تومان</i>")
    lines.append(build_footer())

    return "\n".join(lines)


# ─────────── پیام‌های ساعتی ───────────
def build_hourly_updates(all_data, last_data):
    messages = []
    now = now_tehran()

    if not last_data:
        return []

    new_latest = (all_data.get('latest') or {}).get('data', {})
    old_latest = (last_data.get('latest') or {}).get('data', {})

    # طلا، ارز، کریپتو (ترکیبی)
    changes_by_group = {}

    for group_key, group_data in GROUPS.items():
        group_changes = []
        for key, (label, unit) in group_data['symbols'].items():
            if key in new_latest and key in old_latest:
                old_p = old_latest[key].get('p')
                new_p = new_latest[key].get('p')
                if old_p != new_p:
                    dp = new_latest[key].get('dp', 0)
                    price_str = fmt_price(new_p, unit)
                    change_str = fmt_change(dp)
                    group_changes.append((label, price_str, change_str))
        
        if group_changes:
            changes_by_group[group_key] = group_changes

    # ساخت پیام برای هر گروه
    icons = {"gold": "🥇", "forex": "💵", "crypto": "⚡️", "commodity": "🛢"}
    titles = {
        "gold": "طلا و سکه — به‌روزرسانی",
        "forex": "ارز — به‌روزرسانی",
        "crypto": "ارز دیجیتال — به‌روزرسانی",
        "commodity": "کالا — به‌روزرسانی",
    }

    for group_key, changes in changes_by_group.items():
        header = build_header(icons[group_key], titles[group_key], is_daily=False)
        lines = [header]
        for label, price, change in changes:
            line = f"▪️ {label}  ›  <b>{price}</b>"
            if change:
                line += f"  {change}"
            lines.append(line)
        lines.append(build_footer())
        messages.append("\n".join(lines))

    # خودروهای داخلی
    new_domestic = (all_data.get('domestic') or {}).get('items', [])
    old_domestic_map = {
        i.get('id', '') + str(i.get('rawPriceFactory', '')): i
        for i in (last_data.get('domestic') or {}).get('items', [])
    }

    domestic_changes = []
    for item in new_domestic:
        key = item.get('id', '') + str(item.get('rawPriceFactory', ''))
        old = old_domestic_map.get(key)
        if old and old.get('priceMarket') != item.get('priceMarket'):
            name = short_name(item.get('name', '—'), 38)
            price_m = item['priceMarket'] / 1_000_000
            change = item.get('change') or 0
            change_str = fmt_change_m(change)
            domestic_changes.append((name, price_m, change_str))

    if domestic_changes:
        header = build_header("🚗", "خودروهای داخلی — به‌روزرسانی", is_daily=False)
        lines = [header]
        for name, price_m, change_str in domestic_changes[:10]:
            line = f"▪️ {name}  ›  <b>{fa_digits(f'{price_m:,.0f}')} م.ت</b>"
            if change_str:
                line += f"  {change_str}"
            lines.append(line)
        lines.append(build_footer())
        messages.append("\n".join(lines))

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

    if is_daily:
        print("\n📤 ارسال گزارش روزانه...")
        messages = [
            ("طلا", build_gold_message(all_data.get('latest'), is_daily=True)),
            ("ارز", build_forex_message(all_data.get('latest'), is_daily=True)),
            ("کریپتو", build_crypto_message(all_data.get('latest'), is_daily=True)),
            ("کالا", build_commodity_message(all_data.get('latest'), is_daily=True)),
            ("خودرو", build_domestic_message(all_data.get('domestic'))),
        ]

        sent = 0
        for i, (name, msg) in enumerate(messages):
            if msg:
                print(f"\n📨 پیام {sent+1}: {name}")
                keyboard = make_keyboard() if i == len(messages) - 1 else None
                send_long(msg, keyboard)
                sent += 1
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

    save_state(all_data)
    print("\n✅ تمام شد")


if __name__ == '__main__':
    main()
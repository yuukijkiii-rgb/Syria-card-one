import logging
import json
import os
import uuid
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# تفعيل تسجيل الأحداث (Logging)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

PORT = 8000
CATEGORIES_FILE = "categoriehgs.json"
USERS_FILE = "useknrs.json"
BANNERS_FILE = "bannnkners.json"
SPLASH_FILE = "splasbjnh.json"
PRODUCTS_FILE = "prnnhjoducts.json"
SUBCATEGORIES_FILE = "subcannkktegories.json"
ORDERS_FILE = "ordernnos.json"
DEPOSIT_METHODS_FILE = "deopojsit_methods.json"
DEPOSIT_REQUESTS_FILE = "depojsit_lrequests.json"
PROVIDERS_FILE = "prokkviders.json"
CATEGORY_BANNERS_FILE = "categorym_bajknners.json"
SETTINGS_FILE = "sitem_sjettings.json"

# --------------------------------------------------
# إعدادات بوت التليجرام للإشعارات
# --------------------------------------------------
TELEGRAM_FAIL_BOT_TOKEN = "8809621979:AAGEwl5mXg7w8dfwNxWPqQitWRPFamhRA14"
TELEGRAM_PURCHASE_BOT_TOKEN = "8809621979:AAGEwl5mXg7w8dfwNxWPqQitWRPFamhRA14"
TELEGRAM_ADMIN_CHAT_ID = "8694276183"

def send_telegram_notification(product, subcategory, price, email, reason):
    if not TELEGRAM_FAIL_BOT_TOKEN or TELEGRAM_FAIL_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logging.warning("لم يتم ضبط توكن بوت التليجرام لإرسال الإشعار.")
        return

    message = (
        "فشل ارسال طلبApi\n"
        "تم الارسال للتشيك:\n"
        f"المنتج: {product}\n"
        f"الفئة: {subcategory}\n"
        f"السعر: {price} $\n"
        f"العميل: {email}\n"
        f"سبب الفشل: {reason}"
    )

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_FAIL_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": message
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(telegram_url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as res:
            logging.info("تم إرسال إشعار فشل الـ API إلى بوت التليجرام بنجاح.")
    except Exception as e:
        logging.error(f"فشل إرسال الإشعار للتليجرام: {e}")

def send_telegram_purchase_notification(product, subcategory, price, user_input, system_response, email, user_password, user_ip, current_balance, previous_balance):
    if not TELEGRAM_PURCHASE_BOT_TOKEN:
        logging.warning("لم يتم ضبط توكن بوت إشعارات الشراء.")
        return

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_PURCHASE_BOT_TOKEN}/sendMessage"
    headers = {"Content-Type": "application/json"}

    message_premium = (
        f'<tg-emoji emoji-id="5420323339723881652">🛒</tg-emoji> <b>تم شراء منتج جديد :</b>\n'
        f'<tg-emoji emoji-id="5458603043203327669">📦</tg-emoji> <b>اسم المنتج:</b> {product}\n'
        f'<tg-emoji emoji-id="5253742260054409879">🏷️</tg-emoji> <b>اسم الفئة:</b> {subcategory}\n'
        f'<tg-emoji emoji-id="5039789890133296083">💰</tg-emoji> <b>سعر الفئة:</b> {price} $\n'
        f'<tg-emoji emoji-id="5839437853469186962">📝</tg-emoji> <b>مدخلات المستخدم:</b> {user_input}\n'
        f'<tg-emoji emoji-id="5440660757194744323">⚙️</tg-emoji> <b>رد النظام التابع لطلب:</b> {system_response}\n'
        f'ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ\n'
        f'<tg-emoji emoji-id="5321244246705989720">📧</tg-emoji> <b>ايميل المستخدم:</b> {email}\n'
        f'<tg-emoji emoji-id="5296369303661067030">🔑</tg-emoji> <b>كلمة سر المستخدم:</b> {user_password}\n'
        f'<tg-emoji emoji-id="5287480366330816274">🌐</tg-emoji> <b>IP جهاز المستخدم:</b> {user_ip}\n'
        f'<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> <b>رصيده الان:</b> {current_balance} $\n'
        f'<tg-emoji emoji-id="5420323339723881652">💳</tg-emoji> <b>رصيده قبل طلب:</b> {previous_balance} $'
    )

    payload_premium = json.dumps({
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": message_premium,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(telegram_url, data=payload_premium, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as res:
            logging.info("تم إرسال إشعار الشراء بأسلوب ايموجي البريميوم بنجاح.")
            return
    except Exception as e:
        logging.warning(f"فشل إرسال ايموجي البريميوم المباشر ({e})، جاري المحاولة بالخيار المباشر لضمان وصول الرسالة...")

    message_standard = (
        f'🛒 <b>تم شراء منتج جديد :</b>\n'
        f'📦 <b>اسم المنتج:</b> {product}\n'
        f'🏷️ <b>اسم الفئة:</b> {subcategory}\n'
        f'💰 <b>سعر الفئة:</b> {price} $\n'
        f'📝 <b>مدخلات المستخدم:</b> {user_input}\n'
        f'⚙️ <b>رد النظام التابع لطلب:</b> {system_response}\n'
        f'ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ\n'
        f'📧 <b>ايميل المستخدم:</b> {email}\n'
        f'🔑 <b>كلمة سر المستخدم:</b> {user_password}\n'
        f'🌐 <b>IP جهاز المستخدم:</b> {user_ip}\n'
        f'💵 <b>رصيده الان:</b> {current_balance} $\n'
        f'💳 <b>رصيده قبل طلب:</b> {previous_balance} $'
    )

    payload_standard = json.dumps({
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": message_standard,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(telegram_url, data=payload_standard, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as res:
            logging.info("تم إرسال إشعار الشراء بنجاح بالخط العريض.")
    except Exception as e:
        logging.error(f"فشل إرسال إشعار الشراء للتليجرام بشكل كامل: {e}")

def send_telegram_price_update_notification(product, subcategory, old_price, new_price, old_api_price, new_api_price, provider_name):
    if not TELEGRAM_PURCHASE_BOT_TOKEN:
        return

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_PURCHASE_BOT_TOKEN}/sendMessage"
    headers = {"Content-Type": "application/json"}

    message = (
        f'<tg-emoji emoji-id="5420323339723881652">🔔</tg-emoji><b>تم تحديث سعر المنتج التالي:</b>\n'
        f'<tg-emoji emoji-id="5282843764451195532">📦</tg-emoji><b>المنتج:</b> {product}\n'
        f'<tg-emoji emoji-id="5300758536899276911">🏷️</tg-emoji><b>الفئة:</b> {subcategory}\n'
        f'<tg-emoji emoji-id="5800887979366944343">💰</tg-emoji><b>السعر القديم:</b> {old_price} $\n'
        f'<tg-emoji emoji-id="5800692549765042288">💵</tg-emoji><b>السعر الجديد:</b> {new_price} $\n'
        f'ــــــــــــــــــــــــــــــــــــــــ\n'
        f'<tg-emoji emoji-id="5220015831794067172">📉</tg-emoji><b>السعر القديم API:</b> {old_api_price} $\n'
        f'<tg-emoji emoji-id="5220149804708930165">📈</tg-emoji><b>السعر الجديد Api:</b> {new_api_price} $\n'
        f'<tg-emoji emoji-id="5249040662434685155">🌐</tg-emoji><b>اسم المزود:</b> {provider_name}\n'
        f'ــــــــــــــــــــــــــــــــــــــــ\n'
        f'تم تحديث السعر بنجاح <tg-emoji emoji-id="5769395067244517720">✅</tg-emoji>'
    )

    payload = json.dumps({
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(telegram_url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as res:
            logging.info("تم إرسال إشعار تحديث السعر عبر بوت التليجرام بنجاح.")
    except Exception as e:
        logging.error(f"فشل إرسال إشعار تحديث السعر للتليجرام: {e}")

# --------------------------------------------------
# 1. نظام الحفظ واسترجاع الدائم لـ JSON
# --------------------------------------------------
DEFAULT_CATEGORIES = {
    "قسم العاب": "",
    "قسم التطبيقات": "",
    "قسم رصيد": "",
    "قسم رشق": "",
    "قسم الاشتراكات": "",
    "قسم البريميوم": ""
}

DEFAULT_SETTINGS = {
    "about_us": "مرحباً بكم في SYRIA CARD ONE - منصتكم الرقمية المتكاملة لخدمات الشحن والبطاقات الرقمية.",
    "telegram_support": "",
    "whatsapp_support": "",
    "telegram_channel": "",
    "whatsapp_channel": ""
}

def load_json_file(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"خطأ في قراءة {file_path}: {e}")
            return default_data.copy() if isinstance(default_data, dict) else list(default_data)
    else:
        save_json_file(file_path, default_data)
        return default_data.copy() if isinstance(default_data, dict) else list(default_data)

def save_json_file(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"خطأ في كتابة {file_path}: {e}")

CATEGORIES_DATA = load_json_file(CATEGORIES_FILE, DEFAULT_CATEGORIES)
USERS_DATA = load_json_file(USERS_FILE, {})
BANNERS_DATA = load_json_file(BANNERS_FILE, [])
SPLASH_DATA = load_json_file(SPLASH_FILE, {"image": ""})
PRODUCTS_DATA = load_json_file(PRODUCTS_FILE, [])
SUBCATEGORIES_DATA = load_json_file(SUBCATEGORIES_FILE, [])
ORDERS_DATA = load_json_file(ORDERS_FILE, [])
DEPOSIT_METHODS_DATA = load_json_file(DEPOSIT_METHODS_FILE, [])
DEPOSIT_REQUESTS_DATA = load_json_file(DEPOSIT_REQUESTS_FILE, [])
PROVIDERS_DATA = load_json_file(PROVIDERS_FILE, [])
CATEGORY_BANNERS_DATA = load_json_file(CATEGORY_BANNERS_FILE, {})
SETTINGS_DATA = load_json_file(SETTINGS_FILE, DEFAULT_SETTINGS)

def make_api_request(url, token, timeout=12):
    headers = {
        'api-token': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))

# --------------------------------------------------
# صفحة وثائق الـ API
# --------------------------------------------------
API_DOCS_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>وثائق واجهة برمجة التطبيقات - SYRIA CARD ONE</title>
    <link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #09090b;
            --card: #121212;
            --border: #27272a;
            --accent: #38bdf8;
            --green: #4ade80;
            --text: #ffffff;
            --subtext: #a1a1aa;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Alexandria', sans-serif; }
        body { background-color: var(--bg); color: var(--text); padding: 20px; max-width: 900px; margin: 0 auto; line-height: 1.6; }
        header { border-bottom: 1px solid var(--border); padding-bottom: 15px; margin-bottom: 25px; }
        h1 { font-size: 1.5rem; color: var(--accent); margin-bottom: 5px; }
        .base-url { background: var(--card); border: 1px solid var(--border); padding: 12px; border-radius: 8px; margin-top: 10px; font-family: monospace; }
        .section { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .section-title { font-size: 1.1rem; color: var(--accent); margin-bottom: 12px; font-weight: 700; border-bottom: 1px solid #1f1f23; padding-bottom: 6px; }
        .method { display: inline-block; background: #16a34a; color: #fff; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; margin-left: 8px; }
        .endpoint { font-family: monospace; font-size: 0.9rem; color: var(--green); font-weight: 700; }
        pre { background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 12px; overflow-x: auto; font-family: monospace; font-size: 0.8rem; color: #38bdf8; margin-top: 8px; direction: ltr; text-align: left; }
        footer { text-align: center; font-size: 0.8rem; color: var(--subtext); margin-top: 30px; border-top: 1px solid var(--border); padding-top: 15px; }
    </style>
</head>
<body>
    <header>
        <h1>وثائق واجهة برمجة التطبيقات (API)</h1>
        <p style="color: var(--subtext); font-size: 0.9rem;">SYRIA CARD ONE - التوثيق الرسمي لخدمات الربط البرمجي</p>
        <div class="base-url">
            <b>عنوان URL الأساسي:</b> <span style="color: var(--accent);">https://api.tartousi-store1.com/client/api/</span>
        </div>
    </header>

    <div class="section">
        <div class="section-title">المصادقة مطلوبة</div>
        <p style="font-size: 0.85rem; color: var(--subtext);">قم بتضمين الترويسة التالية في جميع طلبات واجهة برمجة التطبيقات (API):</p>
        <pre>api-token: YOUR_API_TOKEN</pre>
    </div>

    <div class="section">
        <div class="section-title">حساب تعريفي</div>
        <div><span class="method">GET</span> <span class="endpoint">/client/api/profile</span></div>
        <p style="font-size: 0.85rem; color: var(--subtext); margin-top: 5px;">يسترجع رصيد المستخدم ومعلومات ملفه الشخصي.</p>
        <div style="font-size: 0.8rem; margin-top: 10px; color: var(--accent);">مثال على الاستجابة:</div>
<pre>{
    "الرصيد": 8788.683,
    "البريد الإلكتروني": "user@email.com"
}</pre>
    </div>

    <footer>
        © 2026 SYRIA CARD ONE - API Documentation. All rights reserved.
    </footer>
</body>
</html>
"""

# --------------------------------------------------
# 2. واجهة المستخدم العادية (تم تعديل الخط إلى Cairo)
# --------------------------------------------------
USER_HTML_CONTENT = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYRIA CARD ONE</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #050508;
            --card-bg: #121212;
            --border-color: #27272a;
            --accent-color: #38bdf8;
            --text-color: #ffffff;
            --subtext-color: #a1a1aa;
            --sidebar-bg: #09090f;
            --input-bg: #000000;
        }

        body.light-mode {
            --bg-color: #f4f4f5;
            --card-bg: #ffffff;
            --border-color: #e4e4e7;
            --accent-color: #0284c7;
            --text-color: #09090b;
            --subtext-color: #71717a;
            --sidebar-bg: #ffffff;
            --input-bg: #f4f4f5;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif !important;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 0 0 85px 0;
            max-width: 420px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            position: relative;
            min-height: 100vh;
        }

        #topNotification {
            position: fixed;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 380px;
            background-color: #dc2626;
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
            z-index: 10000;
            transition: top 0.4s ease-in-out;
        }

        #topNotification.show {
            top: 15px;
        }

        #greenCopyToast {
            position: fixed;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            max-width: 300px;
            background-color: #16a34a;
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(22, 163, 74, 0.4);
            z-index: 10000;
            transition: top 0.4s ease-in-out;
        }

        #greenCopyToast.show {
            top: 20px;
        }

        #splashScreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #000000;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 25px;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }

        #splashScreen.hidden {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }

        .splash-logo {
            width: 130px;
            height: 130px;
            object-fit: cover;
            border-radius: 50%;
            border: 2px solid var(--border-color);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        }

        .splash-spinner {
            width: 42px;
            height: 42px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
        }

        .btn-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0, 0, 0, 0.2);
            border-top: 2px solid #000;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            vertical-align: middle;
            margin-left: 6px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, #004d40 0%, #00897b 50%, #26a69a 100%);
            padding: 10px 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            width: 100%;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header-logo {
            width: 45px;
            height: 45px;
            border-radius: 8px;
            object-fit: cover;
            border: 1px solid rgba(255,255,255,0.3);
            background: #000;
        }

        .store-name {
            font-size: 1.05rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.5px;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .shield-icon {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
        }

        .add-balance-btn {
            background-color: #ffffff;
            color: #00897b;
            border-radius: 50%;
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1rem;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            border: none;
            text-decoration: none;
            transition: transform 0.1s ease;
        }
        .add-balance-btn:active {
            transform: scale(0.9);
        }

        .balance-text {
            font-size: 0.9rem;
            font-weight: 700;
            color: #ffffff;
            direction: ltr;
        }

        .menu-hamburger {
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 4px;
            width: 24px;
        }

        .menu-hamburger span {
            width: 100%;
            height: 3px;
            background-color: #ffffff;
            border-radius: 2px;
        }

        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
            z-index: 999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease;
        }

        .sidebar-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .sidebar {
            position: fixed;
            top: 0;
            right: -320px;
            width: 300px;
            height: 100vh;
            background-color: var(--sidebar-bg);
            border-left: 1px solid var(--border-color);
            z-index: 1000;
            transition: right 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            padding: 16px 14px;
            gap: 12px;
            overflow-y: auto;
            touch-action: pan-y;
        }

        .sidebar.active { right: 0; }

        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 0 5px;
        }

        .close-btn {
            background: transparent;
            border: none;
            color: var(--subtext-color);
            font-size: 1.5rem;
            cursor: pointer;
        }

        .guest-auth-card {
            background-color: #245831;
            border-radius: 26px;
            padding: 24px 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 12px;
            width: 100%;
            margin-bottom: 5px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.3);
        }

        .guest-auth-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.5px;
        }

        .guest-auth-desc {
            font-size: 0.85rem;
            color: #d1fae5;
            line-height: 1.5;
            font-weight: 500;
            margin-bottom: 4px;
        }

        .guest-btn-blue {
            width: 100%;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%);
            color: #ffffff;
            border: none;
            border-radius: 22px;
            padding: 11px 16px;
            font-size: 0.92rem;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
            transition: transform 0.1s ease, filter 0.2s ease;
        }
        .guest-btn-blue:active { transform: scale(0.97); }

        .guest-btn-google {
            width: 100%;
            background-color: #ffffff;
            color: #1f2937;
            border: none;
            border-radius: 22px;
            padding: 10px 16px;
            font-size: 0.9rem;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            transition: transform 0.1s ease;
        }
        .guest-btn-google:active { transform: scale(0.97); }

        .sidebar-profile-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            width: 100%;
            margin-bottom: 5px;
        }

        .sidebar-avatar {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-color);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
            background-color: var(--input-bg);
        }

        .sidebar-user-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            width: 100%;
        }

        .user-info-rect {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 4px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 3px;
            overflow: hidden;
        }

        .user-info-lbl { font-size: 0.65rem; color: var(--subtext-color); font-weight: 600; }
        .user-info-val { font-size: 0.72rem; color: var(--text-color); font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .sidebar-menu-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 100%;
        }

        .menu-nav-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 13px 18px;
            border-radius: 14px;
            color: var(--text-color);
            font-size: 0.92rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            background: transparent;
            border: none;
            text-align: right;
            text-decoration: none;
        }

        .menu-nav-item:hover { background: rgba(125, 125, 125, 0.1); }
        .menu-nav-item.active-home { 
            background-color: #3b3a4a !important; 
            color: #ffffff !important; 
            border-radius: 14px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
        }

        body.light-mode .menu-nav-item.active-home {
            background-color: #0284c7 !important;
            color: #ffffff !important;
        }

        .nav-icon { font-size: 1.15rem; display: flex; align-items: center; justify-content: center; width: 28px; }

        .dark-mode-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 14px;
            background: transparent;
            margin-top: 5px;
            border-top: 1px solid var(--border-color);
            padding-top: 16px;
        }

        .dark-mode-title { font-size: 0.95rem; font-weight: 700; color: var(--text-color); }

        .toggle-switch { position: relative; display: inline-block; width: 54px; height: 30px; }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .toggle-slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #383842; transition: .3s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 34px;
        }
        .toggle-slider:before {
            position: absolute; content: ""; height: 22px; width: 22px; left: 4px; bottom: 4px;
            background-color: #4ade80; transition: .3s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 50%;
        }
        input:checked + .toggle-slider { background-color: #2e593e; }
        input:checked + .toggle-slider:before { transform: translateX(24px); background-color: #4ade80; }

        .icon-home { color: #00e676; }        
        .icon-deposit { color: #38bdf8; }     
        .icon-payments { color: #3b82f6; }    
        .icon-wallet { color: #facc15; }      
        .icon-orders { color: #f87171; }      
        .icon-agents { color: #60a5fa; }      
        .icon-security { color: #34d399; }    
        .icon-verify { color: #2dd4bf; }      
        .icon-api { color: #4ade80; font-family: monospace; font-weight: 800; font-size: 0.85rem; } 
        .icon-about { color: #2dd4bf; }      
        .icon-support { color: #f472b6; }    

        .logout-btn-nav {
            margin-top: 8px;
            background: rgba(220, 38, 38, 0.12);
            color: #f87171 !important;
            border: 1px solid rgba(220, 38, 38, 0.3);
        }

        .bottom-nav-bar {
            position: fixed; 
            bottom: 0; 
            left: 0; 
            right: 0;
            width: 100%; 
            height: 62px;
            background: linear-gradient(135deg, #022c22 0%, #059669 50%, #0d9488 100%);
            border-radius: 0; 
            display: flex; 
            align-items: center; 
            justify-content: space-around;
            padding: 0 15px; 
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5); 
            z-index: 5000;
        }

        .bottom-nav-btn {
            background: transparent; border: none; color: #ffffff; display: flex;
            align-items: center; justify-content: center; cursor: pointer; width: 42px; height: 42px; border-radius: 50%; transition: all 0.2s ease;
        }
        .bottom-nav-btn:active { transform: scale(0.9); }

        .bottom-btn-pink { background-color: #f43f5e; width: 44px; height: 44px; border-radius: 50%; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.4); }
        .bottom-btn-gradient-search { background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%); width: 44px; height: 44px; border-radius: 50%; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4); }

        .form-input {
            width: 100%; padding: 12px; background-color: var(--input-bg); border: 1px solid var(--border-color);
            border-radius: 10px; color: var(--text-color); font-size: 0.85rem; outline: none;
        }
        .form-input:focus { border-color: #3b82f6; }

        .banner-container {
            width: 92%; margin: 10px auto 0 auto; height: 120px; background: var(--card-bg); border-radius: 12px;
            display: flex; align-items: center; justify-content: center; border: 1px solid var(--border-color); position: relative; overflow: hidden;
        }
        .banner-slide { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; opacity: 0; transition: opacity 0.5s ease-in-out; }
        .banner-slide.active { opacity: 1; }
        .banner-placeholder { font-size: 0.95rem; font-weight: 700; color: var(--text-color); }

        .ticker-wrapper { width: 92%; margin: 0 auto; background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 0; overflow: hidden; }
        .ticker-text { display: inline-block; white-space: nowrap; color: var(--accent-color); font-size: 0.85rem; font-weight: 700; animation: marquee 12s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

        .main-content-wrapper {
            padding: 0 15px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .section-header { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
        .back-btn {
            background-color: var(--card-bg); border: 1px solid var(--border-color); color: var(--accent-color);
            padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; cursor: pointer; display: none; white-space: nowrap;
        }

        .search-container { width: 100%; }
        .search-input {
            width: 100%; padding: 9px 12px; background-color: var(--card-bg); border: 1px solid var(--border-color);
            border-radius: 8px; color: var(--text-color); font-size: 0.8rem; outline: none; transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--accent-color); }

        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px 12px;
            padding: 10px 5px;
        }

        .item-card {
            background: transparent;
            border: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            cursor: pointer;
            overflow: visible;
            position: relative;
            transform: none;
            padding: 0;
            width: 100%;
        }

        .item-img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 14px;
            position: static;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            background-color: var(--card-bg);
            transition: transform 0.15s ease;
        }

        .item-card:active .item-img {
            transform: scale(0.95);
        }

        .item-label {
            width: 100%;
            background: transparent;
            border: none;
            padding: 6px 2px 0 2px;
            text-align: center;
            font-size: 0.82rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            z-index: 1;
        }

        .item-price-tag {
            font-size: 0.82rem;
            font-weight: 800;
            color: #4ade80;
            margin-top: 1px;
            direction: ltr;
            text-align: center;
        }

        #depositPage, #myOrdersPage, #myDepositsPage, #myWalletPage { display: none; flex-direction: column; gap: 14px; width: 100%; padding: 0 15px; }

        .wallet-cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            width: 100%;
            margin-top: 5px;
        }
        .wallet-stat-card {
            border-radius: 14px;
            padding: 16px 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .wallet-stat-card.green { background-color: #22c55e; color: #ffffff; }
        .wallet-stat-card.red { background-color: #ef4444; color: #ffffff; }
        .wallet-stat-card.purple { background-color: #a855f7; color: #ffffff; }
        .wallet-stat-card.teal { background-color: #14b8a6; color: #ffffff; }

        .wallet-stat-value { font-size: 1.4rem; font-weight: 800; direction: ltr; }
        .wallet-stat-label { font-size: 0.82rem; font-weight: 700; text-align: center; }

        .wallet-filters-row {
            display: flex; gap: 10px; width: 100%; margin-top: 5px;
        }
        .wallet-date-box {
            flex: 1; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 25px;
            padding: 8px 14px; display: flex; flex-direction: column; align-items: center;
        }
        .wallet-date-box label { font-size: 0.65rem; color: var(--subtext-color); font-weight: 700; margin-bottom: 2px; }
        .wallet-date-box input[type="date"] {
            background: transparent; border: none; color: var(--text-color); font-size: 0.8rem; font-weight: 700; outline: none; width: 100%; text-align: center;
        }

        .wallet-search-row { display: flex; align-items: center; gap: 10px; width: 100%; }
        .wallet-search-box {
            flex: 1; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 25px;
            padding: 10px 16px; display: flex; align-items: center;
        }
        .wallet-search-box input { background: transparent; border: none; color: var(--text-color); font-size: 0.85rem; outline: none; width: 100%; text-align: right; }
        .wallet-search-btn {
            width: 45px; height: 45px; background: #2dd4bf; border-radius: 50%; border: none; color: #ffffff;
            display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(45,212,191,0.3); flex-shrink: 0;
        }

        .wallet-empty-box {
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; padding: 40px 0; color: var(--subtext-color); font-weight: 700; font-size: 0.9rem;
        }

        .orders-header-title { font-size: 1.25rem; font-weight: 800; color: var(--text-color); text-align: left; margin-bottom: 5px; }
        .orders-date-filters { display: flex; gap: 10px; width: 100%; }
        .orders-date-box {
            flex: 1; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 25px;
            padding: 8px 14px; display: flex; flex-direction: column; align-items: center; position: relative;
        }
        .orders-date-box label { font-size: 0.65rem; color: var(--subtext-color); font-weight: 700; margin-bottom: 2px; }
        .orders-date-box input[type="date"] {
            background: transparent; border: none; color: var(--text-color); font-size: 0.82rem; font-weight: 700; outline: none; width: 100%; text-align: center;
        }

        .orders-search-row { display: flex; align-items: center; gap: 10px; width: 100%; margin-top: 5px; }
        .orders-search-box {
            flex: 1; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 25px;
            padding: 10px 16px; display: flex; align-items: center;
        }
        .orders-search-box input { background: transparent; border: none; color: var(--text-color); font-size: 0.85rem; outline: none; width: 100%; text-align: right; }
        .orders-search-icon-btn {
            width: 45px; height: 45px; background: #2dd4bf; border-radius: 50%; border: none; color: #ffffff;
            display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(45,212,191,0.3); flex-shrink: 0;
        }

        .orders-filters-group { display: flex; flex-direction: column; gap: 8px; margin-top: 5px; }
        .orders-filter-row { display: flex; gap: 8px; flex-wrap: wrap; }
        .filter-pill {
            background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px;
            padding: 6px 14px; font-size: 0.78rem; font-weight: 700; color: var(--subtext-color); cursor: pointer;
            display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
        }
        .filter-pill.active { background: #0284c7; color: #ffffff; border-color: #0284c7; }
        .filter-pill .pill-count { background: rgba(255,255,255,0.2); padding: 1px 6px; border-radius: 10px; font-size: 0.7rem; }

        .orders-bottom-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; gap: 10px; }
        .export-excel-btn {
            background: #0d9488; color: #ffffff; border: none; border-radius: 25px; padding: 10px 22px;
            font-size: 0.85rem; font-weight: 800; cursor: pointer; box-shadow: 0 4px 12px rgba(13,148,136,0.3);
        }
        .total-expense-pill {
            background: var(--card-bg); border: 1px solid #facc15; border-radius: 25px; padding: 8px 16px;
            font-size: 0.85rem; font-weight: 800; color: #facc15; display: inline-flex; align-items: center; gap: 5px; direction: ltr;
        }

        .orders-list { display: flex; flex-direction: column; gap: 10px; margin-top: 5px; }
        
        .order-card-exact {
            background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px;
            padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.25); cursor: pointer; transition: border-color 0.2s;
        }
        .order-card-exact:hover { border-color: var(--accent-color); }

        .order-card-right-exact { display: flex; flex-direction: column; align-items: flex-end; text-align: right; gap: 2px; }
        .order-id-exact { font-size: 0.85rem; font-weight: 800; color: var(--text-color); direction: ltr; }
        .order-subcat-exact { font-size: 0.82rem; font-weight: 700; color: var(--text-color); }
        .order-prod-exact { font-size: 0.72rem; color: var(--subtext-color); }

        .order-card-left-exact { display: flex; flex-direction: column; align-items: flex-start; text-align: left; gap: 2px; }
        .order-price-exact { font-size: 1rem; font-weight: 800; color: var(--text-color); direction: ltr; }
        .order-status-row-exact { display: flex; align-items: center; gap: 4px; font-size: 0.78rem; font-weight: 700; }
        .order-date-exact { font-size: 0.68rem; color: var(--subtext-color); direction: ltr; }
        .order-input-exact { font-size: 0.72rem; color: var(--subtext-color); direction: ltr; font-weight: 600; }

        .order-detail-row { display: flex; align-items: center; justify-content: space-between; font-size: 0.82rem; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
        .order-detail-row:last-child { border-bottom: none; }
        .order-detail-label { color: var(--subtext-color); font-weight: 600; font-size: 0.8rem; }
        .order-detail-value { color: var(--text-color); font-weight: 700; word-break: break-all; text-align: left; font-size: 0.85rem; }
        .order-detail-value.status-badge { padding: 4px 12px; border-radius: 6px; border: 1px solid; font-size: 0.8rem; }
        .status-accept { color: #4ade80; border-color: #4ade80; background: rgba(74, 222, 128, 0.1); }
        .status-pending { color: #f59e0b; border-color: #f59e0b; background: rgba(245, 158, 11, 0.1); }
        .status-reject { color: #f87171; border-color: #f87171; background: rgba(248, 113, 113, 0.1); }

        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(5px); z-index: 3000; display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; transition: opacity 0.3s ease;
        }
        .modal-overlay.active { opacity: 1; visibility: visible; }
        
        .modal-box {
            background-color: #121023; border: 1px solid rgba(217, 163, 62, 0.3); border-radius: 20px;
            width: 92%; max-width: 360px; padding: 22px; display: flex; flex-direction: column; gap: 16px; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }

        .purchase-top-row { display: flex; justify-content: space-between; align-items: center; width: 100%; }

        .purchase-price-badge {
            background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #d4af37 100%); color: #000000;
            padding: 8px 18px; border-radius: 30px; font-size: 1.05rem; font-weight: 800; box-shadow: 0 4px 15px rgba(218, 165, 32, 0.35); direction: ltr;
        }

        .purchase-title-box { display: flex; align-items: center; gap: 8px; color: #ffffff; font-size: 0.95rem; font-weight: 700; text-align: right; }

        .purchase-input-custom {
            width: 100%; padding: 14px 18px; background-color: #1a1730; border: 1px solid #2e2850; border-radius: 16px;
            color: #ffffff; font-size: 0.9rem; text-align: right; outline: none; transition: border-color 0.2s;
        }
        .purchase-input-custom::placeholder { color: #787494; }
        .purchase-input-custom:focus { border-color: #daa520; }

        .purchase-buttons-grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 12px; width: 100%; }

        .buy-btn-gold {
            background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #d4af37 100%); color: #000000;
            border: none; border-radius: 16px; padding: 12px; font-size: 1rem; font-weight: 800; cursor: pointer; text-align: center;
            box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3); transition: transform 0.1s;
        }
        .buy-btn-gold:active { transform: scale(0.96); }

        .cancel-btn-outline {
            background: transparent; color: #f87171; border: 1px solid #f87171; border-radius: 16px;
            padding: 12px; font-size: 1rem; font-weight: 700; cursor: pointer; text-align: center; transition: all 0.2s;
        }
        .cancel-btn-outline:active { transform: scale(0.96); }

        .purchase-notice-box { display: flex; align-items: flex-start; gap: 10px; background-color: #16132d; border-radius: 12px; padding: 12px; position: relative; }
        .purchase-notice-line { width: 3px; background-color: #daa520; border-radius: 3px; position: absolute; right: 0; top: 10px; bottom: 10px; }
        .purchase-notice-text { font-size: 0.8rem; color: #b0aec4; line-height: 1.5; text-align: right; padding-right: 8px; }

        .dep-desc-box { background-color: var(--input-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; font-size: 0.78rem; color: var(--subtext-color); line-height: 1.4; }
        .dep-code-box {
            background-color: var(--input-bg); border: 1px dashed var(--accent-color); border-radius: 8px;
            padding: 10px; font-size: 0.85rem; font-weight: 700; color: var(--text-color); text-align: center; cursor: pointer; word-break: break-all; user-select: all;
        }
        .dep-code-box:hover { background-color: rgba(56, 189, 248, 0.05); }

        .phone-input-wrapper { position: relative; width: 100%; }
        .phone-input-wrapper .form-input { padding-right: 45px; }
        .phone-prefix {
            position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: var(--subtext-color);
            font-size: 0.8rem; font-weight: 700; background: var(--input-bg); padding: 0 5px; border-left: 1px solid var(--border-color);
        }
    </style>
</head>
<body>

    <div id="topNotification">رصيدك غير كافي ياحجي</div>
    <div id="greenCopyToast">تم نسخ بنجاح</div>

    <div id="splashScreen">
        <img id="splashImg" src="" class="splash-logo" style="display:none;" />
        <div class="splash-spinner"></div>
    </div>

    <div class="header">
        <div class="header-right">
            <img id="headerLogoImg" class="header-logo" src="" alt="Logo" />
            <span class="store-name">SYRIA CARD ONE</span>
        </div>
        <div class="header-left">
            <div class="shield-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
                </svg>
            </div>
            <a href="javascript:void(0);" class="add-balance-btn" onclick="openDepositPage()" title="إضافة رصيد">+</a>
            <span class="balance-text" id="userBalance">0.000 $</span>
            <button class="menu-hamburger" onclick="toggleSidebar()">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </div>

    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <button class="close-btn" onclick="toggleSidebar()">&times;</button>
        </div>

        <div class="guest-auth-card" id="guestAuthCard">
            <span class="guest-auth-title">تسجيل الدخول</span>
            <span class="guest-auth-desc">قم بتسجيل الدخول وتمتع بتجربة شراء سهلة</span>
            <button class="guest-btn-blue" onclick="openAuthModal()">تسجيل الدخول</button>
            <button class="guest-btn-google" onclick="openAuthModal()">
                <span>تسجيل بواسطة غوغل</span>
                <svg width="20" height="20" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
            </button>
        </div>

        <div class="sidebar-profile-box" id="userProfileHeader" style="display:none;">
            <img id="sidebarLogoImg" class="sidebar-avatar" src="" />
            <div class="sidebar-user-grid">
                <div class="user-info-rect">
                    <span class="user-info-lbl">البريد الإلكتروني</span>
                    <span class="user-info-val" id="sbUserEmail">زائر</span>
                </div>
                <div class="user-info-rect">
                    <span class="user-info-lbl">رقم الحساب</span>
                    <span class="user-info-val" id="sbUserId" style="color:var(--accent-color);">#1000</span>
                </div>
            </div>
        </div>

        <div class="sidebar-menu-list" id="sidebarMenuList">
            <div class="menu-nav-item active-home" onclick="closeSidebarAndGoHome()">
                <span>الرئيسية</span>
                <span class="nav-icon icon-home">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;" onclick="openDepositPage()">
                <span>اضافة رصيد</span>
                <span class="nav-icon icon-deposit">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19 14V6c0-1.1-.9-2-2-2H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zm-9-1c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm13-6v11c0 1.1-.9 2-2 2H4v-2h17V7h2z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;" onclick="openMyDepositsPage()">
                <span>دفعاتي</span>
                <span class="nav-icon icon-payments">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4V8h16v10zm-10-7h8v2H10z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;" onclick="openMyWalletPage()">
                <span>محفظتي</span>
                <span class="nav-icon icon-wallet">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;" onclick="openMyOrdersPage()">
                <span>طلباتي</span>
                <span class="nav-icon icon-orders">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;">
                <span>وكلاؤنا</span>
                <span class="nav-icon icon-agents">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" style="display:none;">
                <span>الحماية</span>
                <span class="nav-icon icon-security">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item" id="sidebarApiItem" style="display:none;" onclick="openUserApiModal()">
                <span>API</span>
                <span class="nav-icon icon-api">API</span>
            </div>

            <div class="menu-nav-item" onclick="openAboutUsUserModal()">
                <span>من نحن</span>
                <span class="nav-icon icon-about">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item" id="supportNavItem" onclick="openSupportLinks()">
                <span>الدعم</span>
                <span class="nav-icon icon-support">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM6 10h2v2H6v-2zm10 0h2v2h-2v-2z"/></svg>
                </span>
            </div>

            <div class="menu-nav-item logged-in-item logout-btn-nav" style="display:none;" onclick="handleLogout()">
                <span>تسجيل الخروج</span>
                <span class="nav-icon" style="color:#f87171;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
                </span>
            </div>
        </div>

        <div class="dark-mode-item">
            <span class="dark-mode-title">الوضع الداكن</span>
            <label class="toggle-switch">
                <input type="checkbox" id="darkModeToggle" checked onchange="toggleDarkMode(this.checked)">
                <span class="toggle-slider"></span>
            </label>
        </div>
    </div>

    <div class="modal-overlay" id="authModal">
        <div class="modal-box">
            <div style="font-size:1.1rem; font-weight:800; text-align:center; color:#3b82f6; margin-bottom:5px;">تسجيل الدخول</div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <input type="email" id="modalUserEmail" class="form-input" placeholder="البريد الإلكتروني..." required>
                <div class="phone-input-wrapper">
                    <span class="phone-prefix">+963</span>
                    <input type="text" id="modalUserPhone" class="form-input" placeholder="رقم الهاتف..." required>
                </div>
                <input type="password" id="modalUserPassword" class="form-input" placeholder="كلمة السر..." required>
            </div>
            <div class="purchase-buttons-grid" style="margin-top:5px;">
                <button class="cancel-btn-outline" onclick="closeAuthModal()">إلغاء</button>
                <button class="buy-btn-gold" style="background:#2563eb; color:#fff;" onclick="handleModalLogin()">دخول</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="aboutUsUserModal">
        <div class="modal-box">
            <div style="font-size:1.1rem; font-weight:800; text-align:center; color:var(--accent-color); border-bottom:1px solid var(--border-color); padding-bottom:8px;">من نحن</div>
            <div id="aboutUsUserContent" style="font-size:0.88rem; color:#e4e4e7; line-height:1.7; text-align:right; white-space:pre-line; max-height:60vh; overflow-y:auto; padding:5px 0;">
                جاري التحميل...
            </div>
            <button class="buy-btn-gold" style="margin-top:5px; width:100%;" onclick="closeAboutUsUserModal()">إغلاق</button>
        </div>
    </div>

    <div class="bottom-nav-bar">
        <button class="bottom-nav-btn bottom-btn-gradient-search" onclick="focusSearchInput()" title="بحث">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </button>
        <button class="bottom-nav-btn bottom-btn-pink" onclick="openMyOrdersPage()" title="السلة والطلبات">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/></svg>
        </button>
        <button class="bottom-nav-btn" onclick="showTopNotification('لا توجد إشعارات جديدة')" title="الإشعارات">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>
        </button>
        <button class="bottom-nav-btn" onclick="openMyWalletPage()" title="المحفظة">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>
        </button>
        <button class="bottom-nav-btn" onclick="closeSidebarAndGoHome()" title="الرئيسية">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
        </button>
    </div>

    <div class="banner-container" id="bannerContainer">
        <div class="banner-placeholder">مكان البنر الإعلاني</div>
    </div>

    <div class="ticker-wrapper" id="tickerWrapper">
        <div class="ticker-text">عالمك الرقمي الكامل صُمم لك خصيصاً</div>
    </div>

    <div class="main-content-wrapper">
        <div id="shopMainSection">
            <div class="section-header">
                <div class="search-container" id="searchContainer">
                    <input type="text" id="searchInput" class="search-input" placeholder="ابحث هنا..." oninput="handleSearch()">
                </div>
                <button class="back-btn" id="backBtn" onclick="goBack()">رجوع</button>
            </div>
            <div class="grid-container" id="userGrid"></div>
        </div>
    </div>

    <div id="depositPage">
        <div class="section-header">
            <span style="font-size:0.95rem; font-weight:800; color:var(--accent-color);">طرق الإيداع المتاحة</span>
            <button class="back-btn" style="display:block;" onclick="closeDepositPage()">رجوع للمتجر</button>
        </div>
        <div class="search-container">
            <input type="text" id="depositSearchInput" class="search-input" placeholder="ابحث عن طريقة إيداع..." oninput="renderDepositMethods()">
        </div>
        <div class="grid-container" id="depositMethodsGrid"></div>
    </div>

    <div id="myDepositsPage">
        <div class="section-header">
            <span style="font-size:0.95rem; font-weight:800; color:var(--accent-color);">سجل ايداعاتي</span>
            <button class="back-btn" style="display:block;" onclick="closeMyDepositsPage()">رجوع للمتجر</button>
        </div>
        <div class="orders-list" id="myDepositsList"></div>
    </div>

    <div id="myWalletPage">
        <div class="orders-header-title">Wallet</div>
        
        <div class="wallet-cards-grid">
            <div class="wallet-stat-card green">
                <span class="wallet-stat-value" id="walletBalanceVal">0$</span>
                <span class="wallet-stat-label">رصيدك</span>
            </div>
            <div class="wallet-stat-card red">
                <span class="wallet-stat-value" id="walletPurchasesVal">0$</span>
                <span class="wallet-stat-label">إجمالي المشتريات</span>
            </div>
            <div class="wallet-stat-card purple">
                <span class="wallet-stat-value" id="walletReceivedVal">0$</span>
                <span class="wallet-stat-label">الوارد</span>
            </div>
            <div class="wallet-stat-card teal">
                <span class="wallet-stat-value" id="walletDebitVal">0$</span>
                <span class="wallet-stat-label">الرصيد المدين</span>
            </div>
        </div>

        <div class="wallet-filters-row">
            <div class="wallet-date-box">
                <label>إلى</label>
                <input type="date" id="walletDateTo">
            </div>
            <div class="wallet-date-box">
                <label>من</label>
                <input type="date" id="walletDateFrom">
            </div>
        </div>

        <div class="wallet-search-row">
            <button class="wallet-search-btn" onclick="renderMyWallet()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </button>
            <div class="wallet-search-box">
                <input type="text" id="walletSearchInput" placeholder="بحث" oninput="renderMyWallet()">
            </div>
        </div>

        <div class="wallet-empty-box">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
            <span>لا توجد عناصر</span>
        </div>
    </div>

    <div id="myOrdersPage">
        <div class="orders-header-title">الطلبات</div>
        
        <div class="orders-date-filters">
            <div class="orders-date-box">
                <label>إلى</label>
                <input type="date" id="orderDateTo" onchange="renderMyOrders()">
            </div>
            <div class="orders-date-box">
                <label>من</label>
                <input type="date" id="orderDateFrom" onchange="renderMyOrders()">
            </div>
        </div>

        <div class="orders-search-row">
            <button class="orders-search-icon-btn" onclick="renderMyOrders()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </button>
            <div class="orders-search-box">
                <input type="text" id="ordersSearchInput" placeholder="بحث" oninput="renderMyOrders()">
            </div>
        </div>

        <div class="orders-filters-group">
            <div class="orders-filter-row" id="statusFilterRow">
                <div class="filter-pill active" onclick="setOrderStatusFilter('all', this)">الكل <span class="pill-count" id="countAll">0</span></div>
                <div class="filter-pill" onclick="setOrderStatusFilter('changed', this)">تغيرت حالتها <span class="pill-count" id="countChanged">0</span></div>
                <div class="filter-pill" onclick="setOrderStatusFilter('accept', this)">مقبول <span class="pill-count" id="countAccept">0</span></div>
            </div>
            <div class="orders-filter-row" id="typeFilterRow">
                <div class="filter-pill active" onclick="setOrderTypeFilter('all', this)">الكل <span class="pill-count" id="typeCountAll">0</span></div>
                <div class="filter-pill" onclick="setOrderTypeFilter('manual', this)">يدوي <span class="pill-count" id="typeCountManual">0</span></div>
                <div class="filter-pill" onclick="setOrderTypeFilter('api', this)">API <span class="pill-count" id="typeCountApi">0</span></div>
            </div>
        </div>

        <div class="orders-bottom-bar">
            <button class="export-excel-btn" onclick="alert('جاري تصدير الملف...')">تصدير اكسل</button>
            <div class="total-expense-pill">
                <span>اجمالي :</span>
                <span id="totalExpensesVal">0.000 $</span>
            </div>
        </div>

        <div class="orders-list" id="myOrdersList" style="margin-top:10px;"></div>
    </div>

    <div class="modal-overlay" id="orderDetailModal">
        <div class="modal-box">
            <div class="modal-title">تفاصيل الطلب</div>
            <div class="order-detail-row">
                <span class="order-detail-label">رقم الطلب</span>
                <span class="order-detail-value" id="detailOrderId" style="direction:ltr;">-</span>
            </div>
            <div class="order-detail-row">
                <span class="order-detail-label">المنتج</span>
                <span class="order-detail-value" id="detailProduct" style="direction:ltr;">-</span>
            </div>
            <div class="order-detail-row">
                <span class="order-detail-label">الفئة</span>
                <span class="order-detail-value" id="detailSubcategory">-</span>
            </div>
            <div class="order-detail-row">
                <span class="order-detail-label">السعر</span>
                <span class="order-detail-value" id="detailPrice" style="color:#4ade80;">-</span>
            </div>
            <div class="order-detail-row">
                <span class="order-detail-label">المدخلات</span>
                <span class="order-detail-value" id="detailInput">-</span>
            </div>
            <div class="order-detail-row">
                <span class="order-detail-label">حالة الطلب</span>
                <span class="order-detail-value status-badge" id="detailStatus">-</span>
            </div>
            <button class="cancel-btn-outline" style="margin-top:10px; width:100%;" onclick="closeOrderDetailModal()">إغلاق</button>
        </div>
    </div>

    <div class="modal-overlay" id="purchaseModal">
        <div class="modal-box">
            <div class="purchase-top-row">
                <div class="purchase-price-badge" id="pModalPrice">0 $</div>
                <div class="purchase-title-box">
                    <span id="pModalTitle">عنوان الفئة</span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                </div>
            </div>

            <input type="text" id="pModalRequirement" class="purchase-input-custom" placeholder="ايدي المستخدم" />

            <div class="purchase-buttons-grid">
                <button class="cancel-btn-outline" id="cancelPurchaseBtn" onclick="closePurchaseModal()">الغاء</button>
                <button class="buy-btn-gold" id="submitPurchaseBtn" onclick="submitPurchase()">شراء</button>
            </div>

            <div class="purchase-notice-box">
                <div class="purchase-notice-line"></div>
                <div class="purchase-notice-text" id="pModalDescriptionText">
                    😲 هذا المنتج يعمل بشكل يدوي ويستغرق بعض الوقت ليصل للزبون
                </div>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="userApiModal">
        <div class="modal-box">
            <div style="font-size:0.95rem; font-weight:700; text-align:center; border-bottom:1px solid var(--border-color); padding-bottom:8px; color:var(--accent-color);">إعدادات الـ API</div>
            <div style="display:flex; flex-direction:column; gap:4px; margin-top:5px;">
                <label style="font-size:0.75rem; color:var(--subtext-color);">توكن الـ API (32 حرف):</label>
                <div class="dep-code-box" id="userApiTokenBox" onclick="copyUserApiToken()" style="letter-spacing:1px; font-family:monospace; font-size:0.75rem;">-</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:4px; margin-top:5px;">
                <label style="font-size:0.75rem; color:var(--subtext-color);">رابط API:</label>
                <div class="dep-code-box" id="userApiUrlBox" onclick="copyUserApiUrl()" style="font-size:0.75rem;">https://api.tartousi-store1.com/client/api/</div>
            </div>
            <button class="cancel-btn-outline" style="margin-top:10px; width:100%;" onclick="closeUserApiModal()">إغلاق</button>
        </div>
    </div>

    <div class="modal-overlay" id="depositDetailModal">
        <div class="modal-box">
            <div style="font-size:0.95rem; font-weight:700; text-align:center; border-bottom:1px solid var(--border-color); padding-bottom:8px; color:var(--accent-color);" id="depModalTitle">تفاصيل طريقة الإيداع</div>
            <div class="dep-desc-box" id="depModalDesc">الوصف الخاص بالطريقة</div>
            <div class="dep-code-box" id="depModalCode" onclick="copyDepositCode()">انقر هنا لنسخ كود الدفع</div>
            <div style="display:flex; flex-direction:column; gap:8px; margin-top:5px;">
                <input type="number" id="depAmountInput" class="purchase-input-custom" placeholder="المبلغ المحول" step="0.01">
                <input type="text" id="depTxIdInput" class="purchase-input-custom" placeholder="رقم عملية تحويل">
                <div style="display:flex; flex-direction:column; gap:4px;">
                    <label style="font-size:0.7rem; color:var(--subtext-color);">صورة اشعار التحويل:</label>
                    <input type="file" id="depReceiptImageInput" accept="image/*" class="purchase-input-custom">
                </div>
            </div>
            <div class="purchase-buttons-grid" style="margin-top:5px;">
                <button class="cancel-btn-outline" onclick="closeDepositDetailModal()">إلغاء</button>
                <button class="buy-btn-gold" onclick="submitDepositRequest()">إرسال طلب الإيداع</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="receiptModal">
        <div class="modal-box">
            <div style="font-size:0.95rem; font-weight:700; text-align:center; border-bottom:1px solid var(--border-color); padding-bottom:8px; color:var(--accent-color);">تفاصيل طلب الشراء</div>
            <div class="order-detail-row"><span class="order-detail-label">المنتج:</span><span class="order-detail-value" id="rProduct">-</span></div>
            <div class="order-detail-row"><span class="order-detail-label">الفئة:</span><span class="order-detail-value" id="rSubCategory">-</span></div>
            <div class="order-detail-row"><span class="order-detail-label">السعر:</span><span class="order-detail-value" id="rPrice" style="color:#4ade80;">-</span></div>
            <div class="order-detail-row"><span class="order-detail-label">المدخلات:</span><span class="order-detail-value" id="rInputs">-</span></div>
            <div class="order-detail-row"><span class="order-detail-label">حالة طلب:</span><span class="order-detail-value status-badge" id="rStatus">قيد الانتظار</span></div>
            <button class="buy-btn-gold" style="margin-top:10px; width:100%;" onclick="closeReceiptModal()">موافق</button>
        </div>
    </div>

    <script>
        let currentLevel = 'categories';
        let selectedCategory = '';
        let selectedProduct = '';
        let activeSubCategory = null;
        let activeDepositMethod = null;
        let currentStatusFilter = 'all';
        let currentTypeFilter = 'all';

        let dataStore = {
            categories: {},
            products: [],
            subcategories: [],
            depositMethods: [],
            userOrders: [],
            userDeposits: [],
            categoryBanners: {}
        };

        let touchStartX = 0;
        let touchCurrentX = 0;
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        document.addEventListener('touchstart', e => {
            touchStartX = e.touches[0].clientX;
        }, {passive: true});

        document.addEventListener('touchmove', e => {
            touchCurrentX = e.touches[0].clientX;
            let diffX = touchCurrentX - touchStartX;

            if (!sidebar.classList.contains('active') && touchStartX < 35 && diffX > 50) {
                toggleSidebar();
            }
            else if (sidebar.classList.contains('active') && diffX < -50) {
                toggleSidebar();
            }
        }, {passive: true});

        function focusSearchInput() {
            closeDepositPage();
            closeMyOrdersPage();
            closeMyDepositsPage();
            closeMyWalletPage();
            const input = document.getElementById('searchInput');
            if (input) {
                input.focus();
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        function toggleDarkMode(isDark) {
            if (isDark) {
                document.body.classList.remove('light-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
            }
        }

        function initTheme() {
            const savedTheme = localStorage.getItem('theme');
            const toggleBtn = document.getElementById('darkModeToggle');
            if (savedTheme === 'light') {
                document.body.classList.add('light-mode');
                if (toggleBtn) toggleBtn.checked = false;
            } else {
                document.body.classList.remove('light-mode');
                if (toggleBtn) toggleBtn.checked = true;
            }
        }

        function formatBalance(num) {
            const parsed = parseFloat(num);
            if (isNaN(parsed)) return "0.000";
            return Number(parsed.toFixed(3)).toString();
        }

        function showTopNotification(text) {
            const notif = document.getElementById('topNotification');
            notif.innerText = text;
            notif.classList.add('show');
            setTimeout(() => { notif.classList.remove('show'); }, 3000);
        }

        function showGreenCopyToast() {
            const toast = document.getElementById('greenCopyToast');
            toast.classList.add('show');
            setTimeout(() => { toast.classList.remove('show'); }, 2000);
        }

        function generateRandom32CharToken() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let token = '';
            for (let i = 0; i < 32; i++) {
                token += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            return token;
        }

        function updateSidebarVisibility(isLoggedIn) {
            const guestCard = document.getElementById('guestAuthCard');
            const profileBox = document.getElementById('userProfileHeader');
            const loggedInItems = document.querySelectorAll('.logged-in-item');
            
            if (isLoggedIn) {
                guestCard.style.display = 'none';
                profileBox.style.display = 'flex';
                loggedInItems.forEach(el => el.style.display = 'flex');
            } else {
                guestCard.style.display = 'flex';
                profileBox.style.display = 'none';
                loggedInItems.forEach(el => el.style.display = 'none');
            }
        }

        function openAuthModal() {
            document.getElementById('modalUserEmail').value = '';
            document.getElementById('modalUserPhone').value = '';
            document.getElementById('modalUserPassword').value = '';
            document.getElementById('authModal').classList.add('active');
        }

        function closeAuthModal() {
            document.getElementById('authModal').classList.remove('active');
        }

        async function handleModalLogin() {
            const email = document.getElementById('modalUserEmail').value.trim();
            const phone = document.getElementById('modalUserPhone').value.trim();
            const password = document.getElementById('modalUserPassword').value.trim();
            
            if (!email || !phone || !password) {
                alert('يرجى تعبئة جميع الحقول!');
                return;
            }
            
            await loginUser(email, phone, password);
            closeAuthModal();
        }

        function handleLogout() {
            localStorage.removeItem('loggedInUserEmail');
            localStorage.removeItem('loggedInUserPhone');
            document.getElementById('userBalance').innerText = '0.000 $';
            document.getElementById('sbUserEmail').innerText = 'زائر';
            document.getElementById('sbUserId').innerText = '#1000';
            updateSidebarVisibility(false);
            toggleSidebar();
        }

        async function openAboutUsUserModal() {
            if (document.getElementById('sidebar').classList.contains('active')) {
                toggleSidebar();
            }
            const modal = document.getElementById('aboutUsUserModal');
            const content = document.getElementById('aboutUsUserContent');
            content.innerText = 'جاري التحميل...';
            modal.classList.add('active');

            try {
                const res = await fetch('/api/get_site_settings');
                const settings = await res.json();
                content.innerText = settings.about_us || 'أهلاً بكم في متجرنا الرقمي المتكامل!';
            } catch (e) {
                content.innerText = 'أهلاً بكم في متجرنا الرقمي المتكامل!';
            }
        }

        function closeAboutUsUserModal() {
            document.getElementById('aboutUsUserModal').classList.remove('active');
        }

        async function openSupportLinks() {
            if (document.getElementById('sidebar').classList.contains('active')) {
                toggleSidebar();
            }
            
            try {
                const res = await fetch('/api/get_site_settings');
                const settings = await res.json();
                
                let supportLinks = [];
                
                if (settings.telegram_support) {
                    supportLinks.push({
                        name: 'تلغرام (دعم)',
                        url: `https://t.me/${settings.telegram_support.replace('@', '')}`,
                        icon: '✈️'
                    });
                }
                
                if (settings.whatsapp_support) {
                    supportLinks.push({
                        name: 'واتساب (دعم)',
                        url: `https://wa.me/${settings.whatsapp_support.replace(/[^0-9]/g, '')}`,
                        icon: '💬'
                    });
                }
                
                if (settings.telegram_channel) {
                    supportLinks.push({
                        name: 'قناة تلغرام',
                        url: `https://t.me/${settings.telegram_channel.replace('@', '')}`,
                        icon: '📢'
                    });
                }
                
                if (settings.whatsapp_channel) {
                    supportLinks.push({
                        name: 'قناة واتساب',
                        url: settings.whatsapp_channel,
                        icon: '📱'
                    });
                }
                
                if (supportLinks.length === 0) {
                    alert('لا توجد وسائل دعم متاحة حالياً');
                    return;
                }
                
                let linksHTML = supportLinks.map(link => 
                    `<a href="${link.url}" target="_blank" style="display:block; padding:12px; background-color:var(--card-bg); border:1px solid var(--border-color); border-radius:8px; margin:8px 0; color:var(--text-color); text-decoration:none; font-weight:700; text-align:center;">
                        ${link.icon} ${link.name}
                    </a>`
                ).join('');
                
                const tempModal = document.createElement('div');
                tempModal.className = 'modal-overlay active';
                tempModal.style.position = 'fixed';
                tempModal.style.top = '0';
                tempModal.style.left = '0';
                tempModal.style.width = '100vw';
                tempModal.style.height = '100vh';
                tempModal.style.background = 'rgba(0, 0, 0, 0.85)';
                tempModal.style.backdropFilter = 'blur(5px)';
                tempModal.style.zIndex = '9999';
                tempModal.style.display = 'flex';
                tempModal.style.alignItems = 'center';
                tempModal.style.justifyContent = 'center';
                
                tempModal.innerHTML = `
                    <div style="background-color:#121023; border:1px solid rgba(217, 163, 62, 0.3); border-radius:20px; width:92%; max-width:360px; padding:22px; display:flex; flex-direction:column; gap:16px; position:relative; box-shadow:0 10px 30px rgba(0,0,0,0.6);">
                        <div style="font-size:1.1rem; font-weight:800; text-align:center; color:var(--accent-color); border-bottom:1px solid var(--border-color); padding-bottom:8px;">وسائل الدعم</div>
                        ${linksHTML}
                        <button onclick="this.parentElement.parentElement.remove()" style="background:transparent; color:#f87171; border:1px solid #f87171; border-radius:16px; padding:12px; font-size:1rem; font-weight:700; cursor:pointer; text-align:center;">إغلاق</button>
                    </div>
                `;
                
                document.body.appendChild(tempModal);
                
                tempModal.addEventListener('click', (e) => {
                    if (e.target === tempModal) {
                        tempModal.remove();
                    }
                });
                
            } catch (e) {
                alert('حدث خطأ في تحميل معلومات الدعم');
                console.error(e);
            }
        }

        function openUserApiModal() {
            toggleSidebar();
            const savedEmail = localStorage.getItem('loggedInUserEmail');
            if (!savedEmail) { 
                alert('يرجى تسجيل الدخول أولاً!'); 
                return; 
            }

            let userToken = localStorage.getItem('api_token_32_' + savedEmail);
            if (!userToken) {
                userToken = generateRandom32CharToken();
                localStorage.setItem('api_token_32_' + savedEmail, userToken);
            }

            document.getElementById('userApiTokenBox').innerText = userToken;
            document.getElementById('userApiUrlBox').innerText = "https://api.tartousi-store1.com/client/api/";
            document.getElementById('userApiModal').classList.add('active');
        }

        function closeUserApiModal() { document.getElementById('userApiModal').classList.remove('active'); }

        function copyUserApiToken() {
            const token = document.getElementById('userApiTokenBox').innerText;
            if (token && token !== '-') {
                navigator.clipboard.writeText(token).then(() => { showGreenCopyToast(); });
            }
        }

        function copyUserApiUrl() {
            const url = document.getElementById('userApiUrlBox').innerText.trim();
            if (url) {
                navigator.clipboard.writeText(url).then(() => { showGreenCopyToast(); });
            }
        }

        async function initData() {
            try {
                const [cRes, pRes, sRes, dRes, cbRes] = await Promise.all([
                    fetch('/api/categories'),
                    fetch('/api/products'),
                    fetch('/api/subcategories'),
                    fetch('/api/get_deposit_methods'),
                    fetch('/api/category_banners')
                ]);
                dataStore.categories = await cRes.json();
                dataStore.products = await pRes.json();
                dataStore.subcategories = await sRes.json();
                dataStore.depositMethods = await dRes.json();
                dataStore.categoryBanners = await cbRes.json();
            } catch (e) { console.error(e); }
            renderCategories();
        }

        async function loadSplashScreen() {
            const res = await fetch('/api/splash');
            const data = await res.json();
            const splashImg = document.getElementById('splashImg');
            const sidebarImg = document.getElementById('sidebarLogoImg');
            const headerLogoImg = document.getElementById('headerLogoImg');

            if (data.image) {
                splashImg.src = data.image;
                splashImg.style.display = 'block';
                sidebarImg.src = data.image;
                headerLogoImg.src = data.image;
            } else {
                headerLogoImg.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='50' height='50'%3E%3Crect width='50' height='50' fill='%23222'/%3E%3Ctext x='50%25' y='50%25' fill='%23fff' font-size='12' text-anchor='middle' dominant-baseline='middle'%3ELogo%3C/text%3E%3C/svg%3E";
            }

            setTimeout(() => { document.getElementById('splashScreen').classList.add('hidden'); }, 2200);
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('sidebarOverlay').classList.toggle('active');
        }

        function closeSidebarAndGoHome() {
            if (document.getElementById('sidebar').classList.contains('active')) { toggleSidebar(); }
            closeDepositPage();
            closeMyOrdersPage();
            closeMyDepositsPage();
            closeMyWalletPage();
            renderCategories();
        }

        async function loginUser(email, phone, password) {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, phone: phone, password: password })
            });

            const data = await res.json();
            if (data.status === 'success') {
                localStorage.setItem('loggedInUserEmail', email);
                localStorage.setItem('loggedInUserPhone', phone);
                applyLoggedInState(email, data.balance, data.user_id);
                updateSidebarVisibility(true);
            } else {
                alert(data.message || 'حدث خطأ في تسجيل الدخول!');
            }
        }

        function applyLoggedInState(email, balance, userId) {
            const balanceElem = document.getElementById('userBalance');
            balanceElem.innerText = formatBalance(balance) + " $";

            document.getElementById('sbUserEmail').innerText = email;
            document.getElementById('sbUserId').innerText = "#" + (userId || '1001');
            
            // تحديث حالة زر الـ API بناءً على صلاحية المستخدم
            fetch('/api/get_balance?email=' + encodeURIComponent(email))
                .then(r => r.json())
                .then(d => {
                    const apiItem = document.getElementById('sidebarApiItem');
                    if (apiItem) {
                        apiItem.style.display = (d.api_enabled) ? 'flex' : 'none';
                    }
                }).catch(() => {});
            
            updateSidebarVisibility(true);
        }

        async function checkSavedSession() {
            const savedEmail = localStorage.getItem('loggedInUserEmail');
            if (savedEmail) {
                try {
                    const res = await fetch('/api/get_balance?email=' + encodeURIComponent(savedEmail));
                    const data = await res.json();
                    if (data.status === "success") {
                        applyLoggedInState(savedEmail, data.balance, data.user_id);
                        updateSidebarVisibility(true);
                    } else {
                        localStorage.removeItem('loggedInUserEmail');
                        localStorage.removeItem('loggedInUserPhone');
                        updateSidebarVisibility(false);
                    }
                } catch (e) { 
                    console.error(e);
                    updateSidebarVisibility(false);
                }
            } else {
                updateSidebarVisibility(false);
            }
        }

        async function loadBanners() {
            const res = await fetch('/api/banners');
            const banners = await res.json();
            const container = document.getElementById('bannerContainer');

            if (banners.length > 0) {
                container.style.display = 'flex';
                container.innerHTML = '';
                banners.forEach((img, idx) => {
                    const slide = document.createElement('img');
                    slide.src = img;
                    slide.className = 'banner-slide' + (idx === 0 ? ' active' : '');
                    container.appendChild(slide);
                });

                if (banners.length > 1) {
                    let current = 0;
                    setInterval(() => {
                        const slides = container.querySelectorAll('.banner-slide');
                        if (slides.length > 0) {
                            slides[current].classList.remove('active');
                            current = (current + 1) % slides.length;
                            slides[current].classList.add('active');
                        }
                    }, 3000);
                }
            } else {
                container.style.display = 'none';
            }
        }

        function renderCategories(filterQuery = '') {
            currentLevel = 'categories';
            document.getElementById('backBtn').style.display = 'none';
            loadBanners();
            document.getElementById('tickerWrapper').style.display = 'block';

            const searchInput = document.getElementById('searchInput');
            if (!filterQuery) searchInput.value = '';
            searchInput.placeholder = 'ابحث عن قسم...';

            const grid = document.getElementById('userGrid');
            grid.innerHTML = '';

            const entries = Object.entries(dataStore.categories).filter(([name]) => 
                name.toLowerCase().includes(filterQuery.toLowerCase())
            );

            if (entries.length === 0) {
                grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد أقسام مطابقة</div>`;
                return;
            }

            for (const [name, img] of entries) {
                const card = document.createElement('div');
                card.className = 'item-card';
                card.onclick = () => openProductsView(name);

                let imgHTML = img ? `<img src="${img}" class="item-img" />` : `<div class="item-img" style="display:flex;align-items:center;justify-content:center;color:#666;">🎮</div>`;
                card.innerHTML = `${imgHTML}<div class="item-label">${name}</div>`;
                grid.appendChild(card);
            }
        }

        function openProductsView(categoryName, filterQuery = '') {
            currentLevel = 'products';
            selectedCategory = categoryName;

            document.getElementById('backBtn').style.display = 'block';
            
            const container = document.getElementById('bannerContainer');
            const catBanner = dataStore.categoryBanners[categoryName];
            if (catBanner) {
                container.style.display = 'flex';
                container.innerHTML = `<img src="${catBanner}" class="banner-slide active" />`;
            } else {
                container.style.display = 'none';
            }

            document.getElementById('tickerWrapper').style.display = 'none';

            const searchInput = document.getElementById('searchInput');
            if (!filterQuery) searchInput.value = '';
            searchInput.placeholder = 'ابحث عن منتج داخل ' + categoryName + '...';

            const grid = document.getElementById('userGrid');
            grid.innerHTML = '';

            const filteredProducts = dataStore.products.filter(p => 
                p.category === categoryName && p.name.toLowerCase().includes(filterQuery.toLowerCase())
            );

            if (filteredProducts.length === 0) {
                grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد منتجات مطابقة</div>`;
                return;
            }

            filteredProducts.forEach(p => {
                const card = document.createElement('div');
                card.className = 'item-card';
                card.onclick = () => openSubcategoriesView(p.name);

                let imgHTML = p.image ? `<img src="${p.image}" class="item-img" />` : `<div class="item-img" style="display:flex;align-items:center;justify-content:center;color:#666;">📦</div>`;
                card.innerHTML = `${imgHTML}<div class="item-label">${p.name}</div>`;
                grid.appendChild(card);
            });
        }

        function openSubcategoriesView(productName, filterQuery = '') {
            currentLevel = 'subcategories';
            selectedProduct = productName;

            document.getElementById('backBtn').style.display = 'block';
            document.getElementById('bannerContainer').style.display = 'none';
            document.getElementById('tickerWrapper').style.display = 'none';

            const searchInput = document.getElementById('searchInput');
            if (!filterQuery) searchInput.value = '';
            searchInput.placeholder = 'ابحث عن فئة داخل ' + productName + '...';

            const grid = document.getElementById('userGrid');
            grid.innerHTML = '';

            const filteredSubcats = dataStore.subcategories.filter(s => 
                s.product === productName && s.name.toLowerCase().includes(filterQuery.toLowerCase())
            );

            if (filteredSubcats.length === 0) {
                grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد فئات لهذه الخدمة بعد</div>`;
                return;
            }

            filteredSubcats.forEach(s => {
                const card = document.createElement('div');
                card.className = 'item-card';
                card.onclick = () => openPurchaseModal(s);

                let imgHTML = s.image ? `<img src="${s.image}" class="item-img" />` : `<div class="item-img" style="display:flex;align-items:center;justify-content:center;color:#666;">💎</div>`;
                card.innerHTML = `
                    ${imgHTML}
                    <div class="item-label">${s.name}</div>
                    <div class="item-price-tag">$ ${formatBalance(s.price)}</div>
                `;
                grid.appendChild(card);
            });
        }

        function goBack() {
            if (currentLevel === 'subcategories') {
                openProductsView(selectedCategory);
            } else if (currentLevel === 'products') {
                renderCategories();
            }
        }

        function handleSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (currentLevel === 'categories') {
                renderCategories(query);
            } else if (currentLevel === 'products') {
                openProductsView(selectedCategory, query);
            } else if (currentLevel === 'subcategories') {
                openSubcategoriesView(selectedProduct, query);
            }
        }

        async function openDepositPage() {
            if (document.getElementById('sidebar').classList.contains('active')) { toggleSidebar(); }
            document.getElementById('shopMainSection').style.display = 'none';
            document.getElementById('myOrdersPage').style.display = 'none';
            document.getElementById('myDepositsPage').style.display = 'none';
            document.getElementById('myWalletPage').style.display = 'none';
            document.getElementById('bannerContainer').style.display = 'none';
            document.getElementById('tickerWrapper').style.display = 'none';
            document.getElementById('depositPage').style.display = 'flex';

            const res = await fetch('/api/get_deposit_methods');
            dataStore.depositMethods = await res.json();
            renderDepositMethods();
        }

        function closeDepositPage() {
            document.getElementById('depositPage').style.display = 'none';
            document.getElementById('shopMainSection').style.display = 'block';
            if (currentLevel === 'categories') {
                loadBanners();
                document.getElementById('tickerWrapper').style.display = 'block';
            }
        }

        function renderDepositMethods() {
            const searchQ = document.getElementById('depositSearchInput').value.trim().toLowerCase();
            const grid = document.getElementById('depositMethodsGrid');
            grid.innerHTML = '';

            const filtered = dataStore.depositMethods.filter(m => 
                m.name.toLowerCase().includes(searchQ) || 
                (m.description && m.description.toLowerCase().includes(searchQ))
            );

            if (filtered.length === 0) {
                grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد طرق إيداع مضافة تطابق البحث</div>`;
                return;
            }

            filtered.forEach(m => {
                const card = document.createElement('div');
                card.className = 'item-card';
                card.onclick = () => openDepositDetailModal(m);

                let imgHTML = m.image ? `<img src="${m.image}" class="item-img" />` : `<div class="item-img" style="display:flex;align-items:center;justify-content:center;color:#666;">💳</div>`;
                card.innerHTML = `${imgHTML}<div class="item-label">${m.name}</div>`;
                grid.appendChild(card);
            });
        }

        function openDepositDetailModal(method) {
            activeDepositMethod = method;
            document.getElementById('depModalTitle').innerText = method.name;
            document.getElementById('depModalDesc').innerText = method.description || 'لا يوجد وصف متاح لهذه الطريقة.';
            document.getElementById('depModalCode').innerText = method.payment_codes || 'لا توجد أكواد مضافة';
            
            document.getElementById('depAmountInput').value = '';
            document.getElementById('depTxIdInput').value = '';
            document.getElementById('depReceiptImageInput').value = '';

            document.getElementById('depositDetailModal').classList.add('active');
        }

        function closeDepositDetailModal() { document.getElementById('depositDetailModal').classList.remove('active'); }

        function copyDepositCode() {
            const codeText = document.getElementById('depModalCode').innerText;
            if (!codeText || codeText === 'لا توجد أكواد مضافة') return;
            navigator.clipboard.writeText(codeText).then(() => { showGreenCopyToast(); }).catch(err => { console.error("فشل النسخ: ", err); });
        }

        async function submitDepositRequest() {
            const amount = document.getElementById('depAmountInput').value.trim();
            const txId = document.getElementById('depTxIdInput').value.trim();
            const fileInput = document.getElementById('depReceiptImageInput');

            if (!amount || !txId) { alert('يرجى تعبئة جميع الحقول بشكل صحيح!'); return; }

            const savedEmail = localStorage.getItem('loggedInUserEmail');
            if (!savedEmail) {
                alert('يرجى تسجيل الدخول أولاً!');
                closeDepositDetailModal();
                toggleSidebar();
                return;
            }

            const sendReq = async (imageBase64) => {
                await fetch('/api/submit_deposit_request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: savedEmail,
                        method_name: activeDepositMethod.name,
                        amount: amount,
                        tx_id: txId,
                        receipt_image: imageBase64
                    })
                });

                alert('تم إرسال طلب الإيداع بنجاح وسوف يتم التدقيق به قريباً!');
                closeDepositDetailModal();
            };

            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => sendReq(e.target.result);
                reader.readAsDataURL(fileInput.files[0]);
            } else {
                sendReq('');
            }
        }

        async function openMyDepositsPage() {
            if (document.getElementById('sidebar').classList.contains('active')) { toggleSidebar(); }
            document.getElementById('shopMainSection').style.display = 'none';
            document.getElementById('depositPage').style.display = 'none';
            document.getElementById('myOrdersPage').style.display = 'none';
            document.getElementById('myWalletPage').style.display = 'none';
            document.getElementById('bannerContainer').style.display = 'none';
            document.getElementById('tickerWrapper').style.display = 'none';
            document.getElementById('myDepositsPage').style.display = 'flex';

            const savedEmail = localStorage.getItem('loggedInUserEmail');
            const res = await fetch('/api/user_deposits?email=' + encodeURIComponent(savedEmail));
            dataStore.userDeposits = await res.json();
            renderMyDeposits();
        }

        function closeMyDepositsPage() {
            document.getElementById('myDepositsPage').style.display = 'none';
            document.getElementById('shopMainSection').style.display = 'block';
            if (currentLevel === 'categories') {
                loadBanners();
                document.getElementById('tickerWrapper').style.display = 'block';
            }
        }

        function renderMyDeposits() {
            const container = document.getElementById('myDepositsList');
            container.innerHTML = '';

            if (dataStore.userDeposits.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد عمليات إيداع مسبقة</div>`;
                return;
            }

            dataStore.userDeposits.forEach(d => {
                const card = document.createElement('div');
                card.className = 'order-card-exact';

                let statusColor = '#f59e0b';
                if (d.status === "مقبول") statusColor = '#4ade80';
                else if (d.status === "مرفوض") statusColor = '#f87171';

                card.innerHTML = `
                    <div class="order-card-right-exact">
                        <span class="order-id-exact">#${d.tx_id || '-'}</span>
                        <span class="order-subcat-exact">${d.method_name}</span>
                        <span class="order-prod-exact">طريقة الإيداع</span>
                    </div>
                    <div class="order-card-left-exact">
                        <span class="order-price-exact">${formatBalance(d.amount)} $</span>
                        <div class="order-status-row-exact" style="color:${statusColor};">
                            <span>${d.status}</span>
                            ${d.status === 'مقبول' ? '✓' : ''}
                        </div>
                        <span class="order-date-exact">${d.date}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        async function openMyWalletPage() {
            if (document.getElementById('sidebar').classList.contains('active')) { toggleSidebar(); }
            document.getElementById('shopMainSection').style.display = 'none';
            document.getElementById('depositPage').style.display = 'none';
            document.getElementById('myDepositsPage').style.display = 'none';
            document.getElementById('myOrdersPage').style.display = 'none';
            document.getElementById('bannerContainer').style.display = 'none';
            document.getElementById('tickerWrapper').style.display = 'none';
            document.getElementById('myWalletPage').style.display = 'flex';

            const savedEmail = localStorage.getItem('loggedInUserEmail');
            if (savedEmail) {
                try {
                    const res = await fetch('/api/get_balance?email=' + encodeURIComponent(savedEmail));
                    const data = await res.json();
                    if (data.status === "success") {
                        document.getElementById('walletBalanceVal').innerText = formatBalance(data.balance) + "$";
                    }
                } catch (e) { console.error(e); }

                try {
                    const resOrders = await fetch('/api/user_orders?email=' + encodeURIComponent(savedEmail));
                    const orders = await resOrders.json();
                    let totalPurchases = 0;
                    orders.forEach(o => {
                        totalPurchases += parseFloat(o.price || 0);
                    });
                    document.getElementById('walletPurchasesVal').innerText = formatBalance(totalPurchases) + "$";
                } catch (e) { console.error(e); }

                try {
                    const resDeposits = await fetch('/api/user_deposits?email=' + encodeURIComponent(savedEmail));
                    const deposits = await resDeposits.json();
                    let totalReceived = 0;
                    deposits.forEach(d => {
                        if (d.status === "مقبول") {
                            totalReceived += parseFloat(d.amount || 0);
                        }
                    });
                    document.getElementById('walletReceivedVal').innerText = formatBalance(totalReceived) + "$";
                } catch (e) { console.error(e); }
            }
        }

        function closeMyWalletPage() {
            document.getElementById('myWalletPage').style.display = 'none';
            document.getElementById('shopMainSection').style.display = 'block';
            if (currentLevel === 'categories') {
                loadBanners();
                document.getElementById('tickerWrapper').style.display = 'block';
            }
        }

        function renderMyWallet() {}

        function openPurchaseModal(subcat) {
            activeSubCategory = subcat;
            document.getElementById('pModalTitle').innerText = subcat.name;
            document.getElementById('pModalPrice').innerText = "$ " + formatBalance(subcat.price);
            document.getElementById('pModalRequirement').value = '';
            
            const submitBtn = document.getElementById('submitPurchaseBtn');
            const cancelBtn = document.getElementById('cancelPurchaseBtn');
            submitBtn.disabled = false;
            cancelBtn.disabled = false;
            submitBtn.innerHTML = 'شراء';

            const descEl = document.getElementById('pModalDescriptionText');
            if (subcat.description) {
                descEl.innerText = subcat.description;
            } else {
                descEl.innerText = "😲 هذا المنتج يعمل بشكل يدوي ويستغرق بعض الوقت ليصل للزبون";
            }

            document.getElementById('purchaseModal').classList.add('active');
        }

        function closePurchaseModal() { document.getElementById('purchaseModal').classList.remove('active'); }

        async function submitPurchase() {
            const req = document.getElementById('pModalRequirement').value.trim();
            if (!req) { alert('يرجى كتابة متطلبات شراء الخدمة (ايدي المستخدم)!'); return; }

            const savedEmail = localStorage.getItem('loggedInUserEmail');
            if (!savedEmail) {
                alert('يرجى تسجيل الدخول أولاً لإتمام عملية الشراء!');
                toggleSidebar();
                closePurchaseModal();
                return;
            }

            const submitBtn = document.getElementById('submitPurchaseBtn');
            const cancelBtn = document.getElementById('cancelPurchaseBtn');
            
            submitBtn.disabled = true;
            cancelBtn.disabled = true;
            submitBtn.innerHTML = 'جاري الشراء... <span class="btn-spinner"></span>';

            try {
                const res = await fetch('/api/purchase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: savedEmail,
                        product: activeSubCategory.product,
                        subcategory: activeSubCategory.name,
                        price: activeSubCategory.price,
                        provider_name: activeSubCategory.provider_name || '',
                        api_product_id: activeSubCategory.api_product_id || '',
                        input: req
                    })
                });

                const data = await res.json();

                if (data.status === "error") {
                    closePurchaseModal();
                    showTopNotification(data.message || "رصيدك غير كافي ياحجي");
                    return;
                }

                const formattedBal = formatBalance(data.new_balance);
                applyLoggedInState(savedEmail, formattedBal, data.user_id);
                closePurchaseModal();

                document.getElementById('rProduct').innerText = activeSubCategory.product;
                document.getElementById('rSubCategory').innerText = activeSubCategory.name;
                document.getElementById('rPrice').innerText = formatBalance(activeSubCategory.price) + " $";
                document.getElementById('rInputs').innerText = req;
                document.getElementById('rStatus').innerText = data.order_status || "قيد الانتظار";

                document.getElementById('receiptModal').classList.add('active');
            } catch (err) {
                alert('حدث خطأ أثناء الاتصال بالسيرفر، يرجى المحاولة لاحقاً');
                console.error(err);
            } finally {
                submitBtn.disabled = false;
                cancelBtn.disabled = false;
                submitBtn.innerHTML = 'شراء';
            }
        }

        function closeReceiptModal() { document.getElementById('receiptModal').classList.remove('active'); }

        function openOrderDetailModal(order) {
            document.getElementById('detailOrderId').innerText = order.order_uuid ? order.order_uuid.substring(0, 16) : order.id;
            document.getElementById('detailProduct').innerText = order.product || '-';
            document.getElementById('detailSubcategory').innerText = order.subcategory || '-';
            document.getElementById('detailPrice').innerText = formatBalance(order.price) + " $";
            document.getElementById('detailInput').innerText = order.input || '-';

            const statusEl = document.getElementById('detailStatus');
            let statusText = order.status || 'قيد الانتظار';
            let statusClass = 'status-pending';

            if (order.status === "مكتملة") {
                statusText = 'مقبول';
                statusClass = 'status-accept';
            } else if (order.status === "مرفوضة" || order.status === "تم الارسال للتشيك") {
                statusText = 'مرفوض';
                statusClass = 'status-reject';
            }

            statusEl.innerText = statusText;
            statusEl.className = 'order-detail-value status-badge ' + statusClass;

            document.getElementById('orderDetailModal').classList.add('active');
        }

        function closeOrderDetailModal() {
            document.getElementById('orderDetailModal').classList.remove('active');
        }

        async function openMyOrdersPage() {
            if (document.getElementById('sidebar').classList.contains('active')) { toggleSidebar(); }
            document.getElementById('shopMainSection').style.display = 'none';
            document.getElementById('depositPage').style.display = 'none';
            document.getElementById('myDepositsPage').style.display = 'none';
            document.getElementById('myWalletPage').style.display = 'none';
            document.getElementById('bannerContainer').style.display = 'none';
            document.getElementById('tickerWrapper').style.display = 'none';
            document.getElementById('myOrdersPage').style.display = 'flex';

            const savedEmail = localStorage.getItem('loggedInUserEmail');
            
            if (dataStore.userOrders.length === 0) {
                document.getElementById('myOrdersList').innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">جاري التحميل...</div>`;
            }

            try {
                const res = await fetch('/api/user_orders?email=' + encodeURIComponent(savedEmail));
                dataStore.userOrders = await res.json();
            } catch (e) { console.error(e); }

            renderMyOrders();
        }

        function closeMyOrdersPage() {
            document.getElementById('myOrdersPage').style.display = 'none';
            document.getElementById('shopMainSection').style.display = 'block';
            if (currentLevel === 'categories') {
                loadBanners();
                document.getElementById('tickerWrapper').style.display = 'block';
            }
        }

        function setOrderStatusFilter(status, el) {
            currentStatusFilter = status;
            document.querySelectorAll('#statusFilterRow .filter-pill').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
            renderMyOrders();
        }

        function setOrderTypeFilter(type, el) {
            currentTypeFilter = type;
            document.querySelectorAll('#typeFilterRow .filter-pill').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
            renderMyOrders();
        }

        function renderMyOrders() {
            const dateFrom = document.getElementById('orderDateFrom').value;
            const dateTo = document.getElementById('orderDateTo').value;
            const searchQ = document.getElementById('ordersSearchInput').value.trim().toLowerCase();

            let filtered = dataStore.userOrders;
            if (dateFrom) filtered = filtered.filter(o => o.date >= dateFrom);
            if (dateTo) filtered = filtered.filter(o => o.date <= dateTo);
            
            if (searchQ) {
                filtered = filtered.filter(o => 
                    o.id.toString().includes(searchQ) ||
                    o.subcategory.toLowerCase().includes(searchQ) ||
                    o.product.toLowerCase().includes(searchQ)
                );
            }

            let countAll = filtered.length;
            let countChanged = filtered.filter(o => o.status === "مكتملة" || o.status === "مرفوضة" || o.status === "تم الارسال للتشيك").length;
            let countAccept = filtered.filter(o => o.status === "مكتملة").length;

            let typeAll = countAll;
            let typeManual = filtered.filter(o => !o.api_product_id).length;
            let typeApi = filtered.filter(o => o.api_product_id).length;

            document.getElementById('countAll').innerText = countAll;
            document.getElementById('countChanged').innerText = countChanged;
            document.getElementById('countAccept').innerText = countAccept;

            document.getElementById('typeCountAll').innerText = typeAll;
            document.getElementById('typeCountManual').innerText = typeManual;
            document.getElementById('typeCountApi').innerText = typeApi;

            if (currentStatusFilter === 'changed') {
                filtered = filtered.filter(o => o.status === "مكتملة" || o.status === "مرفوضة" || o.status === "تم الارسال للتشيك");
            } else if (currentStatusFilter === 'accept') {
                filtered = filtered.filter(o => o.status === "مكتملة");
            }

            if (currentTypeFilter === 'manual') {
                filtered = filtered.filter(o => !o.api_product_id);
            } else if (currentTypeFilter === 'api') {
                filtered = filtered.filter(o => o.api_product_id);
            }

            let totalExp = 0;
            filtered.forEach(o => {
                totalExp += parseFloat(o.price || 0);
            });

            document.getElementById('totalExpensesVal').innerText = formatBalance(totalExp) + " $";

            const container = document.getElementById('myOrdersList');
            container.innerHTML = '';

            if (filtered.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-color); font-size:0.8rem;">لا توجد طلبات تطابق هذا البحث</div>`;
                return;
            }

            filtered.forEach(o => {
                const card = document.createElement('div');
                card.className = 'order-card-exact';
                card.onclick = () => openOrderDetailModal(o);

                let statusColor = '#f59e0b';
                let statusText = o.status || 'قيد الانتظار';
                let statusIcon = '';

                if (o.status === "مكتملة") {
                    statusColor = '#4ade80';
                    statusText = 'مقبول';
                    statusIcon = '✓';
                } else if (o.status === "مرفوضة" || o.status === "تم الارسال للتشيك") {
                    statusColor = '#f87171';
                    statusText = 'مرفوض';
                }

                card.innerHTML = `
                    <div class="order-card-right-exact">
                        <span class="order-id-exact">ID_${o.order_uuid ? o.order_uuid.substring(0, 16) : o.id}#</span>
                        <span class="order-subcat-exact">${o.subcategory}</span>
                        <span class="order-prod-exact">${o.product}</span>
                    </div>
                    <div class="order-card-left-exact">
                        <span class="order-price-exact">${formatBalance(o.price)} $</span>
                        <div class="order-status-row-exact" style="color:${statusColor};">
                            <span>${statusText}</span>
                            <span>${statusIcon}</span>
                        </div>
                        <span class="order-date-exact">${o.time || ''} ${o.date}</span>
                        <span class="order-input-exact">${o.input || '-'} #</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        initTheme();
        loadSplashScreen();
        checkSavedSession();
        loadBanners();
        initData();
    </script>
</body>
</html>
"""

# --------------------------------------------------
# 3. واجهة الإدمن الخاصة (تم تعديل الخط إلى Cairo)
# --------------------------------------------------
ADMIN_HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة القيادة - Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <style>
        * { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
        body { background-color: #050508; color: #ffffff; padding: 20px; }
        .admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #27272a; }
        .admin-header .menu-btn { background: transparent; border: 1px solid #27272a; border-radius: 8px; width: 40px; height: 40px; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 4px; cursor: pointer; background-color: #121212; }
        .admin-header .menu-btn span { width: 18px; height: 2px; background-color: #ffffff; border-radius: 2px; }
        .admin-header .title { font-size: 1.25rem; font-weight: 800; }
        .sidebar-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.75); backdrop-filter: blur(4px); z-index: 999; opacity: 0; visibility: hidden; transition: opacity 0.3s ease; }
        .sidebar-overlay.active { opacity: 1; visibility: visible; }
        .sidebar { position: fixed; top: 0; right: -320px; width: 300px; height: 100vh; background-color: #09090b; border-left: 1px solid #27272a; z-index: 1000; transition: right 0.3s ease; display: flex; flex-direction: column; padding: 20px 16px; overflow-y: auto; }
        .sidebar.active { right: 0; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #27272a; padding-bottom: 12px; }
        .sidebar-header .close-btn { background: transparent; border: none; color: #a1a1aa; font-size: 1.4rem; cursor: pointer; }
        .admin-menu-btn { width: 100%; padding: 12px; background-color: #121212; border: 1px solid #27272a; border-radius: 8px; color: #ffffff; font-size: 0.85rem; font-weight: 700; cursor: pointer; text-align: right; display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
        .admin-menu-btn:active { background-color: #1f1f23; }
        .sub-menu { display: none; flex-direction: column; gap: 6px; padding-right: 12px; margin-top: 4px; }
        .sub-menu-btn { width: 100%; padding: 10px; background-color: #18181b; border: 1px solid #27272a; border-radius: 6px; color: #a1a1aa; font-size: 0.8rem; font-weight: 600; cursor: pointer; text-align: right; }
        .sub-menu-btn:active { color: #38bdf8; border-color: #38bdf8; }
        .dashboard-title { font-size: 1.25rem; font-weight: 800; margin-bottom: 20px; margin-right: 5px; }
        .admin-card { background-color: #121212 !important; border: 1px solid #27272a !important; border-radius: 12px !important; padding: 15px !important; height: 100%; transition: border-color 0.2s; }
        .admin-card:hover { border-color: #38bdf8 !important; }
        .card-label { color: #a1a1aa; font-size: 0.8rem; font-weight: 600; text-align: left; margin-bottom: 0px; margin-top: 10px; }
        .card-value { font-size: 2rem; font-weight: 800; text-align: left; margin-bottom: 0; direction: ltr; }
        .btn-card-action { width: 100%; background-color: transparent; border: 1px solid; border-radius: 8px; padding: 8px; font-size: 0.85rem; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; margin-top: auto; }
        .btn-card-action:active { transform: scale(0.97); }
        .card-requests .card-value { color: #3b82f6; }
        .card-requests .btn-card-action { color: #3b82f6; border-color: #3b82f6; }
        .card-requests .btn-card-action:hover { background-color: rgba(59, 130, 246, 0.1); }
        .card-pending .card-value { color: #facc15; }
        .card-pending .btn-card-action { color: #facc15; border-color: #facc15; }
        .card-pending .btn-card-action:hover { background-color: rgba(250, 204, 21, 0.1); }
        .card-users .card-value { color: #2dd4bf; }
        .card-users .btn-card-action { color: #2dd4bf; border-color: #2dd4bf; }
        .card-users .btn-card-action:hover { background-color: rgba(45, 212, 191, 0.1); }
        .card-products .card-value { color: #4ade80; }
        .card-products .btn-card-action { color: #4ade80; border-color: #4ade80; }
        .card-products .btn-card-action:hover { background-color: rgba(74, 222, 128, 0.1); }
        .card-balance .card-value { color: #4ade80; }
        .card-deposit-pending .card-value { color: #f87171; }
        .card-deposit-pending .btn-card-action { color: #f87171; border-color: #f87171; }
        .card-deposit-pending .btn-card-action:hover { background-color: rgba(248, 113, 113, 0.1); }
        .main-content-wrapper { max-width: 420px; margin: 0 auto; }
        .row { --bs-gutter-x: 1rem; }
        a { text-decoration: none; }
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); z-index: 2000; display: none; align-items: center; justify-content: center; }
        .modal-overlay.active { display: flex; }
        .modal-box { background-color: #121212; border: 1px solid #27272a; border-radius: 12px; width: 90%; max-width: 340px; padding: 20px; display: flex; flex-direction: column; gap: 12px; max-height: 90vh; overflow-y: auto; }
        .modal-title { font-size: 0.95rem; font-weight: 700; text-align: center; border-bottom: 1px solid #27272a; padding-bottom: 8px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        label { font-size: 0.75rem; color: #a1a1aa; }
        input, select, textarea { background-color: #000; border: 1px solid #27272a; color: #fff; padding: 8px; border-radius: 6px; font-size: 0.8rem; outline: none; width: 100%; }
        .save-btn { background-color: #2563eb; color: #fff; border: none; padding: 10px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .delete-btn { background-color: #dc2626; color: #fff; border: none; padding: 10px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .btn-secondary { background-color: #3f3f46; color: #fff; border: none; padding: 10px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .admin-field-box { background-color: #000; border: 1px solid #27272a; border-radius: 6px; padding: 10px; font-size: 0.8rem; color: #fff; font-weight: 600; word-break: break-all; }
        .action-btns-row { display: flex; gap: 10px; width: 100%; }
        .btn-accept { flex: 1; padding: 10px; background-color: #16a34a; color: #fff; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .btn-reject { flex: 1; padding: 10px; background-color: #dc2626; color: #fff; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .request-card-item { background-color: #121212; border: 1px solid #27272a; border-radius: 10px; padding: 12px 14px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: border-color 0.2s; }
        .request-card-item:hover { border-color: #38bdf8; }
        .card-val-right { font-size: 0.95rem; font-weight: 800; color: #4ade80; }
        .card-title-left { font-size: 0.85rem; font-weight: 700; color: #ffffff; }
        .provider-item-rect { background-color: #121212; border: 1px solid #27272a; border-radius: 10px; padding: 14px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: all 0.2s ease; }
        .provider-item-rect:hover { border-color: #38bdf8; background-color: #18181b; }
        .provider-name-txt { font-size: 0.9rem; font-weight: 700; color: #ffffff; }
        .provider-url-txt { font-size: 0.7rem; color: #a1a1aa; }
        .api-service-card { background-color: #000; border: 1px solid #27272a; border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 6px; margin-top: 8px; text-align: right; }
        .api-service-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; }
        .api-copyable-id { color: #38bdf8; font-weight: 700; cursor: pointer; background-color: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 4px; border: 1px dashed #38bdf8; }
        #apiProductPreviewBox { display: none; background-color: #000; border: 1px solid #38bdf8; border-radius: 6px; padding: 8px 10px; font-size: 0.75rem; color: #38bdf8; font-weight: 700; text-align: center; }
        #checkDepositsPage, #checkOrdersPage, #viewProvidersPage { display: none; flex-direction: column; gap: 12px; width: 100%; }
        .grid-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; padding: 10px 5px; }
        .category-card { background-color: #121212; border: 1px solid #27272a; border-radius: 10px; aspect-ratio: 1 / 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; padding: 5px; overflow: hidden; position: relative; transform: scale(1.1); transform-origin: center; }
        .category-img { width: 100%; height: calc(100% - 28px); object-fit: cover; border-radius: 6px 6px 0 0; position: absolute; top: 0; left: 0; }
        .category-label { width: 100%; background-color: #000000; border: 1px solid #27272a; border-radius: 6px; padding: 4px 2px; text-align: center; font-size: 0.72rem; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; z-index: 2; }
        .success-circle-box { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 15px 5px; gap: 12px; text-align: center; }
        .success-circle { width: 65px; height: 65px; border-radius: 50%; background-color: rgba(74, 222, 128, 0.15); border: 2px solid #4ade80; display: flex; align-items: center; justify-content: center; color: #4ade80; font-size: 2rem; box-shadow: 0 0 15px rgba(74, 222, 128, 0.3); }
        .success-text-sub { font-size: 0.88rem; font-weight: 700; color: #ffffff; line-height: 1.5; }
    </style>
</head>
<body>

    <div class="admin-header">
        <div class="menu-btn" onclick="toggleSidebar()">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="title">لوحة القيادة</div>
    </div>

    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div style="font-size:0.95rem; font-weight:700;">خيارات الإدمن</div>
            <button class="close-btn" onclick="toggleSidebar()">&times;</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('settingsMenu')">
            <span>إعدادات الموقع</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="settingsMenu">
            <button class="sub-menu-btn" onclick="openAboutUsSettingsModal()">تعيين من نحن</button>
            <button class="sub-menu-btn" onclick="openSupportSettingsModal()">تعيين التواصل مع دعم</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('designMenu')">
            <span>إدارة الشكل والصور</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="designMenu">
            <button class="sub-menu-btn" onclick="openCategoryModal()">إضافة صور للأقسام</button>
            <button class="sub-menu-btn" onclick="openBannerModal()">إضافة بنر</button>
            <button class="sub-menu-btn" onclick="openDeleteBannerModal()">حذف بنر</button>
            <button class="sub-menu-btn" onclick="openCategoryBannerModal()">اضافة بنرات لقسم</button>
            <button class="sub-menu-btn" onclick="openSplashModal()">إضافة صورة ترحيبية</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('productsMenu')">
            <span>إدارة المنتجات والخدمات</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="productsMenu">
            <button class="sub-menu-btn" onclick="openAddCategoryModal()">اضافة قسم</button>
            <button class="sub-menu-btn" onclick="openDeleteCategoryModal()">حذف قسم</button>
            <button class="sub-menu-btn" onclick="openCheckOrdersPage()">تشييك طلبات</button>
            <button class="sub-menu-btn" onclick="openAddProductModal()">إضافة منتج</button>
            <button class="sub-menu-btn" onclick="openAddSubCategoryModal()">إضافة فئة</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('apiMenu')">
            <span>إدارة API</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="apiMenu">
            <button class="sub-menu-btn" onclick="openAddApiModal()">اضافة API</button>
            <button class="sub-menu-btn" onclick="openProfitMarginModal()">نسبة الربح</button>
            <button class="sub-menu-btn" onclick="openViewProvidersPage()">عرض المزودات</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('usersMenu')">
            <span>إدارة المستخدمين</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="usersMenu">
            <button class="sub-menu-btn" onclick="openBalanceModal('add')">شحن مستخدم</button>
            <button class="sub-menu-btn" onclick="openBalanceModal('deduct')">خصم من مستخدم</button>
            <!-- زر كشف عميل المضاف لقائمة إدارة المستخدمين -->
            <button class="sub-menu-btn" onclick="openClientInspectPrompt()">كشف عميل</button>
        </div>

        <button class="admin-menu-btn" onclick="toggleSubMenu('depositsMenu')">
            <span>إدارة الإيداعات</span>
            <span>▼</span>
        </button>
        <div class="sub-menu" id="depositsMenu">
            <button class="sub-menu-btn" onclick="openCheckDepositsPage()">تشييك الايداعات</button>
            <button class="sub-menu-btn" onclick="openAddDepositMethodModal()">اضافة طريقة</button>
            <button class="sub-menu-btn" onclick="openDeleteDepositMethodModal()">حذف طريقة</button>
            <button class="sub-menu-btn" onclick="openViewDepositMethodsModal()">عرض الطرق المضافة</button>
        </div>
    </div>

    <div class="main-content-wrapper">
        <div id="dashboardStatsContainer" class="row row-cols-2 g-3"></div>
    </div>

    <div id="adminMainSection" style="margin-top:20px;">
        <div class="grid-container" id="adminGrid"></div>
    </div>

    <!-- ========== النوافذ المنبثقة ========== -->

    <div class="modal-overlay" id="aboutUsSettingsModalOverlay">
        <div class="modal-box">
            <div class="modal-title">تعيين نص (من نحن)</div>
            <div class="form-group">
                <label>اكتب النص الذي سيظهر للمستخدمين:</label>
                <textarea id="aboutUsTextInput" rows="6" placeholder="اكتب نص من نحن هنا..."></textarea>
            </div>
            <button class="save-btn" onclick="saveAboutUsSettings()">حفظ</button>
            <button class="btn-secondary" onclick="closeModal('aboutUsSettingsModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="supportSettingsModalOverlay">
        <div class="modal-box">
            <div class="modal-title">تعيين التواصل مع دعم</div>
            <div class="form-group">
                <label>تلغرام (يوزر المستخدم):</label>
                <input type="text" id="telegramSupportInput" placeholder="مثال: @username أو username">
            </div>
            <div class="form-group">
                <label>واتساب (رقم الهاتف):</label>
                <input type="text" id="whatsappSupportInput" placeholder="مثال: 963987654321">
            </div>
            <div class="form-group">
                <label>قناة تلغرام (معرف القناة):</label>
                <input type="text" id="telegramChannelInput" placeholder="مثال: @channel_name">
            </div>
            <div class="form-group">
                <label>قناة واتساب (رابط القناة):</label>
                <input type="text" id="whatsappChannelInput" placeholder="مثال: https://whatsapp.com/channel/...">
            </div>
            <button class="save-btn" onclick="saveSupportSettings()">تفعيل الدعم</button>
            <button class="btn-secondary" onclick="closeModal('supportSettingsModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="profitMarginModalOverlay">
        <div class="modal-box">
            <div class="modal-title">تحديد نسبة الربح لمنتجات API</div>
            <div class="form-group">
                <label>أدخل نسبة الربح المئوية (%):</label>
                <input type="number" id="profitMarginInput" placeholder="مثال: 10" step="0.1" min="0" required>
            </div>
            <button class="save-btn" onclick="saveProfitMargin()">حفظ وتطبيق</button>
            <button class="btn-secondary" onclick="closeModal('profitMarginModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="profitSuccessModalOverlay">
        <div class="modal-box">
            <div class="success-circle-box">
                <div class="success-circle">✓</div>
                <div class="success-text-sub">
                    تم تطبيق نسبة الربح على : <br>
                    <span id="appliedProductsCount" style="color:#4ade80; font-size:1.1rem; font-weight:800;">0</span> منتج
                </div>
            </div>
            <button class="save-btn" onclick="closeModal('profitSuccessModalOverlay')">موافق</button>
        </div>
    </div>

    <div class="modal-overlay" id="addCategoryModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة قسم جديد</div>
            <div class="form-group">
                <label>1. اسم القسم:</label>
                <input type="text" id="newCategoryNameInput" placeholder="أدخل اسم القسم..." required>
            </div>
            <div class="form-group">
                <label>2. صورة القسم:</label>
                <input type="file" id="newCategoryImgInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveNewCategory()">حفظ القسم</button>
            <button class="btn-secondary" onclick="closeModal('addCategoryModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="deleteCategoryModalOverlay">
        <div class="modal-box">
            <div class="modal-title">حذف قسم</div>
            <div class="form-group">
                <label>اختر القسم المراد حذفه:</label>
                <select id="deleteCategorySelect"></select>
            </div>
            <button class="delete-btn" onclick="confirmDeleteCategory()">حذف الآن</button>
            <button class="btn-secondary" onclick="closeModal('deleteCategoryModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="deleteBannerModalOverlay">
        <div class="modal-box">
            <div class="modal-title">حذف بنر (رئيسي أو قسم)</div>
            <div class="form-group">
                <label>اختر نوع البنر:</label>
                <select id="deleteBannerTypeSelect" onchange="updateDeleteBannerList()">
                    <option value="main">بنر رئيسي</option>
                    <option value="category">بنر قسم</option>
                </select>
            </div>
            <div class="form-group">
                <label>اختر البنر:</label>
                <select id="deleteBannerSelect"></select>
            </div>
            <button class="delete-btn" onclick="confirmDeleteBanner()">حذف البنر</button>
            <button class="btn-secondary" onclick="closeModal('deleteBannerModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="categoryBannerModalOverlay">
        <div class="modal-box">
            <div class="modal-title">اضافة بنر لقسم</div>
            <div class="form-group">
                <label>اختر القسم:</label>
                <select id="catBannerSelect"></select>
            </div>
            <div class="form-group">
                <label>صورة البنر:</label>
                <input type="file" id="catBannerImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveCategoryBanner()">حفظ</button>
            <button class="btn-secondary" onclick="closeModal('categoryBannerModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="categoryModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة صورة للقسم</div>
            <div class="form-group">
                <label>اختر القسم:</label>
                <select id="categorySelect"></select>
            </div>
            <div class="form-group">
                <label>اختر الصورة:</label>
                <input type="file" id="categoryImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveCategoryImage()">حفظ وتحديث</button>
            <button class="btn-secondary" onclick="closeModal('categoryModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="bannerModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة بنر جديد</div>
            <div class="form-group">
                <label>اختر صورة البنر:</label>
                <input type="file" id="bannerImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveBannerImage()">حفظ</button>
            <button class="btn-secondary" onclick="closeModal('bannerModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="splashModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة صورة ترحيبية للموقع</div>
            <div class="form-group">
                <label>اختر الصورة الترحيبية:</label>
                <input type="file" id="splashImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveSplashImage()">حفظ الصورة</button>
            <button class="btn-secondary" onclick="closeModal('splashModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="addProductModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة منتج جديد</div>
            <div class="form-group">
                <label>اسم المنتج:</label>
                <input type="text" id="productNameInput" placeholder="أدخل اسم المنتج..." required>
            </div>
            <div class="form-group">
                <label>حدد القسم:</label>
                <select id="productCategorySelect"></select>
            </div>
            <div class="form-group">
                <label>صورة المنتج:</label>
                <input type="file" id="productImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveProduct()">حفظ</button>
            <button class="btn-secondary" onclick="closeModal('addProductModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="addSubCategoryModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة فئة جديدة</div>
            <div class="form-group">
                <label>1. اسم الفئة:</label>
                <input type="text" id="subCatNameInput" placeholder="أدخل اسم الفئة..." required>
            </div>
            <div class="form-group">
                <label>2. السعر ($):</label>
                <input type="number" id="subCatPriceInput" placeholder="أدخل السعر..." step="0.001" required>
            </div>
            <div class="form-group">
                <label>3. حدد المنتج التابع له:</label>
                <select id="subCatProductSelect"></select>
            </div>
            <div class="form-group">
                <label>4. اختر المزود API (اختياري):</label>
                <select id="subCatProviderSelect" onchange="verifyApiProductId()">
                    <option value="">بدون مزود (يدوي)</option>
                </select>
            </div>
            <div class="form-group">
                <label>5. ايدي المنتج لدى المزود API (اختياري):</label>
                <input type="text" id="subCatApiProductIdInput" placeholder="أدخل ايدي المنتج لدى المزود..." oninput="verifyApiProductId()">
            </div>
            <div id="apiProductPreviewBox"></div>
            <div class="form-group">
                <label>6. وصف الفئة (ملاحظات الشراء):</label>
                <textarea id="subCatDescriptionInput" rows="2" placeholder="أدخل وصف الفئة الذي سيظهر للزبون..."></textarea>
            </div>
            <div class="form-group">
                <label>7. صورة الفئة:</label>
                <input type="file" id="subCatImageInput" accept="image/*">
            </div>
            <button class="save-btn" onclick="saveSubCategory()">حفظ الفئة</button>
            <button class="btn-secondary" onclick="closeModal('addSubCategoryModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="userBalanceModalOverlay">
        <div class="modal-box">
            <div class="modal-title" id="balanceModalTitle">شحن مستخدم</div>
            <div class="form-group">
                <label>البريد الإلكتروني للعميل:</label>
                <input type="email" id="userBalanceEmail" placeholder="example@mail.com" required>
            </div>
            <div class="form-group">
                <label>المبلغ ($):</label>
                <input type="number" id="userBalanceAmount" placeholder="أدخل المبلغ..." step="0.001" required>
            </div>
            <button class="save-btn" onclick="saveUserBalance()">حفظ وتحديث الرصيد</button>
            <button class="btn-secondary" onclick="closeModal('userBalanceModalOverlay')">إلغاء</button>
        </div>
    </div>

    <!-- نافذة إضافة طريقة إيداع (المعدلة) -->
    <div class="modal-overlay" id="addDepositMethodModal">
        <div class="modal-box" style="max-height: 90vh; overflow-y: auto;">
            <div class="modal-title">إضافة طريقة إيداع جديدة</div>
            <div class="form-group">
                <label>1. اسم الطريقة:</label>
                <input type="text" id="depMethodName" placeholder="أدخل اسم الطريقة..." required>
            </div>
            <div class="form-group">
                <label>2. وصف الطريقة:</label>
                <textarea id="depMethodDescription" rows="2" placeholder="أدخل وصف أو تعليمات الطريقة..."></textarea>
            </div>
            <div class="form-group">
                <label>3. سعر صرف الطريقة:</label>
                <input type="number" id="depMethodExchangeRate" placeholder="أدخل سعر الصرف..." step="0.001" required>
            </div>
            <div class="form-group">
                <label>4. صورة الطريقة:</label>
                <input type="file" id="depMethodImageInput" accept="image/*">
            </div>
            <div class="form-group">
                <label>5. أكواد الدفع / الحسابات:</label>
                <textarea id="depMethodPaymentCodes" rows="2" placeholder="أدخل أكواد الدفع أو أرقام الحسابات..."></textarea>
            </div>
            <button class="save-btn" onclick="saveDepositMethod()">حفظ الطريقة</button>
            <button class="btn-secondary" onclick="closeModal('addDepositMethodModal')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="deleteDepositMethodModal">
        <div class="modal-box">
            <div class="modal-title">حذف طريقة إيداع</div>
            <div class="form-group">
                <label>اختر الطريقة المراد حذفها:</label>
                <select id="depMethodDeleteSelect"></select>
            </div>
            <button class="delete-btn" onclick="confirmDeleteDepositMethod()">حذف الآن</button>
            <button class="btn-secondary" onclick="closeModal('deleteDepositMethodModal')">إلغاء</button>
        </div>
    </div>

    <div class="modal-overlay" id="viewDepositMethodsModal">
        <div class="modal-box" style="max-height:80vh; overflow-y:auto;">
            <div class="modal-title">طرق الإيداع المضافة</div>
            <div id="depositMethodsList" style="display:flex; flex-direction:column; gap:10px;"></div>
            <button class="save-btn" onclick="closeModal('viewDepositMethodsModal')">إغلاق</button>
        </div>
    </div>

    <div class="modal-overlay" id="addApiModalOverlay">
        <div class="modal-box">
            <div class="modal-title">إضافة API جديد</div>
            <div class="form-group">
                <label>1. توكن API:</label>
                <input type="text" id="apiTokenInput" placeholder="أدخل API Token الخاص بك..." required>
            </div>
            <div class="form-group">
                <label>2. رابط API:</label>
                <input type="text" id="apiUrlInput" placeholder="مثال: https://api.kaser-card.com/" required>
            </div>
            <div class="form-group">
                <label>3. اسم المزود:</label>
                <input type="text" id="providerNameInput" placeholder="أدخل اسم المزود..." required>
            </div>
            <button class="save-btn" onclick="saveApiProvider()">حفظ</button>
            <button class="btn-secondary" onclick="closeModal('addApiModalOverlay')">إلغاء</button>
        </div>
    </div>

    <div id="viewProvidersPage">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #27272a; padding-bottom:8px; margin-bottom:5px;">
            <span style="font-size:0.95rem; font-weight:800; color:#38bdf8;">قائمة المزودات المضافة</span>
            <button class="btn-secondary" onclick="closeViewProvidersPage()">رجوع</button>
        </div>
        <div id="providersListContainer" style="display:flex; flex-direction:column; gap:10px; margin-top:10px;"></div>
    </div>

    <div class="modal-overlay" id="providerBalanceModal">
        <div class="modal-box" style="max-height:85vh; overflow-y:auto;">
            <div class="modal-title" id="provModalTitle">تفاصيل المزود</div>
            <div class="form-group" style="text-align:center; margin-top:5px;">
                <label style="font-size:0.85rem; font-weight:700;">رصيدك API:</label>
                <div id="provModalBalance" style="font-size:1.2rem; font-weight:800; color:#4ade80; margin-top:4px; background-color:#000; padding:10px; border-radius:8px; border:1px solid #27272a;">جاري التحميل...</div>
            </div>
            <div class="form-group" style="margin-top:10px;">
                <label>البحث عن خدمة لدى المزود:</label>
                <input type="text" id="provServiceSearchInput" placeholder="اكتب اسم الخدمة..." oninput="searchProviderService()">
            </div>
            <div id="provServicesResult" style="display:flex; flex-direction:column; gap:8px;"></div>
            <button class="save-btn" style="background-color:#3f3f46;" onclick="closeModal('providerBalanceModal')">إغلاق</button>
        </div>
    </div>

    <div id="checkOrdersPage">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #27272a; padding-bottom:8px; margin-bottom:5px;">
            <span style="font-size:0.95rem; font-weight:800; color:#38bdf8;">طلبات الشراء قيد الانتظار</span>
            <button class="btn-secondary" onclick="closeCheckOrdersPage()">رجوع</button>
        </div>
        <div id="productOrdersList" style="display:flex; flex-direction:column; gap:10px;"></div>
    </div>

    <div class="modal-overlay" id="reviewOrderModal">
        <div class="modal-box">
            <div class="modal-title">تفاصيل طلب الشراء</div>
            <div class="form-group">
                <label>1. اسم المنتج:</label>
                <div class="admin-field-box" id="revOrdProduct">-</div>
            </div>
            <div class="form-group">
                <label>2. الفئة والسعر:</label>
                <div class="admin-field-box" id="revOrdSubcatPrice" style="color:#4ade80; font-weight:800;">-</div>
            </div>
            <div class="form-group">
                <label>3. إيميل الشخص:</label>
                <div class="admin-field-box" id="revOrdEmail" style="color:#38bdf8;">-</div>
            </div>
            <div class="form-group">
                <label>4. مدخلات / متطلبات الشراء:</label>
                <div class="admin-field-box" id="revOrdInput">-</div>
            </div>
            <div class="action-btns-row">
                <button class="btn-accept" onclick="processOrderDecision('accept')">قبول الطلب</button>
                <button class="btn-reject" onclick="processOrderDecision('reject')">رفض الطلب</button>
            </div>
            <button class="btn-secondary" onclick="closeModal('reviewOrderModal')">إلغاء</button>
        </div>
    </div>

    <div id="checkDepositsPage">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #27272a; padding-bottom:8px; margin-bottom:5px;">
            <span style="font-size:0.95rem; font-weight:800; color:#38bdf8;">طلبات الإيداع المقدمة</span>
            <button class="btn-secondary" onclick="closeCheckDepositsPage()">رجوع</button>
        </div>
        <div id="depositRequestsList" style="display:flex; flex-direction:column; gap:10px;"></div>
    </div>

    <div class="modal-overlay" id="reviewDepositModal">
        <div class="modal-box">
            <div class="modal-title">تفاصيل طلب الإيداع</div>
            <div class="form-group">
                <label>1. المبلغ المحول:</label>
                <div class="admin-field-box" id="revAmount" style="color:#4ade80; font-size:0.9rem; font-weight:800;">-</div>
            </div>
            <div class="form-group">
                <label>2. رقم العملية:</label>
                <div class="admin-field-box" id="revTxId">-</div>
            </div>
            <div class="form-group">
                <label>3. إيميل الشخص:</label>
                <div class="admin-field-box" id="revEmail" style="color:#38bdf8;">-</div>
            </div>
            <div class="form-group">
                <label>4. إشعار التحويل:</label>
                <div class="admin-field-box" id="revReceiptContainer" style="display:flex; justify-content:center; align-items:center;">-</div>
            </div>
            <div class="action-btns-row">
                <button class="btn-accept" onclick="processDepositDecision('accept')">قبول الايداع</button>
                <button class="btn-reject" onclick="processDepositDecision('reject')">رفض الايداع</button>
            </div>
            <button class="btn-secondary" onclick="closeModal('reviewDepositModal')">إلغاء</button>
        </div>
    </div>

    <!-- نافذة طلب رقم الحساب أو الإيميل -->
    <div class="modal-overlay" id="clientInspectModal">
        <div class="modal-box">
            <div class="modal-title">كشف عميل</div>
            <div class="form-group">
                <label>رقم الحساب أو إيميل المستخدم:</label>
                <input type="text" id="inspectUserIdentifier" placeholder="مثال: user@mail.com أو 1001" required>
            </div>
            <button class="save-btn" onclick="executeClientInspection()">كشف</button>
            <button class="btn-secondary" onclick="closeModal('clientInspectModal')">إلغاء</button>
        </div>
    </div>

    <!-- واجهة كشف العميل على كامل الشاشة -->
    <div id="fullClientInspectScreen" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:#050508; z-index:9999; overflow-y:auto; padding:20px; flex-direction:column; gap:15px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #27272a; padding-bottom:10px;">
            <span style="font-size:1.1rem; font-weight:800; color:#38bdf8;" id="inspectHeaderTitle">تقرير حساب العميل</span>
            <button class="btn-secondary" style="padding:6px 14px;" onclick="closeFullClientInspect()">إغلاق</button>
        </div>

        <!-- مربع التمثيل البياني لمشترياته ومصروفاته -->
        <div style="background:#121212; border:1px solid #27272a; border-radius:12px; padding:15px; display:flex; flex-direction:column; gap:10px;">
            <div style="font-size:0.9rem; font-weight:700; color:#a1a1aa;">المخطط البياني (مشتريات ومصروفات)</div>
            <div style="display:flex; align-items:flex-end; gap:20px; height:150px; padding:15px; background:#000; border-radius:8px; border:1px solid #27272a; justify-content:space-around;">
                <div style="display:flex; flex-direction:column; align-items:center; gap:6px; height:100%; justify-content:flex-end;">
                    <span id="chartPurchasesLabel" style="font-size:0.75rem; color:#4ade80; font-weight:700;">0$</span>
                    <div id="chartPurchasesBar" style="width:35px; background:#22c55e; border-radius:6px 6px 0 0; min-height:4px; height:10%;"></div>
                    <span style="font-size:0.7rem; color:#fff;">المشتريات</span>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:6px; height:100%; justify-content:flex-end;">
                    <span id="chartDepositsLabel" style="font-size:0.75rem; color:#38bdf8; font-weight:700;">0$</span>
                    <div id="chartDepositsBar" style="width:35px; background:#0284c7; border-radius:6px 6px 0 0; min-height:4px; height:10%;"></div>
                    <span style="font-size:0.7rem; color:#fff;">المصروفات</span>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#a1a1aa; padding-top:4px;">
                <span>الرصيد الحالي: <b id="inspectUserBalance" style="color:#4ade80;">0$</b></span>
                <span>رقم الحساب: <b id="inspectUserId" style="color:#38bdf8;">#</b></span>
            </div>
        </div>

        <!-- خط فاصل -->
        <hr style="border-color:#27272a; margin:5px 0;">

        <!-- الأزرار التحتية -->
        <div style="display:flex; flex-direction:column; gap:12px;">
            <button class="save-btn" style="background:#2563eb; padding:14px; font-size:0.95rem;" onclick="loginAsClientDirectly()">دخول الى حساب العميل</button>
            
            <!-- زر التبديل لتفعيل/تعطيل الـ API -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:#121212; border:1px solid #27272a; padding:12px 16px; border-radius:12px;">
                <span style="font-size:0.9rem; font-weight:700;">تفعيل خانة API</span>
                <label class="toggle-switch" style="position:relative; display:inline-block; width:50px; height:26px;">
                    <input type="checkbox" id="inspectApiToggle" onchange="toggleClientApiStatus(this.checked)">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
    </div>

    <script>
        // ============================================================
        // دوال القائمة الجانبية
        // ============================================================
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('sidebarOverlay').classList.toggle('active');
        }

        function toggleSubMenu(id) {
            const menu = document.getElementById(id);
            menu.style.display = (menu.style.display === 'flex') ? 'none' : 'flex';
        }

        // ============================================================
        // دوال النوافذ المنبثقة
        // ============================================================
        function openModal(id) {
            const el = document.getElementById(id);
            if (el) el.classList.add('active');
        }
        function closeModal(id) {
            const el = document.getElementById(id);
            if (el) el.classList.remove('active');
        }

        // ============================================================
        // دوال تنسيق الأرقام
        // ============================================================
        function formatBalance(num) {
            const parsed = parseFloat(num);
            if (isNaN(parsed)) return "0.000";
            return Number(parsed.toFixed(3)).toString();
        }

        // ============================================================
        // الكروت الإحصائية
        // ============================================================
        function renderDashboardStats(stats) {
            const container = document.getElementById('dashboardStatsContainer');
            container.innerHTML = '';

            let pendingOrders = 0;
            fetch('/api/get_all_orders')
                .then(r => r.json())
                .then(orders => {
                    pendingOrders = orders.filter(o => o.status === 'قيد الانتظار' || o.status === 'تم الارسال للتشيك').length;
                    updateCards(stats, pendingOrders);
                })
                .catch(() => {
                    updateCards(stats, 0);
                });
        }

        function updateCards(stats, pendingOrders) {
            const container = document.getElementById('dashboardStatsContainer');
            container.innerHTML = '';

            const cardTemplates = [
                { key: 'card-requests', label: 'عدد الطلبات', value: stats.total_orders || 0, actionText: 'عرض التفاصيل', actionUrl: '#', type: 'value_with_btn' },
                { key: 'card-pending', label: 'طلبات قيد الانتظار', value: pendingOrders, actionText: 'إدارة الطلبات', actionUrl: '#', type: 'value_with_btn' },
                { key: 'card-users', label: 'عدد المستخدمين', value: stats.users || 0, actionText: 'عرض المستخدمين', actionUrl: '#', type: 'value_with_btn' },
                { key: 'card-products', label: 'المنتجات النشطة', value: stats.total_products || 0, actionText: 'إدارة المنتجات', actionUrl: '#', type: 'value_with_btn' },
                { key: 'card-balance', label: 'إجمالي رصيد المستخدمين', value: `$${formatBalance(stats.total_balance || 0)}`, type: 'value_only' },
                { key: 'card-deposit-pending', label: 'طلبات شحن معلّقة', value: stats.pending_deposits || 0, actionText: 'إدارة طلبات الشحن', actionUrl: '#', type: 'value_with_btn' }
            ];

            cardTemplates.forEach(cardData => {
                const col = document.createElement('div');
                col.className = 'col';

                let cardContent = `
                    <div class="card admin-card ${cardData.key}">
                        <p class="card-label">${cardData.label}</p>
                        <p class="card-value">${cardData.value}</p>
                `;

                if (cardData.type === 'value_with_btn') {
                    cardContent += `<a href="${cardData.actionUrl}" class="btn-card-action">${cardData.actionText}</a>`;
                }

                cardContent += `</div>`;
                col.innerHTML = cardContent;
                container.appendChild(col);
            });
        }

        // ============================================================
        // جلب الإحصائيات من الخادم
        // ============================================================
        async function fetchStatsAndRender() {
            try {
                const response = await fetch('/api/admin_stats');
                const stats = await response.json();

                let totalProducts = 0;
                try {
                    const subRes = await fetch('/api/subcategories');
                    const subcats = await subRes.json();
                    totalProducts = subcats.length;
                } catch (e) {
                    console.warn("تعذر جلب عدد المنتجات");
                }

                const formattedStats = {
                    users: stats.users || 0,
                    total_orders: stats.total_orders || 0,
                    total_balance: stats.total_balance || 0,
                    pending_deposits: stats.pending_deposits || 0,
                    total_products: totalProducts
                };

                renderDashboardStats(formattedStats);
            } catch (error) {
                console.error('فشل جلب الإحصائيات:', error);
                const container = document.getElementById('dashboardStatsContainer');
                container.innerHTML = `<div class="col-12 text-center text-danger">حدث خطأ في تحميل البيانات</div>`;
            }
        }

        // ============================================================
        // دوال الإعدادات
        // ============================================================
        function openAboutUsSettingsModal() {
            toggleSidebar();
            fetch('/api/get_site_settings')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('aboutUsTextInput').value = data.about_us || '';
                });
            openModal('aboutUsSettingsModalOverlay');
        }

        async function saveAboutUsSettings() {
            const text = document.getElementById('aboutUsTextInput').value.trim();
            await fetch('/api/update_about_us', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ about_us: text })
            });
            alert('تم حفظ نص من نحن بنجاح!');
            closeModal('aboutUsSettingsModalOverlay');
        }

        function openSupportSettingsModal() {
            toggleSidebar();
            fetch('/api/get_site_settings')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('telegramSupportInput').value = data.telegram_support || '';
                    document.getElementById('whatsappSupportInput').value = data.whatsapp_support || '';
                    document.getElementById('telegramChannelInput').value = data.telegram_channel || '';
                    document.getElementById('whatsappChannelInput').value = data.whatsapp_channel || '';
                });
            openModal('supportSettingsModalOverlay');
        }

        async function saveSupportSettings() {
            const data = {
                telegram_support: document.getElementById('telegramSupportInput').value.trim(),
                whatsapp_support: document.getElementById('whatsappSupportInput').value.trim(),
                telegram_channel: document.getElementById('telegramChannelInput').value.trim(),
                whatsapp_channel: document.getElementById('whatsappChannelInput').value.trim()
            };
            await fetch('/api/update_support_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            alert('تم حفظ إعدادات الدعم بنجاح!');
            closeModal('supportSettingsModalOverlay');
        }

        // ============================================================
        // دوال API والمزودات
        // ============================================================
        function openAddApiModal() {
            toggleSidebar();
            document.getElementById('apiTokenInput').value = '';
            document.getElementById('apiUrlInput').value = '';
            document.getElementById('providerNameInput').value = '';
            openModal('addApiModalOverlay');
        }

        async function saveApiProvider() {
            const token = document.getElementById('apiTokenInput').value.trim();
            const url = document.getElementById('apiUrlInput').value.trim();
            const name = document.getElementById('providerNameInput').value.trim();
            if (!token || !url || !name) { alert('يرجى ملء جميع الحقول المطلوبة!'); return; }

            await fetch('/api/add_provider', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, url, name })
            });
            alert('تم حفظ المزود بنجاح!');
            closeModal('addApiModalOverlay');
            fetchStatsAndRender();
        }

        function openProfitMarginModal() {
            toggleSidebar();
            document.getElementById('profitMarginInput').value = '';
            openModal('profitMarginModalOverlay');
        }

        async function saveProfitMargin() {
            const marginVal = parseFloat(document.getElementById('profitMarginInput').value);
            if (isNaN(marginVal) || marginVal < 0) {
                alert('يرجى إدخال نسبة ربح صحيحة!');
                return;
            }

            const res = await fetch('/api/apply_profit_margin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ margin: marginVal })
            });
            const data = await res.json();
            if (data.status === 'success') {
                closeModal('profitMarginModalOverlay');
                document.getElementById('appliedProductsCount').innerText = data.applied_count || 0;
                openModal('profitSuccessModalOverlay');
                fetchStatsAndRender();
            } else {
                alert(data.message || 'حدث خطأ أثناء تطبيق نسبة الربح!');
            }
        }

        function openViewProvidersPage() {
            toggleSidebar();
            document.getElementById('adminMainSection').style.display = 'none';
            document.getElementById('checkOrdersPage').style.display = 'none';
            document.getElementById('checkDepositsPage').style.display = 'none';
            document.getElementById('viewProvidersPage').style.display = 'flex';

            fetch('/api/get_providers')
                .then(r => r.json())
                .then(providers => {
                    const container = document.getElementById('providersListContainer');
                    container.innerHTML = '';
                    if (providers.length === 0) {
                        container.innerHTML = `<div style="text-align:center; color:#a1a1aa; font-size:0.8rem; padding:20px;">لا يوجد مزودين مضافين حالياً</div>`;
                        return;
                    }
                    providers.forEach(p => {
                        const item = document.createElement('div');
                        item.className = 'provider-item-rect';
                        item.onclick = () => openProviderBalanceModal(p);
                        item.innerHTML = `
                            <div style="display:flex; flex-direction:column; gap:4px;">
                                <span class="provider-name-txt">${p.name}</span>
                                <span class="provider-url-txt">${p.url}</span>
                            </div>
                            <span style="font-size:1.1rem; color:#38bdf8;">◀</span>
                        `;
                        container.appendChild(item);
                    });
                });
        }

        function closeViewProvidersPage() {
            document.getElementById('viewProvidersPage').style.display = 'none';
            document.getElementById('adminMainSection').style.display = 'block';
        }

        async function openProviderBalanceModal(provider) {
            document.getElementById('provModalTitle').innerText = provider.name;
            document.getElementById('provModalBalance').innerText = 'جاري التحميل...';
            document.getElementById('provServiceSearchInput').value = '';
            document.getElementById('provServicesResult').innerHTML = '';
            openModal('providerBalanceModal');

            try {
                const res = await fetch('/api/get_provider_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: provider.token, url: provider.url })
                });
                const data = await res.json();
                if (data.status === 'success' && data.profile) {
                    const bal = data.profile.balance !== undefined ? data.profile.balance : (data.profile["الرصيد"] !== undefined ? data.profile["الرصيد"] : "0");
                    document.getElementById('provModalBalance').innerText = formatBalance(bal) + " $";
                } else {
                    document.getElementById('provModalBalance').innerText = "خطأ في الاتصال بالحساب!";
                }
            } catch (e) {
                document.getElementById('provModalBalance').innerText = "فشل الاتصال بالمزود!";
            }

            try {
                const pRes = await fetch('/api/get_provider_products', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: provider.token, url: provider.url })
                });
                const pData = await pRes.json();
                if (pData.status === 'success' && Array.isArray(pData.products)) {
                    window._fetchedProviderProducts = pData.products;
                }
            } catch (e) { console.error("فشل جلب منتجات المزود", e); }
        }

        function searchProviderService() {
            const query = document.getElementById('provServiceSearchInput').value.trim().toLowerCase();
            const container = document.getElementById('provServicesResult');
            container.innerHTML = '';
            if (!query) return;

            const products = window._fetchedProviderProducts || [];
            const matches = products.filter(p => {
                const name = (p.name || p["الاسم"] || "").toString().toLowerCase();
                const id = (p.id || "").toString();
                return name.includes(query) || id.includes(query);
            });

            if (matches.length === 0) {
                container.innerHTML = `<div style="text-align:center; color:#a1a1aa; font-size:0.75rem; padding:10px;">لا توجد خدمات مطابقة</div>`;
                return;
            }

            matches.forEach(p => {
                const pId = p.id || "-";
                const pName = p.name || p["الاسم"] || "-";
                const pPrice = p.price !== undefined ? p.price : (p["السعر"] !== undefined ? p["السعر"] : "-");
                const pType = p.product_type || p["نوع_المنتج"] || "-";
                const pAvailable = (p.available === true || p["متاح"] === true) ? "متاح" : "غير متاح";
                let paramsText = "-";
                if (p.params && Array.isArray(p.params)) paramsText = p.params.join(", ");

                const card = document.createElement('div');
                card.className = 'api-service-card';
                card.innerHTML = `
                    <div class="api-service-row"><span style="color:#a1a1aa;">الاسم:</span> <b>${pName}</b></div>
                    <div class="api-service-row"><span style="color:#a1a1aa;">السعر:</span> <span style="color:#4ade80; font-weight:700;">${formatBalance(pPrice)} $</span></div>
                    <div class="api-service-row"><span style="color:#a1a1aa;">نوع المنتج:</span> <span>${pType}</span></div>
                    <div class="api-service-row"><span style="color:#a1a1aa;">ايدي المنتج:</span> <span class="api-copyable-id" onclick="copyTextToClipboard('${pId}')">${pId} 📋</span></div>
                    <div class="api-service-row"><span style="color:#a1a1aa;">متطلبات شراء:</span> <span>${paramsText}</span></div>
                    <div class="api-service-row"><span style="color:#a1a1aa;">حالة المنتج:</span> <span style="color:${pAvailable === 'متاح' ? '#4ade80' : '#f87171'}; font-weight:700;">${pAvailable}</span></div>
                `;
                container.appendChild(card);
            });
        }

        function copyTextToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('تم نسخ النص: ' + text);
            }).catch(err => console.error("فشل النسخ: ", err));
        }

        function verifyApiProductId() {
            clearTimeout(window._apiVerifyTimeout);
            const providerName = document.getElementById('subCatProviderSelect').value;
            const val = document.getElementById('subCatApiProductIdInput').value.trim();
            const box = document.getElementById('apiProductPreviewBox');

            if (!providerName || !val) {
                box.style.display = 'none';
                box.innerText = '';
                return;
            }

            box.style.display = 'block';
            box.innerText = 'جاري التحقق واستخراج اسم الخدمة...';

            window._apiVerifyTimeout = setTimeout(async () => {
                try {
                    const res = await fetch('/api/verify_product_id', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ provider_name: providerName, product_id: val })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        box.style.borderColor = '#4ade80';
                        box.style.color = '#4ade80';
                        box.innerText = 'اسم المنتج: ' + data.product_name;
                    } else {
                        box.style.borderColor = '#f87171';
                        box.style.color = '#f87171';
                        box.innerText = 'المنتج غير موجود لدى المزود المحدد!';
                    }
                } catch (e) {
                    box.style.borderColor = '#f87171';
                    box.style.color = '#f87171';
                    box.innerText = 'تعذر الاتصال بالمزود!';
                }
            }, 600);
        }

        // ============================================================
        // دوال الأقسام
        // ============================================================
        function openAddCategoryModal() {
            toggleSidebar();
            document.getElementById('newCategoryNameInput').value = '';
            document.getElementById('newCategoryImgInput').value = '';
            openModal('addCategoryModalOverlay');
        }

        function saveNewCategory() {
            const name = document.getElementById('newCategoryNameInput').value.trim();
            const fileInput = document.getElementById('newCategoryImgInput');
            if (!name) { alert('يرجى إدخال اسم القسم!'); return; }

            const processSave = async (image) => {
                await fetch('/api/add_category', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, image })
                });
                alert('تمت إضافة القسم بنجاح!');
                closeModal('addCategoryModalOverlay');
                loadCategories();
                fetchStatsAndRender();
            };

            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => processSave(e.target.result);
                reader.readAsDataURL(fileInput.files[0]);
            } else {
                processSave('');
            }
        }

        function openDeleteCategoryModal() {
            toggleSidebar();
            fetch('/api/categories')
                .then(r => r.json())
                .then(cats => {
                    const select = document.getElementById('deleteCategorySelect');
                    select.innerHTML = '';
                    const keys = Object.keys(cats);
                    if (keys.length === 0) {
                        alert('لا توجد أقسام للحذف!');
                        return;
                    }
                    keys.forEach(k => {
                        select.innerHTML += `<option value="${k}">${k}</option>`;
                    });
                    openModal('deleteCategoryModalOverlay');
                });
        }

        async function confirmDeleteCategory() {
            const select = document.getElementById('deleteCategorySelect');
            const catName = select.value;
            if (!catName) return;

            await fetch('/api/delete_category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: catName })
            });
            alert('تم حذف القسم بنجاح!');
            closeModal('deleteCategoryModalOverlay');
            loadCategories();
            fetchStatsAndRender();
        }

        function openCategoryModal() {
            toggleSidebar();
            fetch('/api/categories')
                .then(r => r.json())
                .then(cats => {
                    const select = document.getElementById('categorySelect');
                    select.innerHTML = '';
                    Object.keys(cats).forEach(k => {
                        select.innerHTML += `<option value="${k}">${k}</option>`;
                    });
                });
            openModal('categoryModalOverlay');
        }

        async function saveCategoryImage() {
            const category = document.getElementById('categorySelect').value;
            const fileInput = document.getElementById('categoryImageInput');
            if (!fileInput.files || !fileInput.files[0]) { alert('يرجى اختيار صورة!'); return; }
            const reader = new FileReader();
            reader.onload = async function(e) {
                await fetch('/api/update_category', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category, image: e.target.result })
                });
                alert('تم حفظ الصورة بنجاح!');
                closeModal('categoryModalOverlay');
                loadCategories();
                fetchStatsAndRender();
            };
            reader.readAsDataURL(fileInput.files[0]);
        }

        function openCategoryBannerModal() {
            toggleSidebar();
            fetch('/api/categories')
                .then(r => r.json())
                .then(cats => {
                    const select = document.getElementById('catBannerSelect');
                    select.innerHTML = '';
                    Object.keys(cats).forEach(k => {
                        select.innerHTML += `<option value="${k}">${k}</option>`;
                    });
                });
            document.getElementById('catBannerImageInput').value = '';
            openModal('categoryBannerModalOverlay');
        }

        async function saveCategoryBanner() {
            const category = document.getElementById('catBannerSelect').value;
            const fileInput = document.getElementById('catBannerImageInput');
            if (!fileInput.files || !fileInput.files[0]) { alert('يرجى اختيار صورة البنر!'); return; }
            const reader = new FileReader();
            reader.onload = async function(e) {
                await fetch('/api/add_category_banner', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category, image: e.target.result })
                });
                alert('تم حفظ بنر القسم بنجاح!');
                closeModal('categoryBannerModalOverlay');
                fetchStatsAndRender();
            };
            reader.readAsDataURL(fileInput.files[0]);
        }

        async function loadCategories() {
            const res = await fetch('/api/categories');
            const categories = await res.json();
            const grid = document.getElementById('adminGrid');
            grid.innerHTML = '';

            const catSelect1 = document.getElementById('categorySelect');
            if (catSelect1) catSelect1.innerHTML = '';

            for (const [name, img] of Object.entries(categories)) {
                const card = document.createElement('div');
                card.className = 'category-card';
                let imgHTML = img ? `<img src="${img}" class="category-img" />` : '';
                card.innerHTML = `${imgHTML}<div class="category-label">${name}</div>`;
                grid.appendChild(card);

                if (catSelect1) catSelect1.innerHTML += `<option value="${name}">${name}</option>`;
            }
        }

        // ============================================================
        // دوال البنرات
        // ============================================================
        function openBannerModal() {
            toggleSidebar();
            document.getElementById('bannerImageInput').value = '';
            openModal('bannerModalOverlay');
        }

        async function saveBannerImage() {
            const fileInput = document.getElementById('bannerImageInput');
            if (!fileInput.files || !fileInput.files[0]) { alert('يرجى اختيار صورة البنر!'); return; }
            const reader = new FileReader();
            reader.onload = async function(e) {
                await fetch('/api/add_banner', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: e.target.result })
                });
                alert('تم إضافة البنر بنجاح!');
                closeModal('bannerModalOverlay');
                fetchStatsAndRender();
            };
            reader.readAsDataURL(fileInput.files[0]);
        }

        function openDeleteBannerModal() {
            toggleSidebar();
            updateDeleteBannerList();
            openModal('deleteBannerModalOverlay');
        }

        async function updateDeleteBannerList() {
            const type = document.getElementById('deleteBannerTypeSelect').value;
            const select = document.getElementById('deleteBannerSelect');
            select.innerHTML = '';

            if (type === 'main') {
                const res = await fetch('/api/banners');
                const banners = await res.json();
                if (banners.length === 0) {
                    select.innerHTML = `<option value="">لا توجد بنرات رئيسية مضافة</option>`;
                } else {
                    banners.forEach((b, idx) => {
                        select.innerHTML += `<option value="${idx}">بنر رئيسي رقم ${idx + 1}</option>`;
                    });
                }
            } else {
                const res = await fetch('/api/category_banners');
                const cbanners = await res.json();
                const keys = Object.keys(cbanners);
                if (keys.length === 0) {
                    select.innerHTML = `<option value="">لا توجد بنرات أقسام مضافة</option>`;
                } else {
                    keys.forEach(k => {
                        select.innerHTML += `<option value="${k}">بنر قسم: ${k}</option>`;
                    });
                }
            }
        }

        async function confirmDeleteBanner() {
            const type = document.getElementById('deleteBannerTypeSelect').value;
            const select = document.getElementById('deleteBannerSelect');
            const val = select.value;
            if (!val) return;

            if (type === 'main') {
                await fetch('/api/delete_banner', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ index: parseInt(val) })
                });
            } else {
                await fetch('/api/delete_category_banner', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: val })
                });
            }
            alert('تم حذف البنر بنجاح!');
            closeModal('deleteBannerModalOverlay');
            fetchStatsAndRender();
        }

        function openSplashModal() {
            toggleSidebar();
            document.getElementById('splashImageInput').value = '';
            openModal('splashModalOverlay');
        }

        async function saveSplashImage() {
            const fileInput = document.getElementById('splashImageInput');
            if (!fileInput.files || !fileInput.files[0]) { alert('يرجى اختيار الصورة الترحيبية!'); return; }
            const reader = new FileReader();
            reader.onload = async function(e) {
                await fetch('/api/update_splash', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: e.target.result })
                });
                alert('تم حفظ الصورة الترحيبية بنجاح!');
                closeModal('splashModalOverlay');
                fetchStatsAndRender();
            };
            reader.readAsDataURL(fileInput.files[0]);
        }

        // ============================================================
        // دوال المنتجات والفئات
        // ============================================================
        function openAddProductModal() {
            toggleSidebar();
            document.getElementById('productNameInput').value = '';
            document.getElementById('productImageInput').value = '';
            fetch('/api/categories')
                .then(r => r.json())
                .then(cats => {
                    const select = document.getElementById('productCategorySelect');
                    select.innerHTML = '';
                    Object.keys(cats).forEach(k => {
                        select.innerHTML += `<option value="${k}">${k}</option>`;
                    });
                });
            openModal('addProductModalOverlay');
        }

        async function saveProduct() {
            const name = document.getElementById('productNameInput').value.trim();
            const category = document.getElementById('productCategorySelect').value;
            const fileInput = document.getElementById('productImageInput');
            if (!name || !category) { alert('يرجى تعبئة اسم المنتج واختيار القسم!'); return; }

            const processSave = async (image) => {
                await fetch('/api/add_product', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, category, image })
                });
                alert('تم إضافة المنتج بنجاح!');
                closeModal('addProductModalOverlay');
                fetchStatsAndRender();
            };

            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => processSave(e.target.result);
                reader.readAsDataURL(fileInput.files[0]);
            } else {
                processSave('');
            }
        }

        function openAddSubCategoryModal() {
            toggleSidebar();
            Promise.all([
                fetch('/api/products').then(r => r.json()),
                fetch('/api/get_providers').then(r => r.json())
            ]).then(([products, providers]) => {
                const prodSelect = document.getElementById('subCatProductSelect');
                prodSelect.innerHTML = '';
                products.forEach(p => {
                    prodSelect.innerHTML += `<option value="${p.name}">${p.name}</option>`;
                });
                const provSelect = document.getElementById('subCatProviderSelect');
                provSelect.innerHTML = '<option value="">بدون مزود (يدوي)</option>';
                providers.forEach(p => {
                    provSelect.innerHTML += `<option value="${p.name}">${p.name}</option>`;
                });
            });
            document.getElementById('subCatNameInput').value = '';
            document.getElementById('subCatPriceInput').value = '';
            document.getElementById('subCatApiProductIdInput').value = '';
            document.getElementById('subCatDescriptionInput').value = '';
            document.getElementById('subCatImageInput').value = '';
            document.getElementById('apiProductPreviewBox').style.display = 'none';
            openModal('addSubCategoryModalOverlay');
        }

        async function saveSubCategory() {
            const name = document.getElementById('subCatNameInput').value.trim();
            const price = parseFloat(document.getElementById('subCatPriceInput').value);
            const product = document.getElementById('subCatProductSelect').value;
            const providerName = document.getElementById('subCatProviderSelect').value;
            const apiProductId = document.getElementById('subCatApiProductIdInput').value.trim();
            const description = document.getElementById('subCatDescriptionInput').value.trim();
            const fileInput = document.getElementById('subCatImageInput');

            if (!name || isNaN(price) || !product) { alert('يرجى تعبئة جميع الحقول المطلوبة!'); return; }

            const processSave = async (image) => {
                await fetch('/api/add_subcategory', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, price, product, provider_name: providerName, api_product_id: apiProductId, description, image })
                });
                alert('تم إضافة الفئة بنجاح!');
                closeModal('addSubCategoryModalOverlay');
                fetchStatsAndRender();
            };

            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => processSave(e.target.result);
                reader.readAsDataURL(fileInput.files[0]);
            } else {
                processSave('');
            }
        }

        // ============================================================
        // دوال المستخدمين
        // ============================================================
        let currentBalanceAction = 'add';

        function openBalanceModal(action) {
            currentBalanceAction = action;
            toggleSidebar();
            document.getElementById('balanceModalTitle').innerText = (action === 'add') ? 'شحن مستخدم' : 'خصم من مستخدم';
            document.getElementById('userBalanceEmail').value = '';
            document.getElementById('userBalanceAmount').value = '';
            openModal('userBalanceModalOverlay');
        }

        async function saveUserBalance() {
            const email = document.getElementById('userBalanceEmail').value.trim();
            const amount = parseFloat(document.getElementById('userBalanceAmount').value);
            if (!email || isNaN(amount) || amount <= 0) {
                alert('يرجى تعبئة كافة الحقول بشكل صحيح!');
                return;
            }

            const res = await fetch('/api/manage_balance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, amount, action: currentBalanceAction })
            });
            const data = await res.json();
            if (data.status === "success") {
                alert('تم تحديث رصيد المستخدم بنجاح! الرصيد الجديد: ' + formatBalance(data.new_balance) + ' $');
                closeModal('userBalanceModalOverlay');
                fetchStatsAndRender();
            } else {
                alert(data.message || 'حدث خطأ!');
            }
        }

        // ============================================================
        // دوال الطلبات
        // ============================================================
        let productOrdersData = [];

        function openCheckOrdersPage() {
            toggleSidebar();
            document.getElementById('adminMainSection').style.display = 'none';
            document.getElementById('checkDepositsPage').style.display = 'none';
            document.getElementById('viewProvidersPage').style.display = 'none';
            document.getElementById('checkOrdersPage').style.display = 'flex';

            fetch('/api/get_all_orders')
                .then(r => r.json())
                .then(orders => {
                    productOrdersData = orders;
                    renderProductOrdersList();
                });
        }

        function closeCheckOrdersPage() {
            document.getElementById('checkOrdersPage').style.display = 'none';
            document.getElementById('adminMainSection').style.display = 'block';
            fetchStatsAndRender();
        }

        function renderProductOrdersList() {
            const container = document.getElementById('productOrdersList');
            container.innerHTML = '';
            const pending = productOrdersData.filter(o => o.status === 'قيد الانتظار' || o.status === 'تم الارسال للتشيك');

            if (pending.length === 0) {
                container.innerHTML = `<div style="text-align:center; color:#a1a1aa; font-size:0.8rem; padding:20px;">لا توجد طلبات شراء قيد الانتظار أو للتشيك حالياً</div>`;
                return;
            }

            pending.forEach(o => {
                const card = document.createElement('div');
                card.className = 'request-card-item';
                card.onclick = () => openReviewOrderModal(o);
                let badgeCol = (o.status === 'تم الارسال للتشيك') ? '#f87171' : '#4ade80';
                card.innerHTML = `
                    <div class="card-val-right">${o.subcategory} <span style="font-size:0.65rem; color:${badgeCol};">(${o.status})</span></div>
                    <div class="card-title-left">${formatBalance(o.price)} $</div>
                `;
                container.appendChild(card);
            });
        }

        let activeReviewOrder = null;

        function openReviewOrderModal(order) {
            activeReviewOrder = order;
            document.getElementById('revOrdProduct').innerText = order.product || 'غير معروف';
            document.getElementById('revOrdSubcatPrice').innerText = order.subcategory + " (" + formatBalance(order.price) + " $)";
            document.getElementById('revOrdEmail').innerText = order.email || 'غير معروف';
            document.getElementById('revOrdInput').innerText = order.input || 'لا يوجد';
            openModal('reviewOrderModal');
        }

        async function processOrderDecision(action) {
            if (!activeReviewOrder) return;
            const res = await fetch('/api/process_product_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: activeReviewOrder.id, action: action })
            });
            const data = await res.json();
            if (data.status === "success") {
                alert(action === 'accept' ? 'تم قبول طلب الشراء بنجاح!' : 'تم رفض طلب الشراء وإعادة المبلغ لحساب المستخدم!');
                closeModal('reviewOrderModal');
                openCheckOrdersPage();
                fetchStatsAndRender();
            } else {
                alert(data.message || 'حدث خطأ في معالجة العملية!');
            }
        }

        // ============================================================
        // دوال الإيداعات
        // ============================================================
        let depositRequestsData = [];

        function openCheckDepositsPage() {
            toggleSidebar();
            document.getElementById('adminMainSection').style.display = 'none';
            document.getElementById('checkOrdersPage').style.display = 'none';
            document.getElementById('viewProvidersPage').style.display = 'none';
            document.getElementById('checkDepositsPage').style.display = 'flex';

            fetch('/api/get_deposit_requests')
                .then(r => r.json())
                .then(requests => {
                    depositRequestsData = requests;
                    renderDepositRequestsList();
                });
        }

        function closeCheckDepositsPage() {
            document.getElementById('checkDepositsPage').style.display = 'none';
            document.getElementById('adminMainSection').style.display = 'block';
            fetchStatsAndRender();
        }

        function renderDepositRequestsList() {
            const container = document.getElementById('depositRequestsList');
            container.innerHTML = '';
            const pending = depositRequestsData.filter(r => r.status === 'قيد التدقيق');

            if (pending.length === 0) {
                container.innerHTML = `<div style="text-align:center; color:#a1a1aa; font-size:0.8rem; padding:20px;">لا توجد طلبات إيداع قيد الانتظار حالياً</div>`;
                return;
            }

            pending.forEach(r => {
                const card = document.createElement('div');
                card.className = 'request-card-item';
                card.onclick = () => openReviewDepositModal(r);
                card.innerHTML = `
                    <div class="card-val-right">${formatBalance(r.amount)} $</div>
                    <div class="card-title-left">${r.method_name}</div>
                `;
                container.appendChild(card);
            });
        }

        let activeReviewDeposit = null;

        function openReviewDepositModal(req) {
            activeReviewDeposit = req;
            document.getElementById('revAmount').innerText = formatBalance(req.amount) + " $";
            document.getElementById('revTxId').innerText = req.tx_id || 'لا يوجد';
            document.getElementById('revEmail').innerText = req.email || 'غير معروف';

            const imgContainer = document.getElementById('revReceiptContainer');
            if (req.receipt_image) {
                imgContainer.innerHTML = `<img src="${req.receipt_image}" style="max-width:100%; max-height:180px; border-radius:6px; border:1px solid #27272a;" />`;
            } else {
                imgContainer.innerText = 'لا توجد صورة مرفقة';
            }
            openModal('reviewDepositModal');
        }

        async function processDepositDecision(action) {
            if (!activeReviewDeposit) return;
            const res = await fetch('/api/process_deposit_request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: activeReviewDeposit.id, action: action })
            });
            const data = await res.json();
            if (data.status === "success") {
                alert(action === 'accept' ? 'تم قبول الإيداع وإضافة الرصيد لحساب المستخدم!' : 'تم رفض الإيداع!');
                closeModal('reviewDepositModal');
                openCheckDepositsPage();
                fetchStatsAndRender();
            } else {
                alert(data.message || 'حدث خطأ في معالجة العملية!');
            }
        }

        // ============================================================
        // دوال طرق الإيداع - النسخة المعدلة والمصححة
        // ============================================================
        function openAddDepositMethodModal() {
            toggleSidebar();
            document.getElementById('depMethodName').value = '';
            document.getElementById('depMethodDescription').value = '';
            document.getElementById('depMethodExchangeRate').value = '';
            document.getElementById('depMethodImageInput').value = '';
            document.getElementById('depMethodPaymentCodes').value = '';
            openModal('addDepositMethodModal');
        }

        async function saveDepositMethod() {
            const name = document.getElementById('depMethodName').value.trim();
            const description = document.getElementById('depMethodDescription').value.trim();
            const exchangeRate = parseFloat(document.getElementById('depMethodExchangeRate').value);
            const paymentCodes = document.getElementById('depMethodPaymentCodes').value.trim();
            const fileInput = document.getElementById('depMethodImageInput');

            if (!name) { 
                alert('يرجى إدخال اسم الطريقة!'); 
                return; 
            }

            if (isNaN(exchangeRate) || exchangeRate <= 0) {
                alert('يرجى إدخال سعر صرف صحيح (أكبر من 0)!');
                return;
            }

            try {
                const saveBtn = document.querySelector('#addDepositMethodModal .save-btn');
                const originalText = saveBtn.textContent;
                saveBtn.textContent = 'جاري الحفظ...';
                saveBtn.disabled = true;

                let imageData = '';
                if (fileInput.files && fileInput.files[0]) {
                    const reader = new FileReader();
                    imageData = await new Promise((resolve) => {
                        reader.onload = (e) => resolve(e.target.result);
                        reader.readAsDataURL(fileInput.files[0]);
                    });
                }

                const payload = {
                    name: name,
                    description: description,
                    exchange_rate: exchangeRate,
                    image: imageData,
                    payment_codes: paymentCodes
                };

                console.log('جاري إرسال طلب إضافة طريقة إيداع:', payload);

                const response = await fetch('/api/add_deposit_method', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                console.log('استجابة الخادم:', result);

                if (result.status === 'success') {
                    alert('تمت إضافة طريقة الإيداع بنجاح!');
                    closeModal('addDepositMethodModal');
                    
                    // تحديث القائمة إذا كانت مفتوحة
                    if (document.getElementById('viewDepositMethodsModal').classList.contains('active')) {
                        openViewDepositMethodsModal();
                    }
                    fetchStatsAndRender();
                } else {
                    alert('حدث خطأ: ' + (result.message || 'يرجى المحاولة مرة أخرى'));
                }
            } catch (error) {
                console.error('خطأ في حفظ طريقة الإيداع:', error);
                alert('حدث خطأ في الاتصال بالخادم: ' + error.message);
            } finally {
                const saveBtn = document.querySelector('#addDepositMethodModal .save-btn');
                saveBtn.textContent = 'حفظ الطريقة';
                saveBtn.disabled = false;
            }
        }

        function openDeleteDepositMethodModal() {
            toggleSidebar();
            fetch('/api/get_deposit_methods')
                .then(r => r.json())
                .then(methods => {
                    const select = document.getElementById('depMethodDeleteSelect');
                    select.innerHTML = '';
                    if (methods.length === 0) { alert('لا توجد طرق إيداع مضافة للحذف!'); return; }
                    methods.forEach((m, idx) => {
                        select.innerHTML += `<option value="${idx}">${m.name}</option>`;
                    });
                    openModal('deleteDepositMethodModal');
                });
        }

        async function confirmDeleteDepositMethod() {
            const select = document.getElementById('depMethodDeleteSelect');
            const index = parseInt(select.value);
            if (isNaN(index)) return;

            await fetch('/api/delete_deposit_method', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: index })
            });
            alert('تم حذف طريقة الإيداع بنجاح!');
            closeModal('deleteDepositMethodModal');
            fetchStatsAndRender();
        }

        function openViewDepositMethodsModal() {
            toggleSidebar();
            fetch('/api/get_deposit_methods')
                .then(r => r.json())
                .then(methods => {
                    const list = document.getElementById('depositMethodsList');
                    list.innerHTML = '';
                    if (methods.length === 0) {
                        list.innerHTML = `<div style="text-align:center; color:#a1a1aa; font-size:0.8rem; padding:10px;">لا توجد طرق إيداع مضافة حالياً</div>`;
                    } else {
                        methods.forEach(m => {
                            let imgHTML = m.image ? `<img src="${m.image}" style="width:100%; max-height:80px; object-fit:cover; border-radius:6px; margin-bottom:4px;" />` : '';
                            list.innerHTML += `
                                <div style="background-color:#121212; border:1px solid #27272a; border-radius:8px; padding:10px;">
                                    ${imgHTML}
                                    <div style="font-weight:700; font-size:0.9rem;">${m.name}</div>
                                    <div style="font-size:0.75rem; color:#a1a1aa;">${m.description || 'لا يوجد وصف'}</div>
                                    <div style="font-size:0.75rem; color:#4ade80;">الصرف: ${formatBalance(m.exchange_rate || 0)}</div>
                                </div>
                            `;
                        });
                    }
                    openModal('viewDepositMethodsModal');
                });
        }

        // ============================================================
        // دوال كشف العميل (الإضافات الجديدة)
        // ============================================================
        let inspectedClientData = null;

        function openClientInspectPrompt() {
            toggleSidebar();
            document.getElementById('inspectUserIdentifier').value = '';
            openModal('clientInspectModal');
        }

        async function executeClientInspection() {
            const query = document.getElementById('inspectUserIdentifier').value.trim();
            if (!query) { alert('يرجى كتابة الإيميل أو رقم الحساب!'); return; }

            const res = await fetch('/api/inspect_client', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier: query })
            });

            const data = await res.json();
            if (data.status === 'success') {
                inspectedClientData = data;
                closeModal('clientInspectModal');
                
                document.getElementById('inspectHeaderTitle').innerText = 'كشف العميل: ' + data.email;
                document.getElementById('inspectUserBalance').innerText = formatBalance(data.balance) + ' $';
                document.getElementById('inspectUserId').innerText = '#' + data.id;
                
                const totalSpent = data.total_spent || 0;
                const totalDep = data.total_deposits || 0;
                const maxVal = Math.max(totalSpent, totalDep, 1);
                
                document.getElementById('chartPurchasesLabel').innerText = formatBalance(totalSpent) + '$';
                document.getElementById('chartDepositsLabel').innerText = formatBalance(totalDep) + '$';
                
                document.getElementById('chartPurchasesBar').style.height = `${Math.min(100, Math.max(10, (totalSpent / maxVal) * 100))}%`;
                document.getElementById('chartDepositsBar').style.height = `${Math.min(100, Math.max(10, (totalDep / maxVal) * 100))}%`;

                document.getElementById('inspectApiToggle').checked = data.api_enabled || false;
                document.getElementById('fullClientInspectScreen').style.display = 'flex';
            } else {
                alert(data.message || 'تعذر العثور على المستخدم!');
            }
        }

        function closeFullClientInspect() {
            document.getElementById('fullClientInspectScreen').style.display = 'none';
        }

        async function toggleClientApiStatus(isEnabled) {
            if (!inspectedClientData) return;
            await fetch('/api/toggle_user_api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: inspectedClientData.email, enabled: isEnabled })
            });
            inspectedClientData.api_enabled = isEnabled;
        }

        function loginAsClientDirectly() {
            if (!inspectedClientData) return;
            localStorage.setItem('loggedInUserEmail', inspectedClientData.email);
            localStorage.setItem('loggedInUserPhone', inspectedClientData.phone || '');
            window.location.href = '/';
        }

        // ============================================================
        // تحميل البيانات عند بدء التشغيل
        // ============================================================
        loadCategories();
        fetchStatsAndRender();
        setInterval(fetchStatsAndRender, 30000);
    </script>
</body>
</html>
"""

# --------------------------------------------------
# 4. السيرفر ومعالجة الطلبات
# --------------------------------------------------
class WebAppHandler(BaseHTTPRequestHandler):
    def sync_orders_status_with_api(self):
        changed = False
        if not PROVIDERS_DATA:
            return

        for order in ORDERS_DATA:
            if order.get('status') in ["قيد الانتظار", "تم الارسال للتشيك"] and order.get('order_uuid'):
                p_name = order.get('provider_name')
                provider = next((p for p in PROVIDERS_DATA if p.get('name') == p_name), PROVIDERS_DATA[0])
                token = provider.get('token')
                url = provider.get('url', '').rstrip('/') + '/'

                try:
                    order_uuid_val = order.get('order_uuid')
                    check_url = f"{url}client/api/check?orders=[{order_uuid_val}]&uuid=1"
                    res = make_api_request(check_url, token, timeout=5)
                    
                    if res.get('status') == "OK" and res.get('data') and len(res['data']) > 0:
                        api_status = res['data'][0].get('status')
                        if api_status == "accept":
                            order['status'] = "مكتملة"
                            changed = True
                        elif api_status == "reject":
                            order['status'] = "مرفوضة"
                            u_email = order.get('email')
                            if u_email in USERS_DATA:
                                cur_b = round(float(USERS_DATA[u_email].get('balance', 0)), 3)
                                USERS_DATA[u_email]['balance'] = round(cur_b + float(order.get('price', 0)), 3)
                                save_json_file(USERS_FILE, USERS_DATA)
                            changed = True
                except Exception as e:
                    logging.error(f"خطأ بمزامنة الطلب #{order.get('id')}: {e}")

        if changed:
            save_json_file(ORDERS_FILE, ORDERS_DATA)

    def sync_prices_with_providers(self):
        if not PROVIDERS_DATA:
            return

        changed = False
        for provider in PROVIDERS_DATA:
            p_name = provider.get('name')
            p_token = provider.get('token')
            p_url = provider.get('url', '').rstrip('/') + '/client/api/products'

            try:
                provider_products = make_api_request(p_url, p_token, timeout=8)
                if not isinstance(provider_products, list):
                    continue

                prod_map = {}
                for p in provider_products:
                    pid = str(p.get('id', ''))
                    price = p.get('price') if p.get('price') is not None else p.get('السعر')
                    if pid and price is not None:
                        prod_map[pid] = float(price)

                for sub in SUBCATEGORIES_DATA:
                    if sub.get('provider_name') == p_name and sub.get('api_product_id'):
                        api_id = str(sub.get('api_product_id'))
                        if api_id in prod_map:
                            new_api_price = round(prod_map[api_id], 3)
                            old_api_price = round(float(sub.get('base_price', sub.get('price', 0))), 3)

                            # التحقق في حال وجود اختلاف في سعر المزود (ارتفاع أو انخفاض)
                            if new_api_price != old_api_price:
                                margin = float(sub.get('profit_margin', 0))
                                old_sell_price = round(float(sub.get('price', 0)), 3)
                                new_sell_price = round(new_api_price * (1 + (margin / 100.0)), 3)

                                sub['base_price'] = new_api_price
                                sub['price'] = new_sell_price
                                changed = True

                                send_telegram_price_update_notification(
                                    product=sub.get('product', ''),
                                    subcategory=sub.get('name', ''),
                                    old_price=old_sell_price,
                                    new_price=new_sell_price,
                                    old_api_price=old_api_price,
                                    new_api_price=new_api_price,
                                    provider_name=p_name
                                )
            except Exception as e:
                logging.error(f"خطأ أثناء مزامنة وتحديث أسعار المزود {p_name}: {e}")

        if changed:
            save_json_file(SUBCATEGORIES_FILE, SUBCATEGORIES_DATA)

    def do_GET(self):
        if self.path == "/admin/1":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ADMIN_HTML_CONTENT.encode("utf-8"))

        elif self.path == "/api/admin_stats":
            total_users = len(USERS_DATA)
            total_orders = len(ORDERS_DATA)
            
            total_balance = 0
            for email, data in USERS_DATA.items():
                total_balance += float(data.get('balance', 0))
            
            pending_deposits = len([r for r in DEPOSIT_REQUESTS_DATA if r.get('status') == 'قيد التدقيق'])
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "users": total_users,
                "total_orders": total_orders,
                "total_balance": round(total_balance, 3),
                "pending_deposits": pending_deposits
            }, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/get_site_settings":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(SETTINGS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api-docs":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(API_DOCS_HTML.encode("utf-8"))

        elif self.path == "/client/api/profile":
            auth_token = self.headers.get('api-token')
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            if not auth_token:
                self.wfile.write(json.dumps({"error": 120, "message": "Api Token is required!"}).encode("utf-8"))
            else:
                self.wfile.write(json.dumps({"الرصيد": 0.0, "البريد الإلكتروني": "user@syriacard.com"}, ensure_ascii=False).encode("utf-8"))

        elif self.path.startswith("/client/api/products"):
            auth_token = self.headers.get('api-token')
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            if not auth_token:
                self.wfile.write(json.dumps({"error": 120, "message": "Api Token is required!"}).encode("utf-8"))
            else:
                formatted_products = []
                for idx, sub in enumerate(SUBCATEGORIES_DATA):
                    formatted_products.append({
                        "id": idx + 100,
                        "الاسم": sub.get('name'),
                        "السعر": sub.get('price'),
                        "params": ["ادخل الايدي الأرقام"],
                        "اسم_الفئة": sub.get('product'),
                        "متاح": True,
                        "qty_values": None,
                        "نوع_المنتج": "package",
                        "parent_id": 0,
                        "السعر_الأساسي": sub.get('price'),
                        "category_img": sub.get('image', '')
                    })
                self.wfile.write(json.dumps(formatted_products, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/categories":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(CATEGORIES_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/banners":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(BANNERS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/category_banners":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(CATEGORY_BANNERS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/splash":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(SPLASH_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/products":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(PRODUCTS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/subcategories":
            self.sync_prices_with_providers()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(SUBCATEGORIES_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/get_deposit_methods":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(DEPOSIT_METHODS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/get_deposit_requests":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(DEPOSIT_REQUESTS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/get_all_orders":
            self.sync_orders_status_with_api()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(ORDERS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/get_providers":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(PROVIDERS_DATA, ensure_ascii=False).encode("utf-8"))

        elif self.path.startswith("/api/get_balance"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            email = params.get('email', [''])[0]

            if email in USERS_DATA:
                bal = round(float(USERS_DATA[email].get('balance', 0)), 3)
                u_id = USERS_DATA[email].get('id', 1001)
                api_en = USERS_DATA[email].get('api_enabled', False)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "balance": bal, "user_id": u_id, "api_enabled": api_en}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error"}).encode("utf-8"))

        elif self.path.startswith("/api/user_orders"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            email = params.get('email', [''])[0]
            user_orders = [o for o in ORDERS_DATA if o.get('email') == email]
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(user_orders, ensure_ascii=False).encode("utf-8"))

        elif self.path.startswith("/api/user_deposits"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            email = params.get('email', [''])[0]
            user_deposits = [d for d in DEPOSIT_REQUESTS_DATA if d.get('email') == email]
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(user_deposits, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(USER_HTML_CONTENT.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == "/api/update_about_us":
            about_text = data.get('about_us', '')
            SETTINGS_DATA['about_us'] = about_text
            save_json_file(SETTINGS_FILE, SETTINGS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/update_support_settings":
            SETTINGS_DATA['telegram_support'] = data.get('telegram_support', '')
            SETTINGS_DATA['whatsapp_support'] = data.get('whatsapp_support', '')
            SETTINGS_DATA['telegram_channel'] = data.get('telegram_channel', '')
            SETTINGS_DATA['whatsapp_channel'] = data.get('whatsapp_channel', '')
            save_json_file(SETTINGS_FILE, SETTINGS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/apply_profit_margin":
            margin = float(data.get('margin', 0))
            applied_count = 0

            for sub in SUBCATEGORIES_DATA:
                if sub.get('api_product_id'):
                    base_p = sub.get('base_price')
                    if base_p is None:
                        base_p = sub.get('price', 0)
                        sub['base_price'] = base_p

                    new_p = round(float(base_p) * (1 + (margin / 100.0)), 3)
                    sub['price'] = new_p
                    sub['profit_margin'] = margin
                    applied_count += 1

            save_json_file(SUBCATEGORIES_FILE, SUBCATEGORIES_DATA)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "applied_count": applied_count}).encode("utf-8"))

        elif self.path == "/api/verify_product_id":
            p_id = str(data.get('product_id', '')).strip()
            prov_name = str(data.get('provider_name', '')).strip()
            
            if not PROVIDERS_DATA:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "لا يوجد مزودين مضافين"}).encode("utf-8"))
                return

            provider = next((p for p in PROVIDERS_DATA if p.get('name') == prov_name), PROVIDERS_DATA[0])
            token = provider.get('token')
            url = provider.get('url', '').rstrip('/') + '/' + "client/api/products"

            try:
                products = make_api_request(url, token)
                found = None
                for p in products:
                    if str(p.get('id')) == p_id:
                        found = p
                        break

                if found:
                    p_name = found.get('name') or found.get('الاسم') or 'غير معروف'
                    self.send_response(200)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "product_name": p_name}, ensure_ascii=False).encode("utf-8"))
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "لم يتم العثور على المنتج"}).encode("utf-8"))
            except Exception as e:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

        elif self.path == "/api/add_provider":
            PROVIDERS_DATA.append({
                "token": data.get('token'),
                "url": data.get('url'),
                "name": data.get('name')
            })
            save_json_file(PROVIDERS_FILE, PROVIDERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/get_provider_profile":
            token = data.get('token')
            url = data.get('url')
            if not url.endswith('/'):
                url += '/'
            target_url = url + "client/api/profile"

            try:
                profile_data = make_api_request(target_url, token)
                balance_val = profile_data.get("الرصيد") or profile_data.get("balance") or profile_data.get("credit") or 0
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "balance": balance_val, "profile": profile_data}, ensure_ascii=False).encode("utf-8"))
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8') if e.fp else ''
                logging.error(f"HTTPError من المزود: {e.code} - {err_body}")
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": f"رمز الخطأ من المزود: {e.code}"}).encode("utf-8"))
            except Exception as e:
                logging.error(f"خطأ في الاتصال بالـ API: {e}")
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

        elif self.path == "/api/get_provider_products":
            token = data.get('token')
            url = data.get('url')
            if not url.endswith('/'):
                url += '/'
            target_url = url + "client/api/products"

            try:
                products_data = make_api_request(target_url, token)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "products": products_data}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                logging.error(f"خطأ في جلب منتجات الـ API: {e}")
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

        elif self.path == "/api/login":
            email = data.get('email')
            phone = data.get('phone', '')
            password = data.get('password')

            if email not in USERS_DATA:
                new_user_id = 1000 + len(USERS_DATA) + 1
                USERS_DATA[email] = {
                    "id": new_user_id,
                    "phone": phone,
                    "password": password,
                    "balance": 0
                }
                save_json_file(USERS_FILE, USERS_DATA)

            user_balance = round(float(USERS_DATA[email].get("balance", 0)), 3)
            user_id = USERS_DATA[email].get("id", 1001)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "balance": user_balance, "user_id": user_id}).encode("utf-8"))

        elif self.path == "/api/purchase":
            email = data.get('email')
            price = round(float(data.get('price', 0)), 3)
            provider_name = data.get('provider_name', '')
            api_product_id = data.get('api_product_id', '')

            if email in USERS_DATA:
                current_balance = round(float(USERS_DATA[email].get('balance', 0)), 3)
                if current_balance < price:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "رصيدك غير كافي ياحجي"}).encode("utf-8"))
                    return

                new_balance = round(current_balance - price, 3)
                USERS_DATA[email]['balance'] = new_balance
                save_json_file(USERS_FILE, USERS_DATA)

                now = datetime.now()
                order_id = 1000 + len(ORDERS_DATA) + 1
                order_uuid_val = str(uuid.uuid4())
                order_status = "قيد الانتظار"
                system_response = "تم تسجيل الطلب في انتظار القبول"

                if api_product_id and PROVIDERS_DATA:
                    provider = next((p for p in PROVIDERS_DATA if p.get('name') == provider_name), PROVIDERS_DATA[0])
                    token = provider.get('token')
                    base_url = provider.get('url', '').rstrip('/') + '/'
                    player_id_input = urllib.parse.quote(str(data.get('input', '')))
                    order_api_url = f"{base_url}client/api/newOrder/{api_product_id}/params?qty=1&playerId={player_id_input}&order_uuid={order_uuid_val}"

                    try:
                        api_res = make_api_request(order_api_url, token)
                        if api_res.get('status') == "OK":
                            res_data = api_res.get('data', {})
                            st = res_data.get('status')
                            system_response = f"API OK - Status: {st}"
                            if st == 'accept':
                                order_status = "مكتملة"
                            elif st == 'reject':
                                order_status = "مرفوضة"
                                USERS_DATA[email]['balance'] = current_balance
                                save_json_file(USERS_FILE, USERS_DATA)
                                new_balance = current_balance
                        else:
                            fail_reason = api_res.get('message') or api_res.get('code') or 'خطأ بالاستجابة من المزود'
                            order_status = "تم الارسال للتشيك"
                            system_response = f"API Error: {fail_reason}"
                            send_telegram_notification(data.get('product'), data.get('subcategory'), price, email, str(fail_reason))
                    except Exception as e:
                        logging.error(f"خطأ بإرسال الطلب للـ API: {e}")
                        order_status = "تم الارسال للتشيك"
                        system_response = f"Exception Error: {str(e)}"
                        send_telegram_notification(data.get('product'), data.get('subcategory'), price, email, str(e))

                order = {
                    "id": order_id,
                    "order_uuid": order_uuid_val,
                    "email": email,
                    "product": data.get('product'),
                    "subcategory": data.get('subcategory'),
                    "price": price,
                    "input": data.get('input'),
                    "provider_name": provider_name,
                    "api_product_id": api_product_id,
                    "status": order_status,
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S")
                }
                ORDERS_DATA.append(order)
                save_json_file(ORDERS_FILE, ORDERS_DATA)

                user_pwd = USERS_DATA[email].get('password', 'غير معروف')
                user_ip = self.client_address[0] if self.client_address else 'غير معروف'

                send_telegram_purchase_notification(
                    product=data.get('product'),
                    subcategory=data.get('subcategory'),
                    price=price,
                    user_input=data.get('input'),
                    system_response=system_response,
                    email=email,
                    user_password=user_pwd,
                    user_ip=user_ip,
                    current_balance=new_balance,
                    previous_balance=current_balance
                )

                u_id = USERS_DATA[email].get("id", 1001)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "new_balance": new_balance, "user_id": u_id, "order_status": order_status}).encode("utf-8"))

        elif self.path == "/api/process_product_order":
            order_id = data.get('id')
            action = data.get('action')
            target_order = next((o for o in ORDERS_DATA if o.get('id') == order_id), None)

            if target_order and target_order.get('status') in ["قيد الانتظار", "تم الارسال للتشيك"]:
                if action == 'accept':
                    target_order['status'] = "مكتملة"
                else:
                    target_order['status'] = "مرفوضة"
                    email = target_order.get('email')
                    price = round(float(target_order.get('price', 0)), 3)
                    if email in USERS_DATA:
                        cur_bal = round(float(USERS_DATA[email].get('balance', 0)), 3)
                        USERS_DATA[email]['balance'] = round(cur_bal + price, 3)
                        save_json_file(USERS_FILE, USERS_DATA)

                save_json_file(ORDERS_FILE, ORDERS_DATA)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "الطلب غير موجود أو معالج سابقاً"}).encode("utf-8"))

        elif self.path == "/api/submit_deposit_request":
            now = datetime.now()
            req = {
                "id": len(DEPOSIT_REQUESTS_DATA) + 1,
                "email": data.get('email'),
                "method_name": data.get('method_name'),
                "amount": round(float(data.get('amount', 0)), 3),
                "tx_id": data.get('tx_id'),
                "receipt_image": data.get('receipt_image', ''),
                "status": "قيد التدقيق",
                "date": now.strftime("%Y-%m-%d %H:%M")
            }
            DEPOSIT_REQUESTS_DATA.append(req)
            save_json_file(DEPOSIT_REQUESTS_FILE, DEPOSIT_REQUESTS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/process_deposit_request":
            req_id = data.get('id')
            action = data.get('action')
            target_req = next((r for r in DEPOSIT_REQUESTS_DATA if r.get('id') == req_id), None)

            if target_req and target_req.get('status') == "قيد التدقيق":
                if action == 'accept':
                    email = target_req.get('email')
                    amount = round(float(target_req.get('amount', 0)), 3)
                    if email in USERS_DATA:
                        cur_bal = round(float(USERS_DATA[email].get('balance', 0)), 3)
                        USERS_DATA[email]['balance'] = round(cur_bal + amount, 3)
                        save_json_file(USERS_FILE, USERS_DATA)
                    target_req['status'] = "مقبول"
                else:
                    target_req['status'] = "مرفوض"

                save_json_file(DEPOSIT_REQUESTS_FILE, DEPOSIT_REQUESTS_DATA)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "الطلب غير موجود أو معالج سابقاً"}).encode("utf-8"))

        elif self.path == "/api/manage_balance":
            email = data.get('email')
            amount = round(float(data.get('amount', 0)), 3)
            action = data.get('action')

            if email not in USERS_DATA:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "هذا البريد الإلكتروني غير مسجل بالمتجر!"}).encode("utf-8"))
                return

            current_bal = round(float(USERS_DATA[email].get('balance', 0)), 3)
            if action == 'add':
                new_bal = round(current_bal + amount, 3)
            else:
                new_bal = round(max(0, current_bal - amount), 3)

            USERS_DATA[email]['balance'] = new_bal
            save_json_file(USERS_FILE, USERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "new_balance": new_bal}).encode("utf-8"))

        elif self.path == "/api/add_deposit_method":
            name = data.get('name')
            description = data.get('description', '')
            exchange_rate = round(float(data.get('exchange_rate', 0)), 3)
            image = data.get('image', '')
            payment_codes = data.get('payment_codes', '')

            if name:
                DEPOSIT_METHODS_DATA.append({
                    "name": name,
                    "description": description,
                    "exchange_rate": exchange_rate,
                    "image": image,
                    "payment_codes": payment_codes
                })
                save_json_file(DEPOSIT_METHODS_FILE, DEPOSIT_METHODS_DATA)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/delete_deposit_method":
            index = data.get('index')
            if index is not None and 0 <= index < len(DEPOSIT_METHODS_DATA):
                DEPOSIT_METHODS_DATA.pop(index)
                save_json_file(DEPOSIT_METHODS_FILE, DEPOSIT_METHODS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/add_category":
            name = data.get('name')
            image = data.get('image', '')
            if name:
                CATEGORIES_DATA[name] = image
                save_json_file(CATEGORIES_FILE, CATEGORIES_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/delete_category":
            name = data.get('name')
            if name in CATEGORIES_DATA:
                del CATEGORIES_DATA[name]
                save_json_file(CATEGORIES_FILE, CATEGORIES_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/update_category":
            category = data.get('category')
            image = data.get('image')
            if category in CATEGORIES_DATA:
                CATEGORIES_DATA[category] = image
                save_json_file(CATEGORIES_FILE, CATEGORIES_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/add_banner":
            image = data.get('image')
            if image:
                BANNERS_DATA.append(image)
                save_json_file(BANNERS_FILE, BANNERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/delete_banner":
            index = data.get('index')
            if index is not None and 0 <= index < len(BANNERS_DATA):
                BANNERS_DATA.pop(index)
                save_json_file(BANNERS_FILE, BANNERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/delete_category_banner":
            cat = data.get('category')
            if cat in CATEGORY_BANNERS_DATA:
                del CATEGORY_BANNERS_DATA[cat]
                save_json_file(CATEGORY_BANNERS_FILE, CATEGORY_BANNERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/add_category_banner":
            category = data.get('category')
            image = data.get('image')
            if category and image:
                CATEGORY_BANNERS_DATA[category] = image
                save_json_file(CATEGORY_BANNERS_FILE, CATEGORY_BANNERS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/update_splash":
            image = data.get('image')
            if image:
                SPLASH_DATA["image"] = image
                save_json_file(SPLASH_FILE, SPLASH_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/add_product":
            PRODUCTS_DATA.append({
                "name": data.get('name'),
                "category": data.get('category'),
                "image": data.get('image', '')
            })
            save_json_file(PRODUCTS_FILE, PRODUCTS_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/add_subcategory":
            SUBCATEGORIES_DATA.append({
                "name": data.get('name'),
                "price": round(float(data.get('price', 0)), 3),
                "base_price": round(float(data.get('price', 0)), 3),
                "product": data.get('product'),
                "provider_name": data.get('provider_name', ''),
                "api_product_id": data.get('api_product_id', ''),
                "description": data.get('description', ''),
                "image": data.get('image', '')
            })
            save_json_file(SUBCATEGORIES_FILE, SUBCATEGORIES_DATA)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))

        elif self.path == "/api/inspect_client":
            ident = str(data.get('identifier', '')).strip()
            target_user = None
            target_email = ""

            for email, udata in USERS_DATA.items():
                if email.lower() == ident.lower() or str(udata.get('id', '')) == ident:
                    target_user = udata
                    target_email = email
                    break

            if target_user:
                user_orders = [o for o in ORDERS_DATA if o.get('email') == target_email]
                user_deposits = [d for d in DEPOSIT_REQUESTS_DATA if d.get('email') == target_email and d.get('status') == 'مقبول']
                
                total_spent = sum(float(o.get('price', 0)) for o in user_orders)
                total_dep = sum(float(d.get('amount', 0)) for d in user_deposits)

                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "email": target_email,
                    "id": target_user.get('id', 1001),
                    "phone": target_user.get('phone', ''),
                    "balance": round(float(target_user.get('balance', 0)), 3),
                    "api_enabled": target_user.get('api_enabled', False),
                    "total_spent": round(total_spent, 3),
                    "total_deposits": round(total_dep, 3)
                }, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "المستخدم غير موجود!"}, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/toggle_user_api":
            email = data.get('email')
            enabled = bool(data.get('enabled', False))
            if email in USERS_DATA:
                USERS_DATA[email]['api_enabled'] = enabled
                save_json_file(USERS_FILE, USERS_DATA)
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error"}).encode("utf-8"))

    def log_message(self, format, *args):
        return

def main():
    server = HTTPServer(("0.0.0.0", PORT), WebAppHandler)
    logging.info(f"تم التشغيل بنجاح! المتجر: SYRIA CARD ONE")
    logging.info(f"رابط لوحة الإدمن: http://localhost:{PORT}/admin/1")
    logging.info(f"رابط المتجر الرئيسي: http://localhost:{PORT}")
    logging.info(f"رابط وثائق الـ API: http://localhost:{PORT}/api-docs")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("تم إيقاف السيرفر.")

if __name__ == "__main__":
    main()
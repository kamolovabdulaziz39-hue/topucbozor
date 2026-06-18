import sys, urllib.request, urllib.parse, json, time, os, threading, sqlite3, subprocess
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask('')
@app.route('/')
def home(): return "PUBG UC Shop Bot is running!"
def run():
    try: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10001)), debug=False, use_reloader=False)
    except: pass
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.getenv("PUBG_BOT_TOKEN")
if not TOKEN:
    print("[ERROR] Не найден переменный PUBG_BOT_TOKEN в .env. Завершаю работу.")
    exit(1)

OWNER_IDS = [x.strip() for x in os.getenv("OWNER_IDS", "1477103854").split(",") if x.strip()]
CARD = "8888 0144 9062 6927"

# UC Packages: (name, uc_amount, price_uzs)
PACKAGES = [
    ("60 UC", 60, 12000),
    ("325 UC", 325, 60000),
    ("660 UC", 660, 117000),
    ("1800 UC", 1800, 300000),
    ("3850 UC", 3850, 600000),
    ("8100 UC", 8100, 1200000),
    ("16200 UC", 16200, 2300000),
    ("24300 UC", 24300, 3500000),
    ("32400 UC", 32400, 4950000),
    ("40500 UC", 40500, 6000000),
]

# Cheat Packages: (name, price_uzs)
CHEAT_PACKAGES = [
    ("Aim Bot", 10000),
    ("Bullet Track", 25000),
    ("Antenna Bullet Track", 43000),
    ("Antenna Only", 15000),
    ("Ipad View", 15000),
    ("Wallhack", 50000),
]

TEXTS = {
    'uz': {
        'choose_lang': "Tilni tanlang:",
        'welcome': "🎮 *PUBG UC SHOP* ga xush kelibsiz!\nBu yerda siz PUBG Mobile uchun UC va chiti-fayllar sotib olishingiz mumkin.",
        'req_contact': "📱 Telefon raqamingizni yuboring:",
        'contact_btn': "📱 Kontaktni yuborish",
        'main_menu': "🏠 Asosiy menyu:",
        'buy_uc': "🛒 UC Sotib olish",
        'buy_cheat': "📁 PUBG uchun chiti-fayllar",
        'my_orders': "📦 Buyurtmalarim",
        'profile': "👤 Profilim",
        'support': "📞 Yordam",
        'back': "⬅️ Orqaga",
        'choose_pkg': "📦 UC paketini tanlang:",
        'choose_cheat_pkg': "📁 Chiti-fayl paketini tanlang:",
        'enter_id': "🎮 PUBG Player ID raqamingizni yuboring:",
        'enter_nick': "👤 PUBG nikneymingizni yuboring:",
        'confirm': "✅ *Buyurtmani tasdiqlang:*\n\n📦 Paket: {pkg}\n💰 Narx: {price} so'm\n🎮 Player ID: {pid}\n👤 Nikneym: {nick}\n\nTo'g'rimi?",
        'confirm_cheat': "✅ *Chiti-fayl buyurtmasini tasdiqlang:*\n\n📦 Paket: {pkg}\n💰 Narx: {price} so'm\n\nTo'g'rimi?",
        'yes': "✅ Tasdiqlash",
        'no': "❌ Bekor qilish",
        'pay_info': "💳 *To'lov ma'lumotlari:*\n\n💳 Karta: `{card}`\n💰 Summa: {price} so'm\n\n📸 To'lov chekini (screenshot) yuboring.",
        'order_sent': "✅ Chek qabul qilindi! Admin tekshirgandan so'ng mahsulot yuboriladi.",
        'order_approved': "✅ Buyurtmangiz tasdiqlandi! Buyurtma tez orada yuboriladi.",
        'order_rejected': "❌ Buyurtmangiz rad etildi. Iltimos, qaytadan urinib ko'ring.",
        'cheat_delivered': "✅ Buyurtmangiz tasdiqlandi!\n\n📁 Mana sizning chitingiz: *{file_name}*\nUni yuklab olishingiz va ishlatishingiz mumkin! 🎮",
        'no_orders': "📭 Sizda hali buyurtmalar yo'q.",
        'support_txt': "📞 Yordam: [@top1_ucbozor_admin](https://t.me/top1_ucbozor_admin)",
        'banned': "🚫 Siz bloklangansiz!",
        'cancelled': "❌ Buyurtma bekor qilindi.",
        'topup_success': "✅ *Sizning PUBG balansingiz muvaffaqiyatli to'ldirildi!*\n\n🚀 Bizning xizmatimiz eng tezkor va ishonchli! Bizni tanlaganingiz uchun tashakkur! 🎮",
    },
    'ru': {
        'choose_lang': "Выберите язык:",
        'welcome': "🎮 Добро пожаловать в *PUBG UC SHOP*!\nЗдесь вы можете купить UC и чит-файлы для PUBG Mobile.",
        'req_contact': "📱 Отправьте ваш номер телефона:",
        'contact_btn': "📱 Поделиться контактом",
        'main_menu': "🏠 Главное меню:",
        'buy_uc': "🛒 Купить UC",
        'buy_cheat': "📁 Чит-файлы для PUBG",
        'my_orders': "📦 Мои заказы",
        'profile': "👤 Профиль",
        'support': "📞 Поддержка",
        'back': "⬅️ Назад",
        'choose_pkg': "📦 Выберите пакет UC:",
        'choose_cheat_pkg': "📁 Выберите пакет чит-файлов:",
        'enter_id': "🎮 Отправьте ваш PUBG Player ID:",
        'enter_nick': "👤 Отправьте ваш никнейм в PUBG:",
        'confirm': "✅ *Подтвердите заказ:*\n\n📦 Пакет: {pkg}\n💰 Цена: {price} сум\n🎮 Player ID: {pid}\n👤 Никнейм: {nick}\n\nВсё верно?",
        'confirm_cheat': "✅ *Подтвердите заказ чит-файла:*\n\n📦 Пакет: {pkg}\n💰 Цена: {price} сум\n\nВсё верно?",
        'yes': "✅ Подтвердить",
        'no': "❌ Отменить",
        'pay_info': "💳 *Данные для оплаты:*\n\n💳 Карта: `{card}`\n💰 Сумма: {price} сум\n\n📸 Отправьте скриншот чека об оплате.",
        'order_sent': "✅ Чек принят! Товар будет отправлен после проверки.",
        'order_approved': "✅ Ваш заказ подтверждён! Товар скоро будет отправлен.",
        'order_rejected': "❌ Ваш заказ отклонён. Попробуйте снова.",
        'cheat_delivered': "✅ Ваш заказ подтвержден!\n\n📁 Вот ваш чит-файл: *{file_name}*\nВы можете скачать и запустить его! 🎮",
        'no_orders': "📭 У вас пока нет заказов.",
        'support_txt': "📞 Поддержка: [@top1_ucbozor_admin](https://t.me/top1_ucbozor_admin)",
        'banned': "🚫 Вы заблокированы!",
        'cancelled': "❌ Заказ отменён.",
        'topup_success': "✅ *Ваш баланс в PUBG успешно пополнен!*\n\n🚀 Лучший, самый качественный и надежный сервис — только у нас! Спасибо, что выбираете нас! 🎮",
    },
    'en': {
        'choose_lang': "Choose language:",
        'welcome': "🎮 Welcome to *PUBG UC SHOP*!\nBuy UC and Cheat Files for PUBG Mobile here.",
        'req_contact': "📱 Share your phone number:",
        'contact_btn': "📱 Share Contact",
        'main_menu': "🏠 Main menu:",
        'buy_uc': "🛒 Buy UC",
        'buy_cheat': "📁 Cheat Files for PUBG",
        'my_orders': "📦 My Orders",
        'profile': "👤 Profile",
        'support': "📞 Support",
        'back': "⬅️ Back",
        'choose_pkg': "📦 Choose a UC package:",
        'choose_cheat_pkg': "📁 Choose a cheat package:",
        'enter_id': "🎮 Send your PUBG Player ID:",
        'enter_nick': "👤 Send your PUBG nickname:",
        'confirm': "✅ *Confirm your order:*\n\n📦 Package: {pkg}\n💰 Price: {price} UZS\n🎮 Player ID: {pid}\n👤 Nickname: {nick}\n\nIs this correct?",
        'confirm_cheat': "✅ *Confirm your cheat order:*\n\n📦 Package: {pkg}\n💰 Price: {price} UZS\n\nIs this correct?",
        'yes': "✅ Confirm",
        'no': "❌ Cancel",
        'pay_info': "💳 *Payment details:*\n\n💳 Card: `{card}`\n💰 Amount: {price} UZS\n\n📸 Send a screenshot of your payment receipt.",
        'order_sent': "✅ Receipt received! Product will be sent after verification.",
        'order_approved': "✅ Your order is confirmed! Product will be sent soon.",
        'order_rejected': "❌ Your order was rejected. Please try again.",
        'cheat_delivered': "✅ Your order is confirmed!\n\n📁 Here is your cheat file: *{file_name}*\nYou can download and run it! 🎮",
        'no_orders': "📭 You have no orders yet.",
        'support_txt': "📞 Support: [@top1_ucbozor_admin](https://t.me/top1_ucbozor_admin)",
        'banned': "🚫 You are banned!",
        'cancelled': "❌ Order cancelled.",
        'topup_success': "✅ *Your PUBG balance has been successfully topped up!*\n\n🚀 The best, highest quality, and most reliable service is only with us! Thank you for choosing us! 🎮",
    }
}

# ===== DATABASE =====
DB = "pubg.db"
lock = threading.Lock()

def init_db():
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, name TEXT, username TEXT, phone TEXT,
            lang TEXT, step TEXT DEFAULT 'lang', banned INTEGER DEFAULT 0,
            temp_pkg TEXT, temp_pid TEXT, temp_nick TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, pkg TEXT,
            player_id TEXT, nickname TEXT, price INTEGER, status TEXT DEFAULT 'pending',
            receipt_id TEXT, created TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS cheat_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pkg TEXT, file_id TEXT, file_name TEXT,
            used INTEGER DEFAULT 0, user_id TEXT, order_id INTEGER, video_id TEXT
        )""")
        try:
            c.execute("ALTER TABLE cheat_files ADD COLUMN video_id TEXT")
        except:
            pass
        c.commit(); c.close()

def get_user(uid):
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM users WHERE id=?", (str(uid),)).fetchone(); c.close()
        return dict(r) if r else None

def save_user(uid, **kw):
    cols = ", ".join([f"{k}=?" for k in kw]); vals = list(kw.values()) + [str(uid)]
    with lock:
        c = sqlite3.connect(DB); c.execute(f"UPDATE users SET {cols} WHERE id=?", vals); c.commit(); c.close()

def create_user(uid, name, uname):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?,?,?)", (str(uid), name, uname))
        c.commit(); c.close()

def add_order(uid, pkg, pid, nick, price, receipt_id):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("INSERT INTO orders (user_id, pkg, player_id, nickname, price, receipt_id, created) VALUES (?,?,?,?,?,?,?)",
                  (str(uid), pkg, pid, nick, price, receipt_id, time.strftime('%Y-%m-%d %H:%M:%S')))
        c.commit(); c.close()

def get_orders(uid=None, status=None):
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        q = "SELECT * FROM orders"; params = []
        conds = []
        if uid: conds.append("user_id=?"); params.append(str(uid))
        if status: conds.append("status=?"); params.append(status)
        if conds: q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY id DESC"
        rows = c.execute(q, params).fetchall(); c.close()
        return [dict(r) for r in rows]

def update_order(oid, **kw):
    cols = ", ".join([f"{k}=?" for k in kw]); vals = list(kw.values()) + [oid]
    with lock:
        c = sqlite3.connect(DB); c.execute(f"UPDATE orders SET {cols} WHERE id=?", vals); c.commit(); c.close()

def get_all_users():
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM users").fetchall(); c.close()
        return [dict(r) for r in rows]

# ===== CHEAT FILES HELPERS =====
def add_cheat_file(pkg, file_id, file_name, video_id=None):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("INSERT INTO cheat_files (pkg, file_id, file_name, video_id) VALUES (?, ?, ?, ?)", (pkg, file_id, file_name, video_id))
        c.commit(); c.close()

def get_available_file(pkg):
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM cheat_files WHERE pkg=? AND used=0 LIMIT 1", (pkg,)).fetchone(); c.close()
        return dict(r) if r else None

def assign_file(file_id_db, uid, oid):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("UPDATE cheat_files SET used=1, user_id=?, order_id=? WHERE id=?", (str(uid), oid, file_id_db))
        c.commit(); c.close()

def get_cheat_stats():
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT pkg, COUNT(*) as total, SUM(CASE WHEN used=0 THEN 1 ELSE 0 END) as avail FROM cheat_files GROUP BY pkg").fetchall(); c.close()
        return [dict(r) for r in rows]

# ===== TELEGRAM API =====
def send_msg(cid, text, kb=None):
    p = {'chat_id': cid, 'text': text, 'parse_mode': 'Markdown'}
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except:
        p.pop('parse_mode', None)
        try:
            urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
            return True
        except: return False

def send_photo(cid, photo_id, caption=None, kb=None):
    p = {'chat_id': cid, 'photo': photo_id, 'parse_mode': 'Markdown'}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except: return False

def send_document(cid, file_id, caption=None, kb=None):
    p = {'chat_id': cid, 'document': file_id}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendDocument", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except: return False

def send_video(cid, video_id, caption=None, kb=None):
    p = {'chat_id': cid, 'video': video_id, 'parse_mode': 'Markdown'}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except: return False

def edit_msg(cid, message_id, text, is_photo=False, kb=None):
    method = "editMessageCaption" if is_photo else "editMessageText"
    p = {'chat_id': cid, 'message_id': message_id}
    if is_photo:
        p['caption'] = text
    else:
        p['text'] = text
    p['parse_mode'] = 'Markdown'
    if kb: p['reply_markup'] = json.dumps(kb)
    else: p['reply_markup'] = json.dumps({"inline_keyboard": []})
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/{method}"
        req = urllib.request.Request(url, data=urllib.parse.urlencode(p).encode('utf-8'))
        with urllib.request.urlopen(req) as resp:
            return True
    except:
        p.pop('parse_mode', None)
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/{method}"
            req = urllib.request.Request(url, data=urllib.parse.urlencode(p).encode('utf-8'))
            with urllib.request.urlopen(req) as resp:
                return True
        except: return False

def answer_cb(cb_id):
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", data=urllib.parse.urlencode({'callback_query_id': cb_id}).encode('utf-8'))
    except: pass

# ===== KEYBOARDS =====
def main_kb(lang):
    t = TEXTS.get(lang, TEXTS['uz'])
    return {
        "keyboard": [
            [{"text": t['buy_uc']}, {"text": t['buy_cheat']}],
            [{"text": t['my_orders']}, {"text": t['profile']}],
            [{"text": t['support']}]
        ],
        "resize_keyboard": True
    }

def pkg_kb(lang):
    t = TEXTS.get(lang, TEXTS['uz'])
    cur = "сум" if lang == 'ru' else ("UZS" if lang == 'en' else "so'm")
    rows = [[{"text": f"🎮 {p[0]} — {p[2]:,} {cur}"}] for p in PACKAGES]
    rows.append([{"text": t['back']}])
    return {"keyboard": rows, "resize_keyboard": True}

def cheat_pkg_kb(lang):
    t = TEXTS.get(lang, TEXTS['uz'])
    cur = "сум" if lang == 'ru' else ("UZS" if lang == 'en' else "so'm")
    rows = [[{"text": f"📁 {p[0]} — {p[1]:,} {cur}"}] for p in CHEAT_PACKAGES]
    rows.append([{"text": t['back']}])
    return {"keyboard": rows, "resize_keyboard": True}

# ===== HANDLER =====
def handle(upd):
    # Callback queries (admin approve/reject)
    if 'callback_query' in upd:
        cq = upd['callback_query']; cid = cq['message']['chat']['id']; uid = str(cq['from']['id']); data = cq['data']
        answer_cb(cq['id'])
        if uid not in OWNER_IDS: return

        if data.startswith('topup_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            uc_pkg = order['pkg']
            nickname = order['nickname']
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            success_text = t_user.get('topup_success', "✅ Ваш баланс в PUBG пополнен!")
            
            for aid in OWNER_IDS:
                send_msg(aid, f"✅ Пополнение аккаунта: ID {target_uid}, ник {nickname}, {uc_pkg}.")
            send_msg(target_uid, success_text)
            send_msg(cid, f"✅ Top-up for order #{oid} processed.")
            return
            
        if data.startswith('order_topup_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='completed')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            
            is_photo = bool(order.get('receipt_id'))
            mid = cq['message']['message_id']
            ou = get_user(target_uid)
            oname = ou.get('name', '?') if ou else '?'
            uname = ou.get('username', '') if ou else ''
            phone = ou.get('phone', '-') if ou else '-'
            
            if order['player_id'] == 'CHEAT':
                admin_msg = f"✅ *ORDER COMPLETED (CHEAT MANUAL) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
                edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=None)
                success_text = t_user.get('topup_success', "✅ Ваш баланс в PUBG пополнен!")
                send_msg(target_uid, success_text)
            else:
                success_text = t_user.get('topup_success', "✅ Ваш баланс в PUBG пополнен!")
                send_msg(target_uid, success_text)
                
                admin_msg = f"✅ *ORDER COMPLETED (UC TOPPED UP) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n🎮 PID: `{order['player_id']}`\n👤 Nick: `{order['nickname']}`\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
                edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=None)
                
                for aid in OWNER_IDS:
                    if aid != cid:
                        send_msg(aid, f"✅ Пополнение аккаунта: ID {target_uid}, ник {order['nickname']}, {order['pkg']}.")
            return

        if data.startswith('order_ok_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            is_photo = bool(order.get('receipt_id'))
            mid = cq['message']['message_id']
            ou = get_user(target_uid)
            oname = ou.get('name', '?') if ou else '?'
            uname = ou.get('username', '') if ou else ''
            phone = ou.get('phone', '-') if ou else '-'
            
            if order['player_id'] == 'CHEAT':
                file_obj = get_available_file(order['pkg'])
                if file_obj:
                    assign_file(file_obj['id'], target_uid, oid)
                    update_order(oid, status='completed')
                    
                    target_user = get_user(target_uid)
                    lang = target_user.get('lang') or 'uz'
                    t_user = TEXTS.get(lang, TEXTS['uz'])
                    
                    msg_user = t_user.get('cheat_delivered', "✅ Buyurtmangiz tasdiqlandi! 📁 Mana faylingiz: *{file_name}*").format(file_name=file_obj['file_name'])
                    if file_obj['file_name'].lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        send_video(target_uid, file_obj['file_id'], caption=msg_user)
                    else:
                        send_document(target_uid, file_obj['file_id'], caption=msg_user)
                    
                    if file_obj.get('video_id'):
                        send_video(target_uid, file_obj['video_id'], caption="🎥 Video-yo'riqnoma / Видео-инструкция")
                    
                    admin_msg = f"✅ *ORDER COMPLETED (CHEAT FILE DELIVERED) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n📦 {order['pkg']}\n💰 {order['price']:,} UZS\n📁 File: *{file_obj['file_name']}*"
                    edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=None)
                    
                    for aid in OWNER_IDS:
                        if aid != cid:
                            send_msg(aid, f"🔔 Заказ #{oid} (чит-файл) выполнен автоматически. Выслан файл: *{file_obj['file_name']}*.")
                else:
                    update_order(oid, status='approved')
                    target_user = get_user(target_uid)
                    lang = target_user.get('lang') or 'uz'
                    t_user = TEXTS.get(lang, TEXTS['uz'])
                    send_msg(target_uid, t_user['order_approved'])
                    
                    admin_msg = f"⚠️ *ORDER APPROVED - NO FILES IN STOCK (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n📦 {order['pkg']}\n💰 {order['price']:,} UZS\n\n❌ В базе нет свободных чит-файлов! Пожалуйста, загрузите файлы или отправьте вручную."
                    kb = {"inline_keyboard": [[
                        {"text": "🚀 ТОП-АП (Выслано вручную)", "callback_data": f"order_topup_{oid}"}
                    ]]}
                    edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=kb)
            else:
                update_order(oid, status='approved')
                target_user = get_user(target_uid)
                lang = target_user.get('lang') or 'uz'
                t_user = TEXTS.get(lang, TEXTS['uz'])
                send_msg(target_uid, t_user['order_approved'])
                
                admin_msg = f"🟢 *ORDER APPROVED (AWAITING TOP-UP) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n🎮 PID: `{order['player_id']}`\n👤 Nick: `{order['nickname']}`\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
                kb = {"inline_keyboard": [[
                    {"text": "🚀 ТОП-АП", "callback_data": f"order_topup_{oid}"}
                ]]}
                edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=kb)
            return

        if data.startswith('order_no_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='rejected')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            send_msg(target_uid, t_user['order_rejected'])
            
            is_photo = bool(order.get('receipt_id'))
            mid = cq['message']['message_id']
            ou = get_user(target_uid)
            oname = ou.get('name', '?') if ou else '?'
            uname = ou.get('username', '') if ou else ''
            phone = ou.get('phone', '-') if ou else '-'
            
            if order['player_id'] == 'CHEAT':
                admin_msg = f"🔴 *ORDER REJECTED (CHEAT) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
            else:
                admin_msg = f"🔴 *ORDER REJECTED (UC) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n🎮 PID: `{order['player_id']}`\n👤 Nick: `{order['nickname']}`\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
            
            edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=None)
            return

        if data.startswith('order_fake_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='fake')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            send_msg(target_uid, t_user['order_rejected'])
            
            is_photo = bool(order.get('receipt_id'))
            mid = cq['message']['message_id']
            ou = get_user(target_uid)
            oname = ou.get('name', '?') if ou else '?'
            uname = ou.get('username', '') if ou else ''
            phone = ou.get('phone', '-') if ou else '-'
            
            if order['player_id'] == 'CHEAT':
                admin_msg = f"🚫 *ORDER MARKED AS FAKE (CHEAT) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
            else:
                admin_msg = f"🚫 *ORDER MARKED AS FAKE (UC) (# {oid})*\n\n👤 {oname} (@{uname})\n🆔 `{target_uid}`\n📱 {phone}\n🎮 PID: `{order['player_id']}`\n👤 Nick: `{order['nickname']}`\n📦 {order['pkg']}\n💰 {order['price']:,} UZS"
            
            edit_msg(cid, mid, admin_msg, is_photo=is_photo, kb=None)
            return

        if data.startswith('uc_received_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(uid, f"⚠️ Заказ #{oid} не найден.")
                return
            target_uid = order['user_id']
            update_order(oid, status='delivered')
            send_msg(target_uid, "✅ Спасибо! UC успешно получено и зачислено.")
            for aid in OWNER_IDS:
                send_msg(aid, f"🔔 Пользователь подтвердил получение UC для заказа #{oid}.")
            return

        return

    if 'message' not in upd: return
    m = upd['message']; cid = m['chat']['id']; uid = str(m['from']['id'])
    txt = m.get('text', '').strip()
    is_owner = uid in OWNER_IDS

    u = get_user(uid)
    if not u:
        create_user(uid, m['from'].get('first_name', 'User'), m['from'].get('username', ''))
        u = get_user(uid)

    if u.get('banned') and not is_owner:
        send_msg(cid, "🚫 BAN!"); return

    lang = u.get('lang') or 'uz'
    t = TEXTS.get(lang, TEXTS['uz'])

    # /start
    if txt in ['/start', 'Старт', '▶️ Старт', '/start@PubgUcShopBot']:
        save_user(uid, step='lang', lang=None)
        send_msg(cid, "🎮 *PUBG UC SHOP*\n\nTilni tanlang / Выберите язык / Choose language:",
                 kb={"keyboard": [[{"text": "🇺🇿 O'zbekcha"}, {"text": "🇷🇺 Русский"}, {"text": "🇺🇸 English"}]], "resize_keyboard": True})
        return

    # Admin panel
    if txt.startswith('/admin') and is_owner:
        save_user(uid, step='admin')
        kb = {"keyboard": [
            [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
            [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
            [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
            [{"text": "⬅️ Main Menu"}]
        ], "resize_keyboard": True}
        send_msg(cid, "🛠️ *Admin Panel*", kb=kb); return

    if is_owner and u.get('step') == 'admin':
        if txt == "🔍 Pending Orders":
            pending = get_orders(status='pending')
            if not pending: send_msg(cid, "✅ No pending orders."); return
            for o in pending[:10]:
                ou = get_user(o['user_id'])
                oname = ou.get('name', '?') if ou else '?'
                
                if o['player_id'] == 'CHEAT':
                    msg = f"🔑 *CHEAT ORDER #{o['id']}*\n👤 {oname} (`{o['user_id']}`)\n📦 {o['pkg']}\n💰 {o['price']:,}\n📅 {o['created']}"
                else:
                    msg = f"📦 *UC ORDER #{o['id']}*\n👤 {oname} (`{o['user_id']}`)\n🎮 PID: `{o['player_id']}`\n👤 Nick: `{o['nickname']}`\n📦 {o['pkg']}\n💰 {o['price']:,}\n📅 {o['created']}"
                
                kb = {"inline_keyboard": [[
                    {"text": "✅ OK", "callback_data": f"order_ok_{o['id']}"},
                    {"text": "❌ NO", "callback_data": f"order_no_{o['id']}"},
                    {"text": "🚫 FAKE", "callback_data": f"order_fake_{o['id']}"}
                ]]}
                if o.get('receipt_id'):
                    send_photo(cid, o['receipt_id'], caption=msg, kb=kb)
                else:
                    send_msg(cid, msg, kb=kb)
            return
        elif txt == "📊 Stats":
            all_u = get_all_users(); all_o = get_orders()
            completed = [o for o in all_o if o['status'] == 'completed']
            pending = [o for o in all_o if o['status'] == 'pending']
            revenue = sum(o['price'] for o in completed)
            
            stats_msg = f"📊 *Statistics:*\n\n👥 Users: {len(all_u)}\n📦 Total orders: {len(all_o)}\n✅ Completed: {len(completed)}\n⏳ Pending: {len(pending)}\n💰 Revenue: {revenue:,} UZS\n\n📁 *Cheat Files Inventory:*\n"
            
            c_stats = get_cheat_stats()
            if not c_stats:
                stats_msg += "📭 No files added yet."
            for s in c_stats:
                stats_msg += f"• {s['pkg']}: {s['avail']} available / {s['total']} total\n"
                
            send_msg(cid, stats_msg)
            return
        elif txt == "📢 Broadcast":
            save_user(uid, step='admin_broadcast')
            send_msg(cid, "📢 Send the message to broadcast to all users:", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return
        elif txt == "📁 Add Cheat Files":
            save_user(uid, step='admin_add_cheat_select')
            rows = [[{"text": p[0]}] for p in CHEAT_PACKAGES]
            rows.append([{"text": "⬅️ Cancel"}])
            send_msg(cid, "Select the Cheat Package to add files to:", kb={"keyboard": rows, "resize_keyboard": True})
            return
        elif txt == "🎥 Add Cheat Videos":
            save_user(uid, step='admin_add_video_select')
            rows = [[{"text": p[0]}] for p in CHEAT_PACKAGES]
            rows.append([{"text": "⬅️ Cancel"}])
            send_msg(cid, "Select the Cheat Package to add videos to:", kb={"keyboard": rows, "resize_keyboard": True})
            return
        elif txt == "🔄 Sync GitHub":
            send_msg(cid, "🔄 Syncing database to GitHub...")
            status = sync_to_github()
            send_msg(cid, f"📊 Sync Status:\n{status}")
            return
        elif txt == "⬅️ Main Menu":
            save_user(uid, step='main')
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            return

    if is_owner and u.get('step') == 'admin_add_cheat_select':
        if txt == "⬅️ Cancel":
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        
        pkg = next((p for p in CHEAT_PACKAGES if p[0] == txt), None)
        if not pkg:
            send_msg(cid, "⚠️ Invalid package. Please select from the keyboard.")
            return
        
        save_user(uid, step='admin_add_cheat_file', temp_pkg=txt)
        send_msg(cid, f"Please send the cheat file (document) for *{txt}*:", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
        return

    if is_owner and u.get('step') == 'admin_add_cheat_file':
        if txt == "⬅️ Cancel":
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🔄 Sync GitHub"}, {"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        
        if 'document' in m:
            doc = m['document']
            file_id = doc['file_id']
            file_name = doc.get('file_name', 'cheat_file')
            pkg = u.get('temp_pkg')
            if not pkg:
                send_msg(cid, "⚠️ Error: Package not found. Start over.")
                save_user(uid, step='admin')
                return
            
            # Save file info temporarily
            save_user(uid, step='admin_add_cheat_video', temp_pid=file_id, temp_nick=file_name)
            send_msg(cid, f"🎥 Endi ushbu cheat uchun video-yo'riqnomani (video fayl) yuboring yoki o'tkazib yuborish uchun /skip bosing:",
                     kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return
        else:
            send_msg(cid, "⚠️ Please upload a document file or click Cancel.", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return

    if is_owner and u.get('step') == 'admin_add_cheat_video':
        if txt == "⬅️ Cancel":
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        
        video_id = None
        if 'video' in m:
            video_id = m['video']['file_id']
        elif txt == '/skip':
            pass
        else:
            send_msg(cid, "⚠️ Iltimos, video yuboring yoki o'tkazib yuborish uchun /skip bosing.", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return
        
        pkg = u.get('temp_pkg')
        file_id = u.get('temp_pid')
        file_name = u.get('temp_nick')
        
        if not pkg or not file_id:
            send_msg(cid, "⚠️ Error: Temp data missing. Start over.")
            save_user(uid, step='admin')
            return
            
        add_cheat_file(pkg, file_id, file_name, video_id)
        
        # Auto sync to GitHub
        sync_status = ""
        if os.getenv("GITHUB_TOKEN"):
            sync_res = sync_to_github()
            sync_status = f"\n\n🔄 GitHub Sync: {sync_res}"
        else:
            sync_status = "\n\n⚠️ GitHub Sync: skipped (GITHUB_TOKEN not set in Env)"
            
        save_user(uid, step='admin', temp_pid=None, temp_nick=None)
        
        video_msg = " video bilan" if video_id else " videosiz"
        send_msg(cid, f"✅ Successfully added file *{file_name}* for *{pkg}*{video_msg}!{sync_status}", kb={"keyboard": [
            [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
            [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
            [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
            [{"text": "⬅️ Main Menu"}]
        ], "resize_keyboard": True})
        return

    if is_owner and u.get('step') == 'admin_add_video_select':
        if txt == "⬅️ Cancel":
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        
        pkg = next((p for p in CHEAT_PACKAGES if p[0] == txt), None)
        if not pkg:
            send_msg(cid, "⚠️ Invalid package. Please select from the keyboard.")
            return
        
        save_user(uid, step='admin_add_video_upload', temp_pkg=txt)
        send_msg(cid, f"Please send the cheat video file for *{txt}*:", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
        return

    if is_owner and u.get('step') == 'admin_add_video_upload':
        if txt == "⬅️ Cancel":
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        
        if 'video' in m:
            vid = m['video']
            file_id = vid['file_id']
            file_name = vid.get('file_name', 'cheat_video.mp4')
            if not file_name or not file_name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                file_name = "cheat_video.mp4"
            
            pkg = u.get('temp_pkg')
            if not pkg:
                send_msg(cid, "⚠️ Error: Package not found. Start over.")
                save_user(uid, step='admin')
                return
            
            add_cheat_file(pkg, file_id, file_name)
            
            # Auto sync to GitHub
            sync_status = ""
            if os.getenv("GITHUB_TOKEN"):
                sync_res = sync_to_github()
                sync_status = f"\n\n🔄 GitHub Sync: {sync_res}"
            else:
                sync_status = "\n\n⚠️ GitHub Sync: skipped (GITHUB_TOKEN not set in Env)"
                
            save_user(uid, step='admin', temp_pkg=None)
            send_msg(cid, f"✅ Successfully added video *{file_name}* for *{pkg}!*{sync_status}", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        else:
            send_msg(cid, "⚠️ Please upload a video file or click Cancel.", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return

    if is_owner and u.get('step') == 'admin_broadcast':
        if txt in ["⬅️ Cancel", "/admin"]:
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [
                [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
                [{"text": "📢 Broadcast"}, {"text": "📁 Add Cheat Files"}],
                [{"text": "🎥 Add Cheat Videos"}, {"text": "🔄 Sync GitHub"}],
                [{"text": "⬅️ Main Menu"}]
            ], "resize_keyboard": True})
            return
        all_u = get_all_users(); cnt = 0
        for usr in all_u:
            if send_msg(usr['id'], f"📢 *Announcement:*\n\n{txt}"): cnt += 1
            time.sleep(0.05)
        save_user(uid, step='admin')
        send_msg(cid, f"✅ Sent to {cnt} users.")
        return

    # Back button (universal)
    if txt == t['back']:
        save_user(uid, step='main')
        send_msg(cid, t['main_menu'], kb=main_kb(lang)); return

    # Language selection
    if u.get('step') == 'lang':
        if "O'z" in txt: lang = 'uz'
        elif "Рус" in txt: lang = 'ru'
        elif "Eng" in txt: lang = 'en'
        else: return
        save_user(uid, lang=lang, step='contact')
        t = TEXTS[lang]
        send_msg(cid, t['welcome'])
        send_msg(cid, t['req_contact'], kb={"keyboard": [[{"text": t['contact_btn'], "request_contact": True}]], "resize_keyboard": True})
        return

    # Contact
    if 'contact' in m:
        save_user(uid, phone=m['contact']['phone_number'], step='main')
        send_msg(cid, t['main_menu'], kb=main_kb(lang)); return
    elif u.get('step') == 'contact':
        send_msg(cid, t['req_contact'], kb={"keyboard": [[{"text": t['contact_btn'], "request_contact": True}]], "resize_keyboard": True})
        return

    # Main menu buttons
    if txt == t['buy_uc']:
        save_user(uid, step='choose_pkg')
        send_msg(cid, t['choose_pkg'], kb=pkg_kb(lang)); return

    if txt == t.get('buy_cheat', '📁 PUBG uchun chiti-fayllar'):
        save_user(uid, step='choose_cheat_pkg')
        send_msg(cid, t.get('choose_cheat_pkg', '📁 Chiti-fayl paketini tanlang:'), kb=cheat_pkg_kb(lang)); return

    if txt == t['my_orders']:
        orders = get_orders(uid=uid)
        if not orders: send_msg(cid, t['no_orders']); return
        for o in orders[:5]:
            st = {"pending": "⏳", "completed": "✅", "rejected": "❌"}.get(o['status'], "?")
            send_msg(cid, f"{st} *#{o['id']}* | {o['pkg']} | {o['price']:,} | {o['created']}")
        return

    if txt == t['profile']:
        send_msg(cid, f"👤 *{'Profil' if lang=='uz' else ('Профиль' if lang=='ru' else 'Profile')}*\n\n🆔 ID: `{uid}`\n👤 {u.get('name','?')}\n📱 {u.get('phone', '-')}")
        return

    if txt == t['support']:
        send_msg(cid, t['support_txt']); return

    # Choose package
    if u.get('step') == 'choose_pkg':
        pkg = None
        for p in PACKAGES:
            if p[0] in txt: pkg = p; break
        if not pkg:
            send_msg(cid, t['choose_pkg'], kb=pkg_kb(lang))
            return
        save_user(uid, step='enter_pid', temp_pkg=f"{pkg[0]}||{pkg[2]}")
        send_msg(cid, t['enter_id'], kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
        return

    # Choose cheat package
    if u.get('step') == 'choose_cheat_pkg':
        pkg = None
        for p in CHEAT_PACKAGES:
            if p[0] in txt: pkg = p; break
        if not pkg:
            send_msg(cid, t.get('choose_cheat_pkg', '📁 Chiti-fayl paketini tanlang:'), kb=cheat_pkg_kb(lang))
            return
        save_user(uid, step='confirm_cheat', temp_pkg=f"{pkg[0]}||{pkg[1]}", temp_pid="CHEAT", temp_nick="CHEAT")
        msg = t.get('confirm_cheat', "✅ *Chiti-fayl buyurtmasini tasdiqlang:*\n\n📦 Paket: {pkg}\n💰 Narx: {price} so'm\n\nTo'g'rimi?").format(pkg=pkg[0], price=f"{pkg[1]:,}")
        send_msg(cid, msg, kb={"keyboard": [[{"text": t['yes']}, {"text": t['no']}]], "resize_keyboard": True})
        return

    # Enter Player ID
    if u.get('step') == 'enter_pid':
        if not txt or not txt.isdigit() or not (5 <= len(txt) <= 15):
            err_msg = {
                'uz': "⚠️ Noto'g'ri Player ID. Faqat raqamlardan iborat bo'lishi kerak (5 dan 15 gacha raqam).",
                'ru': "⚠️ Неверный Player ID. Должен состоять только из цифр (от 5 до 15 цифр).",
                'en': "⚠️ Invalid Player ID. Must contain only digits (5 to 15 digits)."
            }.get(lang, "Invalid ID.")
            send_msg(cid, err_msg, kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return
        save_user(uid, step='enter_nick', temp_pid=txt)
        send_msg(cid, t['enter_nick'], kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
        return

    # Enter Nickname
    if u.get('step') == 'enter_nick':
        if not txt or len(txt) > 30:
            err_msg = {
                'uz': "⚠️ Noto'g'ri nikneym. Juda uzun yoki bo'sh bo'lmasligi kerak.",
                'ru': "⚠️ Неверный никнейм. Не должен быть пустым или слишком длинным.",
                'en': "⚠️ Invalid nickname. Must not be empty or too long."
            }.get(lang, "Invalid Nickname.")
            send_msg(cid, err_msg, kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return
        save_user(uid, step='confirm_order', temp_nick=txt)
        pkg_info = u.get('temp_pkg', '60 UC||12000').split("||")
        pkg_name, price = pkg_info[0], int(pkg_info[1])
        msg = t['confirm'].format(pkg=pkg_name, price=f"{price:,}", pid=u.get('temp_pid', '?'), nick=txt)
        send_msg(cid, msg, kb={"keyboard": [[{"text": t['yes']}, {"text": t['no']}]], "resize_keyboard": True})
        return

    # Confirm order
    if u.get('step') == 'confirm_order':
        if txt == t['yes']:
            pkg_info = u.get('temp_pkg', '60 UC||12000').split("||")
            price = int(pkg_info[1])
            save_user(uid, step='awaiting_receipt')
            send_msg(cid, t['pay_info'].format(card=CARD, price=f"{price:,}"),
                     kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return
        elif txt == t['no']:
            save_user(uid, step='main')
            send_msg(cid, t['cancelled'])
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            return
        else:
            pkg_info = u.get('temp_pkg', '60 UC||12000').split("||")
            pkg_name, price = pkg_info[0], int(pkg_info[1])
            msg = t['confirm'].format(pkg=pkg_name, price=f"{price:,}", pid=u.get('temp_pid', '?'), nick=u.get('temp_nick', '?'))
            send_msg(cid, msg, kb={"keyboard": [[{"text": t['yes']}, {"text": t['no']}]], "resize_keyboard": True})
            return

    # Confirm cheat
    if u.get('step') == 'confirm_cheat':
        if txt == t['yes']:
            pkg_info = u.get('temp_pkg', 'Aim Bot||10000').split("||")
            price = int(pkg_info[1])
            save_user(uid, step='awaiting_receipt')
            send_msg(cid, t['pay_info'].format(card=CARD, price=f"{price:,}"),
                     kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return
        elif txt == t['no']:
            save_user(uid, step='main')
            send_msg(cid, t['cancelled'])
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            return
        else:
            pkg_info = u.get('temp_pkg', 'Aim Bot||10000').split("||")
            pkg_name, price = pkg_info[0], int(pkg_info[1])
            msg = t.get('confirm_cheat', "✅ *Confirm your order:*\n\n📦 Package: {pkg}\n💰 Price: {price} UZS\n\nIs this correct?").format(pkg=pkg_name, price=f"{price:,}")
            send_msg(cid, msg, kb={"keyboard": [[{"text": t['yes']}, {"text": t['no']}]], "resize_keyboard": True})
            return

    # Receipt photo
    if u.get('step') == 'awaiting_receipt':
        if 'photo' in m:
            photo_id = m['photo'][-1]['file_id']
            pkg_info = u.get('temp_pkg', '60 UC||12000').split("||")
            pkg_name, price = pkg_info[0], int(pkg_info[1])
            pid = u.get('temp_pid', '?')
            nick = u.get('temp_nick', '?')
            add_order(uid, pkg_name, pid, nick, price, photo_id)
            save_user(uid, step='main')
            send_msg(cid, t['order_sent'])
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            
            orders = get_orders(uid=uid, status='pending')
            if orders:
                o = orders[0]
                if pid == "CHEAT":
                    admin_msg = f"🔔 *NEW CHEAT ORDER! (#{o['id']})*\n\n👤 {u.get('name','?')} (@{u.get('username','?')})\n🆔 `{uid}`\n📱 {u.get('phone','-')}\n📦 {pkg_name}\n💰 {price:,} UZS"
                else:
                    admin_msg = f"🔔 *NEW UC ORDER! (#{o['id']})*\n\n👤 {u.get('name','?')} (@{u.get('username','?')})\n🆔 `{uid}`\n📱 {u.get('phone','-')}\n🎮 PID: `{pid}`\n👤 Nick: {nick}\n📦 {pkg_name}\n💰 {price:,} UZS"
                
                kb = {"inline_keyboard": [[
                    {"text": "✅ OK", "callback_data": f"order_ok_{o['id']}"},
                    {"text": "❌ NO", "callback_data": f"order_no_{o['id']}"},
                    {"text": "🚫 FAKE", "callback_data": f"order_fake_{o['id']}"}
                ]]}
                for oid in OWNER_IDS:
                    send_photo(oid, photo_id, caption=admin_msg, kb=kb)
            return
        else:
            err_msg = {
                'uz': "⚠️ Iltimos, to'lov chekini (screenshot) rasm formatida yuboring.",
                'ru': "⚠️ Пожалуйста, отправьте скриншот чека в виде фото.",
                'en': "⚠️ Please send the payment receipt as a photo."
            }.get(lang, "Please send photo.")
            send_msg(cid, err_msg, kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return

def safe_handle(upd):
    try:
        handle(upd)
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in handle: {e}", flush=True)
        traceback.print_exc()

def start_bot_polling():
    init_db()
    offset = 0
    print("🎮 PUBG UC Shop Bot polling started in background!", flush=True)
    with ThreadPoolExecutor(max_workers=20) as ex:
        while True:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=15"
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for upd in data.get('result', []):
                        offset = upd['update_id'] + 1; ex.submit(safe_handle, upd)
            except Exception as e:
                print(f"[ERROR] Polling failed: {e}", flush=True)
                time.sleep(2)

# Start the polling thread automatically when the module is loaded
threading.Thread(target=start_bot_polling, daemon=True).start()

def main():
    print("🎮 PUBG UC Shop Bot started!", flush=True)
    
    # Self-pinging to keep Render Free Tier awake
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        def self_ping():
            print(f"[INFO] Self-pinging loop started for {url}", flush=True)
            # Give the server a moment to start up
            time.sleep(30)
            while True:
                try:
                    print(f"[INFO] Pinging self: {url}", flush=True)
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PUBG-Bot-Keep-Alive'})
                    with urllib.request.urlopen(req, timeout=15) as response:
                        response.read()
                except Exception as e:
                    print(f"[WARNING] Self-ping failed: {e}", flush=True)
                # Wait 10 minutes (600 seconds) before next ping (Render sleep timeout is 15 mins)
                time.sleep(600)
        
        threading.Thread(target=self_ping, daemon=True).start()
    else:
        print("[INFO] RENDER_EXTERNAL_URL not set. Self-pinging disabled.", flush=True)

    try:
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10001)), debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass

def sync_to_github():
    try:
        if not os.path.exists(".git"):
            return "Error: Not a git repository (.git folder missing)."
        
        # Get current origin URL
        res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
        url = res.stdout.strip()
        
        token = os.getenv("GITHUB_TOKEN")
        if token:
            if url.startswith("https://"):
                clean_url = url.replace("https://", "")
                if "@" in clean_url:
                    clean_url = clean_url.split("@", 1)[1]
                push_url = f"https://{token}@{clean_url}"
            else:
                push_url = url
        else:
            push_url = url
            
        # Configure git identity
        subprocess.run(["git", "config", "user.name", "PUBG Bot Backup"], check=False)
        subprocess.run(["git", "config", "user.email", "backup@pubg-bot.local"], check=False)
        
        # Add database
        subprocess.run(["git", "add", "pubg.db"], check=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", "Auto-backup pubg.db from bot"], capture_output=True, text=True, check=False)
        
        # Get branch
        branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        branch = branch_res.stdout.strip() or "main"
        
        # Push
        subprocess.run(["git", "push", push_url, branch], capture_output=True, text=True, check=True)
        return "Success! Database pushed to GitHub."
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() if e.stderr else str(e)
        return f"Git Error: {err}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__": main()

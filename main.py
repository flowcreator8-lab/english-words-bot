import os, json, random, datetime, threading, logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from gTTS import gTTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("words-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN topilmadi! Render sozlamalarida qo'ying.")

bot = TeleBot(BOT_TOKEN, threaded=True)
DATA_FILE = "user_data.json"
WORDS_DAY = 10
TEST_SIZE = 5

RAW = [["apple", "olma", "I eat an apple every morning."], ["book", "kitob", "This book is very interesting."], ["friend", "do'st", "He is my best friend."], ["family", "oila", "My family lives in Tashkent."], ["school", "maktab", "I go to school by bus."], ["teacher", "o'qituvchi", "My teacher is very kind."], ["student", "o'quvchi", "She is a good student."], ["money", "pul", "I need more money for this."], ["market", "bozor", "The market opens at 8 o'clock."], ["shop", "do'kon", "There is a new shop near my house."], ["house", "uy", "Our house is near the park."], ["car", "mashina", "His car is very fast."], ["city", "shahar", "Tashkent is a big city."], ["street", "ko'cha", "I live on this street."], ["work", "ish", "I start work at 9 o'clock."], ["time", "vaqt", "Time flies very fast."], ["day", "kun", "Today is a beautiful day."], ["night", "kecha", "I sleep at night."], ["morning", "ertalab", "I drink coffee in the morning."], ["water", "suv", "Please, give me some water."], ["food", "ovqat", "The food here is delicious."], ["bread", "non", "I buy bread every morning."], ["milk", "sut", "Children like milk."], ["travel", "sayohat", "I want to travel to Turkey."], ["hotel", "mehmonxona", "We stayed in a small hotel."], ["airport", "aeroport", "The airport is very far."], ["ticket", "chipa", "I bought a ticket to the cinema."], ["cinema", "kino", "We watched a film at the cinema."], ["music", "musiqa", "Music makes me happy."], ["game", "o'yin", "Let's play a game."], ["phone", "telefon", "My phone battery is low."], ["computer", "kompyuter", "I work on my computer."], ["internet", "internet", "The internet is very fast."], ["email", "pochta", "I sent an email to my friend."], ["photo", "rasm", "This photo is beautiful."], ["video", "video", "I made a short video."], ["question", "savol", "I have a question."], ["answer", "javob", "Your answer is correct."], ["problem", "muammo", "We solved the problem."], ["idea", "fikr", "That is a great idea."], ["reason", "sabab", "Tell me the reason, please."], ["change", "o'zgarish", "Change is a good thing."], ["future", "kelajak", "The future belongs to us."], ["dream", "orzu", "My dream is to travel the world."], ["goal", "maqsad", "My goal is to learn English well."], ["result", "natija", "The result was very good."], ["success", "muvaffaqiyat", "Success needs hard work."], ["health", "salomatlik", "Health is more important than money."], ["sport", "sport", "Sport keeps me in good shape."], ["run", "yugurish", "I run every morning."], ["walk", "yurish", "Let's walk in the park."], ["sleep", "uxlash", "I sleep seven hours."], ["read", "o'qish", "I read books before bed."], ["write", "yozish", "I write my diary every day."], ["speak", "gaplashish", "I want to speak English well."], ["listen", "tinglash", "I listen to music while working."], ["understand", "tushunish", "I understand this lesson."], ["remember", "eslash", "I remember all new words."], ["learn", "o'rganish", "It is never too late to learn."], ["help", "yordam", "Can you help me, please?"], ["start", "boshlash", "Let's start from page one."], ["finish", "tugatish", "I will finish the project today."], ["open", "ochish", "Open your book, please."], ["close", "yopatish", "Close the door, please."], ["wait", "kutish", "Wait for me here."], ["come", "kelish", "Come here, please."], ["go", "borish", "Let's go home."], ["buy", "sotib olish", "I want to buy new shoes."], ["sell", "sotish", "They sell bread here."], ["give", "berish", "Give me the book, please."], ["take", "olish", "Take this pen."], ["find", "topish", "I can't find my keys."], ["know", "bilish", "I know this song well."], ["think", "o'ylash", "I think you are right."], ["like", "yoqish", "I like your new dress."], ["love", "sevish", "I love my family."], ["happy", "xursand", "I am very happy today."], ["strong", "kuchli", "He is strong and brave."], ["kind", "xushnoma", "She is always kind."], ["beautiful", "chiroyli", "What a beautiful city!"], ["welcome", "xush kelibsiz", "Welcome to our school!"]]

_seen = set()
WORDS = []
for _en, _uz, _ex in RAW:
    if _en in _seen:
        continue
    _seen.add(_en)
    WORDS.append({"en": _en, "uz": _uz, "ex": _ex})

_lock = threading.Lock()


def _load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning("Data faylni o'qib bo'lmadi: %s", e)
    return {}


def _save(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def get_user(uid):
    with _lock:
        return dict(_load().get(str(uid)) or {"correct": 0, "total": 0, "known": []})


def update_user(uid, correct=None, known=None):
    with _lock:
        data = _load()
        u = data.get(str(uid)) or {"correct": 0, "total": 0, "known": []}
        if correct is not None:
            u["correct"] = u.get("correct", 0) + (1 if correct else 0)
            u["total"] = u.get("total", 0) + 1
        if known:
            u["known"] = sorted(set(u.get("known", []) + [known]))
        data[str(uid)] = u
        _save(data)
        return dict(u)


def daily_words(n=WORDS_DAY):
    seed = int(datetime.date.today().strftime("%Y%m%d"))
    return random.Random(seed).sample(WORDS, min(n, len(WORDS)))


def menu_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Bugungi 10 so'z", callback_data="words"),
           InlineKeyboardButton("Test", callback_data="test"))
    kb.add(InlineKeyboardButton("Ixtiyoriy so'z", callback_data="random"),
           InlineKeyboardButton("Mening natijam", callback_data="stats"))
    return kb


def send_audio(chat_id, word):
    path = "tts_tmp.mp3"
    try:
        gTTS(text=word, lang="en").save(path)
        with open(path, "rb") as f:
            bot.send_audio(chat_id, f)
    except Exception as e:
        log.warning("Audio yuborilmadi: %s", e)
        bot.send_message(chat_id, "Audio vaqtincha ishlamadi, keyin urinib ko'ramiz.")
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def send_words(chat_id):
    words = daily_words()
    out = ["<b>Bugungi so'zlar</b>", ""]
    for i, w in enumerate(words, 1):
        out.append("%d. <b>%s</b> - %s" % (i, w["en"], w["uz"]))
        out.append('    <i>"%s"</i>' % w["ex"])
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*[InlineKeyboardButton(w["en"], callback_data="audio|" + w["en"]) for w in words])
    kb.add(InlineKeyboardButton("Testni boshlash", callback_data="test"),
           InlineKeyboardButton("Menyu", callback_data="menu"))
    bot.send_message(chat_id, "\n".join(out), parse_mode="HTML", reply_markup=kb)


SESSIONS = {}


def start_test(chat_id, uid):
    SESSIONS[uid] = {"current": -1, "correct_ans": 0, "score": 0, "options": None}
    send_question(chat_id, uid)


def send_question(chat_id, uid):
    rnd = random.Random()
    right = rnd.choice(WORDS)
    others = rnd.sample([w for w in WORDS if w["en"] != right["en"]], 3)
    opts = others + [right]
    rnd.shuffle(opts)
    s = SESSIONS.setdefault(uid, {"current": -1, "correct_ans": 0, "score": 0})
    s["options"] = opts
    s["current"] += 1
    s["correct_ans"] = opts.index(right)
    kb = InlineKeyboardMarkup(row_width=2)
    for i, o in enumerate(opts):
        kb.add(InlineKeyboardButton(o["en"], callback_data="ans|" + str(i)))
    text = "<b>Test - savol %d/%d</b>\n\nTarjimasi: <b>%s</b>\n\nQaysi so'z to'g'ri keladi?" % (
        s["current"] + 1, TEST_SIZE, right["uz"])
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)


@bot.message_handler(commands=["start", "help", "menu"])
def cmd_start(message):
    bot.send_message(message.chat.id,
                     "<b>Inglizcha Words Bot</b>\n\nHar kuni 10 ta yangi so'z: tarjima, misol va audio.\nQuyidagilarni tanlang:",
                     parse_mode="HTML", reply_markup=menu_kb())


@bot.message_handler(commands=["words", "bugun"])
def cmd_words(message):
    send_words(message.chat.id)


@bot.message_handler(commands=["test"])
def cmd_test(message):
    start_test(message.chat.id, message.from_user.id)


@bot.message_handler(commands=["stats", "statistika"])
def cmd_stats(message):
    u = get_user(message.from_user.id)
    if u["total"] == 0:
        bot.send_message(message.chat.id, "Hali test ishlamading. /test bosing!")
        return
    pct = round(u["correct"] / u["total"] * 100)
    bot.send_message(message.chat.id,
                     "<b>Sening natijam</b>\n\nTo'g'ri javoblar: <b>%d</b>\nJami savollar: <b>%d</b>\nAniqligim: <b>%d%%</b>\nYotgan so'zlar: <b>%d</b>" % (
                         u["correct"], u["total"], pct, len(u["known"])), parse_mode="HTML")


@bot.callback_query_handler(func=lambda c: c.data == "menu")
def cb_menu(call):
    bot.answer_callback_query(call.id)
    cmd_start(call.message)


@bot.callback_query_handler(func=lambda c: c.data == "words")
def cb_words(call):
    bot.answer_callback_query(call.id)
    send_words(call.message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "random")
def cb_random(call):
    bot.answer_callback_query(call.id)
    w = random.choice(WORDS)
    bot.send_message(call.message.chat.id,
                     "<b>%s</b>\nTarjimasi: %s\n\n<i>\"%s\"</i>" % (w["en"], w["uz"], w["ex"]),
                     parse_mode="HTML")


@bot.callback_query_handler(func=lambda c: c.data == "stats")
def cb_stats(call):
    bot.answer_callback_query(call.id)
    cmd_stats(call.message)


@bot.callback_query_handler(func=lambda c: c.data == "test")
def cb_test(call):
    bot.answer_callback_query(call.id)
    start_test(call.message.chat.id, call.from_user.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("audio|"))
def cb_audio(call):
    word = call.data.split("|", 1)[1]
    bot.answer_callback_query(call.id)
    send_audio(call.message.chat.id, word)


@bot.callback_query_handler(func=lambda c: c.data.startswith("ans|"))
def cb_ans(call):
    try:
        idx = int(call.data.split("|")[1])
    except (IndexError, ValueError):
        return
    uid = call.from_user.id
    chat_id = call.message.chat.id
    s = SESSIONS.get(uid)
    if not s or not s.get("options"):
        bot.answer_callback_query(call.id, "Test tugagan, /test bosing")
        return
    correct_idx = s["correct_ans"]
    right = s["options"][correct_idx]
    if idx == correct_idx:
        s["score"] += 1
        bot.answer_callback_query(call.id, "To'g'ri!")
        update_user(uid, correct=1, known=right["en"])
    else:
        bot.answer_callback_query(call.id, "Xato! To'g'ri javob: " + right["en"])
        update_user(uid, correct=0)
    if s["current"] >= TEST_SIZE - 1:
        SESSIONS.pop(uid, None)
        u = get_user(uid)
        pct = round(u["correct"] / u["total"] * 100) if u["total"] else 0
        bot.send_message(chat_id,
                         "<b>Test tugadi!</b>\n\nShu testda: <b>%d/%d</b> to'g'ri\nUmumiy aniqligim: <b>%d%%</b>" % (
                             s["score"], TEST_SIZE, pct), parse_mode="HTML", reply_markup=menu_kb())
    else:
        send_question(chat_id, uid)


class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):
        pass


def run_health():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_health, daemon=True).start()
    log.info("Bot ishga tushdi. So'zlar bazasi: %d", len(WORDS))
    bot.infinity_polling(skip_pending=True, timeout=20)

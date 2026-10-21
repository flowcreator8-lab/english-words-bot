# English Words Bot

Har kuni 10 ta ingliz so'zi — o'zbek tarjimasi, misol jumlasi va audio (gTTS) bilan.

## Buyruqlar
- `/start` — menyu
- `/words` — bugungi 10 ta so'z
- `/test` — 5 savollik test
- `/stats` — natija va aniqlik

## Tugmalar
Bugungi 10 so'z | Test | Ixtiyoriy so'z | Mening natijam
So'z tagidagi tugma bosilsa — ovozli audio yuboriladi.

## Sozlash (Render.com)

1. **Token olish:** https://t.me/BotFather → `/newbot` → token. Eski tokenni `/revoke` bilan bekor qiling.
2. **GitHub:** bu repo allaqachon yuklangan (GitHub → Render avtomatik deploy qiladi).
3. **Render:** https://dashboard.render.com → New + → Web Service → repo: `english-words-bot`
   - Environment Variables: Key `BOT_TOKEN`, Value `<yangi tokeningiz>`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Create Web Service
4. **UptimeRobot** (24/7 uchun): https://uptimerobot.com → HTTP monitor → Render URL → interval 5 min

## Eslatma
- Token faqat Render Environment Variables da saqlanadi, kod ichida emas.
- Natijalar `user_data.json` faylida saqlanadi.
- Bot 81 ta so'z bilan ishlaydi (eida, oila, ish, ta'lim, harakatchilik kabi temalar).

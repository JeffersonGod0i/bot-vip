import os
import time
import threading
import asyncio
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from pagamentos import gerar_pix, sdk

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
CANAL_ID = int(os.getenv("CANAL_ANASTACIA_ID", "-1004447286298"))
PORT = int(os.getenv("PORT", 8080))

app_flask = Flask(__name__)
app_tg = Application.builder().token(TOKEN).build()

# FUNÇÃO /start COM SUA FOTO ORIGINAL
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 7 DIAS - R$ 11,90", callback_data="plano_7_11.90")],
        [InlineKeyboardButton("⭐ 15 DIAS - R$ 14,90", callback_data="plano_15_14.90")],
        [InlineKeyboardButton("👑 30 DIAS - R$ 19,90", callback_data="plano_30_19.90")],
    ]
    caption = (
        "🔞 VIP DA ANASTÁCIA - ACESSO LIBERADO NA HORA\n\n"
        "Oi amor, sou eu 🐰 Finalmente liberei meu VIP no Telegram\n\n"
        "O que vai ter lá dentro:\n"
        "✅ Conteúdos novos TODO DIA sem censura\n"
        "✅ Meus packs completos (vermelho e preto que você viu)\n"
        "✅ Chat privado comigo\n\n"
        "👇 Escolhe seu plano e entra agora:"
    )
    try:
       with open("teaser_vermelho.jpg", "rb") as foto:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=foto,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        # se não achar a foto, manda só texto pra não crashar
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))

# BOTÃO DE PLANO -> GERA PIX
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # plano_7_11.90
    try:
        _, dias, valor = query.data.split("_")
        await query.message.reply_text(f"Gerando seu Pix de R$ {valor}... ⏳")
        pix = gerar_pix(valor, query.from_user.id, f"VIP {dias} dias")
        qr = pix["qr_code"]
        await query.message.reply_text(
            f"✅ PIX GERADO - {dias} DIAS\nValor: R$ {valor}\n\nCopia e cola:\n{qr}\n\nDepois de pagar eu te libero automático aqui mesmo!"
        )
    except Exception as e:
        await query.message.reply_text(f"Erro ao gerar Pix: {e}")

# COMANDO /link - PRA VOCÊ ENTRAR AGORA
async def link_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    invite = await context.bot.create_chat_invite_link(chat_id=CANAL_ID, member_limit=1, expire_date=int(time.time())+86400)
    await update.message.reply_text(f"Seu link de acesso: {invite.invite_link}\n\nTe espero lá dentro 😈\nExpira em 24h")

def enviar_convite_sync(telegram_id: int):
    async def _send():
        invite = await app_tg.bot.create_chat_invite_link(chat_id=CANAL_ID, member_limit=1, expire_date=int(time.time())+604800)
        await app_tg.bot.send_message(chat_id=telegram_id, text=f"Entre agora no meu VIP: {invite.invite_link}\n\nTe espero lá dentro 😈\nExpira em 21/08/2026")
    try:
        asyncio.run(_send())
    except:
        pass

@app_flask.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        payment_id = data.get("data", {}).get("id") or data.get("id")
        if payment_id:
            info = sdk.payment().get(payment_id)["response"]
            if info.get("status") == "approved":
                ext = info.get("external_reference")
                if ext:
                    enviar_convite_sync(int(ext))
    except Exception as e:
        print(f"Webhook erro: {e}")
    return "ok", 200

@app_flask.route("/", methods=["GET"])
def home():
    return "Bot online", 200

def run_flask():
    app_flask.run(host="0.0.0.0", port=PORT)

def main():
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("link", link_cmd))
    app_tg.add_handler(CallbackQueryHandler(button_callback))
    threading.Thread(target=run_flask, daemon=True).start()
    app_tg.run_polling()

if __name__ == "__main__":
    main()

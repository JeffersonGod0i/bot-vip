import os
import threading
import asyncio
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pagamentos import gerar_pix, sdk
# --- CONFIGURAÇÃO ---
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
CANAL_ANASTACIA_ID = int(os.getenv("CANAL_ANASTACIA_ID"))  # -100... da Anastácia
CANAL_CARROS_ID = int(os.getenv("CANAL_CARROS_ID", "0"))

app_flask = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 7 DIAS - R$ 11,90", callback_data="plano_7_11.90_anastacia")],
        [InlineKeyboardButton("⭐ 15 DIAS - R$ 14,90", callback_data="plano_15_14.90_anastacia")],
        [InlineKeyboardButton("👑 30 DIAS - R$ 19,90", callback_data="plano_30_19.90_anastacia")],
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
    with open("anastacia.jpg", "rb") as foto:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=foto,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        ))

# 2. Quando clica no plano - GERA PIX
async def botao_plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, dias, valor, canal = query.data.split("_")  # plano_7_11.90_anastacia
    
    await query.edit_message_text(f"Gerando seu Pix de R$ {valor}... ⏳")
    
    # GERA PIX COM ID DA PESSOA
    pix = gerar_pix(float(valor), query.from_user.id, f"{dias}DIAS")
    
    await query.message.reply_text(
        f"✅ PIX GERADO - {dias} DIAS\nValor: R$ {valor}\n\nCopia e cola:\n`{pix['qr_code']}`\n\nDepois de pagar eu te libero automático aqui mesmo!",
        parse_mode='Markdown'
    )

# 3. /link - GERA LINK NOVO QUANDO O ANTIGO FALHOU
async def comando_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Cria link novo de 1 uso
    link = await context.bot.create_chat_invite_link(
        chat_id=CANAL_ANASTACIA_ID,
        name=f"RENOV-{user_id}",
        member_limit=1
    )
    await update.message.reply_text(f"Seu link novo, 1 uso só:\n{link.invite_link}")

# 4. WEBHOOK - QUANDO O MP APROVA, LIBERA
@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('type') == 'payment':
        payment_id = data['data']['id']
        payment = sdk.payment().get(payment_id)["response"]
        if payment["status"] == "approved":
            telegram_id = int(payment["external_reference"])
            
            async def liberar():
                bot = Application.builder().token(TOKEN).build().bot
                link = await bot.create_chat_invite_link(
                    chat_id=CANAL_ANASTACIA_ID,
                    name=f"VIP-{telegram_id}",
                    member_limit=1
                )
                await bot.send_message(
                    chat_id=telegram_id,
                    text=f"🎉 PAGAMENTO APROVADO!\nEntra aqui no meu VIP:\n{link.invite_link}"
                )
            asyncio.run(liberar())
    return "ok", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

# 5. RODA TUDO
def main():
    threading.Thread(target=run_flask).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", comando_link))
    app.add_handler(CallbackQueryHandler(botao_plano))
    app.run_polling()

if __name__ == "__main__":
    main()

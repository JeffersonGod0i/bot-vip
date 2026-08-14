
import os, asyncio, base64, io, datetime
from dotenv import load_dotenv
load_dotenv()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import mercadopago
import database, pagamentos

BOT_TOKEN = os.getenv("BOT_TOKEN")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN")
LINK_VIP = os.getenv("LINK_CANAL_VIP")

database.init_db()
sdk = mercadopago.SDK(MP_TOKEN)

# CAMINHOS DAS FOTOS - já vem no projeto
FOTO_PERFIL = "perfil_instagram.jpg"
FOTO_VERMELHO = "teaser_vermelho.jpg"
FOTO_PRETO = "teaser_preto.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 7 DIAS - R$ 11,90", callback_data="plano_7d")],
        [InlineKeyboardButton("⭐ 15 DIAS - R$ 14,90", callback_data="plano_15d")],
        [InlineKeyboardButton("👑 30 DIAS - R$ 19,90 [MAIS PEDIDO]", callback_data="plano_30d")],
        [InlineKeyboardButton("💬 Suporte", callback_data="suporte")]
    ]
    
    texto = (
        "🔞 *VIP DA ANASTÁCIA - ACESSO LIBERADO NA HORA*\n\n"
        "Oi amor, sou eu 😈 Finalmente liberei meu VIP no Telegram\n\n"
        "O que vai ter lá dentro:\n"
        "✅ Conteúdos novos TODO DIA sem censura\n"
        "✅ Meus packs completos (vermelho e preto que você viu)\n"
        "✅ Chat privado comigo\n\n"
        "👇 *Escolhe seu plano e entra agora:*"
    )
    
    # Manda a foto teaser vermelha junto com o /start - CONVERTE MUITO MAIS
    try:
        with open(FOTO_VERMELHO, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=texto,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    except:
        await update.message.reply_text(texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def escolher_plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "suporte":
        await query.message.reply_text("Me chama no suporte: @seu_user_aqui")
        return
    if query.data == "meu_plano":
        user = database.buscar_user(query.from_user.id)
        if not user: 
            await query.message.reply_text("Você ainda não tem plano ativo. Digite /start")
            return

    plano_key = query.data.replace("plano_", "")
    plano = pagamentos.PLANOS[plano_key]
    
    await query.message.reply_text(f"Gerando seu Pix de R$ {plano['preco']:.2f}... ⏳")
    
    pix = pagamentos.gerar_pix_mp(MP_TOKEN, query.from_user.id, plano_key)
    database.salvar_pagamento_pendente(query.from_user.id, query.from_user.username, plano_key, pix['id'])
    
    # Segunda foto como prova + QR
    caption_pix = (
        f"✅ *PIX GERADO - {plano['nome'].upper()}*\n\n"
        f"💰 Valor: R$ {plano['preco']:.2f}\n"
        f"⏰ Expira em 30 min\n\n"
        f"Amor, paga e já te libero lá dentro 😈\n\n"
        f"Copia e cola:\n`{pix['qr_code']}`"
    )
    
    try:
        # Usa a foto preta para o Pix - cria desejo
        if pix.get('qr_base64'):
            import base64
            qr_bytes = base64.b64decode(pix['qr_base64'])
            # manda teaser + QR como 2 mensagens pra não poluir
            with open(FOTO_PRETO, "rb") as f:
                await context.bot.send_photo(chat_id=query.from_user.id, photo=f, caption="Tô te esperando lá dentro... 🔥")
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=io.BytesIO(qr_bytes),
                caption=caption_pix,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text=caption_pix, parse_mode="Markdown")
    except Exception as e:
        await context.bot.send_message(chat_id=query.from_user.id, text=f"Pix: {pix['qr_code']}")

    # Verifica pagamento a cada 15s
    context.job_queue.run_repeating(
        verificar_pagamento,
        interval=15,
        first=15,
        data={"payment_id": pix['id'], "telegram_id": query.from_user.id, "plano_key": plano_key, "chat_id": query.from_user.id},
        name=f"check_{pix['id']}"
    )

async def verificar_pagamento(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        info = sdk.payment().get(job.data["payment_id"])["response"]
        if info["status"] == "approved":
            expira = database.liberar_acesso(job.data["telegram_id"], pagamentos.PLANOS[job.data["plano_key"]]["dias"])
            await context.bot.send_message(
                chat_id=job.data["chat_id"],
                text=f"🎉 *PAGAMENTO APROVADO AMOR!*\n\nEntre agora no meu VIP: {LINK_VIP}\n\nTe espero lá dentro 😈\nExpira em {expira.strftime('%d/%m/%Y')}",
                parse_mode="Markdown"
            )
            job.schedule_removal()
    except Exception as e:
        print(e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(escolher_plano))
    print("Bot VIP Anastácia rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()

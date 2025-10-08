import json
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === CONFIGURAÇÕES ===
BOT_TOKEN = "8477842120:AAF9qg6-84vhgEpTW_WKlCSqwv135TPRWVI"
GRUPO_POSTAGEM = -1002261068752  # coloque aqui o ID do grupo onde o bot deve postar
ARQUIVO_POSTS = "posts.json"

# === AGENDADOR ===
scheduler = AsyncIOScheduler()
scheduler.start()

# === FUNÇÃO PARA SALVAR POSTS ===
def salvar_post(post):
    try:
        with open(ARQUIVO_POSTS, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except:
        posts = []
    posts.append(post)
    with open(ARQUIVO_POSTS, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

# === QUANDO RECEBE MENSAGEM ===
async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # pega o tipo de conteúdo
    conteudo = {}
    if msg.text:
        conteudo["texto"] = msg.text
    if msg.photo:
        conteudo["foto"] = msg.photo[-1].file_id
    if msg.video:
        conteudo["video"] = msg.video.file_id

    if not conteudo:
        await msg.reply_text("Envie um texto, foto ou vídeo para agendar.")
        return

    await msg.reply_text("Que horas você quer postar isso? (ex: 20:30)")
    context.user_data["conteudo"] = conteudo

# === QUANDO RECEBE O HORÁRIO ===
async def receber_horario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    try:
        hora, minuto = map(int, texto.split(":"))
        agora = datetime.now()
        agendado = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if agendado < agora:
            agendado += timedelta(days=1)  # se já passou, agenda pra amanhã
    except:
        await update.message.reply_text("Formato inválido. Use HH:MM (ex: 20:30)")
        return

    conteudo = context.user_data.get("conteudo")
    if not conteudo:
        await update.message.reply_text("Envie primeiro o conteúdo do post.")
        return

    post = {"conteudo": conteudo, "horario": agendado.isoformat()}
    salvar_post(post)

    scheduler.add_job(postar, "date", run_date=agendado, args=[conteudo, context])
    await update.message.reply_text(f"Post agendado para {agendado.strftime('%H:%M')} ✅")

# === FUNÇÃO PARA POSTAR NO GRUPO ===
async def postar(conteudo, context):
    chat_id = GRUPO_POSTAGEM

    if "foto" in conteudo:
        await context.bot.send_photo(chat_id, conteudo["foto"], caption=conteudo.get("texto", ""))
    elif "video" in conteudo:
        await context.bot.send_video(chat_id, conteudo["video"], caption=conteudo.get("texto", ""))
    elif "texto" in conteudo:
        await context.bot.send_message(chat_id, conteudo["texto"])

# === COMANDO /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie uma foto, vídeo ou texto para agendar a postagem.")

# === FUNÇÃO PRINCIPAL ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT & (~filters.COMMAND), receber_mensagem))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receber_horario))

    print("🤖 Bot rodando...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

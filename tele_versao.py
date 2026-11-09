import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# 1. Carrega as variáveis de ambiente
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not GEMINI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Certifique-se de configurar GEMINI_API_KEY e TELEGRAM_BOT_TOKEN no arquivo .env")

# 2. Inicializa o cliente Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Dicionário para armazenar o histórico individual de cada usuário (chave: chat_id)
user_chats = {}

SYSTEM_INSTRUCTION = """
Você é um assistente especializado em clima e calamidades em épocas de chuva.

Regras de prioridade de resposta (siga na ordem descrita):

1. Agradecimentos: Se a mensagem contiver agradecimentos como "obrigado" ou "obrigada", responda exatamente:
   "De nada, feliz em ajudar."

2. Saudações: Se o usuário enviar saudações (como "oi", "olá", "bom dia"), cumprimente de forma amigável e informe que você pode ajudar com dúvidas sobre clima e chuvas.

3. Clima e Calamidades: Se a pergunta for sobre clima, chuvas ou calamidades relacionadas, responda de forma clara e objetiva.

4. Outros assuntos (Regra de bloqueio): Para qualquer outro assunto que NÃO seja saudação, agradecimento ou relacionado a clima e chuvas, responda exatamente:
   "Desculpe, só posso responder perguntas sobre clima e calamidades relacionadas às chuvas."

Nunca invente previsões meteorológicas em tempo real.
"""

def get_user_chat(chat_id: int):
    """Recupera ou cria a sessão de chat do Gemini dedicada ao chat_id."""
    if chat_id not in user_chats:
        user_chats[chat_id] = client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
    return user_chats[chat_id]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata o comando /start do Telegram e reinicia o contexto do usuário."""
    chat_id = update.effective_chat.id
    
    # Reseta a sessão do usuário ao iniciar
    user_chats[chat_id] = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION
        )
    )
    
    await update.message.reply_text(
        "🌦️ Olá! Sou seu assistente de clima e calamidades relacionadas a chuvas. Como posso ajudar?"
    )

async def tratar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe mensagens de texto do Telegram e envia para o Gemini."""
    chat_id = update.effective_chat.id
    texto_usuario = update.message.text

    chat_session = get_user_chat(chat_id)

    try:
        # Exibe o indicador "digitando..." no Telegram
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Envia a mensagem para a API do Gemini
        resposta = chat_session.send_message(texto_usuario)
        
        # Responde o usuário no Telegram
        await update.message.reply_text(resposta.text.strip())

    except Exception as erro:
        print(f"Erro no chat {chat_id}: {erro}")
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem.")

if __name__ == "__main__":
    # Inicializa a aplicação do Telegram
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra o comando /start
    app.add_handler(CommandHandler("start", start_command))

    # Registra o manipulador para mensagens de texto comuns
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tratar_mensagem))

    print("🤖 Bot do Telegram iniciado! Pressione Ctrl+C para encerrar.")
    app.run_polling()
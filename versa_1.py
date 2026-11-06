from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(
    model="gemini-3.8-flash",
    config=types.GenerateContentConfig(
        system_instruction="""
        Você é um assistente especializado em clima e calamidades
        em épocas de chuva.


        Se a pergunta não estiver relacionada a esses assuntos,
        responda:
        "Desculpe, só posso responder perguntas sobre clima
        e calamidades relacionadas às chuvas."

        e se o usuario responder "obrigado" ou "obrigada"
        responda:
        "De nada, feliz em ajudar."

        Não invente previsões meteorológicas atuais.
        """
    )
)

print("🌦️ Assistente do Clima iniciado!")
print("Digite 'sair' ou 'fim' para encerrar.\n")

while True:
    entrada_usuario = input("Você: ").strip()
    pergunta_lowercase = entrada_usuario.lower()

    if not entrada_usuario:
        continue

    if pergunta_lowercase in ["sair", "fim"]:
        print("IA: Foi um prazer ajudar. Até logo!")
        break

    if pergunta_lowercase in ["oi", "ola", "olá"]:
        print("IA: Olá! Como posso ajudar com dúvidas sobre clima ou calamidades causadas por chuvas?")
        continue

    try:
        # Envia a mensagem original para o modelo
        resposta = chat.send_message(entrada_usuario)
        print("IA:", resposta.text)

    except Exception as erro:
        print("Erro ao comunicar com o Gemini:", erro)
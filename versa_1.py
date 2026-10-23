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

        Não invente previsões meteorológicas atuais.
        """
    )
)

print("🌦️ Assistente do Clima iniciado!")
print("Digite 'sair' ou 'fim' para encerrar.\n")

palavras_clima = [
    "clima", "tempo", "chuva", "sol",
    "temperatura", "previsão", "previsao"
]

while True:
    pergunta = input("Você: ").strip().lower()

    if pergunta in ["oi", "ola", "olá"]:
        print("IA: Olá, como posso ajudar?")

    elif pergunta in ["sair", "fim"]:
        print("IA: Foi um prazer ajudar. Até logo!")
        break

    elif not any(palavra in pergunta for palavra in palavras_clima):
        print("IA: Desculpe, eu não entendi direito.")

    else:
        try:
            resposta = chat.send_message(pergunta)
            print("IA:", resposta.text)

        except Exception as erro:
            print("Erro ao comunicar com o Gemini:", erro)
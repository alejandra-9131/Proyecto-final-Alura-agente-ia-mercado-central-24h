import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

respuesta = llm.invoke("Hola, responde con la palabra 'Conectado' si puedes leerme correctamente.")

print(respuesta.content)
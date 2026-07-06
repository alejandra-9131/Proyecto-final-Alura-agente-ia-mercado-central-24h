import os # Visualizar archivos
import pandas as pd # libreria para manejar datos
from pypdf import PdfReader # leer archivos PDF
from langchain_core.tools import tool # Decorador
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Conector que envia archivos a Gemini
from langchain_text_splitters import RecursiveCharacterTextSplitter # cortar texto en fragmentos
from langchain_community.vectorstores import FAISS # Es la memoria temporal


# Variable globales
acumulador_datos_texto = ""

respuesta_BaseDeDatos = None


#FUNCIÓN PARA LEER PDF

def agregar_pdf(_pdf):
    """
    Toma el archivo PDF que el usuario haya caegado, extrae su texto, lo acumula en la sesión y actualiza la base de datos vectorial en la memoria RAM.
    """
    
    global acumulador_datos_texto , respuesta_BaseDeDatos
    
    if not os.path.exists(_pdf):
        print(f"✖️ El archivo {_pdf} no existe.")
        return False
    
    print(f"📄 Leyendo el archivo PDF: {_pdf}")
    nuevo_texto = ""

#Abrir el PDF y extraer el texto
    try:
        lectura = PdfReader(_pdf)
        for pagina in lectura.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                nuevo_texto += texto_extraido + "\n"
    except Exception as e:
        print(f"✖️ Error al leer el texto del PDF: {e}")
        return False
    
# Busqueda RAG - Consulta


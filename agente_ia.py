import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from herramientas import (
    herramientas_cargadas,
    agregar_pdf,
    agregar_excel,
    limpiar_pdf,
    limpiar_excel,
)

load_dotenv()

# 2. Inicializar el modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

SYSTEM_PROMPT = (
    "Eres un Agente de Inteligencia Artificial experto en gestión de inventarios y análisis de datos para MERCADO CENTRAL 24 HORAS. "
    "Tu objetivo es ayudar al usuario a entender sus documentos (PDFs) y analizar sus tablas de datos (Excel).\n\n"
    "REGLAS ABSOLUTAS DE TRABAJO:\n"
    "1. Si el usuario te pregunta por políticas, textos o reglas del supermercado, usa SIEMPRE la herramienta 'consultar_info_pdf'.\n"
    "2. Si el usuario te pide cálculos, estadísticas, revisar stock o resúmenes de tablas, usa SIEMPRE la herramienta 'consultar_info_excel'.\n"
    "3. Responde siempre con un tono profesional, claro, usando viñetas y emojis para estructurar los reportes de manera ejecutiva y legible."
)

# SE CREA EL ORQUESTADOR
herramientas = herramientas_cargadas()

# ✅ Nueva API de LangChain 1.x: create_agent reemplaza a
# create_tool_calling_agent + AgentExecutor
agente_ejecutor = create_agent(
    model=llm,
    tools=herramientas,
    system_prompt=SYSTEM_PROMPT,
)

# MENU INTERACTIVO

st.set_page_config(page_title="Agente Mercado Central 24H", layout="centered")
st.title("🤖 BIENVENIDO AL AGENTE DE MERCADO CENTRAL 24H")

# Dejar memoria guardada (ahora como lista de mensajes estilo LangChain 1.x)
if "datos_historial" not in st.session_state:
    st.session_state["datos_historial"] = []

st.markdown("### Opciones: ")

def hacer_consulta_al_agente():
    pregunta = st.text_input("Pregúntale algo al Agente: ")
    if pregunta:
        with st.spinner("⏳ Procesando tu consulta, un momento por favor"):
            try:
                mensajes = st.session_state["datos_historial"] + [
                    {"role": "user", "content": pregunta}
                ]
                respuesta = agente_ejecutor.invoke({"messages": mensajes})
                ultimo_mensaje = respuesta["messages"][-1]
                salida = ultimo_mensaje.content

                st.markdown(f"**🤖 Respuesta del Agente:**")
                st.write(salida)

                st.session_state["datos_historial"].append({"role": "user", "content": pregunta})
                st.session_state["datos_historial"].append({"role": "assistant", "content": salida})
            except Exception as e:
                st.error(f"✖️ Ocurrió un error al procesar la consulta: {e}")

opcion = st.selectbox(
    "Selecciona una opción del menú:",
    [
        "Seleccione una opción...",
        "1. Cargar un archivo PDF",
        "2. Cargar un archivo Excel",
        "3. Hacer una consulta al agente",
        "4. Salir"
    ]
)

if "1." in opcion:
    st.write(opcion)
    st.markdown("#### 📄 Opción 1: Cargar un archivo PDF")
    archivo_pdf = st.file_uploader("Selecciona tu archivo PDF", type=["pdf"])
    if archivo_pdf:
        with open(archivo_pdf.name, "wb") as f:
            f.write(archivo_pdf.getbuffer())
        if agregar_pdf(archivo_pdf.name):
            st.success(f"✔️ Archivo PDF '{archivo_pdf.name}' cargado con éxito.")
            hacer_consulta_al_agente()
    else:
        limpiar_pdf()       
            
            
elif "2." in opcion:
    st.markdown("### 📊 Opción 2: Cargar un archivo EXCEL")
    archivo_excel = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx", "xls"])
    if archivo_excel:
        with open(archivo_excel.name, "wb") as f:
            f.write(archivo_excel.getbuffer())
        if agregar_excel(archivo_excel.name):
            st.success(f"✅ Archivo Excel '{archivo_excel.name}' cargado con éxito.")
            hacer_consulta_al_agente()
    else:
        limpiar_excel() 
            
            
elif "3." in opcion:
    st.markdown("#### 🧠 Opción 3: Hacer una consulta al agente")
    hacer_consulta_al_agente()

elif "4." in opcion:
    limpiar_pdf()
    limpiar_excel()
    st.session_state["datos_historial"] = []
    st.info("👋 ¡Gracias por usar el Agente de IA de Mercado Central 24H, ¡Hasta luego!")
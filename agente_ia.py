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

# ---------------------------------------------------------
# 1. Modelo y agente
# ---------------------------------------------------------
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

herramientas = herramientas_cargadas()

agente_ejecutor = create_agent(
    model=llm,
    tools=herramientas,
    system_prompt=SYSTEM_PROMPT,
)

# ---------------------------------------------------------
# 2. Función reutilizable: hacer una pregunta al agente
# ---------------------------------------------------------
def hacer_consulta_al_agente():
    pregunta = st.text_input("Pregúntale algo al Agente: ")

    if not pregunta:
        return

    with st.spinner("⏳ Procesando tu consulta, un momento por favor"):
        try:
            mensajes = st.session_state["datos_historial"] + [
                {"role": "user", "content": pregunta}
            ]

            respuesta = agente_ejecutor.invoke({"messages": mensajes})
            ultimo_mensaje = respuesta["messages"][-1]
            contenido = ultimo_mensaje.content

            # A veces el contenido viene como texto plano (str),
            # y a veces como una lista de bloques tipo [{'type': 'text', 'text': '...'}].
            # Aquí lo normalizamos para quedarnos solo con el texto (sin corchetes).
            if isinstance(contenido, list):
                salida = "".join(
                    bloque.get("text", "") if isinstance(bloque, dict) else str(bloque)
                    for bloque in contenido
                )
            else:
                salida = contenido

            st.markdown("### 🤖 Respuesta del Agente")
            st.markdown(salida)

            st.session_state["datos_historial"].append({"role": "user", "content": pregunta})
            st.session_state["datos_historial"].append({"role": "assistant", "content": salida})

        except Exception as e:
            st.error(f"✖️ Ocurrió un error al procesar la consulta: {e}")


# ---------------------------------------------------------
# 3. Configuración de página y estado inicial
# ---------------------------------------------------------
st.set_page_config(page_title="Agente Mercado Central 24H", layout="wide")

st.markdown("""
    <div style="
        text-align: center;
        padding: 20px 0 16px 0;
        border-bottom: 1px solid rgba(0,0,0,0.08);
        margin-bottom: 24px;
    ">
        <h1 style="margin: 0 0 6px 0; font-size: 2rem; font-weight: 600; color: #1a1a2e;">
            🛒 Mercado Central 24 Horas
        </h1>
        <p style="margin: 0; font-size: 0.95rem; color: #6b7280;">
            Agente Inteligente para Gestión de Inventarios · Analiza PDF, Excel y responde con IA
        </p>
    </div>
""", unsafe_allow_html=True)

if "datos_historial" not in st.session_state:
    st.session_state["datos_historial"] = []

col_izquierda, col_derecha = st.columns([1, 3])

# ---------------------------------------------------------
# 4. Columna izquierda: info + menú
# ---------------------------------------------------------
with col_izquierda:
    #st.markdown("## 🤖 Mercado Central 24H")

    st.markdown("""
    <div style="
        background-color:#f8f9fa;
        padding:15px;
        border-radius:10px;
        border:1px solid #dcdcdc;
    ">
    <h4>🤖 Agente IA</h4>
    <p>Especialista en análisis de inventarios, documentos PDF y archivos Excel.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📋 Estado")
    st.success("📄 PDF")
    st.caption("No hay ningún PDF cargado")
    st.success("📊 Excel")
    st.caption("No hay ningún Excel cargado")
    st.divider()

# ---------------------------------------------------------
# 5. Columna derecha: menú + contenido según la opción elegida
# ---------------------------------------------------------
with col_derecha:
    st.markdown("## 💬 Asistente IA")
    st.caption("Consulta información del PDF o del Excel cargado.")

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

    with st.container(border=True):

        if "1." in opcion:
            st.markdown("#### 📄 Cargar PDF")
            archivo_pdf = st.file_uploader("Selecciona tu archivo PDF", type=["pdf"])

            if archivo_pdf:
                with open(archivo_pdf.name, "wb") as f:
                    f.write(archivo_pdf.getbuffer())
                if agregar_pdf(archivo_pdf.name):
                    st.success(f"✔️ {archivo_pdf.name} cargado correctamente.")
                    hacer_consulta_al_agente()
            else:
                limpiar_pdf()

        elif "2." in opcion:
            st.markdown("#### 📊 Cargar Excel")
            archivo_excel = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx", "xls"])

            if archivo_excel:
                with open(archivo_excel.name, "wb") as f:
                    f.write(archivo_excel.getbuffer())
                if agregar_excel(archivo_excel.name):
                    st.success(f"✔️ {archivo_excel.name} cargado correctamente.")
                    hacer_consulta_al_agente()
            else:
                limpiar_excel()

        elif "3." in opcion:
            st.markdown("#### 🧠 Hacer una consulta al agente")
            hacer_consulta_al_agente()

        elif "4." in opcion:
            limpiar_pdf()
            limpiar_excel()
            st.session_state["datos_historial"] = []
            st.success("👋 ¡Gracias por usar el Agente de IA de Mercado Central 24H, hasta luego!")

        else:
            st.info("👈 Selecciona una opción del menú para comenzar.")
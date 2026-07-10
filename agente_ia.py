import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from sympy import div
from herramientas import (
    herramientas_cargadas,
    agregar_pdf,
    agregar_excel,
    limpiar_pdf,
    limpiar_excel,
)
import herramientas

# ---------------------------------------------------------
# 1. Configuración de la página (DEBE SER LO PRIMERO DE STREAMLIT)
# ---------------------------------------------------------
st.set_page_config(page_title="Agente Mercado Central 24H", layout="wide")

# ========================= Cargar Estilos =========================
def cargar_css(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css("styles.css")
# =================================================================

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

SYSTEM_PROMPT = (
    "Eres un Agente de Inteligencia Artificial experto en gestión de inventarios y análisis de datos para MERCADO CENTRAL 24 HORAS. "
    "Tu objetivo es ayudar al usuario a entender sus documentos (PDFs), analizar sus tablas de datos (Excel) y generar visualizaciones gráficas.\n\n"
    "ESTRUCTURA DEL EXCEL DISPONIBLE:\n"
    "Las columnas exactas del archivo son: Categoría, Subcategoría, Descripción, Marca, Stock, Ubicación, Fecha de Fabricación, Fecha de Vencimiento, Costo Unitario, Precio de Venta Unitario.\n\n"
    "REGLAS ABSOLUTAS DE TRABAJO:\n"
    "1. Si el usuario te pregunta por políticas, textos, preguntas frecuentes o reglas del supermercado, usa SIEMPRE la herramienta 'consultar_info_pdf'.\n"
    "2. Si el usuario te pide cálculos, estadísticas, revisar stock, precios o resúmenes numéricos, usa SIEMPRE la herramienta 'consultar_info_excel'.\n"
    "3. Si el usuario te pide una gráfica, un gráfico de barras, un top, o la comparación visual de datos del Excel, usa SIEMPRE la herramienta 'generar_grafica_excel'.\n"
    "   - Asigna correctamente la columna de texto/categoría (e.g., 'Categoría', 'Marca' o 'Descripción') y la columna numérica (e.g., 'Stock', 'Costo Unitario' o 'Precio de Venta Unitario').\n"
    "4. Responde siempre con un tono profesional, claro, usando viñetas y emojis para estructurar los reportes de manera ejecutiva y legible."
)

 
# ---------------------------------------------------------
# Función para hacer preguntas al agente
# ---------------------------------------------------------
def hacer_consulta_al_agente():
    pregunta = st.text_input("Pregúntale algo al Agente: ")

    if not pregunta:
        return

    with st.spinner("⏳ Procesando tu consulta, un momento por favor"):
        try:

            lista_herramientas_frescas = herramientas_cargadas()
            agente_ejecutor = create_agent(
                model=llm,
                tools=lista_herramientas_frescas,
                system_prompt=SYSTEM_PROMPT,
            )
            mensajes = st.session_state["datos_historial"] + [
                {"role": "user", "content": pregunta}
            ]

            respuesta = agente_ejecutor.invoke({"messages": mensajes})
            ultimo_mensaje = respuesta["messages"][-1]
            contenido = ultimo_mensaje.content

            if isinstance(contenido, list):
                salida = "".join(
                    bloque.get("text", "") if isinstance(bloque, dict) else str(bloque)
                    for bloque in contenido
                )
            else:
                salida = contenido

            st.markdown("### 🤖 Respuesta del Agente")
            st.markdown(salida)
            
            if os.path.exists("grafico_inventario.png"):
                st.image(
                    "grafico_inventario.png", 
                    caption="📊 Visualización de Datos - Mercado Central 24H", 
                    use_container_width=True
                )
                os.remove("grafico_inventario.png")

            st.session_state["datos_historial"].append({"role": "user", "content": pregunta})
            st.session_state["datos_historial"].append({"role": "assistant", "content": salida})

        except Exception as e:
            st.error(f"✖️ Ocurrió un error al procesar la consulta: {e}")

# ---------------------------------------------------------
# Encabezado Principal
# ---------------------------------------------------------
st.markdown("""
    <div class="header-container">
        <div class="header-icon">🛒</div>
        <div class="header-content">
            <div class="header-title-wrapper">
                <h1 class="header-title">Mercado Central <span class="header-title-highlight">24 Horas</span></h1>
                <span class="header-badge">● AGENTE ACTIVO</span>
            </div>
            <p class="header-subtitle">Agente Inteligente de Inventarios & Análisis con Inteligencia Artificial</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Inicializar Estados de Sesión
if "datos_historial" not in st.session_state:
    st.session_state["datos_historial"] = []

if "pdf_cargado" not in st.session_state:
    st.session_state["pdf_cargado"] = False
    st.session_state["nombre_pdf"] = None

if "excel_cargado" not in st.session_state:
    st.session_state["excel_cargado"] = False
    st.session_state["nombre_excel"] = None

# Definir Columnas
col_izquierda, col_derecha = st.columns([1, 3])

# ---------------------------------------------------------
# Columna Izquierda
# ---------------------------------------------------------
with col_izquierda:

    st.markdown("""
<div class="agent-card">
    <div class="agent-card-header">
        <div class="agent-card-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="10" rx="2"/>
                <circle cx="12" cy="5" r="2"/>
                <path d="M12 7v4"/>
                <line x1="8" y1="16" x2="8.01" y2="16" stroke-width="3"/>
                <line x1="16" y1="16" x2="16.01" y2="16" stroke-width="3"/>
            </svg>
            <div class="agent-card-dot"></div>
        </div>
        <div class="agent-card-titles">
            <p class="agent-card-title">Agente IA</p>
            <span class="agent-card-badge">ESPECIALISTA ACTIVO</span>
        </div>
    </div>
    <div class="agent-card-body">
        Especialista en análisis de inventarios, documentos PDF y archivos Excel.
    </div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📋 Estado")

    with st.container():
        if st.session_state["pdf_cargado"]:
            st.success(f"🟢 PDF: {st.session_state['nombre_pdf']}")
            st.caption("✅ Documento cargado con éxito.")
        else:
            st.info("📄 PDF")
            st.caption("🔴 No hay ningún PDF cargado")

    with st.container():
        if st.session_state["excel_cargado"]:
            st.success(f"🟢 Excel: {st.session_state['nombre_excel']}")
            st.caption("✅ Documento cargado con éxito ")
        else:
            st.info("📊 Excel")
            st.caption("🔴 No hay ningún Excel cargado")
            
    st.divider()

# ---------------------------------------------------------
# Columna Derecha
# ---------------------------------------------------------
with col_derecha:
    st.markdown("## 💬 Asistente IA")
    st.markdown("""
    <div style="
        background-color: #eef6ff;
        border-left: 5px solid #1e88e5;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
    ">
        <p style="margin: 0 0 8px 0; font-size: 1.05rem; color: #333333;"">
            👋 <b>¡Hola! Soy tu Agente Inteligente</b> para el <b>Mercado Central 24 Horas</b>.
        </p>
        <p style="margin: 0 0 8px 0; color: #333333;">
            Estoy listo para ayudarte a analizar los niveles de inventario, políticas, preguntas frecuentes, reglamento interno y manuales de la empresa.
        </p>
        <p style="margin: 0; color: #1e88e5; font-weight: 500;">
            📌 <b>Para comenzar:</b> Selecciona una opción del Menú ubicado en el panel lateral 👇.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Etiqueta y Menú
    st.markdown('<p class="menu-label, color: white">SELECCIONA UNA OPCIÓN DEL MENÚ:</p>', unsafe_allow_html=True)

    opcion = st.selectbox(
        "SELECCIONA UNA OPCIÓN DEL MENÚ:",
        ["Seleccione una opción...", 
        "1. 📄 Cargar PDF", 
        "2. 🎢 Cargar Excel", 
        "3. 🤖 Consultar al Agente", 
        "4. 🧹 Reiniciar / Limpiar"],
        label_visibility="collapsed"
    )

    # Lógica del Menú alineada
    if "1." in opcion:
        st.markdown("#### 📄 Cargar PDF")
        archivo_pdf = st.file_uploader("Selecciona tu archivo PDF", type=["pdf"], key="uploader_pdf")
        if archivo_pdf:
            if not st.session_state["pdf_cargado"]:
                with open(archivo_pdf.name, "wb") as f:
                    f.write(archivo_pdf.getbuffer())
                if agregar_pdf(archivo_pdf.name):
                    st.session_state["pdf_cargado"] = True
                    st.session_state["nombre_pdf"] = archivo_pdf.name
                    st.rerun()

            st.success(f"✔️ {st.session_state['nombre_pdf']} cargado correctamente.")
            hacer_consulta_al_agente()

    elif "2." in opcion:
        st.markdown("#### 📊 Cargar Excel")
        archivo_excel = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx", "xls"], key="uploader_excel")

        if archivo_excel:
            if not st.session_state["excel_cargado"]:
                with open(archivo_excel.name, "wb") as f:
                    f.write(archivo_excel.getbuffer())
                if agregar_excel(archivo_excel.name):
                    st.session_state["excel_cargado"] = True
                    st.session_state["nombre_excel"] = archivo_excel.name
                    st.rerun()

            st.success(f"✔️ {st.session_state['nombre_excel']} cargado correctamente.")
            hacer_consulta_al_agente()

    elif "3." in opcion:
        st.markdown("#### 🧠 Hacer una consulta al agente")
        hacer_consulta_al_agente()

    elif "4." in opcion:
        limpiar_pdf()
        limpiar_excel()

        st.session_state["datos_historial"] = []
        st.session_state["pdf_cargado"] = False
        st.session_state["nombre_pdf"] = None
        st.session_state["excel_cargado"] = False
        st.session_state["nombre_excel"] = None

        st.success("👋 ¡Gracias por usar el Agente de IA de Mercado Central 24H, hasta luego!")
        st.info("💡 Si deseas comenzar de nuevo, selecciona otra opción del menú.")

    else:
        st.markdown("""
            <div class="card-inicial">
                <div style="font-size: 2rem;">🤪 </div>
                <p class="card-inicial-titulo">Selecciona una opción del menú para comenzar.</p>
                <p class="card-inicial-subtitulo">La IA analizará inmediatamente el inventario activo o el archivo que cargues.</p>
            </div>
        """, unsafe_allow_html=True)
        
# ========PIE DE PAGINA ==============
st.markdown("""
<div class="footer-container">
    <p>© 2026 <span class="footer-highlight">Mercado Central 24 Horas</span>. Todos los derechos reservados.</p>
    <span class="footer-badge">
        <svg class="shield-pulse" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="m9 12 2 2 4-4"/>
        </svg>
        Impulsado por Agente IA
    </span>
</div>
""", unsafe_allow_html=True)
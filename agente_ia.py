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
import herramientas

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

lista_herramientas = herramientas_cargadas()

agente_ejecutor = create_agent(
    model=llm,
    tools=lista_herramientas,
    system_prompt=SYSTEM_PROMPT,
)

# ---------------------------------------------------------
# Hacer una pregunta al agente
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
                st.image("grafico_inventario.png", 
                caption="📊 Visualización de Datos - Mercado Central 24H", use_container_width=True)
                os.remove("grafico_inventario.png")  # La eliminamos para no repetirla en futuras preguntas

            st.session_state["datos_historial"].append({"role": "user", "content": pregunta})
            st.session_state["datos_historial"].append({"role": "assistant", "content": salida})

        except Exception as e:
            st.error(f"✖️ Ocurrió un error al procesar la consulta: {e}")



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

# Banderas para saber si hay PDF/Excel cargado en esta sesión
if "pdf_cargado" not in st.session_state:
    st.session_state["pdf_cargado"] = False
    st.session_state["nombre_pdf"] = None

if "excel_cargado" not in st.session_state:
    st.session_state["excel_cargado"] = False
    st.session_state["nombre_excel"] = None

col_izquierda, col_derecha = st.columns([1, 3])

# ---------------------------------------------------------
# Aqui empieza la columna izquierda
# ---------------------------------------------------------
with col_izquierda:
    st.markdown("## 🤖 Mercado Central 24H")

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

    # ✅ Usamos contenedores dinámicos en lugar de funciones estáticas
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
# Aqui empieza la columna derecha
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
            archivo_pdf = st.file_uploader("Selecciona tu archivo PDF", type=["pdf"], key="uploader_pdf")
            if archivo_pdf:
                if not st.session_state["pdf_cargado"]:
                    with open(archivo_pdf.name, "wb") as f:
                        f.write(archivo_pdf.getbuffer())
                    if agregar_pdf(archivo_pdf.name):
                        st.session_state["pdf_cargado"] = True
                        st.session_state["nombre_pdf"] = archivo_pdf.name
                        st.rerun()  # Ahora sí, solo recarga una vez
                
                # Esto se muestra cuando ya está cargado y evita el bucle
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
                        st.rerun()  # Solo recarga una vez
                
                st.success(f"✔️ {st.session_state['nombre_excel']} cargado correctamente.")
                hacer_consulta_al_agente()
        elif "3." in opcion:
            st.markdown("#### 🧠 Hacer una consulta al agente")
            hacer_consulta_al_agente()

        elif "4." in opcion:
            # 1. Limpiamos las variables globales de memoria
            limpiar_pdf()
            limpiar_excel()

            # 2. Reiniciamos todas las variables de sesión
            st.session_state["datos_historial"] = []
            st.session_state["pdf_cargado"] = False
            st.session_state["nombre_pdf"] = None
            st.session_state["excel_cargado"] = False
            st.session_state["nombre_excel"] = None

            # 3. Mostramos el mensaje de despedida PRIMERO
            st.success("👋 ¡Gracias por usar el Agente de IA de Mercado Central 24H, hasta luego!")
            st.info("💡 Si deseas comenzar de nuevo, selecciona otra opción del menú.")

        else:
            st.info("😃👆Selecciona una opción del menú para comenzar.")
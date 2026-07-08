import os # Visualizar archivos
import pandas as pd # libreria para manejar datos
from pypdf import PdfReader # leer archivos PDF
from langchain_core.tools import tool # Decorador
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Conector que envia archivos a Gemini
from langchain_text_splitters import RecursiveCharacterTextSplitter # cortar texto en fragmentos
from langchain_community.vectorstores import FAISS # Es la memoria temporal
from langchain_community.embeddings import HuggingFaceEmbeddings
import matplotlib.pyplot as plt
from torch import cat # Para crear graficos


# Variable globales
acumulador_datos_texto = ""

respuesta_BaseDeDatos = None

grafica_generada = None



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
    
    
    acumulador_datos_texto += nuevo_texto + "\n"

    # 2. Cortamos todo el texto acumulado en fragmentos de 1000 caracteres
    separador_de_texto = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    textos = separador_de_texto.create_documents([acumulador_datos_texto])

    # 3. Traducimos los fragmentos a números (vectores) 
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    

    respuesta_BaseDeDatos = FAISS.from_documents(textos, embeddings)
    
    print(f"✅ ¡Archivo PDF procesado e indexado en la memoria!\n")
    return True
# Busqueda RAG - Consulta // CREANDO LAS HERRAMIENTAS PARA EL AGENTE

@tool 
def consultar_info_pdf(pregunta: str) ->str:
    """
    Utiliza esta herramienta cuando el usuario haga preguntas sobre el contenido, reglas, políticas, textos o cualquier dato que se encuentre dentro del PDF cargado.
    """
    global respuesta_BaseDeDatos
    
    # Este if sirve en caso que el usiario consulte un documento pero aun no lo ha cargado
    if respuesta_BaseDeDatos is None:
        return "⚠️ No se ha cargado ningún PDF. Por favor, primero carga un archivo PDF para poder consultar su contenido."
    
    texto_importante =respuesta_BaseDeDatos.similarity_search(pregunta, k=3)
    
    texto_limpio_con_rag= ""
    for documento in texto_importante:
        texto_limpio_con_rag += documento.page_content + "\n--- Fragmento ---\n"
        
    return texto_limpio_con_rag
    
# Herramienta para consultar datos en Excel

datos_respuesta_excel = None


# Función para agregar un archivo de Excel y almacenar sus datos en memoria
def agregar_excel(_excel):
    """
    Toma la ruta de un archivo Excel que el usuario haya cargado, 
    lo lee usando Pandas y lo guarda en la memoria RAM para la sesión.
    """
    global datos_respuesta_excel
    
    if not os.path.exists(_excel):
        print(f"✖️ El archivo {_excel} no existe.")
        return False
    
    try:
        # Leer el archivo Excel y almacenar los datos en memoria
        datos_respuesta_excel = pd.read_excel(_excel)
        print(f"✅ ¡Archivo Excel procesado y cargado en la memoria!\n")
        return True
    except Exception as e:
        print(f"✖️ Error al leer el archivo Excel: {e}")
        return False

@tool 
def consultar_info_excel(informa:str)-> str:
    """
        Utiliza esta herramienta SIEMPRE que el usuario haga preguntas sobre la información contenida en el archivo Excel cargado.

        Esta herramienta permite responder consultas relacionadas con:

        - Productos.
        - Marcas.
        - Categorías.
        - Subcategorías.
        - Unidades.
        - Ubicaciones.
        - Stock.
        - Fechas de fabricación.
        - Fechas de vencimiento.
        - Costos.
        - Precios de venta.
        
        

        También debe utilizarse cuando el usuario solicite:

        - Buscar productos.
        - Listar categorías o subcategorías.
        - Mostrar marcas.
        - Contar registros.
        - Filtrar información.
        - Comparar productos.
        - Calcular promedios, máximos, mínimos o totales.
        - Analizar inventario.
        - Detectar productos con stock.
        - Detectar productos próximos a vencer.
        - Generar resúmenes o estadísticas.
        - Responder cualquier pregunta cuya respuesta se encuentre en el archivo Excel.

        Nunca utilices la herramienta del PDF cuando la información solicitada pertenezca al archivo Excel.
        """
    
    global datos_respuesta_excel
    
    # validar igualmente si el usuario no ha cargado un archivo de Excel
    if datos_respuesta_excel is None:
        return "⚠️ No se ha cargado ningún archivo de Excel. Por favor, primero carga un archivo de Excel para poder consultar su contenido."
    
    try: 
        columnas = str(datos_respuesta_excel.columns.tolist())
        filas_mostradas = str(datos_respuesta_excel.head(5).to_string())
        
        reporte_contexto = f"Estructura del Excel cargado (Columnas): {columnas}\n"
        reporte_contexto += f"Muestra de las primeras 5 filas:\n{filas_mostradas}\n\n"
        reporte_contexto += f"Pregunta del usuario a resolver: {informa}"
        
        return reporte_contexto
    except Exception as e:
        return f"✖️ Error al procesar la consulta en el archivo de Excel: {e}"
    
#================= genera la grafica =========================

@tool
def generar_grafica_excel(columna_categoria: str, columna_valor: str, top_n: int = 5) -> str:
    """
    Genera una gráfica de barras agrupando los datos del Excel.
    Úsala SIEMPRE que el usuario pida una gráfica, un gráfico de barras o la comparación visual de datos.

    columna_categoria: Nombre exacto de la columna de texto a agrupar. Puede ser: 'Categoría', 'Subcategoría', 'Marca', 'Descripción' o 'Ubicación'.
    columna_valor: Nombre exacto de la columna numérica a sumar o comparar. Puede ser: 'Stock', 'Costo Unitario' o 'Precio de Venta Unitario'.
    top_n: Cantidad de elementos a mostrar en el gráfico.
    """
    global datos_respuesta_excel
    
    # 1. Validar si hay Excel cargado
    if datos_respuesta_excel is None:
        return "⚠️ No se ha cargado ningún archivo de Excel. Por favor, carga un archivo primero."
    
    # 2. Validar que la columna de agrupación exista
    if columna_categoria not in datos_respuesta_excel.columns:
        return f"✖️ La columna '{columna_categoria}' no existe en el Excel. Columnas disponibles: {list(datos_respuesta_excel.columns)}"
    
    # 3. Validar que la columna numérica exista
    if columna_valor not in datos_respuesta_excel.columns:
        return f"✖️ La columna '{columna_valor}' no existe en el Excel. Columnas disponibles: {list(datos_respuesta_excel.columns)}"
    
    try: 
        agrupado = (
            datos_respuesta_excel.groupby(columna_categoria)[columna_valor]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )
        
        fig, ax = plt.subplots(figsize=(7, 4.5))
        agrupado.plot(kind="bar", ax=ax, color="#43A047")
        ax.set_title(f"Top {top_n} {columna_categoria} por {columna_valor}", fontsize=12, fontweight="bold")
        ax.set_ylabel(columna_valor)
        ax.set_xlabel(columna_categoria)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        # Guardamos la imagen física para Streamlit
        fig.savefig("grafico_inventario.png", dpi=300)
        plt.close(fig)
        
        resumen = ", ".join(f"{cat}: {val}" for cat, val in agrupado.items())
        return f"✅ Gráfica generada correctamente y guardada en 'grafico_inventario.png'. Top {top_n} de {columna_categoria}: {resumen}"
    
    except Exception as e:
        return f"✖️ Error al generar la gráfica: {e}"


#================= termina de generar la grafica =========================
    
def herramientas_cargadas():
    """
    Agrupa las herramientas de análisis disponibles 
    y se las entrega ordenadas al agente principal.
    """
    return [consultar_info_pdf, consultar_info_excel, generar_grafica_excel]


# este codigo sirve para limpiar la pagina de los documentos y el chat no se quede con la info
def limpiar_pdf():
    global respuesta_BaseDeDatos, acumulador_datos_texto
    respuesta_BaseDeDatos = None
    acumulador_datos_texto = ""

def limpiar_excel():
    global datos_respuesta_excel
    datos_respuesta_excel = None
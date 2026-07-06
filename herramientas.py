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
    
    
    acumulador_datos_texto += nuevo_texto + "\n"

    # 2. Cortamos todo el texto acumulado en fragmentos de 1000 caracteres
    separador_de_texto = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    textos = separador_de_texto.create_documents([acumulador_datos_texto])

    # 3. Traducimos los fragmentos a números (vectores) con el modelo de Google
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # 4. Guardamos los vectores en nuestra base de datos en la memoria RAM
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
    Utiliza esta herramienta cuando el usuario pida resúmenes, estadísticas,revisar filas, columnas o hacer cálculos numéricos sobre el archivo de Excel cargado.
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
    
def herramientas_cargadas():
    """
    Agrupa las herramientas de análisis disponibles 
    y se las entrega ordenadas al agente principal.
    """
    return [consultar_info_pdf, consultar_info_excel]
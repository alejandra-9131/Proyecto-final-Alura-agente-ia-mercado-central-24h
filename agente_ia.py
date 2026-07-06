import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from herramientas import herramientas_cargadas, agregar_pdf, agregar_excel

# 1. Cargar la API Key desde el archivo .env
load_dotenv()

# 2. Inicializar el modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

prompt_react_es = ChatPromptTemplate.from_messages([
    ("system",
        "Eres un Agente de Inteligencia Artificial experto en gestión de inventarios y análisis de datos para supermercados LATAM. "
        "Tu objetivo es ayudar al usuario a entender sus documentos (PDFs) y analizar sus tablas de datos (Excel).\n\n"
        "REGLAS ABSOLUTAS DE TRABAJO:\n"
        "1. Si el usuario te pregunta por políticas, textos o reglas del supermercado, usa SIEMPRE la herramienta 'consultar_info_pdf'.\n"
        "2. Si el usuario te pide cálculos, estadísticas, revisar stock o resúmenes de tablas, usa SIEMPRE la herramienta 'consultar_info_excel'.\n"
        "3. Responde siempre con un tono profesional, claro, usando viñetas y emojis para estructurar los reportes de manera ejecutiva y legible."
    ),
    # Este marcador es obligatorio para que el agente recuerde la conversación
    MessagesPlaceholder(variable_name="chat_history"),
    # el agente recibe la pregunta actual del usuario
    ("human", "{input}"),
    # Este marcador le permite a Gemini decidir 
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# SE CREA EL ORQUESTADOR

herramientas = herramientas_cargadas()

motor_de_agente = create_tool_calling_agent(llm, herramientas, prompt=prompt_react_es)

agente_ejecutor = AgentExecutor(
    agent= motor_de_agente,
    tools= herramientas,
    verbose=True
)

# MENU INTERACTIVO

def chat_interactivo_agente():
    datos_historial = []
    
    print("======================================================")
    print("🤖 ¡BIENVENIDO AL AGENTE DE MERCADO CENTRAL 24H!")
    print("======================================================")
    
    while True:
        print("\nOpciones:")
        print("1. Cargar un archivo PDF")
        print("2. Cargar un archivo Excel")
        print("3. Hacer una consulta al agente")
        print("4. Salir")
        
        opcion = input("Selecciona una opción (1-4): ").strip()
        
        if opcion =="1":
            ruta_pdf = input("Ingresa la ruta del archivo PDF: ")
            agregar_pdf(ruta_pdf)
        elif opcion =="2":
            ruta_excel = input("Ingresa la ruta del archivo Excel: ")
            agregar_excel(ruta_excel)
        elif opcion =="3":
            pregunta = input("\n💬 Pregúntale algo al agente de IA: ").strip()
            if not pregunta:
                continue
            
            print("\n⏳ Procesando tu consulta...")
            try:
                respuesta = agente_ejecutor.invoke({"input": pregunta, "chat_history": datos_historial
                })
                
                print(f"\n🤖 Respuesta del Agente:\n{respuesta['output']}")
                
                #MEMORIA GUARDADA
                datos_historial.append(("human", pregunta))
                datos_historial.append(("ai", respuesta['output']))
            except Exception as e:
                print(f"✖️ Ocurrió un error al procesar la consulta: {e}")
        
        elif opcion =="4":
            print("👋 ¡Gracias por usar el Agente de IA de Mercado Central 24H, ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida. Por favor, selecciona una opción del 1 al 4.")
    
    if __name__ == "__main__":
        chat_interactivo_agente()
















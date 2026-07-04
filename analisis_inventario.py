import os
import pandas as pd

def leer_inventario():
    ruta_archivo = os.path.join("documentos", "inventario_de_supermercado_latam.xlsx")
    print(f"El archivo se encuentra en: {ruta_archivo}")
    
    if not os.path.exists(ruta_archivo):
        print("El archivo no existe. Por favor, verifica la ruta.")
        return None
    
    try:
        df = pd.read_excel(ruta_archivo)
        print("✅ ¡Inventario cargado con éxito!")
        return df
    except Exception as e:
        print(f"❌ Ocurrió un error al leer el archivo: {e}")
        return None


if __name__ == "__main__":
    
    inventario = leer_inventario()
    
    if inventario is not None:
        print("\n--- Vista previa de los primeros 5 productos ---")
        print(inventario.head())
        
        print("\n--- Información general del inventario ---")
        print(inventario.info())
        
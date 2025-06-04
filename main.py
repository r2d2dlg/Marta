# main.py

import os
import sys

# Ensure the project root (marta_ai/) is in sys.path.
# This allows importing 'marta_core' as a package from main.py.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import from marta_core.agent
try:
    # MODIFIED: Changed import to be explicit from marta_core package
    from marta_core.agent import ask_marta, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION, llm
except ImportError as e:
    print("Error: No se pudo importar desde 'marta_core.agent'.")
    print(f"Detalle del error: {e}")
    print("Asegúrate de que la carpeta 'marta_core' exista en la raíz del proyecto,")
    print("contenga un archivo '__init__.py', y que 'agent.py' esté dentro de 'marta_core'.")
    sys.exit(1)
except Exception as e:
    print(f"Ocurrió un error inesperado durante la importación: {e}")
    sys.exit(1)


def run_marta_cli():
    """
    Ejecuta la interfaz de línea de comandos para interactuar con Marta.
    """
    print("*" * 50)
    print("Inicializando a Marta Maria Mendez...")
    print("*" * 50)

    if not GOOGLE_CLOUD_PROJECT or not GOOGLE_CLOUD_REGION:
        print("\nADVERTENCIA: Las variables de entorno GOOGLE_CLOUD_PROJECT o GOOGLE_CLOUD_REGION no están configuradas.")
        print("Asegúrate de que tu archivo .env esté correctamente configurado y que 'load_dotenv()' se ejecute en agent.py.")
        print("Marta podría no funcionar correctamente sin estas variables.\n")

    if not llm: # llm se importa desde agent.py
        print("\nERROR CRÍTICO: El modelo LLM (Gemini) no se pudo cargar.")
        print("Revisa los mensajes de error en 'marta_core/agent.py' al inicializar ChatVertexAI.")
        print("Marta no puede operar sin el LLM. Saliendo...")
        return

    print(f"\nConectada a Google Cloud Project: {GOOGLE_CLOUD_PROJECT}")
    print(f"Usando la región: {GOOGLE_CLOUD_REGION}")
    print("Modelo LLM cargado. Marta está lista.")
    print("\n--- Marta Maria Mendez ---")
    print("¡Hola! Soy Marta. ¿En qué puedo ayudarte hoy?")
    print("Escribe 'salir', 'adiós' o 'chao' para terminar la conversación.")
    print("-" * 26)

    while True:
        try:
            user_query = input("Tú: ")
            if user_query.strip().lower() in ['salir', 'adiós', 'chao', 'exit']:
                print("Marta: ¡Ha sido un placer ayudarte! Que tengas un excelente día.")
                break
            
            if not user_query.strip(): # Si el usuario solo presiona Enter
                continue

            print("Marta: Pensando...") # Indicador de que está procesando
            marta_response = ask_marta(user_query)
            print(f"Marta: {marta_response}")

        except KeyboardInterrupt:
            print("\nMarta: Conversación interrumpida. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nOcurrió un error inesperado en la CLI: {e}")
            print("Marta: Parece que tuve un problema técnico. Intentemos de nuevo.")
            # Podrías querer terminar el bucle aquí o intentar recuperarte.

if __name__ == "__main__":
    run_marta_cli()

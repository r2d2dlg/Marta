# marta_core/agent.py

import os
from datetime import datetime
import pytz 

from langchain_google_vertexai import ChatVertexAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    MessagesPlaceholder, 
    HumanMessagePromptTemplate
)
from langchain_core.messages import SystemMessage 
from langchain import hub 

from .tools import available_tools 
from dotenv import load_dotenv

load_dotenv()

# --- Configuración Inicial ---
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
raw_region_agent = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1') 
GOOGLE_CLOUD_REGION = raw_region_agent.split('#')[0].strip() 
MODEL_NAME = os.getenv('GEMINI_CHAT_MODEL', "gemini-2.0-flash-001") 

# --- Variables Globales para el Agente (se inicializarán de forma perezosa) ---
llm_instance = None
prompt_instance = None
agent_instance = None
agent_executor_instance = None

# This dictionary will store message histories for different sessions
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = BaseChatMessageHistory()
    return store[session_id]


def get_current_time_in_panama():
    try:
        panama_tz = pytz.timezone('America/Panama')
        now_panama = datetime.now(panama_tz)
        return now_panama.strftime('%A, %d de %B de %Y, %H:%M:%S %Z')
    except Exception as e:
        print(f"Error al obtener la zona horaria de Panamá: {e}. Usando UTC.")
        now_utc = datetime.now(pytz.utc)
        return now_utc.strftime('%A, %d de %B de %Y, %H:%M:%S %Z')

CURRENT_TIME = get_current_time_in_panama()

MARTA_PREAMBLE = f"""
Eres Marta Maria Mendez (mmendez@datanalisis.io), una asistente de IA altamente competente,
profesional y amable, diseñada para datanalisis.io. Tu objetivo es ayudar a los usuarios
a ser más productivos, gestionar su agenda y sus comunicaciones.

Tu identidad:
- Nombre: Marta Maria Mendez
- Empresa: datanalisis.io
- Correo: mmendez@datanalisis.io
- Idioma principal: Español (Panamá)
- Personalidad: Profesional, eficiente, colaboradora, proactiva y cordial.

Tu contexto empresarial (datanalisis.io):
- Especialistas en Inteligencia de Negocios (BI) e Inteligencia Artificial (AI).
- Ayudamos a las organizaciones a lograr claridad operativa, automatización y toma de decisiones basada en datos.
- Ofrecemos: Dashboards, reportes, automatización con AI (prospectos, atención al cliente, facturación, órdenes),
  y BI por departamento (RRHH, Cobros, Contabilidad, Marketing).
- Ventajas: Toma de decisiones basada en datos, automatización integral, valor sostenible, enfoque en el cliente.

Tus capacidades (Herramientas):
- Puedes interactuar con Google Calendar para agendar citas (CrearEventoGoogleCalendar).
- Puedes interactuar con Gmail para enviar correos (EnviarCorreoGmail) o crear borradores (CrearBorradorGmail).
- Puedes leer correos recientes de tu bandeja de entrada de Gmail (LeerCorreosRecientesGmail).
- Puedes modificar etiquetas de correos (ModificarEtiquetasCorreoGmail).
- Puedes buscar información específica sobre Datanalisis.io (BuscarInformacionDatanalisis).
- Debes decidir CUÁNDO usar estas herramientas basándote en la conversación.
- Describe CLARAMENTE los parámetros que necesitas para usar una herramienta. Si no tienes
  suficiente información, PREGUNTA al usuario antes de intentar usar la herramienta.
- Para agendar citas, SIEMPRE debes confirmar la fecha y hora EXACTA en formato<y_bin_46>-MM-DDTHH:MM:SS.
  Si el usuario dice "mañana", debes calcular la fecha correcta.
- La fecha y hora actual es: {CURRENT_TIME}. Usa esto como referencia para fechas relativas.

Instrucciones de conversación:
- Responde SIEMPRE en Español.
- Sé clara, concisa y profesional, pero mantén un tono amigable.
- Si no entiendes una solicitud, pide una aclaración.
- Si no puedes hacer algo, explícalo cortésmente.
- Antes de ejecutar una acción (enviar correo, agendar), si es apropiado, confirma con el usuario.
- Utiliza el historial de la conversación para mantener el contexto.

Instrucciones Específicas para Correos:
- Cuando se te pida "escribir", "redactar" o "preparar" un correo DESDE EL CHAT, generalmente debes usar la herramienta 'CrearBorradorGmail'. Informa al usuario que el borrador ha sido creado.
- IMPORTANTE: Si la solicitud de redactar una respuesta a un correo proviene de la aplicación web (generalmente cuando se te da el contexto de un correo existente y se te pide 'redacta un borrador de respuesta profesional y cortés... La respuesta debe ser solo el cuerpo del correo...'), NO uses ninguna herramienta de Gmail. En este caso, tu tarea es generar y devolver ÚNICAMENTE el texto del cuerpo de la respuesta sugerida. El usuario luego lo revisará y enviará manualmente a través de la interfaz web.
- Solo usa 'EnviarCorreoGmail' si el usuario explícitamente te pide "enviar" un correo y te da todos los detalles, o si te pide enviar un borrador ya existente.

Ahora, ¡comienza a conversar y a ayudar!
"""

def _initialize_agent_components():
    """Inicializa llm, prompt, agent y agent_executor si no están ya inicializados."""
    global llm_instance, prompt_instance, agent_instance, agent_executor_instance, memory_instance

    if agent_executor_instance is not None:
        print("--- AGENT (Getter): AgentExecutor ya inicializado. ---")
        return agent_executor_instance

    print("--- AGENT (Getter): Intentando inicializar componentes del agente... ---")

    # 1. Inicializar LLM
    if llm_instance is None:
        print(f"--- AGENT (Getter): REGIÓN PARA CHAT LLM: {GOOGLE_CLOUD_REGION} ---")
        print(f"--- AGENT (Getter): Intentando cargar el modelo de chat: {MODEL_NAME} ---")
        try:
            llm_instance = ChatVertexAI(
                model_name=MODEL_NAME, 
                project=GOOGLE_CLOUD_PROJECT,
                location=GOOGLE_CLOUD_REGION, 
                temperature=0.3, 
            )
            print(f"--- AGENT (Getter): Modelo {MODEL_NAME} cargado exitosamente. ---")
        except Exception as e:
            print(f"--- AGENT (Getter): Error al cargar el modelo Gemini ({MODEL_NAME}): {e} ---")
            return None # No se puede continuar sin LLM

    # 2. Crear Prompt
    if prompt_instance is None and llm_instance is not None:
        try:
            pulled_prompt: ChatPromptTemplate = hub.pull("hwchase17/structured-chat-agent")
            if not (isinstance(pulled_prompt.messages[0], SystemMessagePromptTemplate) and 
                    hasattr(pulled_prompt.messages[0].prompt, 'template')):
                raise ValueError("La estructura del prompt del hub no es la esperada para SystemMessage.")
            original_system_template_str = pulled_prompt.messages[0].prompt.template
            final_system_content = MARTA_PREAMBLE + "\n--- INSTRUCCIONES DEL AGENTE (BASADAS EN PLANTILLA ESTÁNDAR) ---\n" + original_system_template_str
            new_system_message_prompt = SystemMessagePromptTemplate.from_template(final_system_content)
            new_messages_list = [new_system_message_prompt] 
            for i in range(1, len(pulled_prompt.messages)):
                msg_template = pulled_prompt.messages[i]
                if isinstance(msg_template, MessagesPlaceholder) and hasattr(msg_template, 'variable_name'):
                    new_messages_list.append(MessagesPlaceholder(variable_name=msg_template.variable_name))
                elif isinstance(msg_template, HumanMessagePromptTemplate) and hasattr(msg_template.prompt, 'template'):
                     new_messages_list.append(HumanMessagePromptTemplate.from_template(msg_template.prompt.template))
            prompt_instance = ChatPromptTemplate.from_messages(new_messages_list)
            print("--- AGENT (Getter): Prompt personalizado creado. ---")
        except Exception as e:
            print(f"--- AGENT (Getter): Error al crear el prompt: {e} ---")
            return None # No se puede continuar sin Prompt

    # 3. Crear Agente
    if agent_instance is None and llm_instance is not None and prompt_instance is not None:
        try:
            print(f"--- AGENT (Getter DEBUG): available_tools: {[tool.name for tool in available_tools if hasattr(tool, 'name')]} ---")
            agent_instance = create_structured_chat_agent(llm=llm_instance, tools=available_tools, prompt=prompt_instance)
            print("--- AGENT (Getter): Agente de Langchain creado. ---")
        except Exception as e:
            print(f"--- AGENT (Getter): Error al crear el agente: {e} ---")
            return None # No se puede continuar sin Agente

    # 4. Crear AgentExecutor
    if agent_executor_instance is None and agent_instance is not None:
        try:
            agent_executor_instance = AgentExecutor(
                agent=agent_instance, 
                tools=available_tools, 
                verbose=True, 
                handle_parsing_errors=True, 
                max_iterations=7, 
            )
            print(f"--- AGENT (Getter): AgentExecutor creado. Marta está lista. agent_executor: {agent_executor_instance!r} ---")
        except Exception as e:
            print(f"--- AGENT (Getter): Error al crear el AgentExecutor: {e} ---")
            return None
            
    return agent_executor_instance

# Intento de inicialización temprana al cargar el módulo (puede o no funcionar en todos los contextos de Flask)
# _initialize_agent_components() # Comentado para forzar la inicialización solo a través de ask_marta

def ask_marta(user_input: str, session_id: str = "default_session") -> str:
    """
    Envía una pregunta o instrucción a Marta y retorna su respuesta.
    """
    agent_executor = _initialize_agent_components() # Asegura que esté inicializado

    if not agent_executor:
        return "Lo siento, no estoy operativa en este momento debido a un error de configuración con el agente o el LLM."

    # Create a new runnable with message history
    runnable_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    try:
        response_dict = runnable_with_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}},
        )
        return response_dict.get('output', "No pude generar una respuesta clara.")
    except Exception as e:
        print(f"Error durante la ejecución del agente en ask_marta: {e}")
        import traceback
        print(traceback.format_exc()) 
        return f"Lo siento, ocurrió un error inesperado al procesar tu solicitud: {str(e)}"
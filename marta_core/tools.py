
import os
import datetime 
from email.utils import parsedate_to_datetime 
import base64
from email.mime.text import MIMEText
from typing import List, Optional, Dict, Any 

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai.embeddings import VertexAIEmbeddings 
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# --- Configuración de Autenticación de Google ---
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar']
SCOPES_GMAIL = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose', 
    'https://www.googleapis.com/auth/gmail.modify' 
]
ALL_SCOPES = SCOPES_CALENDAR + SCOPES_GMAIL
CREDENTIALS_FILE_PATH = os.getenv('CREDENTIALS_PATH', 'credentials/credentials.json')
TOKEN_FILE_PATH = 'credentials/token.json'

# --- Variables Globales para RAG ---
CONTEXT_DOCUMENT_PATH = "data/contexto_datanalisis.txt" 
datanalisis_retriever = None 

def get_google_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, ALL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error al refrescar el token: {e}. Re-autenticando...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_PATH, ALL_SCOPES)
                creds = flow.run_local_server(port=8080) 
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_PATH, ALL_SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_calendar_service():
    creds = get_google_credentials(); service = None
    try: 
        service = build('calendar', 'v3', credentials=creds)
    except HttpError as e: 
        print(f'Ocurrió un error al construir el servicio de Calendar: {e}')
    return service

def get_gmail_service():
    creds = get_google_credentials(); service = None
    try: 
        service = build('gmail', 'v1', credentials=creds)
    except HttpError as e: 
        print(f'Ocurrió un error al construir el servicio de Gmail: {e}')
    return service

def initialize_datanalisis_retriever():
    global datanalisis_retriever
    if datanalisis_retriever is None:
        try:
            print("Inicializando retriever de Datanalisis.io...")
            if not os.path.exists(CONTEXT_DOCUMENT_PATH):
                print(f"Error: No se encontró el documento de contexto en {CONTEXT_DOCUMENT_PATH}")
                return None
            loader = TextLoader(CONTEXT_DOCUMENT_PATH, encoding='utf-8')
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            docs = text_splitter.split_documents(documents)
            if not docs:
                print("Error: No se pudieron generar fragmentos del documento.")
                return None
            
            # Leer configuración desde .env, con defaults a los valores que funcionaron
            embeddings_model_name = os.getenv('EMBEDDING_MODEL', "text-embedding-004") 
            gcp_project = os.getenv('GOOGLE_CLOUD_PROJECT')
            raw_gcp_region_tools = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1') 
            gcp_region = raw_gcp_region_tools.split('#')[0].strip() # Limpiar comentarios
            print(f"--- TOOLS: REGIÓN PARA EMBEDDINGS (desde .env o default): {gcp_region} ---")

            if not gcp_project:
                print("Error: GOOGLE_CLOUD_PROJECT no está configurado para embeddings.")
                return None

            print(f"Usando modelo de embeddings: {embeddings_model_name} en proyecto {gcp_project}, región {gcp_region}")
            embeddings = VertexAIEmbeddings(
                model_name=embeddings_model_name, 
                project=gcp_project, 
                location=gcp_region
            )
            vector_store = FAISS.from_documents(docs, embeddings)
            datanalisis_retriever = vector_store.as_retriever(search_kwargs={"k": 3}) 
            print("Retriever de Datanalisis.io inicializado exitosamente.")
        except Exception as e:
            print(f"Error al inicializar el retriever de Datanalisis.io: {e}")
            datanalisis_retriever = None 
    return datanalisis_retriever

class CalendarInput(BaseModel):
    summary: str = Field(description="Título o resumen del evento.")
    start_time_str: str = Field(description="Fecha y hora de inicio en formato ISO: YYYY-MM-DDTHH:MM:SS.")
    end_time_str: str = Field(description="Fecha y hora de fin en formato ISO: YYYY-MM-DDTHH:MM:SS.")
    attendees: Optional[List[Dict[str, str]]] = Field(default=None, description="Lista de diccionarios con los correos de los asistentes. Ejemplo: [{'email': 'juan@example.com'}].")
    description: Optional[str] = Field(default=None, description="Descripción más detallada del evento.")
    location: Optional[str] = Field(default=None, description="Ubicación física o virtual del evento.")
    timezone: Optional[str] = Field(default="America/Panama", description="Zona horaria del evento (defecto: America/Panama).")

class GmailInput(BaseModel): 
    to: str = Field(description="Dirección de correo del destinatario principal.")
    subject: str = Field(description="Asunto del correo.")
    message_text: str = Field(description="Cuerpo del mensaje en texto plano.")
    cc: Optional[str] = Field(default=None, description="Direcciones de correo para CC, separadas por coma si son múltiples.")

class ReadEmailsInput(BaseModel):
    max_results: Optional[int] = Field(default=5, description="Número máximo de correos a leer.")
    query: Optional[str] = Field(default="is:unread", description="Consulta para filtrar correos (ej. 'is:unread', 'from:cliente@example.com').")

class DatanalisisInfoInput(BaseModel):
    pregunta: str = Field(description="La pregunta del usuario sobre Datanalisis.io, sus servicios, ventajas, etc.")

class ModifyEmailLabelsInput(BaseModel):
    message_id: str = Field(description="El ID del mensaje de Gmail a modificar.")
    labels_to_add: Optional[List[str]] = Field(default=None, description="Lista de IDs de etiquetas para añadir (ej. ['STARRED', 'IMPORTANT']).")
    labels_to_remove: Optional[List[str]] = Field(default=None, description="Lista de IDs de etiquetas para quitar (ej. ['UNREAD', 'INBOX']).")

def crear_evento_calendario(summary: str, start_time_str: str, end_time_str: str, attendees: Optional[List[Dict[str, str]]] = None, description: Optional[str] = None, location: Optional[str] = None, timezone: str = 'America/Panama') -> str:
    service = get_calendar_service();
    if not service: return "Error: No se pudo conectar al servicio de Google Calendar."
    REQUIRED_ATTENDEE = "arturodlg@datanalisis.io"; event_attendees_list = []
    if attendees:
        for att_dict in attendees:
            if isinstance(att_dict, dict) and 'email' in att_dict and att_dict['email'].lower() != REQUIRED_ATTENDEE.lower():
                event_attendees_list.append({'email': att_dict['email']})
    if not any(att['email'].lower() == REQUIRED_ATTENDEE.lower() for att in event_attendees_list):
        event_attendees_list.append({'email': REQUIRED_ATTENDEE})
    effective_timezone = timezone if timezone else 'America/Panama'
    event = {'summary': summary, 'location': location, 'description': description, 'start': {'dateTime': start_time_str, 'timeZone': effective_timezone}, 'end': {'dateTime': end_time_str, 'timeZone': effective_timezone}, 'attendees': event_attendees_list, 'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24 * 60}, {'method': 'popup', 'minutes': 10}]}}
    try: created_event = service.events().insert(calendarId='primary', body=event, sendUpdates="all").execute(); return f"Evento '{summary}' creado exitosamente para el {start_time_str}. Link: {created_event.get('htmlLink')}"
    except HttpError as error: return f"Error al crear el evento: {error}"
    except Exception as e: return f"Un error inesperado ocurrió al crear el evento: {e}"

def enviar_correo_gmail(to: str, subject: str, message_text: str, cc: Optional[str] = None) -> str:
    service = get_gmail_service();
    if not service: return "Error: No se pudo conectar al servicio de Gmail."
    try:
        mime_message = MIMEText(message_text); mime_message['to'] = to; mime_message['subject'] = subject
        if cc: mime_message['cc'] = cc
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        sent_message = service.users().messages().send(userId='me', body=create_message).execute()
        return f"Correo enviado exitosamente a {to} (CC: {cc if cc else 'Ninguno'}) con asunto '{subject}'."
    except HttpError as error: return f"Error al enviar el correo: {error}"
    except Exception as e: return f"Un error inesperado ocurrió al enviar el correo: {e}"

def crear_borrador_gmail(to: str, subject: str, message_text: str, cc: Optional[str] = None) -> str:
    service = get_gmail_service()
    if not service: return "Error: No se pudo conectar al servicio de Gmail."
    try:
        mime_message = MIMEText(message_text); mime_message['to'] = to; mime_message['subject'] = subject
        if cc: mime_message['cc'] = cc
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        message_body = {'message': {'raw': encoded_message}}
        draft = service.users().drafts().create(userId='me', body=message_body).execute()
        draft_id = draft.get('id'); draft_link = f"https://mail.google.com/mail/u/0/#drafts/{draft_id}"
        return f"Borrador de correo creado exitosamente para {to} (CC: {cc if cc else 'Ninguno'}) con asunto '{subject}'. ID: {draft_id}. Link: {draft_link}"
    except HttpError as error: return f"Error al crear el borrador: {error}"
    except Exception as e: return f"Un error inesperado ocurrió al crear el borrador: {e}"

def _parse_email_details(msg: Dict[str, Any]) -> Dict[str, Any]:
    email_content = {"id": msg.get("id"), "snippet": msg.get("snippet")}
    payload = msg.get('payload'); headers = payload.get('headers') if payload else []
    date_str = None
    for header in headers:
        name = header.get('name', '').lower()
        if name == 'subject': email_content['subject'] = header.get('value')
        if name == 'from': email_content['from'] = header.get('value')
        if name == 'date': date_str = header.get('value'); email_content['date_str'] = date_str
    if date_str:
        try: email_content['date_dt'] = parsedate_to_datetime(date_str)
        except Exception: email_content['date_dt'] = None
    else: email_content['date_dt'] = None
    body_data = ""
    if payload and 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body_data += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8'); break
            elif part['mimeType'] == 'multipart/alternative':
                for sub_part in part.get('parts', []):
                    if sub_part['mimeType'] == 'text/plain' and 'data' in sub_part['body']:
                        body_data += base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8'); break
                if body_data: break
    elif payload and 'body' in payload and 'data' in payload['body']:
        body_data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    email_content['body'] = body_data.strip() if body_data else "Cuerpo del correo no encontrado."
    return email_content

def leer_correos_recientes_gmail(max_results: int = 5, query: str = "is:unread") -> List[Dict[str, Any]]:
    service = get_gmail_service()
    if not service: print("Error: No se pudo conectar al servicio de Gmail."); return [{"error": "No se pudo conectar."}]
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages_info = results.get('messages', [])
        emails_data = []
        if not messages_info: print(f"No se encontraron correos: {query}"); return [{"info": f"No se encontraron correos: {query}"}]
        for msg_info in messages_info:
            msg = service.users().messages().get(userId='me', id=msg_info['id'], format='full').execute()
            emails_data.append(_parse_email_details(msg))
        
        valid_dates_for_sorting = True
        for email in emails_data:
            if not isinstance(email.get('date_dt'), datetime.datetime):
                valid_dates_for_sorting = False; break
        
        if valid_dates_for_sorting and emails_data: emails_data.sort(key=lambda x: x['date_dt'], reverse=True)
        elif emails_data: print("Advertencia: No se pudieron ordenar todos los correos por fecha datetime.")
        return emails_data
    except HttpError as e: print(f"Error al leer correos: {e}"); return [{"error": f"Error al leer: {str(e)}"}]
    except Exception as e: print(f"Error inesperado al leer correos: {e}"); return [{"error": f"Error inesperado: {str(e)}"}]

def get_email_details_by_id(message_id: str) -> Optional[Dict[str, Any]]:
    service = get_gmail_service()
    if not service: print("Error: No se pudo conectar a Gmail."); return {"error": "No se pudo conectar a Gmail."}
    try:
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        return _parse_email_details(msg)
    except HttpError as e: print(f"Error al obtener correo {message_id}: {e}"); return {"error": f"Error al obtener correo: {str(e)}"}
    except Exception as e: print(f"Error inesperado al obtener correo {message_id}: {e}"); return {"error": f"Error inesperado: {str(e)}"}

def modify_email_labels(message_id: str, labels_to_add: Optional[List[str]] = None, labels_to_remove: Optional[List[str]] = None) -> str:
    service = get_gmail_service();
    if not service: return "Error: No se pudo conectar a Gmail."
    body = {};
    if labels_to_add: body['addLabelIds'] = labels_to_add
    if labels_to_remove: body['removeLabelIds'] = labels_to_remove
    if not body: return "No se especificaron etiquetas."
    try: service.users().messages().modify(userId='me', id=message_id, body=body).execute(); return f"Etiquetas del correo {message_id} modificadas."
    except HttpError as e: return f"Error al modificar etiquetas {message_id}: {e}"
    except Exception as e: return f"Error inesperado al modificar etiquetas: {e}"

def buscar_informacion_datanalisis(pregunta: str) -> str:
    global datanalisis_retriever
    if datanalisis_retriever is None:
        retriever_temp = initialize_datanalisis_retriever()
        if not retriever_temp: return "Error: Sistema de búsqueda no disponible (falló init retriever)."
    if not datanalisis_retriever: return "Error: Sistema de búsqueda no inicializado."
    try:
        print(f"Buscando info para: {pregunta}")
        docs_relevantes = datanalisis_retriever.invoke(pregunta) 
        if not docs_relevantes: return "No encontré info relevante. ¿Puedes reformular?"
        contexto = "\n\n---\n\n".join([doc.page_content for doc in docs_relevantes])
        print(f"Contexto encontrado:\n{contexto[:500]}...") 
        return f"Basado en la información de Datanalisis.io:\n{contexto}"
    except Exception as e: print(f"Error al buscar info: {e}"); return f"Problema al buscar info: {str(e)}"

calendar_tool = StructuredTool.from_function(func=crear_evento_calendario, name="CrearEventoGoogleCalendar", description="Útil para crear un nuevo evento o cita en Google Calendar cuando tienes todos los detalles: título (summary), hora de inicio (start_time_str), hora de fin (end_time_str) y opcionalmente asistentes (attendees), descripción (description), ubicación (location) y zona horaria (timezone).", args_schema=CalendarInput)
gmail_tool = StructuredTool.from_function(func=enviar_correo_gmail, name="EnviarCorreoGmail", description="Útil para enviar un correo electrónico a través de Gmail. Recibe destinatario (to), asunto (subject), cuerpo del mensaje (message_text) y opcionalmente copias (cc).", args_schema=GmailInput)
read_emails_tool = StructuredTool.from_function(func=leer_correos_recientes_gmail, name="LeerCorreosRecientesGmail", description="Útil para leer correos electrónicos recientes de la bandeja de entrada. Puedes especificar cuántos leer (max_results) y una consulta de búsqueda (query), por ejemplo 'is:unread' para no leídos o 'from:alguien@example.com'. Devuelve una lista de correos con su id, remitente, asunto, fecha y cuerpo, ordenados del más reciente al más antiguo.", args_schema=ReadEmailsInput)
datanalisis_info_tool = StructuredTool.from_function(func=buscar_informacion_datanalisis, name="BuscarInformacionDatanalisis", description="Útil para responder preguntas específicas sobre Datanalisis.io, sus servicios, propuesta de valor, ventajas competitivas, portafolio, etc. Recibe la pregunta del usuario como entrada.", args_schema=DatanalisisInfoInput)
modify_email_labels_tool = StructuredTool.from_function(func=modify_email_labels, name="ModificarEtiquetasCorreoGmail", description="Útil para modificar las etiquetas de un correo específico, como marcarlo como leído (quitando 'UNREAD') o añadir/quitar otras etiquetas.", args_schema=ModifyEmailLabelsInput)
crear_borrador_gmail_tool = StructuredTool.from_function(func=crear_borrador_gmail, name="CrearBorradorGmail", description="Útil para crear un borrador de correo electrónico en Gmail. Recibe destinatario (to), asunto (subject), cuerpo del mensaje (message_text) y opcionalmente copias (cc). Devuelve ID y enlace al borrador.", args_schema=GmailInput)

available_tools = [calendar_tool, gmail_tool, read_emails_tool, datanalisis_info_tool, modify_email_labels_tool, crear_borrador_gmail_tool]

if __name__ == '__main__':
    print("Probando la autenticación y los servicios...")
    test_creds = get_google_credentials()
    if test_creds: print("Credenciales obtenidas o refrescadas exitosamente.")
    else: print("Fallo al obtener las credenciales.")

    if test_creds:
        print("\nProbando el retriever de Datanalisis.io...")
        retriever = initialize_datanalisis_retriever() 
        if retriever:
            print("Retriever inicializado. Probando búsqueda...")
            respuesta_busqueda = buscar_informacion_datanalisis("¿Quiénes somos en Datanalisis.io?")
            print(f"\nRespuesta de la búsqueda de información:\n{respuesta_busqueda}")
        else:
            print("Fallo al inicializar el retriever de Datanalisis.io.")

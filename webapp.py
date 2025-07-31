# webapp.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
import sys
from datetime import datetime 

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from marta_core.agent import ask_marta 
    from marta_core.tools import (
        leer_correos_recientes_gmail, 
        enviar_correo_gmail, 
        get_google_credentials,
        get_email_details_by_id, 
        modify_email_labels,
        crear_evento_calendario, 
        buscar_informacion_datanalisis 
    )
except ImportError as e:
    print("Error crítico: No se pudieron importar los módulos de marta_core.")
    print(f"Detalle: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.urandom(24) 

GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
raw_region_app = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
GOOGLE_CLOUD_REGION = raw_region_app.split('#')[0].strip()
GEMINI_CHAT_MODEL = os.getenv('GEMINI_CHAT_MODEL', "gemini-2.0-flash-001")
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', "text-embedding-004")

print(f"--- APP: Usando Región: {GOOGLE_CLOUD_REGION}, Modelo Chat: {GEMINI_CHAT_MODEL}, Modelo Embedding: {EMBEDDING_MODEL} ---")

try:
    print("Inicializando credenciales para la app web...")
    get_google_credentials() 
    print("Credenciales listas (o se solicitará autenticación al primer uso de API).")
except Exception as e:
    print(f"Advertencia: No se pudieron inicializar las credenciales de Google al inicio: {e}")

@app.route('/')
def index():
    view_type = request.args.get('view', 'unread') 
    query_filter = "is:unread" if view_type == 'unread' else ""
    page_title = "Bandeja de Entrada (No Leídos)" if view_type == 'unread' else "Todos los Correos Recientes"
    no_emails_message = "No hay correos no leídos." if view_type == 'unread' else "No se encontraron correos recientes."
    if view_type not in ['unread', 'all']:
        flash("Vista de correo no válida, mostrando no leídos.", "warning"); view_type = 'unread'
    try:
        correos = leer_correos_recientes_gmail(max_results=20, query=query_filter) 
        if correos and isinstance(correos, list) and len(correos) > 0 and correos[0].get("error"):
            flash(f"Error al leer correos: {correos[0]['error']}", "danger"); correos_display = []
        elif correos and isinstance(correos, list) and len(correos) > 0 and correos[0].get("info"):
            flash(correos[0]['info'], "info"); correos_display = []
        else:
            correos_display = correos if isinstance(correos, list) else []
            if not correos_display: flash(no_emails_message, "info")
    except Exception as e:
        flash(f"Error inesperado al cargar correos: {str(e)}", "danger"); correos_display = []
    return render_template('index.html', correos=correos_display, page_title=page_title, active_view=view_type)

@app.route('/email/<message_id>')
def view_email(message_id):
    correo_seleccionado = get_email_details_by_id(message_id)
    if not correo_seleccionado or correo_seleccionado.get("error"):
        flash(f"No se encontró el correo con ID {message_id} o hubo un error: {correo_seleccionado.get('error', '') if correo_seleccionado else 'Error desconocido'}", "warning")
        return redirect(url_for('index'))
    respuesta_sugerida = request.args.get('respuesta_sugerida', '')
    return render_template('view_email.html', correo=correo_seleccionado, respuesta_sugerida=respuesta_sugerida)

@app.route('/suggest_reply/<message_id>', methods=['POST'])
def suggest_reply(message_id):
    correo_original = get_email_details_by_id(message_id)
    if not correo_original or correo_original.get("error") or not correo_original.get('body'):
        flash_message = "No se pudo obtener el contenido del correo original."
        if correo_original and correo_original.get("error"): flash_message += f" Detalle: {correo_original.get('error')}"
        flash(flash_message, "danger"); return redirect(url_for('view_email', message_id=message_id))
    prompt_para_marta = (f"Recibí este correo:\nDe: {correo_original.get('from')}\nAsunto: {correo_original.get('subject')}\nCuerpo:\n{correo_original.get('body')}\n\nRedacta un borrador de respuesta profesional y cortés en español. Considera el contexto de datanalisis.io si es relevante. Devuelve solo el cuerpo del correo para la respuesta.")
    respuesta_sugerida_marta = ""
    try:
        raw_marta_response = ask_marta(prompt_para_marta)
        if isinstance(raw_marta_response, str): respuesta_sugerida_marta = raw_marta_response
        elif isinstance(raw_marta_response, dict) and 'output' in raw_marta_response: respuesta_sugerida_marta = raw_marta_response['output']
        else: respuesta_sugerida_marta = "Marta no pudo generar una respuesta."; flash(respuesta_sugerida_marta, "warning")
    except Exception as e: flash(f"Error al generar respuesta con Marta: {str(e)}", "danger")
    return redirect(url_for('view_email', message_id=message_id, respuesta_sugerida=respuesta_sugerida_marta))

@app.route('/send_reply/<message_id>', methods=['POST'])
def send_reply(message_id):
    destinatario_form = request.form.get('destinatario')
    cc_form = request.form.get('cc_address') 
    asunto_respuesta = request.form.get('asunto_respuesta')
    cuerpo_respuesta = request.form.get('cuerpo_respuesta')
    if not destinatario_form or not asunto_respuesta or not cuerpo_respuesta:
        flash("Faltan datos para enviar (destinatario, asunto o cuerpo).", "danger")
        return redirect(url_for('view_email', message_id=message_id, respuesta_sugerida=cuerpo_respuesta, cc_address=cc_form))
    try:
        destinatario_email = destinatario_form
        if '<' in destinatario_form and '>' in destinatario_form:
            try: destinatario_email = destinatario_form.split('<')[1].split('>')[0]
            except IndexError: pass 
        destinatario_email = destinatario_email.strip()
        resultado_envio = enviar_correo_gmail(to=destinatario_email, subject=asunto_respuesta, message_text=cuerpo_respuesta, cc=cc_form if cc_form and cc_form.strip() else None)
        if "exitosamente" in resultado_envio.lower():
            flash(f"Respuesta enviada a {destinatario_email}: {resultado_envio}", "success")
            try:
                print(f"Marcando correo {message_id} como leído.")
                resultado_mod_label = modify_email_labels(message_id=message_id, labels_to_remove=['UNREAD'])
                print(f"Resultado de marcar como leído {message_id}: {resultado_mod_label}")
            except Exception as e_label: flash(f"Correo enviado, error al marcar como leído: {str(e_label)}", "warning")
        else: flash(f"Error al enviar respuesta: {resultado_envio}", "danger")
    except Exception as e: flash(f"Error inesperado al enviar correo: {str(e)}", "danger")
    return redirect(url_for('index', view='unread')) 

@app.route('/chat')
def chat_interface(): return render_template('chat.html')

@app.route('/api/chat', methods=['POST']) 
def api_send_chat_message():
    user_message = request.json.get('message')
    if not user_message: return jsonify({"error": "No se recibió ningún mensaje."}), 400
    print(f"API: Mensaje recibido para chat: {user_message}")
    try:
        marta_response = ask_marta(user_message)
        if isinstance(marta_response, str): response_text = marta_response
        elif isinstance(marta_response, dict) and 'output' in marta_response: response_text = marta_response['output']
        else: response_text = "Lo siento, no pude procesar esa respuesta."
        print(f"API: Respuesta de Marta para chat: {response_text}")
        return jsonify({"reply": response_text})
    except Exception as e:
        print(f"API Error en send_chat_message: {str(e)}")
        return jsonify({"error": f"Error al procesar el mensaje con Marta: {str(e)}"}), 500

@app.route('/api/emails', methods=['GET'])
def api_get_emails():
    view_type = request.args.get('view', 'unread')
    max_results_str = request.args.get('max', '10')
    try: max_r = int(max_results_str)
    except ValueError: return jsonify({"error": "Parámetro 'max' debe ser un número entero."}), 400
    query_filter = "is:unread" if view_type == 'unread' else ""
    if view_type not in ['unread', 'all']: return jsonify({"error": "Parámetro 'view' inválido. Usar 'unread' o 'all'."}), 400
    try: correos = leer_correos_recientes_gmail(max_results=max_r, query=query_filter); return jsonify(correos)
    except Exception as e: return jsonify({"error": f"Error al leer correos: {str(e)}"}), 500

@app.route('/api/email/<message_id>', methods=['GET'])
def api_get_email_details(message_id):
    try:
        correo = get_email_details_by_id(message_id)
        if correo:
            if correo.get("error"): return jsonify(correo), 404 
            return jsonify(correo)
        else: return jsonify({"error": f"Correo con ID {message_id} no encontrado."}), 404
    except Exception as e: return jsonify({"error": f"Error al obtener detalles del correo: {str(e)}"}), 500

@app.route('/api/email/<message_id>/suggest_reply', methods=['POST']) 
def api_suggest_email_reply(message_id):
    try:
        correo_original = get_email_details_by_id(message_id)
        if not correo_original or correo_original.get("error") or not correo_original.get('body'):
            error_msg = "No se pudo obtener el contenido del correo original."
            if correo_original and correo_original.get("error"): error_msg += f" Detalle: {correo_original.get('error')}"
            return jsonify({"error": error_msg}), 404
        prompt_para_marta = (f"Recibí este correo:\nDe: {correo_original.get('from')}\nAsunto: {correo_original.get('subject')}\nCuerpo:\n{correo_original.get('body')}\n\nRedacta un borrador de respuesta profesional y cortés en español. Considera el contexto de datanalisis.io si es relevante. Devuelve solo el cuerpo del correo para la respuesta.")
        raw_marta_response = ask_marta(prompt_para_marta)
        if isinstance(raw_marta_response, str): respuesta_sugerida = raw_marta_response
        elif isinstance(raw_marta_response, dict) and 'output' in raw_marta_response: respuesta_sugerida = raw_marta_response['output']
        else: respuesta_sugerida = "Marta no pudo generar una respuesta en el formato esperado."
        return jsonify({"suggested_reply": respuesta_sugerida})
    except Exception as e: return jsonify({"error": f"Error al generar la respuesta sugerida: {str(e)}"}), 500

@app.route('/api/email/send', methods=['POST'])
def api_send_email():
    data = request.json
    to = data.get('to'); subject = data.get('subject'); message_text = data.get('message_text')
    cc = data.get('cc'); original_message_id = data.get('original_message_id')
    if not to or not subject or not message_text: return jsonify({"error": "Faltan campos: to, subject, message_text."}), 400
    try:
        destinatario_email = to
        if '<' in to and '>' in to: 
            try: destinatario_email = to.split('<')[1].split('>')[0]
            except IndexError: pass
        destinatario_email = destinatario_email.strip()
        resultado_envio = enviar_correo_gmail(to=destinatario_email, subject=subject, message_text=message_text, cc=cc if cc and cc.strip() else None)
        response_data = {"status": resultado_envio}
        if "exitosamente" in resultado_envio.lower() and original_message_id:
            try:
                resultado_mod_label = modify_email_labels(message_id=original_message_id, labels_to_remove=['UNREAD'])
                response_data["label_modification_status"] = resultado_mod_label
            except Exception as e_label: response_data["label_modification_error"] = str(e_label)
        return jsonify(response_data)
    except Exception as e: return jsonify({"error": f"Error inesperado al enviar correo: {str(e)}"}), 500

@app.route('/api/calendar/create_event', methods=['POST'])
def api_create_calendar_event():
    data = request.json
    try:
        summary = data.get('summary'); start_time_str = data.get('start_time_str'); end_time_str = data.get('end_time_str')
        if not all([summary, start_time_str, end_time_str]): return jsonify({"error": "Faltan campos: summary, start_time_str, end_time_str."}), 400
        resultado = crear_evento_calendario(summary=summary, start_time_str=start_time_str, end_time_str=end_time_str, attendees=data.get('attendees'), description=data.get('description'), location=data.get('location'), timezone=data.get('timezone', 'America/Panama'))
        return jsonify({"status": resultado})
    except Exception as e: return jsonify({"error": f"Error al crear evento: {str(e)}"}), 500

@app.route('/api/datanalisis_info', methods=['POST'])
def api_datanalisis_info():
    data = request.json; pregunta = data.get('pregunta')
    if not pregunta: return jsonify({"error": "Falta el campo 'pregunta'."}), 400
    try: respuesta = buscar_informacion_datanalisis(pregunta); return jsonify({"respuesta": respuesta})
    except Exception as e: return jsonify({"error": f"Error al buscar información: {str(e)}"}), 500

@app.route('/client/<phone_number>')
def view_client(phone_number):
    client = CRMService.getClientByPhone(phone_number)
    if not client:
        flash(f"No se encontró el cliente con el teléfono {phone_number}", "warning")
        return redirect(url_for('index'))
    return render_template('client_profile.html', client=client)

if __name__ == '__main__':
    if not os.path.exists('templates'): os.makedirs('templates')
    
    base_html_path = os.path.join('templates', 'base.html')
    if not os.path.exists(base_html_path):
        with open(base_html_path, 'w', encoding='utf-8') as f:
            f.write("""<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Marta AI{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .email-snippet { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
        .nav-tab { color: #e0f2fe; padding-left: 0.75rem; padding-right: 0.75rem; padding-top: 0.5rem; padding-bottom: 0.5rem; border-radius: 0.375rem; font-size: 0.875rem; line-height: 1.25rem; font-weight: 500; }
        .nav-tab:hover { background-color: #075985; }
        .nav-tab-active { background-color: #0369a1; color: white; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800">
    <nav class="bg-sky-700 text-white p-4 shadow-md">
        <div class="container mx-auto flex justify-between items-center">
            <a href="{{ url_for('index') }}" class="text-2xl font-bold">Marta AI</a>
            <div>
                <a href="{{ url_for('index', view='unread') }}" class="nav-tab {% if active_view == 'unread' or active_view is none %}nav-tab-active{% endif %}">No Leídos</a>
                <a href="{{ url_for('index', view='all') }}" class="nav-tab {% if active_view == 'all' %}nav-tab-active{% endif %}">Todos</a>
                <a href="{{ url_for('chat_interface') }}" class="nav-tab {% if request.endpoint == 'chat_interface' %}nav-tab-active{% endif %}">Chat</a>
            </div>
        </div>
    </nav>
    <main class="container mx-auto p-4 mt-6">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="my-3 p-3 rounded-md {% if category == 'danger' %}bg-red-200 text-red-800{% elif category == 'success' %}bg-green-200 text-green-800{% else %}bg-blue-200 text-blue-800{% endif %}" role="alert">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <footer class="text-center p-4 mt-12 text-sm text-slate-600">
        &copy; {{ now().year }} Datanalisis.io - Marta AI
    </footer>
    {% block scripts %}{% endblock %}
</body>
</html>
""")

    index_html_path = os.path.join('templates', 'index.html')
    if not os.path.exists(index_html_path):
        with open(index_html_path, 'w', encoding='utf-8') as f:
            f.write("""{% extends "base.html" %}
{% block title %}{{ page_title }} - Marta AI{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-lg shadow-lg">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-semibold text-sky-700">{{ page_title }}</h1>
    </div>
    {% if correos %}
        <ul class="space-y-4">
            {% for correo in correos %}
            <li class="border border-slate-300 p-4 rounded-md hover:shadow-md transition-shadow duration-200">
                <a href="{{ url_for('view_email', message_id=correo.id) }}" class="block">
                    <div class="flex justify-between items-center mb-1">
                        <h2 class="text-lg font-medium text-sky-600">{{ correo.subject if correo.subject else '(Sin Asunto)' }}</h2>
                        <span class="text-xs text-slate-500">{{ correo.date_str if correo.date_str else correo.date }}</span>
                    </div>
                    <p class="text-sm text-slate-600 mb-2"><strong>De:</strong> {{ correo.from }}</p>
                    <p class="text-sm text-slate-500 email-snippet"><em>{{ correo.snippet }}</em></p>
                </a>
            </li>
            {% endfor %}
        </ul>
    {% else %}
        <p class="text-slate-600">{{ no_emails_message if no_emails_message else "No hay correos para mostrar." }}</p>
    {% endif %}
    <div class="mt-6">
        <a href="{{ url_for('index', view=active_view if active_view else 'unread') }}" class="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition-colors">Refrescar Vista Actual</a>
    </div>
</div>
{% endblock %}
""")

    view_email_html_path = os.path.join('templates', 'view_email.html')
    if not os.path.exists(view_email_html_path):
        with open(view_email_html_path, 'w', encoding='utf-8') as f:
            f.write("""{% extends "base.html" %}
{% block title %}Ver Correo - {{ correo.subject if correo.subject else '(Sin Asunto)' }}{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-lg shadow-lg">
    <div class="mb-6 pb-4 border-b border-slate-300">
        <h1 class="text-2xl font-semibold text-sky-700 mb-1">{{ correo.subject if correo.subject else '(Sin Asunto)' }}</h1>
        <p class="text-sm text-slate-600"><strong>De:</strong> {{ correo.from }}</p>
        <p class="text-sm text-slate-500"><strong>Fecha:</strong> {{ correo.date_str if correo.date_str else correo.date }}</p>
    </div>
    <div class="mb-6 prose max-w-none">
        <h3 class="text-xl font-medium mb-2 text-sky-600">Contenido del Correo:</h3>
        <div class="bg-slate-50 p-4 rounded-md border border-slate-200 whitespace-pre-wrap">{{ correo.body }}</div>
    </div>
    <hr class="my-8">
    <div>
        <h3 class="text-xl font-medium mb-3 text-sky-600">Gestionar Respuesta:</h3>
        <form action="{{ url_for('suggest_reply', message_id=correo.id) }}" method="POST" class="mb-6">
            <button type="submit" class="px-4 py-2 bg-amber-500 text-white rounded-md hover:bg-amber-600 transition-colors">Generar Respuesta Sugerida por Marta</button>
        </form>
        <form action="{{ url_for('send_reply', message_id=correo.id) }}" method="POST">
            <div class="mb-4">
                <label for="destinatario" class="block text-sm font-medium text-slate-700 mb-1">Para:</label>
                <input type="text" name="destinatario" id="destinatario" value="{{ correo.from }}" required class="w-full p-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500">
            </div>
            <div class="mb-4">
                <label for="cc_address" class="block text-sm font-medium text-slate-700 mb-1">CC:</label>
                <input type="text" name="cc_address" id="cc_address" value="arturodlg@datanalisis.io" 
                       class="w-full p-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500">
            </div>
            <div class="mb-4">
                <label for="asunto_respuesta" class="block text-sm font-medium text-slate-700 mb-1">Asunto de Respuesta:</label>
                <input type="text" name="asunto_respuesta" id="asunto_respuesta" value="Re: {{ correo.subject if correo.subject else '' }}" required class="w-full p-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500">
            </div>
            <div class="mb-4">
                <label for="cuerpo_respuesta" class="block text-sm font-medium text-slate-700 mb-1">Cuerpo de la Respuesta:</label>
                <textarea name="cuerpo_respuesta" id="cuerpo_respuesta" rows="10" required class="w-full p-2 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500">{% if respuesta_sugerida %}{{ respuesta_sugerida | safe }}{% else %}Estimado/a [Nombre del contacto],\n\nGracias por tu correo.\n\n[Aquí tu respuesta...]\n\nSaludos cordiales,\nMarta Maria Mendez\nmmendez@datanalisis.io{% endif %}</textarea>
            </div>
            <div class="flex items-center space-x-4">
                <button type="submit" class="px-6 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition-colors">Aprobar y Enviar Respuesta</button>
                <a href="{{ url_for('index') }}" class="px-4 py-2 bg-slate-200 text-slate-700 rounded-md hover:bg-slate-300 transition-colors">Volver a Bandeja</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
""")

    chat_html_path = os.path.join('templates', 'chat.html')
    if not os.path.exists(chat_html_path):
        with open(chat_html_path, 'w', encoding='utf-8') as f:
            f.write("""{% extends "base.html" %}
{% block title %}Chat con Marta - Marta AI{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-lg shadow-lg">
    <h1 class="text-3xl font-semibold mb-6 text-sky-700">Chat con Marta</h1>
    <div id="chatLog" class="mb-4 border border-slate-300 rounded-md p-4 h-96 overflow-y-auto bg-slate-50 space-y-3">
        <div class="p-2 rounded-md bg-sky-100 text-sky-800 self-start max-w-xl">
            <strong>Marta:</strong> ¡Hola! Soy Marta. ¿En qué puedo ayudarte hoy?
        </div>
    </div>
    <form id="chatForm" class="flex space-x-3">
        <input type="text" id="chatInput" placeholder="Escribe tu mensaje a Marta..." required class="flex-grow p-3 border border-slate-300 rounded-md shadow-sm focus:ring-sky-500 focus:border-sky-500">
        <button type="submit" class="px-6 py-3 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition-colors font-medium">Enviar</button>
    </form>
</div>
{% endblock %}
{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const chatLog = document.getElementById('chatLog');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');

    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        appendMessageToLog('Tú', userMessage, true);
        chatInput.value = '';
        chatInput.disabled = true;

        const thinkingDiv = appendMessageToLog('Marta', 'Pensando...', false, true);

        fetch("{{ url_for('api_send_chat_message') }}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userMessage
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Error de red o del servidor');
                });
            }
            return response.json();
        })
        .then(data => {
            if (thinkingDiv && thinkingDiv.parentNode === chatLog) {
                chatLog.removeChild(thinkingDiv);
            }
            appendMessageToLog('Marta', data.reply);
        })
        .catch(error => {
            console.error('Error en chat:', error);
            if (thinkingDiv && thinkingDiv.parentNode === chatLog) {
                chatLog.removeChild(thinkingDiv);
            }
            appendMessageToLog('Marta', 'Lo siento, ocurrió un error al procesar tu mensaje: ' + error.message, false, false, true);
        })
        .finally(() => {
            chatInput.disabled = false;
            chatInput.focus();
        });
    });

    function appendMessageToLog(sender, message, isUser = false, isThinking = false, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('p-2', 'rounded-md', 'max-w-xl', 'break-words');
        
        let bgColor = 'bg-sky-100';
        let textColor = 'text-sky-800';
        let align = 'self-start';
        
        if (isUser) {
            bgColor = 'bg-green-100';
            textColor = 'text-green-800';
            align = 'self-end';
        } else if (isError) {
            bgColor = 'bg-red-100';
            textColor = 'text-red-800';
        } else if (isThinking) {
            bgColor = 'bg-slate-200';
            textColor = 'text-slate-600';
            message = '<span class="italic">' + message + '</span>';
        }
        
        messageDiv.classList.add(bgColor, textColor, align);
        
        const messageText = message ? message.toString() : '';
        const messageContent = messageText.replace(/\\n/g, '<br>').replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = '<strong>' + sender + ':</strong> ' + messageContent;
        
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
        return messageDiv;
    }
});
</script>
{% endblock %}
""")
    
    app.jinja_env.globals['now'] = datetime.utcnow 
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)

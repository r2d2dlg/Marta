from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from google.cloud.sql.connector import Connector # Corrected import
import logging
import pandas as pd
import io
from datetime import datetime, timedelta # timedelta was in your new simple_dashboard.py
import secrets
import re
import json

# Authentication imports
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

# Vertex AI imports
try:
    import vertexai # Main Vertex AI SDK
    from vertexai.generative_models import GenerativeModel # For Gemini
    from google.auth import default # For ADC
    VERTEX_AI_AVAILABLE = True # Set to True on successful import
    gemini_model = None
except ImportError as e:
    # This means a core library is missing, AI features definitely won't work.
    logging.basicConfig(level=logging.INFO) # Ensure logger is configured
    logger = logging.getLogger(__name__)
    logger.warning(f"Vertex AI core dependencies (vertexai or google.auth) not available: {e}. AI features will be disabled.")
    VERTEX_AI_AVAILABLE = False
    gemini_model = None
except Exception as e: # Catch any other unexpected error during import
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error during Vertex AI import: {e}. AI features likely disabled.", exc_info=True)
    VERTEX_AI_AVAILABLE = False
    gemini_model = None

# Google Cloud AI Platform imports - TEMPORARILY DISABLED for deployment debugging
# try:
#     from google.cloud import aiplatform
#     from google.cloud import aiplatform_v1 # For MatchServiceClient and FindNeighborsRequest
#     from vertexai.preview.language_models import TextEmbeddingModel as PreviewTextEmbeddingModel
#     from vertexai.preview.language_models import TextEmbeddingInput as PreviewTextEmbeddingInput
#     logger.info("Google Cloud AI Platform imports successful")
# except ImportError as e:
#     logger.warning(f"Failed to import Google Cloud AI Platform modules: {e}")
aiplatform = None
aiplatform_v1 = None
PreviewTextEmbeddingModel = None
PreviewTextEmbeddingInput = None

# Set up logging (if not already set up by Vertex AI import failure)
if 'logger' not in globals():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# --- RAG Configuration ---
# Ensure logger is defined before this usage if you uncomment logger lines here.
RAG_PROJECT_ID_STRING = os.environ.get("RAG_PROJECT_ID") or "veterinaria-neuman-456818" # Your actual project ID
RAG_LOCATION = os.environ.get("RAG_LOCATION") or "us-south1"
RAG_EMBEDDING_MODEL_NAME = "textembedding-gecko@003"
RAG_INDEX_ID = os.getenv('RAG_INDEX_ID', '3385176399596748800')  # Get from env with fallback

# Endpoint details from your Vertex AI setup
RAG_INDEX_ENDPOINT_PROJECT_NUMBER = os.environ.get("RAG_INDEX_ENDPOINT_PROJECT_NUMBER") or "828930759180"
RAG_INDEX_ENDPOINT_ID = os.environ.get("RAG_INDEX_ENDPOINT_ID") or "ariadna_endpoint"
RAG_DEPLOYED_INDEX_ID = os.environ.get("RAG_DEPLOYED_INDEX_ID") or "ariadna_1749172515035"

RAG_API_ENDPOINT = f"{RAG_LOCATION}-aiplatform.googleapis.com"
RAG_INDEX_ENDPOINT_RESOURCE_NAME = f"projects/{RAG_INDEX_ENDPOINT_PROJECT_NUMBER}/locations/{RAG_LOCATION}/indexEndpoints/{RAG_INDEX_ENDPOINT_ID}"

# Optional: Log the RAG configuration being used (good for debugging at startup)
logger.info(f"RAG Config - Project ID: {RAG_PROJECT_ID_STRING}, Location: {RAG_LOCATION}")
logger.info(f"RAG Config - Embedding Model: {RAG_EMBEDDING_MODEL_NAME}")
logger.info(f"RAG Config - API Endpoint: {RAG_API_ENDPOINT}")
logger.info(f"RAG Config - Index Endpoint Resource Name: {RAG_INDEX_ENDPOINT_RESOURCE_NAME}")
logger.info(f"RAG Config - Deployed Index ID: {RAG_DEPLOYED_INDEX_ID}")
# --- End RAG Configuration ---

# --- Vertex AI Initialization ---
if VERTEX_AI_AVAILABLE is not False: # Proceed if core imports didn't fail
    # This block will attempt to initialize Vertex AI. If it fails, VERTEX_AI_AVAILABLE will be set to False.
    # If core imports failed above, VERTEX_AI_AVAILABLE is already False and this block is skipped.
    try:
        # Log all environment variables for debugging in Cloud Run
        import os
        logger.info("--- Cloud Run Environment Variables (Startup) ---")
        for key, value in os.environ.items():
            logger.info(f"ENV - {key}: {value}")
        logger.info("------------------------------------")
        
        logger.info("Starting Vertex AI initialization...")
        PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not PROJECT_ID:
            PROJECT_ID = os.environ.get("GCP_PROJECT_ID") # As per your .env

        LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")
        if not LOCATION:
            instance_name = os.environ.get("INSTANCE_CONNECTION_NAME")
            if instance_name and len(instance_name.split(':')) == 3:
                LOCATION = instance_name.split(':')[1]
                logger.info(f"Inferred GOOGLE_CLOUD_LOCATION='{LOCATION}' from INSTANCE_CONNECTION_NAME.")
            else:
                LOCATION = "us-south1"
                logger.info(f"GOOGLE_CLOUD_LOCATION not set and could not infer. Defaulting to '{LOCATION}' for optimal performance with RAG index.")

        if not PROJECT_ID:
            logger.error("FATAL: GCP Project ID (GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID) not set. Vertex AI cannot be initialized.")
            VERTEX_AI_AVAILABLE = False
        else:
            logger.info(f"Getting Google Cloud credentials...")
            creds, project_inferred = default()
            final_project_id = project_inferred if project_inferred else PROJECT_ID
            
            logger.info(f"Attempting to initialize Vertex AI for project: {final_project_id}, location: {LOCATION}")
            vertexai.init(project=final_project_id, location=LOCATION, credentials=creds)
            
            GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash-001")
            logger.info(f"Loading Gemini model: {GEMINI_MODEL_NAME}")
            gemini_model = GenerativeModel(GEMINI_MODEL_NAME) # Using the newer SDK style
            logger.info(f"✅ Vertex AI initialized successfully! Gemini model '{GEMINI_MODEL_NAME}' loaded.")
            VERTEX_AI_AVAILABLE = True # Explicitly set to True on success

    except Exception as e:
        # More explicit logging to ensure visibility
        import traceback
        logger.error(f"ERROR: An unhandled exception occurred during Vertex AI initialization.")
        logger.error(f"Exception Type: {type(e).__name__}")
        logger.error(f"Exception Message: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        VERTEX_AI_AVAILABLE = False
else:
    logger.warning("Vertex AI core imports failed, skipping initialization.")

def decodificar_customer_id(customer_id):
    """
    Decodifica un Customer ID con el formato: ZZJ-BT-1-C-002
    Donde:
    ZZ = Tipo de venta (ZZ = Venta de Distribuidora)
    J = Vendedor (J = Jose, E = Euri, P = Paula)
    BT = Provincia
    1 = Número de ruta
    C = Tipo de cliente (C = Clínica, T = Tienda, F = Finca)
    002 = Número secuencial del cliente
    """
    
    # Diccionarios de mapeo
    VENDEDORES = {
        'J': 'Jose',
        'E': 'Euri',
        'P': 'Paula'
    }
    
    PROVINCIAS = {
        'CENTRO': 'Panamá Centro',
        'OESTE': 'Panamá Oeste',
        'HE': 'Herrera',
        'LS': 'Los Santos',
        'CH': 'Chiriquí',
        'MUES RET': 'Muestra',
        'VE': 'Veraguas',
        'BT': 'Bocas del Toro',
        'C': 'Colón'
    }
    
    TIPO_CLIENTE = {
        'T': 'Tienda',
        'C': 'Clínica',
        'F': 'Finca'
    }
    
    try:
        customer_id_str = str(customer_id).strip()
        
        # Manejar casos especiales como "A-0" (cliente simple sin formato estándar)
        if not '-' in customer_id_str or len(customer_id_str.split('-')) < 3:
            return {
                'vendedor': 'SIN ASIGNAR',
                'provincia': 'SIN ASIGNAR', 
                'ruta': 'SIN ASIGNAR',
                'tipo_cliente': 'SIN ASIGNAR'
            }
        
        # Separar el código por guiones
        partes = customer_id_str.split('-')
        
        # Extraer cada componente
        codigo_venta = partes[0]
        tipo_venta = codigo_venta[:2]  # ZZ
        vendedor = codigo_venta[2] if len(codigo_venta) > 2 else 'SIN ASIGNAR'
        
        provincia = partes[1]  # BT, CH, etc.
        
        # Manejar casos especiales
        if 'EMP' in partes:
            tipo_cliente = 'Empleado'
            ruta = 'SIN ASIGNAR'
        else:
            ruta = partes[2] if len(partes) > 2 else 'SIN ASIGNAR'
            tipo_cliente_code = partes[3] if len(partes) > 3 else 'SIN ASIGNAR'
            tipo_cliente = TIPO_CLIENTE.get(tipo_cliente_code, 'SIN ASIGNAR')
        
        # Mapeo de códigos a descripciones
        vendedor_desc = VENDEDORES.get(vendedor, 'SIN ASIGNAR')
        provincia_desc = PROVINCIAS.get(provincia, 'SIN ASIGNAR')
        
        return {
            'vendedor': vendedor_desc,
            'provincia': provincia_desc,
            'ruta': ruta,
            'tipo_cliente': tipo_cliente
        }
    except Exception as e:
        logger.warning(f"Error decodificando Customer ID {customer_id}: {str(e)}")
        return {
            'vendedor': 'SIN ASIGNAR',
            'provincia': 'SIN ASIGNAR',
            'ruta': 'SIN ASIGNAR',
            'tipo_cliente': 'SIN ASIGNAR'
        }

app = Flask(__name__)

# Force HTTPS behind proxy (Cloud Run) - must be before app configuration
if os.environ.get('GOOGLE_CLOUD_PROJECT'):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuration for Flask-Login
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['JSON_AS_ASCII'] = False

# Force HTTPS for redirects in production
if os.environ.get('GOOGLE_CLOUD_PROJECT'):
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# User model
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role='user', is_active=True, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self._is_active = is_active
        self.created_at = created_at
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self._is_active

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# User management functions (Copied from your new simple_dashboard.py)
def create_users_table():
    try:
        conn, message = get_db_connection()
        if not conn:
            logger.error(f"Cannot connect to database: {message}")
            return False
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY, username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user', is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_login TIMESTAMP,
                permissions TEXT DEFAULT 'dashboard'
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating users table: {str(e)}")
        return False

def get_user_by_id(user_id):
    try:
        conn, message = get_db_connection()
        if not conn: return None
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash, role, is_active, created_at FROM usuarios WHERE id = %s AND is_active = true', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return User(id=result[0], username=result[1], email=result[2], password_hash=result[3], role=result[4], is_active=result[5], created_at=result[6])
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        return None

def get_user_by_username(username):
    try:
        conn, message = get_db_connection()
        if not conn: return None
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash, role, is_active, created_at FROM usuarios WHERE username = %s AND is_active = true', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return User(id=result[0], username=result[1], email=result[2], password_hash=result[3], role=result[4], is_active=result[5], created_at=result[6])
        return None
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}")
        return None

def create_user(username, email, password, role='user'):
    try:
        conn, message = get_db_connection()
        if not conn: return False, message
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (username, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id', (username, email, password_hash, role))
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"User created successfully: {username}")
        return True, f"Usuario {username} creado exitosamente"
    except Exception as e:
        error_msg = f"Error creating user: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def get_all_users():
    try:
        conn, message = get_db_connection()
        if not conn: return []
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, role, is_active, created_at, last_login, permissions FROM usuarios ORDER BY created_at DESC')
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        users = [{'id': r[0], 'username': r[1], 'email': r[2], 'role': r[3], 'is_active': r[4], 'created_at': r[5], 'last_login': r[6], 'permissions': r[7] or 'dashboard'} for r in results]
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

def update_user_status(user_id, is_active):
    try:
        conn, message = get_db_connection()
        if not conn: return False, message
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET is_active = %s WHERE id = %s', (is_active, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        status = "activado" if is_active else "desactivado"
        return True, f"Usuario {status} exitosamente"
    except Exception as e:
        error_msg = f"Error updating user status: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def update_user_role(user_id, role):
    try:
        conn, message = get_db_connection()
        if not conn: return False, message
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET role = %s WHERE id = %s', (role, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Rol actualizado exitosamente"
    except Exception as e:
        error_msg = f"Error updating user role: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def update_last_login(user_id):
    try:
        conn, message = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET last_login = CURRENT_TIMESTAMP WHERE id = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating last login: {str(e)}")

def ensure_admin_user():
    try:
        create_users_table()
        conn, message = get_db_connection()
        if not conn:
            logger.error(f"Cannot connect to database for admin check: {message}")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", ('aneuman',))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw('#Vetneuman4012'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO usuarios (username, email, password_hash, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                           ('aneuman', 'admin@veterinarianeuman.com', password_hash, 'admin', True))
            conn.commit()
            logger.info("Default admin user created successfully")
        else:
            logger.info("Admin user already exists")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error ensuring admin user: {e}")
        if 'conn' in locals() and conn: conn.close()

def get_db_connection():
    try:
        # Get environment variables
        db_instance_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
        db_user = os.environ.get('DB_USER') 
        db_name = os.environ.get('DB_NAME')
        db_password = os.environ.get('DB_PASSWORD')
        
        logger.info(f"[DB_CONNECTION] Attempting connection with user: {db_user}, db: {db_name}, instance: {db_instance_connection_name}")
        logger.info(f"[DB_CONNECTION] Password length: {len(db_password) if db_password else 0}")
        
        if not all([db_instance_connection_name, db_user, db_name, db_password]):
            missing = [item for item, var in [('INSTANCE_CONNECTION_NAME', db_instance_connection_name), ('DB_USER', db_user), ('DB_NAME', db_name), ('DB_PASSWORD', db_password)] if not var]
            error_msg = f"Variables de entorno de base de datos faltantes: {', '.join(missing)}"
            logger.error(error_msg)
            return None, error_msg
        
        # Try Cloud SQL Connector first
        try:
            logger.info("[DB_CONNECTION] Attempting Cloud SQL Connector connection")
            connector = Connector()
            conn = connector.connect(
                db_instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
            )
            logger.info("[DB_CONNECTION] Cloud SQL Connector connection successful")
            return conn, "Conexión exitosa con Cloud SQL Connector"
        except Exception as cloud_sql_error:
            logger.warning(f"[DB_CONNECTION] Cloud SQL Connector failed: {cloud_sql_error}")
            
            # Fallback to direct connection
            try:
                import psycopg2
                logger.info("[DB_CONNECTION] Attempting direct psycopg2 connection")
                
                # For direct connection, we need DB_HOST
                db_host = os.environ.get('DB_HOST', 'localhost')
                
                conn = psycopg2.connect(
                    host=db_host,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                logger.info("[DB_CONNECTION] Direct psycopg2 connection successful")
                return conn, "Conexión exitosa con conexión directa"
            except Exception as direct_error:
                logger.error(f"[DB_CONNECTION] Direct connection also failed: {direct_error}")
                raise cloud_sql_error  # Re-raise the original Cloud SQL error
                
    except Exception as e:
        error_msg = f"Error de conexión a la base de datos: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg

def standardize_date_format(date_str):
    """
    Convert date string to standardized DD/M/YY format.
    Handles various input formats. If parsing fails, returns original string.
    """
    if not date_str or pd.isna(date_str): return date_str
    date_str = str(date_str).strip()
    # If already in correct DD/M/YY format, return as-is
    if '/' in date_str and len(date_str.split('/')[-1]) == 2:
        parts = date_str.split('/')
        if len(parts) == 3 and len(parts[2]) == 2: # Basic check for D/M/YY or DD/MM/YY
            try: # Further validate if it's a parseable date in this format
                datetime.strptime(date_str, f"%d/%m/%y" if int(parts[0]) <=31 and int(parts[1]) <=12 else f"%m/%d/%y")
                return date_str
            except ValueError:
                pass # Continue to other parsing attempts
    try:
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%d/%m/%y', '%m/%d/%y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return f"{dt.day}/{dt.month}/{dt.year % 100:02d}" # DD/M/YY with 2-digit year
            except ValueError:
                continue
        dt = pd.to_datetime(date_str, errors='raise') # Fallback to pandas flexible parsing
        return f"{dt.day}/{dt.month}/{dt.year % 100:02d}"
    except Exception: # Broad exception if all parsing fails
        # logger.warning(f"Could not standardize date '{date_str}' after all attempts. Returning original.")
        return date_str

# --- RAG Knowledge Base (Updated for new codebase context) ---
RAG_KNOWLEDGE_BASE = {
    "general": "Este es el panel de Analytics Avanzados de Veterinaria Neuman. Proporciona análisis detallados sobre inventario, clientes y ventas. El usuario que interactúa es un administrador.",
    "date_handling": {
        "storage_format": "Las fechas en la tabla de base de datos 'ventas_vet_neuman' (accedida a través de la vista 'vista_ventas_con_tipo_por_desc') se almacenan como TEXTO y se espera que estén en formato DD/M/YY (ej: 13/3/24) después del procesamiento.",
        "standardization_process": "Los archivos Excel subidos a través del dashboard principal (`simple_dashboard.py` -> `/api/upload/excel`) o del dashboard de ventas (`dashboard_ventas.py` -> `cargar_archivo_excel`) pasan por una función `standardize_date_format` que intenta convertir varios formatos de fecha de entrada al formato DD/M/YY. Esta función está definida en `simple_dashboard.py`.",
        "standalone_script_info": "Existe un script independiente (`standardize_dates.py` ejecutado por `run_date_standardization.py`) diseñado para una corrección masiva de formatos de fecha directamente en la tabla 'ventas_vet_neuman' de la base de datos. Este script crea respaldos antes de modificar los datos.",
        "query_considerations": "Al consultar la columna 'date' en SQL, se debe usar `TO_DATE(\"date\", 'DD/MM/YY')` para convertirla a un tipo de fecha para comparaciones correctas, ya que se almacena como texto.",
        "impact": "La estandarización busca asegurar que los filtros de fecha y los análisis basados en fechas en todos los dashboards funcionen consistentemente."
    },
    "tabs": { # Descriptions from analytics.html
        "inventory": {
            "description": "La pestaña de Análisis de Inventario muestra KPIs como productos con bajo stock, productos de rotación lenta. Incluye tablas de 'Productos con Bajo Stock' (cantidad < 10), 'Productos de Rotación Lenta' (alto stock, bajas ventas), y gráficos de 'Análisis ABC' (top productos por ventas) y 'Performance por Marca' (ventas por marca).",
            "metrics": { "lowStockCount": "Número total de productos con cantidad en mano menor a 10.", "slowMovingCount": "Número de productos con alto stock pero pocas ventas recientes.", "topProductsCount": "Número de productos considerados 'top' según el análisis ABC por ventas.", "totalBrands": "Número total de marcas distintas con productos en inventario y/o ventas."} ,
            "charts": { "abcChart": "Gráfico de barras mostrando los top 15 productos por monto total de ventas. Ayuda a identificar los productos más importantes (Clase A).", "brandChart": "Gráfico de pastel mostrando la distribución de las ventas totales entre las diferentes marcas de productos."} ,
            "tables": { "lowStockTable": "Lista productos con cantidad en stock ('Stock') menor a 10. Muestra 'Código', 'Descripción', 'Stock', y 'Marca'.", "slowMovingTable": "Lista productos con alto stock y pocas unidades vendidas ('Vendido'). Muestra 'Código', 'Stock', 'Vendido', y 'Marca'."}
        },
        "customers": {
            "description": "La pestaña de Análisis de Clientes ofrece información sobre el comportamiento y segmentación de clientes. KPIs incluyen Clientes VIP, clientes de alta frecuencia, nuevos clientes y provincias activas. Presenta una tabla de 'Top 20 Clientes por Facturación', y gráficos de 'Frecuencia de Compra' y 'Distribución Geográfica de Ventas'. Los datos para esta pestaña se obtienen a través de la función `get_customer_analytics` que puede filtrar por un período de meses (1, 3, 6, 12, o 60 meses).",
             "metrics": { "vipCustomers": "Número de clientes identificados como VIP basado en alto volumen de compras y frecuencia.", "highFreqCustomers": "Número de clientes que compran con alta frecuencia (ej: 10+ facturas).", "newCustomers": "Número de clientes que han realizado su primera compra recientemente o tienen una sola compra.", "totalProvinces": "Número de provincias distintas donde se han registrado ventas."} ,
            "charts": { "frequencyChart": "Gráfico de pastel que segmenta a los clientes por su frecuencia de compra (ej: 'Alta Frecuencia (10+)', 'Compra Única').", "geoChart": "Gráfico de barras mostrando las ventas totales por cada provincia."} ,
            "tables": { "topCustomersTable": "Lista los top 20 clientes por monto total de ventas. Muestra 'Cliente' (ID), 'Nombre', 'Facturas' (conteo), 'Ventas Totales' ($), 'Última Compra' (fecha), y 'Segmento' (ej: VIP, Regular)."}
        },
        "sales": {
            "description": "La pestaña de Análisis de Ventas detalla la performance de ventas. KPIs incluyen el top vendedor, producto, ruta y categoría. Muestra gráficos de 'Performance por Vendedor', 'Performance por Ruta', una tabla de 'Top 30 Productos por Ventas', y un gráfico de 'Ventas por Categoría'. Los datos para esta pestaña se obtienen a través de la función `get_sales_analytics` que puede filtrar por un período de meses (1, 3, 6, 12, o 36 meses).",
            "metrics": { "topVendor": "El vendedor con el mayor monto total de ventas.", "topProduct": "El producto (por ID) con el mayor monto total de ventas.", "topRoute": "La ruta de ventas con el mayor monto total de ventas.", "topCategory": "La categoría de producto con el mayor monto total de ventas."} ,
            "charts": { "vendorChart": "Gráfico de barras mostrando las ventas totales ($) por cada vendedor.", "routeChart": "Gráfico de barras mostrando las ventas totales ($) por cada ruta de ventas.", "categoryChart": "Gráfico de pastel mostrando la distribución de las ventas totales entre las diferentes categorías de productos."} ,
            "tables": { "productPerformanceTable": "Lista los top 30 productos por monto total de ventas. Muestra 'Código', 'Descripción', 'Categoría', 'Cant. Vendida', 'Ventas Totales' ($), 'Clientes' (conteo de clientes únicos que compraron el producto), y 'Precio Prom.' (precio unitario promedio)."}
        }
    },
    "database_schema": {
        "vista_ventas_con_tipo_por_desc": "Vista principal para análisis de ventas. Columnas: invoice_cm_ (factura), date (fecha TEXT, formato DD/M/YY), customer_id, name (nombre cliente), qty (cantidad), item_id, item_description, unit_price, vendedor, provincia, ruta, tipo_cliente, tipo (tipo producto de matches_neuman).",
        "inventarioneuman": "Tabla de inventario. Columnas: Item (ID producto, PK), Description, Qty on Hand (cantidad), marca (VARCHAR(50)), Unit Price (NUMERIC, opcional). La 'marca' se deriva de 'Item' ('ACH' para CHINFIELD, 'EDO' para Laboratorios EDO) o es 'otra'. La ruta /admin/fix-brands puede corregir marcas.",
        "matches_neuman": "Tabla para mapear item_description a un 'tipo' de producto (ej. bovino, canino). Usada para poblar la columna 'tipo' en la vista de ventas."
    },
    "functions": { # Descriptions of functions in simple_dashboard.py
        "get_inventory_analytics": "Calcula y retorna datos para el análisis de inventario: productos con bajo stock (cantidad < 10), análisis ABC por ventas, productos de rotación lenta (alto stock, bajas ventas), y performance por marca. Usa la tabla 'inventarioneuman' y la vista 'vista_ventas_con_tipo_por_desc'.",
        "get_customer_analytics": "Calcula y retorna datos para análisis de clientes (top clientes, frecuencia, geo-distribución, segmentos). Acepta `date_months` (1,3,6,12,60) para filtrar por período; si el filtro de fecha SQL falla (debido al formato TEXT de la columna 'date'), usa datos recientes limitados como fallback. Usa 'vista_ventas_con_tipo_por_desc'.",
        "get_sales_analytics": "Calcula y retorna datos para análisis de ventas (performance por vendedor, producto, ruta, categoría). Acepta `date_months` (1,3,6,12,36) para filtrar; si el filtro de fecha SQL falla, usa datos recientes limitados como fallback. Usa 'vista_ventas_con_tipo_por_desc'.",
        "standardize_date_format": "Función interna que convierte varias cadenas de fecha al formato DD/M/YY. Usada durante el procesamiento de Excel y potencialmente por otras funciones.",
        "process_ventas_excel": "Procesa archivos Excel de ventas, mapea columnas flexiblemente, y estandariza fechas a DD/M/YY usando `standardize_date_format` antes de la carga a la base de datos.",
        "process_inventario_excel": "Procesa archivos Excel de inventario, mapea columnas y deriva la 'marca' de 'item_id'. Asegura que 'Item' (ID de producto) sea válido."
    },
    "admin_tools": {
        "/admin/fix-brands": "Ruta administrativa (accesible vía GET) que re-evalúa y actualiza la columna 'marca' en la tabla 'inventarioneuman' basándose en los prefijos 'ACH' o 'EDO' en la columna 'Item'. Útil para corregir asignaciones de marca."
    }
}

# --- Vertex AI RAG Configuration ---
RAG_PROJECT_ID_NUMERIC = "828930759180" # Your Project Number
RAG_PROJECT_ID_STRING = "veterinaria-neuman-456818" # Your Project ID string
RAG_LOCATION = "us-south1" # Region of your Index and Endpoint

# From your SDK example
RAG_API_ENDPOINT = "1091571738.us-south1-828930759180.vdb.vertexai.goog"
RAG_INDEX_ENDPOINT_RESOURCE_NAME = f"projects/{RAG_PROJECT_ID_NUMERIC}/locations/{RAG_LOCATION}/indexEndpoints/{RAG_INDEX_ENDPOINT_ID}"
RAG_DEPLOYED_INDEX_ID = "ariadna_1749172515035" # Crucial!

RAG_EMBEDDING_MODEL_NAME = "gemini-embedding-001" # Must match model used for ingestion

# Initialize AIPlatform client (if not done elsewhere globally for the app)
# This is for general aiplatform operations. MatchServiceClient has its own init.
try:
    if aiplatform and RAG_PROJECT_ID_STRING and RAG_LOCATION and not aiplatform.initializer.global_config.project:
        aiplatform.init(project=RAG_PROJECT_ID_STRING, location=RAG_LOCATION)
        logger.info(f"AIPlatform initialized for project {RAG_PROJECT_ID_STRING} in {RAG_LOCATION}")
    else:
        logger.info("AIPlatform not available or RAG environment variables not set, will use local text files for context")
except Exception as e:
    logger.warning(f"Failed to initialize AIPlatform: {e}. Will use local text files for context.")

# This stores the original text chunks.
TEXT_CHUNK_STORE = {}

def get_product_location_analytics(product_id=None, product_name=None, location=None):
    """Get analytics for specific product sales by location"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return f"Error de conexión: {message}"
        
        cursor = conn.cursor()
        
        # First, find the exact product name from the database
        if product_name:
            search_query = """
                SELECT DISTINCT "item_description"
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE LOWER("item_description") LIKE %s
                LIMIT 1
            """
            cursor.execute(search_query, [f"%{product_name.lower()}%"])
            result = cursor.fetchone()
            if result:
                product_name = result[0]  # Use the exact product name from the database
        
        # Calculate date range for last 3 months
        today = datetime.now()
        three_months_ago = today - timedelta(days=90)
        
        # Build the main query
        query = """
            SELECT 
                v."item_id",
                v."item_description",
                v."provincia",
                SUM(v."qty") as total_qty,
                COUNT(DISTINCT v."invoice_cm_") as total_invoices,
                COUNT(DISTINCT v."customer_id") as unique_customers,
                SUM(v."qty" * v."unit_price") as total_sales,
                MAX(v."date") as last_sale,
                MIN(v."date") as first_sale
            FROM public."vista_ventas_con_tipo_por_desc" v
            WHERE v."qty" IS NOT NULL 
            AND v."unit_price" IS NOT NULL
            AND TO_DATE(v."date", 'DD/MM/YY') >= TO_DATE(%s, 'DD/MM/YY')
            AND TO_DATE(v."date", 'DD/MM/YY') <= TO_DATE(%s, 'DD/MM/YY')
        """
        
        params = [three_months_ago.strftime("%d/%m/%y"), today.strftime("%d/%m/%y")]
        
        # Add product and location filters
        if product_name:
            query += " AND v.\"item_description\" = %s"
            params.append(product_name)
        elif product_id:
            query += " AND v.\"item_id\" = %s"
            params.append(product_id)
            
        if location:
            query += " AND LOWER(v.\"provincia\") = LOWER(%s)"
            params.append(location)
            
        query += """
            GROUP BY v."item_id", v."item_description", v."provincia"
            ORDER BY total_qty DESC
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if results:
            response = []
            for row in results:
                item_id, description, province, qty, invoices, customers, sales, last_sale, first_sale = row
                response.append({
                    'item_id': item_id,
                    'description': description,
                    'province': province,
                    'total_qty': float(qty) if qty else 0,
                    'total_invoices': int(invoices) if invoices else 0,
                    'unique_customers': int(customers) if customers else 0,
                    'total_sales': float(sales) if sales else 0,
                    'last_sale': last_sale,
                    'first_sale': first_sale
                })
            
            # Format the response as text
            text_response = f"Análisis de ventas para {description} en los últimos 3 meses:\n\n"
            for data in response:
                text_response += f"En {data['province']}:\n"
                text_response += f"- Cantidad vendida: {data['total_qty']} unidades\n"
                text_response += f"- Facturas generadas: {data['total_invoices']}\n"
                text_response += f"- Clientes únicos: {data['unique_customers']}\n"
                text_response += f"- Total ventas: ${data['total_sales']:,.2f}\n"
                text_response += f"- Primera venta: {data['first_sale']}\n"
                text_response += f"- Última venta: {data['last_sale']}\n\n"
            
            cursor.close()
            conn.close()
            return text_response
        else:
            # Try without date filter to see if the product exists at all
            query = query.replace(
                "AND TO_DATE(v.\"date\", 'DD/MM/YY') >= TO_DATE(%s, 'DD/MM/YY')\n            AND TO_DATE(v.\"date\", 'DD/MM/YY') <= TO_DATE(%s, 'DD/MM/YY')",
                ""
            )
            params = params[2:]  # Remove date parameters
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if results:
                response = []
                for row in results:
                    item_id, description, province, qty, invoices, customers, sales, last_sale, first_sale = row
                    response.append({
                        'item_id': item_id,
                        'description': description,
                        'province': province,
                        'total_qty': float(qty) if qty else 0,
                        'total_invoices': int(invoices) if invoices else 0,
                        'unique_customers': int(customers) if customers else 0,
                        'total_sales': float(sales) if sales else 0,
                        'last_sale': last_sale,
                        'first_sale': first_sale
                    })
                
                # Format the response as text
                text_response = f"No hay ventas en los últimos 3 meses, pero aquí está el histórico completo de ventas para {description}:\n\n"
                for data in response:
                    text_response += f"En {data['province']}:\n"
                    text_response += f"- Cantidad vendida total: {data['total_qty']} unidades\n"
                    text_response += f"- Facturas totales: {data['total_invoices']}\n"
                    text_response += f"- Clientes únicos: {data['unique_customers']}\n"
                    text_response += f"- Total ventas: ${data['total_sales']:,.2f}\n"
                    text_response += f"- Primera venta registrada: {data['first_sale']}\n"
                    text_response += f"- Última venta registrada: {data['last_sale']}\n\n"
                
                cursor.close()
                conn.close()
                return text_response
            else:
                # Try to find similar products
                search_query = """
                    SELECT DISTINCT "item_description"
                    FROM public."vista_ventas_con_tipo_por_desc"
                    WHERE LOWER("item_description") LIKE %s
                    LIMIT 5
                """
                cursor.execute(search_query, [f"%{product_name.lower() if product_name else ''}%"])
                similar_products = cursor.fetchall()
                
                if similar_products:
                    text_response = f"No se encontraron ventas del producto exacto, pero encontré productos similares:\n\n"
                    for product in similar_products:
                        text_response += f"- {product[0]}\n"
                    text_response += "\n¿Te gustaría ver las ventas de alguno de estos productos?"
                    
                    cursor.close()
                    conn.close()
                    return text_response
                else:
                    cursor.close()
                    conn.close()
                    return f"No se encontraron ventas ni productos similares{' en ' + location if location else ''}."
        
    except Exception as e:
        logger.error(f"Error in product location analytics: {str(e)}")
        return f"Error al analizar datos del producto: {str(e)}"

def get_rag_context(user_question, active_tab=None):
    """
    Retrieves relevant context from Vertex AI Vector Search for the user question.
    If Vertex AI is not available, falls back to local text files.
    """
    if not VERTEX_AI_AVAILABLE or not aiplatform or not PreviewTextEmbeddingModel:
        logger.warning("RAG context: Vertex AI or required modules not available. Using local text files.")
        return get_local_ariadna_context(user_question, active_tab)

    try:
        logger.info(f"RAG: Generating embedding for question: '{user_question[:50]}...'")
        
        # 1. Generate embedding for the user's question
        embedding_model = PreviewTextEmbeddingModel.from_pretrained(RAG_EMBEDDING_MODEL_NAME)
        question_instance = PreviewTextEmbeddingInput(text=user_question, task_type="RETRIEVAL_QUERY")
        embedding_response = embedding_model.get_embeddings([question_instance])

        if not embedding_response or not embedding_response[0].values:
            logger.error("RAG: Failed to generate embedding for the user question.")
            return get_local_ariadna_context(user_question, active_tab)

        query_embedding = embedding_response[0].values

        # 2. Find neighboring datapoints in the index using environment variable
        my_index = aiplatform.MatchingEngineIndex(index_name=RAG_INDEX_ID)

        logger.info(f"RAG: Querying index {RAG_INDEX_ID} for nearest neighbors.")

        # Find neighbors
        neighbors = my_index.find_neighbors(
            queries=[query_embedding],
            num_neighbors=3 # Retrieve the top 3 most relevant documents
        )
        
        # 3. Process the response to extract context
        retrieved_texts = []
        if neighbors and neighbors[0]:
            for neighbor in neighbors[0]:
                try:
                    # The crowding_attribute in our ingestion script holds a JSON string
                    crowding_data = json.loads(neighbor.datapoint.crowding_tag.crowding_attribute)
                    if 'text' in crowding_data:
                        retrieved_texts.append(crowding_data['text'])
                        logger.info(f"RAG: Retrieved context for ID {neighbor.id} with distance {neighbor.distance:.4f}")
                except (json.JSONDecodeError, AttributeError, KeyError) as e:
                    logger.warning(f"RAG: Could not parse context from neighbor {neighbor.id}: {e}")
        
        if not retrieved_texts:
            logger.info("RAG: No relevant documents found in Vector Search. Falling back to local files.")
            return get_local_ariadna_context(user_question, active_tab)

        # 4. Construct the final context string
        final_rag_context = "\n\n--- Información Relevante Encontrada ---\n"
        final_rag_context += "\n\n---\n".join(retrieved_texts)
        final_rag_context += "\n--- Fin de la Información Relevante ---\n"
        
        logger.info(f"RAG: Constructed context (first 200 chars): {final_rag_context[:200]}...")
        return final_rag_context
        
    except Exception as e:
        logger.error(f"RAG: An unhandled error occurred in get_rag_context: {str(e)}", exc_info=True)
        logger.info("RAG: Falling back to local text files due to error.")
        return get_local_ariadna_context(user_question, active_tab)

def get_local_ariadna_context(user_question, active_tab=None):
    """
    Fallback function to read context from local text files when Vertex AI is not available.
    """
    try:
        import os
        context_parts = []
        
        # Read main context file
        context_file = "pdfproductos/Ariadna/context.txt"
        if os.path.exists(context_file):
            with open(context_file, 'r', encoding='utf-8') as f:
                main_context = f.read()
                context_parts.append("--- CONTEXTO GENERAL ARIADNA ---\n" + main_context)
                logger.info(f"Loaded main context from {context_file} ({len(main_context)} chars)")
        
        # Read routes context file
        routes_file = "pdfproductos/Ariadna/rutas_context.txt"
        if os.path.exists(routes_file):
            with open(routes_file, 'r', encoding='utf-8') as f:
                routes_context = f.read()
                context_parts.append("--- CONTEXTO DE RUTAS Y CLIENTES ---\n" + routes_context)
                logger.info(f"Loaded routes context from {routes_file} ({len(routes_context)} chars)")
        
        if context_parts:
            full_context = "\n\n".join(context_parts)
            logger.info(f"Local RAG context loaded successfully ({len(full_context)} total chars)")
            return full_context
        else:
            logger.warning("No local context files found")
            return "CONTEXTO LOCAL: No se encontraron archivos de contexto local."
            
    except Exception as e:
        logger.error(f"Error loading local context files: {str(e)}")
        return "CONTEXTO LOCAL: Error al cargar archivos de contexto local."

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Ensure admin user exists on first app usage (lazy initialization)
    try:
        ensure_admin_user()
    except Exception as e:
        logger.error(f"Error during lazy admin user initialization: {e}")
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Por favor ingrese usuario y contraseña', 'error')
            return render_template('auth/login.html') # Assumes auth/login.html exists
        user = get_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            update_last_login(user.id)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin(): # type: ignore
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    users = get_all_users()
    return render_template('admin/admin_panel.html', users=users) # Assumes admin/admin_panel.html exists

@app.route('/admin/create-user', methods=['POST'])
@login_required
def admin_create_user():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    data = request.form
    success, message = create_user(data.get('username'), data.get('email'), data.get('password'), data.get('role', 'user'))
    return jsonify({'success': success, 'message' if success else 'error': message}), 200 if success else 400

@app.route('/admin/update-user-status', methods=['POST'])
@login_required  
def admin_update_user_status():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    success, message = update_user_status(request.form.get('user_id'), request.form.get('is_active') == 'true')
    return jsonify({'success': success, 'message' if success else 'error': message}), 200 if success else 400

@app.route('/admin/update-user-role', methods=['POST'])
@login_required
def admin_update_user_role():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    success, message = update_user_role(request.form.get('user_id'), request.form.get('role'))
    return jsonify({'success': success, 'message' if success else 'error': message}), 200 if success else 400

@app.route('/analytics')
@login_required
def analytics():
    if not current_user.is_admin(): # type: ignore
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('analytics/analytics.html', user=current_user) # Assumes analytics/analytics.html exists

@app.route('/analytics_minimal')
@login_required
def analytics_minimal():
    if not current_user.is_admin(): # type: ignore
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('analytics_minimal.html', user=current_user)

@app.route('/ariadna')
@login_required
def ariadna_chat():
    """Dedicated Ariadna chatbot interface"""
    return render_template('ariadna_chat.html', user=current_user)

@app.route('/inventario')
@login_required
def inventario():
    return render_template('inventario/inventario.html', user=current_user) # Assumes inventario/inventario.html exists

@app.route('/api/analytics/inventory')
@login_required
def api_analytics_inventory():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    try:
        analytics_data = get_inventory_analytics()
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"Error in inventory analytics API: {str(e)}", exc_info=True)
        return jsonify({"error": "Error procesando análisis de inventario."}), 500

@app.route('/api/analytics/customers')
@login_required
def api_analytics_customers():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    try:
        date_months = int(request.args.get('date_months', 3))
        valid_periods = [1, 3, 6, 12, 60] # 60 for 5 years
        if date_months not in valid_periods: date_months = 3
        analytics_data = get_customer_analytics(date_months) # Pass date_months
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"Error in customer analytics API: {str(e)}", exc_info=True)
        return jsonify({"error": "Error procesando análisis de clientes."}), 500

@app.route('/api/analytics/sales')
@login_required
def api_analytics_sales():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    try:
        date_months = int(request.args.get('date_months', 3))
        valid_periods = [1, 3, 6, 12, 36] # 36 for 3 years
        if date_months not in valid_periods: date_months = 3
        analytics_data = get_sales_analytics(date_months) # Pass date_months
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"Error in sales analytics API: {str(e)}", exc_info=True)
        return jsonify({"error": "Error procesando análisis de ventas."}), 500

@app.route('/api/inventario')
@login_required
def api_inventario():
    try:
        conn, message = get_db_connection()
        if not conn: return jsonify({"error": f"Database connection failed: {message}"})
        cursor = conn.cursor()
        search = request.args.get('search', '').strip()
        marca_filter = request.args.get('marca', 'all')
        sort_by = request.args.get('sort', 'description')
        sort_dir = request.args.get('dir', 'asc')
        limit = int(request.args.get('limit', 100))
        where_conditions = []
        params = []
        if search:
            where_conditions.append('("Item" ILIKE %s OR "Description" ILIKE %s)')
            params.extend([f'%{search}%', f'%{search}%'])
        if marca_filter and marca_filter != 'all':
            where_conditions.append('marca = %s')
            params.append(marca_filter)
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        valid_sorts = {'description': '"Description"', 'stock': '"Qty on Hand"', 'item_id': '"Item"', 'marca': 'marca'}
        sort_column = valid_sorts.get(sort_by, '"Description"')
        sort_direction = 'DESC' if sort_dir == 'desc' else 'ASC'
        query = f'''SELECT "Item" as item_id, "Description" as description, "Qty on Hand" as stock, marca,
                        CASE WHEN "Qty on Hand" <= 0 THEN 'sin-stock' WHEN "Qty on Hand" <= 5 THEN 'bajo-stock'
                             WHEN "Qty on Hand" <= 20 THEN 'stock-medio' ELSE 'stock-alto' END as stock_status
                    FROM public."inventarioneuman" {where_clause} ORDER BY {sort_column} {sort_direction} LIMIT %s'''
        params.append(limit)
        cursor.execute(query, tuple(params))
        inventory_data = [{'item_id': r[0], 'description': r[1], 'stock': float(r[2] or 0), 'marca': r[3] or 'otra', 'stock_status': r[4]} for r in cursor.fetchall()]
        summary_query = f'''SELECT COUNT(*) as total_products,
                SUM(CASE WHEN "Qty on Hand" <= 0 THEN 1 ELSE 0 END) as sin_stock,
                SUM(CASE WHEN "Qty on Hand" > 0 AND "Qty on Hand" <= 5 THEN 1 ELSE 0 END) as bajo_stock,
                SUM(CASE WHEN "Qty on Hand" > 5 AND "Qty on Hand" <= 20 THEN 1 ELSE 0 END) as stock_medio,
                SUM(CASE WHEN "Qty on Hand" > 20 THEN 1 ELSE 0 END) as stock_alto,
                                COUNT(DISTINCT marca) as total_marcas, SUM("Qty on Hand") as total_stock
                            FROM public."inventarioneuman" {where_clause}'''
        summary_params = params[:-1] if params else []
        cursor.execute(summary_query, tuple(summary_params))
        s = cursor.fetchone()
        summary_data = {'total_products': int(s[0] or 0), 'sin_stock': int(s[1] or 0), 'bajo_stock': int(s[2] or 0), 
                        'stock_medio': int(s[3] or 0), 'stock_alto': int(s[4] or 0), 'total_marcas': int(s[5] or 0), 
                        'total_stock': float(s[6] or 0)}
        cursor.execute('SELECT DISTINCT marca FROM public."inventarioneuman" WHERE marca IS NOT NULL ORDER BY marca')
        brands = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'inventory': inventory_data, 'summary': summary_data, 'brands': brands, 'total_records': len(inventory_data)})
    except Exception as e:
        logger.error(f"Error in inventory API: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/api/data')
@login_required
def api_data():
    try:
        filters = { 'start_date': request.args.get('start_date'), 'end_date': request.args.get('end_date'),
                    'provincia': request.args.getlist('provincia'), 'ruta': request.args.getlist('ruta'),
                    'vendedor': request.args.getlist('vendedor'), 'tipo': request.args.getlist('tipo'),
                    'columns': request.args.getlist('columns')}
        filter_options, _ = load_filter_options()
        kpis, _ = calculate_filtered_kpis(filters)
        data, _ = load_filtered_data(filters)
        view_data = []
        if filters.get('columns') and data:
            selected_columns = [col for col in filters['columns'] if data and any(col in record for record in data)]
            if selected_columns:
                view_data = [{col: record.get(col, '') for col in selected_columns} for record in data]
        return jsonify({ "total_ventas": kpis.get("total_ventas",0), "cantidad_facturas": kpis.get("cantidad_facturas",0),
                         "cantidad_clientes": kpis.get("cantidad_clientes",0), "ticket_promedio": kpis.get("ticket_promedio",0),
                         "filter_options": filter_options, "data": data, "view_data": view_data,
                         "message": f"Datos filtrados: {kpis.get('total_records',0)} registros"})
    except Exception as e:
        logger.error(f"Error in api_data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/db-status')
@login_required
def api_db_status():
    try:
        conn, message = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            return jsonify({"status": True, "message": f"Conectado. PostgreSQL version: {version[0][:50]}..."}) #type: ignore
        else:
            return jsonify({"status": False, "message": message})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})

# --- AI Assistant Endpoint (Integrated) ---
@app.route('/api/ai/analytics_assistant', methods=['POST'])
@login_required
def api_ai_analytics_assistant():
    import uuid
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[REQUEST-{request_id}] AI Assistant endpoint called. VERTEX_AI_AVAILABLE: {VERTEX_AI_AVAILABLE}, gemini_model: {gemini_model is not None}")
    
    if not VERTEX_AI_AVAILABLE or not gemini_model:
        logger.warning("Vertex AI / Gemini model not available. AI Assistant call failed.")
        return jsonify({"error": "Servicio de IA no disponible en este momento."}), 503
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        active_tab = data.get('active_tab')
        if not user_question:
            return jsonify({"error": "La pregunta no puede estar vacía."}), 400
        
        logger.info(f"[REQUEST-{request_id}] AI Assistant question: '{user_question}' for tab: '{active_tab}'")
        
        # Get RAG context (dynamic from Vector Search)
        rag_dynamic_context = "" # Initialize
        try:
            # Note: active_tab is passed but might not be used by the new RAG function
            rag_dynamic_context = get_rag_context(user_question, active_tab) 
            logger.info(f"RAG dynamic context generated, length: {len(rag_dynamic_context)}")
        except Exception as rag_error:
            logger.error(f"Error generating RAG dynamic context: {str(rag_error)}", exc_info=True)
            # Decide on a fallback. Maybe an empty string or a generic error message.
            rag_dynamic_context = "Error al obtener información de la base de conocimiento RAG."
        
        # Get real-time data based on question type with specialized functions
        live_data_context = ""
        try:
            question_lower = user_question.lower()
            
            # Import specialized analytics functions
            from specific_analytics import (
                query_1_cantidad_producto_provincia,
                query_2_cantidad_producto_ruta,
                query_3_top_clientes_producto,
                query_4_comparacion_compras_cliente,
                query_5_ranking_clientes_periodo,
                query_6_productos_inventario_ventas
            )
            
            # Check for specific analytical questions and call specialized functions
            if any(phrase in question_lower for phrase in ['cantidad', 'vendo', 'vendí', 'veraguas', 'yodacalcio', 'provincia']):
                logger.info(f"Detected specialized question type 1: {user_question}")
                # Pregunta 1: Ventas por producto y provincia
                # Extract product and province from question
                product_match = None
                province_match = None
                
                # Look for specific products mentioned
                if 'yodacalcio' in question_lower:
                    product_match = 'YODACALCIO'
                    logger.info(f"Product detected: {product_match}")
                
                # Look for provinces mentioned
                province_patterns = {
                    'veraguas': 'Veraguas',
                    'chiriquí': 'Chiriquí', 
                    'chiriqui': 'Chiriquí',
                    'coclé': 'Coclé',
                    'cocle': 'Coclé', 
                    'panamá': 'Panamá',
                    'panama': 'Panamá',
                    'herrera': 'Herrera',
                    'los santos': 'Los Santos'
                }
                
                for pattern, proper_name in province_patterns.items():
                    if pattern in question_lower:
                        province_match = proper_name
                        logger.info(f"Province detected: {province_match}")
                        break
                
                if product_match and province_match:
                    # Extract date filtering from question
                    from specific_analytics import extract_date_from_question
                    date_filter = extract_date_from_question(user_question)
                    fecha_inicio = None
                    fecha_fin = None
                    
                    if date_filter:
                        if isinstance(date_filter, tuple):
                            fecha_inicio, fecha_fin = date_filter
                        elif isinstance(date_filter, dict):
                            # For comparative queries, use current period
                            fecha_inicio, fecha_fin = date_filter.get('current', (None, None))
                    
                    logger.info(f"Specialized query: Product sales by province - {product_match} in {province_match}")
                    if fecha_inicio and fecha_fin:
                        logger.info(f"Date filter applied: {fecha_inicio} to {fecha_fin}")
                    
                    result = query_1_cantidad_producto_provincia(product_match, province_match, fecha_inicio, fecha_fin)
                    logger.info(f"[DEBUG] Query result: success={result.get('success') if result else 'None'}, data_length={len(result.get('data', [])) if result and result.get('data') else 0}, result={result}")
                    
                    if result and result.get('success') and result.get('data'):
                        logger.info(f"[REQUEST-{request_id}] Building specialized response with {len(result['data'])} items")
                        
                        # Use summary data if available, otherwise calculate from individual records
                        if result.get('summary'):
                            total_cantidad = result['summary']['total_cantidad']
                            total_ventas = result['summary']['total_ventas']
                            productos_diferentes = result['summary']['productos_encontrados']
                        else:
                            total_cantidad = sum(item['total_cantidad'] for item in result['data'])
                            total_ventas = sum(item['numero_ventas'] for item in result['data'])
                            productos_diferentes = len(result['data'])
                        
                        logger.info(f"[REQUEST-{request_id}] Totals calculated: cantidad={total_cantidad}, ventas={total_ventas}")
                        
                        # Return specialized response immediately - ENHANCED WITH DATE INFO
                        try:
                            logger.info(f"[REQUEST-{request_id}] Building response with product: {product_match}, province: {province_match}")
                            logger.info(f"[REQUEST-{request_id}] Data available: total_cantidad={total_cantidad}, total_ventas={total_ventas}")
                            
                            specialized_response = f"CONSULTA ESPECIALIZADA - VENTAS POR PROVINCIA\n\n"
                            specialized_response += f"Producto: {product_match}\n"
                            specialized_response += f"Provincia: {province_match}\n"
                            
                            # Add date filter information
                            if fecha_inicio and fecha_fin:
                                specialized_response += f"Período: {fecha_inicio} a {fecha_fin}\n"
                                specialized_response += f"Filtro temporal: Aplicado\n\n"
                            else:
                                specialized_response += f"Período: Histórico completo\n"
                                specialized_response += f"Filtro temporal: No aplicado\n\n"
                            
                            specialized_response += f"RESUMEN EJECUTIVO:\n"
                            specialized_response += f"- Cantidad total vendida: {total_cantidad} unidades\n"
                            specialized_response += f"- Numero total de ventas: {total_ventas} transacciones\n"
                            specialized_response += f"- Productos encontrados: {productos_diferentes} variantes\n\n"
                            
                            logger.info(f"[REQUEST-{request_id}] Basic response built, length: {len(specialized_response)}")
                            
                        except Exception as e:
                            logger.error(f"[REQUEST-{request_id}] Error building specialized response: {str(e)}")
                            specialized_response = f"Error construyendo respuesta: {str(e)}"

                        logger.info(f"[REQUEST-{request_id}] Specialized response length: {len(specialized_response) if specialized_response else 'None'}")
                        logger.info(f"[REQUEST-{request_id}] Specialized response preview: {specialized_response[:100] if specialized_response else 'None'}")
                        logger.info(f"[REQUEST-{request_id}] Returning specialized analytics result immediately")
                        logger.info(f"[REQUEST-{request_id}] ABOUT TO RETURN - THIS SHOULD BE THE LAST LOG FOR THIS REQUEST")
                        return jsonify({"response": specialized_response})
                        logger.error(f"[REQUEST-{request_id}] ERROR - CODE CONTINUED AFTER RETURN!")
                    else:
                        error_response = f"Error: No se encontraron datos de ventas para {product_match} en {province_match}. {result.get('error', '')}"
                        return jsonify({"response": error_response})
            
            elif any(phrase in question_lower for phrase in ['ruta donde opera', 'vendo en la ruta', 'vendí en la ruta', 'ruta']):
                # Pregunta 2: Ventas por producto y ruta
                product_match = None
                route_match = None
                
                if 'yodacalcio' in question_lower:
                    product_match = 'YODACALCIO'
                
                # Extract route number or name
                import re
                route_search = re.search(r'ruta\s*(\d+|[a-zA-Z]+)', question_lower)
                if route_search:
                    route_match = route_search.group(1)
                
                if product_match and route_match:
                    logger.info(f"Specialized query: Product sales by route - {product_match} in route {route_match}")
                    result = query_2_cantidad_producto_ruta(product_match, route_match)
                    
                    if result.get('success') and result.get('data'):
                        total_cantidad = sum(item['total_cantidad'] for item in result['data'])
                        total_ventas = sum(item['numero_ventas'] for item in result['data'])
                        
                        live_data_context += f"""
                        
DATOS ESPECÍFICOS - VENTAS POR RUTA:
Producto: {product_match}
Ruta: {route_match}

RESUMEN:
• Cantidad total vendida: {total_cantidad:,.0f} unidades
• Número total de ventas: {total_ventas:,} transacciones
• Productos encontrados: {len(result['data'])} variantes

PRINCIPALES PRODUCTOS:
"""
                        for item in result['data'][:3]:
                            live_data_context += f"• {item['producto']} (Provincia: {item['provincia']}): {item['total_cantidad']:,.0f} unidades\n"
                    else:
                        live_data_context += f"\nError: {result.get('error', 'No se encontraron datos para esa ruta')}"
            
            elif any(phrase in question_lower for phrase in ['negocios del top', 'ranking', 'nos compra', 'nos compran', 'top', 'clientes']):
                # Pregunta 3: Top clientes por producto
                product_match = None
                top_n = 10
                
                if 'yodacalcio' in question_lower:
                    product_match = 'YODACALCIO'
                
                # Extract top number
                import re
                top_match = re.search(r'top\s*(\d+)', question_lower)
                if top_match:
                    top_n = int(top_match.group(1))
                
                if product_match:
                    logger.info(f"Specialized query: Top clients by product - {product_match}")
                    result = query_3_top_clientes_producto(product_match, top_n)
                    
                    if result.get('success') and result.get('data'):
                        total_clientes = len(result['data'])
                        total_cantidad = sum(item['total_cantidad'] for item in result['data'])
                        total_valor = sum(item['total_valor'] for item in result['data'])
                        
                        live_data_context += f"""
                        
DATOS ESPECÍFICOS - TOP CLIENTES:
Producto: {product_match}
Total clientes encontrados: {total_clientes}
Cantidad total vendida: {total_cantidad:,.0f} unidades
Valor total de ventas: ${total_valor:,.2f}

RANKING TOP {top_n}:
"""
                        for client in result['data'][:top_n]:
                            live_data_context += f"{client['ranking']}. {client['cliente']} ({client['provincia']}, Ruta {client['ruta']})\n"
                            live_data_context += f"   • Cantidad: {client['total_cantidad']:,.0f} unidades\n"
                            live_data_context += f"   • Valor: ${client['total_valor']:,.2f}\n"
                            live_data_context += f"   • Facturas: {client['numero_facturas']} | Tipo: {client['tipo_cliente'] or 'N/A'}\n\n"
                    else:
                        live_data_context += f"\nError: {result.get('error', 'No se encontraron clientes')}"
            
            elif any(phrase in question_lower for phrase in ['comparativo de compras', 'compras del cliente', 'coopugan', 'bramador']):
                # Pregunta 4: Comparativo de compras por cliente
                client_match = None
                
                if 'coopugan' in question_lower:
                    client_match = 'COOPUGAN'
                elif 'casa el bramador' in question_lower or 'bramador' in question_lower:
                    client_match = 'BRAMADOR'
                
                # Extract date range from question
                import re
                from datetime import datetime
                
                # Default date range (March 2025 to May 2025)
                start_date = "2025-03-01"
                end_date = "2025-05-31"
                
                # Try to extract dates from question
                if 'marzo' in question_lower and 'mayo' in question_lower:
                    year_match = re.search(r'(\d{4})', user_question)
                    if year_match:
                        year = year_match.group(1)
                        start_date = f"{year}-03-01"
                        end_date = f"{year}-05-31"
                
                if client_match:
                    logger.info(f"Specialized query: Client purchase comparison - {client_match}")
                    result = query_4_comparacion_compras_cliente(client_match, start_date, end_date)
                    
                    if result.get('success') and result.get('data'):
                        resumen = result['resumen']
                        live_data_context += f"""
                        
DATOS ESPECÍFICOS - COMPARATIVO CLIENTE:
Cliente: {client_match}
Período: {start_date} a {end_date}

RESUMEN GENERAL:
• Cantidad total comprada: {resumen['total_cantidad_comprada']:,.0f} unidades
• Valor total de compras: ${resumen['total_valor_compras']:,.2f}
• Productos diferentes: {resumen['productos_diferentes']}
• Número de transacciones: {resumen['numero_transacciones']}

ÚLTIMAS COMPRAS:
"""
                        for item in result['data'][:5]:
                            live_data_context += f"• {item['fecha']} - {item['producto']}\n"
                            live_data_context += f"  Cantidad: {item['cantidad']:,.1f} | Total: ${item['total_item']:,.2f} | Vendedor: {item['vendedor']}\n\n"
                    else:
                        live_data_context += f"\nError: {result.get('error', 'No se encontraron compras para este cliente')}"
            
            elif any(phrase in question_lower for phrase in ['ranking de clientes', 'top.*clientes.*compras', 'ranking']):
                # Pregunta 5: Ranking de clientes por período
                top_n = 20
                
                # Extract top number
                import re
                top_match = re.search(r'top\s*(\d+)', question_lower)
                if top_match:
                    top_n = int(top_match.group(1))
                
                # Extract date range from question (same logic as pregunta 4)
                start_date = "2025-03-01"
                end_date = "2025-05-31"
                
                if 'marzo' in question_lower and 'mayo' in question_lower:
                    year_match = re.search(r'(\d{4})', user_question)
                    if year_match:
                        year = year_match.group(1)
                        start_date = f"{year}-03-01"
                        end_date = f"{year}-05-31"
                
                logger.info(f"Specialized query: Clients ranking by period")
                result = query_5_ranking_clientes_periodo(start_date, end_date, top_n)
                
                if result.get('success'):
                        live_data_context += f"""
                        
DATOS ESPECÍFICOS - RANKING CLIENTES:
Período: {result['period']}
Total clientes analizados: {result['total_clients_found']}

TOP {top_n} CLIENTES POR COMPRAS:
"""
                        for client in result['top_clients']:
                            live_data_context += f"{client['ranking']}. {client['client_name']} ({client['province']})\n"
                            live_data_context += f"   • Valor total: ${client['total_value']:,.2f}\n"
                            live_data_context += f"   • Facturas: {client['total_invoices']}\n"
                            live_data_context += f"   • Productos únicos: {client['unique_products']}\n\n"
                else:
                    live_data_context += f"\nError: {result.get('message', 'Error en ranking de clientes')}"
            
            elif any(phrase in question_lower for phrase in ['ritmo de ventas', 'ventas lento', 'ventas rápido', 'inventario vendido']):
                # Pregunta 6: Análisis de ritmo de ventas vs inventario
                reference_product = None
                
                if 'yodacalcio' in question_lower:
                    reference_product = 'YODACALCIO B-12-D'
                
                if start_date and end_date:
                    logger.info(f"Specialized query: Sales pace analysis")
                    result = query_6_productos_inventario_ventas()
                    
                    if result.get('success'):
                        summary = result['resumen']
                        live_data_context += f"""
                        
DATOS ESPECÍFICOS - ANÁLISIS DE RITMO DE VENTAS:

RESUMEN:
• Total productos analizados: {summary['total_productos_analizados']}
• Productos ritmo rápido: {summary['productos_ritmo_rapido']}
• Productos ritmo lento: {summary['productos_ritmo_lento']}
• Productos inventario bajo: {summary['productos_inventario_bajo']}
• Productos inventario alto: {summary['productos_inventario_alto']}

TOP PRODUCTOS RITMO RÁPIDO:
"""
                        fast_products = [p for p in result['data'] if p['clasificacion_ritmo'] == 'RÁPIDO']
                        for product in fast_products[:5]:
                            live_data_context += f"• {product['descripcion']}: {product['ritmo_venta_diario']:.1f} unidades/día ({product['dias_inventario_restante']:.0f} días inventario)\n"
                        
                        live_data_context += "\nPRODUCTOS RITMO LENTO:\n"
                        slow_products = [p for p in result['data'] if p['clasificacion_ritmo'] == 'LENTO']
                        for product in slow_products[:5]:
                            live_data_context += f"• {product['descripcion']}: {product['ritmo_venta_diario']:.1f} unidades/día ({product['dias_inventario_restante']:.0f} días inventario)\n"
                        
                        # Look for reference product if specified
                        if reference_product:
                            ref_products = [p for p in result['data'] if reference_product.upper() in p['descripcion'].upper()]
                            if ref_products:
                                ref = ref_products[0]
                                live_data_context += f"""
                            
PRODUCTO DE REFERENCIA ({reference_product}):
• Ritmo: {ref['clasificacion_ritmo']}
• Velocidad: {ref['ritmo_venta_diario']:.1f} unidades/día
• Días de inventario: {ref['dias_inventario_restante']:.0f} días
• Stock actual: {ref['cantidad_inventario']:,.0f} unidades
• Nivel inventario: {ref['nivel_inventario']}
"""
                    else:
                        live_data_context += f"\nError: {result.get('error', 'Error en análisis de ritmo')}"
            
            # --- Enhanced Date Months Parsing ---
            def get_months_from_question(q_lower):
                import re
                # Check for "X meses" or "últimos X meses"
                match = re.search(r'(?:ultimos|últimos|los ultimos|los últimos|pasados|past)\s+(\w+)\s+meses', q_lower)
                if not match: # Try without "ultimos"
                    match = re.search(r'(\w+)\s+meses', q_lower)

                if match:
                    num_word = match.group(1)
                    if num_word.isdigit():
                        return int(num_word)
                    else:
                        word_to_num = {
                            'un': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 
                            'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 
                            'nueve': 9, 'diez': 10, 'once': 11, 'doce': 12
                        }
                        return word_to_num.get(num_word.lower())

                # Check for "este mes", "ultimo mes", "mes actual" (singular)
                if any(phrase in q_lower for phrase in ['este mes', 'mes actual', 'ultimo mes', 'último mes', 'last month', 'current month']):
                    return 1
                return None # Return None if no specific duration found

            parsed_months = get_months_from_question(question_lower)
            # --- End Enhanced Date Months Parsing ---

            # Check for brand-specific queries
            brand_specific_data = ""
            if any(brand in question_lower for brand in ['edo', 'chinfield', 'laboratorios edo', 'marca edo', 'marca chinfield']):
                logger.info("Question requires brand-specific analysis")
                brand_specific_data = get_brand_specific_analytics(user_question)
                if brand_specific_data:
                    live_data_context += f"\n\nAnálisis específico por marca:\n{brand_specific_data}"
            
            # Check for product name queries (when user asks about specific products)
            if any(keyword in question_lower for keyword in ['mektina', 'producto', 'medicamento', 'tratamiento']) and not any(keyword in question_lower for keyword in ['productos más vendidos', 'top productos']):
                logger.info("Question requires product name matching")
                product_specific_data = get_product_name_analytics(user_question)
                if product_specific_data:
                    live_data_context += f"\n\nAnálisis específico de productos:\n{product_specific_data}"
            
            # Additional check for specific product information requests
            if any(phrase in question_lower for phrase in ['información sobre', 'datos sobre', 'detalles sobre', 'ingresos generados', 'ventas de']) and any(brand in question_lower for brand in ['edo', 'chinfield']):
                logger.info("Question requires specific product information analysis")
                product_specific_data = get_product_name_analytics(user_question)
                if product_specific_data:
                    live_data_context += f"\n\nInformación específica del producto:\n{product_specific_data}"
            
            # Check if the question needs real-time sales data
            if any(keyword in question_lower for keyword in ['productos', 'vendidos', 'ventas', 'top', 'mejores', 'más vendidos', 'bestseller']):
                logger.info("Question requires sales analytics data")
                # Use parsed_months if available, else default to 3
                months_for_sales_data = parsed_months if parsed_months is not None else 3
                sales_data = get_sales_analytics(date_months=months_for_sales_data)
                if sales_data.get('product_analysis'):
                    live_data_context += f"\n\nDatos actuales de productos más vendidos (últimos {months_for_sales_data} {'mes' if months_for_sales_data == 1 else 'meses'}):\n{sales_data['product_analysis']}"
                if sales_data.get('category_performance'):
                    live_data_context += f"\n\nRendimiento por categorías (últimos {months_for_sales_data} {'mes' if months_for_sales_data == 1 else 'meses'}):\n{sales_data['category_performance']}"
            
            # Check if the question needs real-time customer data
            if any(keyword in question_lower for keyword in ['clientes', 'customers', 'compradores', 'frecuencia']) or any(location in question_lower for location in ['veraguas', 'chiriquí', 'chiriqui', 'coclé', 'cocle', 'herrera', 'los santos', 'panamá', 'panama']): # Added location keywords
                logger.info("Question requires customer analytics data")
                # Use parsed_months if available, else default to 3. Specific "este mes" etc. handled by get_months_from_question
                months_for_customer_data = parsed_months if parsed_months is not None else 3
                
                # Extract location from question if present
                location = None
                for loc in ['veraguas', 'chiriquí', 'chiriqui', 'coclé', 'cocle', 'herrera', 'los santos', 'panamá', 'panama']:
                    if loc in question_lower:
                        location = loc.replace('chiriqui', 'chiriquí').replace('cocle', 'coclé').replace('panama', 'panamá')
                        break
                
                customer_data = get_customer_analytics(date_months=months_for_customer_data)
                if customer_data.get('top_customers'):
                    # Filter customers by location if specified
                    if location:
                        filtered_customers = [
                            customer for customer in customer_data['top_customers']
                            if (customer.get('province') or '').lower() == location
                        ]
                        if filtered_customers:
                            live_data_context += f"\n\nTop clientes en {location.title()} (últimos {months_for_customer_data} {'mes' if months_for_customer_data == 1 else 'meses'}):\n"
                            for customer in filtered_customers:
                                live_data_context += f"- {customer['name']}: ${customer['total_sales']:,.2f} en {customer['invoice_count']} facturas\n"
                        else:
                            live_data_context += f"\n\nNo se encontraron clientes en {location.title()} para el período especificado.\n"
                    else:
                        live_data_context += f"\n\nTop clientes por compras (últimos {months_for_customer_data} {'mes' if months_for_customer_data == 1 else 'meses'}):\n{customer_data['top_customers']}"
                
                if customer_data.get('customer_analysis'):
                    live_data_context += f"\n\nAnálisis de clientes:\n{customer_data['customer_analysis']}"
                if customer_data.get('geographic_distribution'):
                    live_data_context += f"\n\nDistribución geográfica:\n{customer_data['geographic_distribution']}"
            
            # Check if the question needs vendor/sales performance data
            if any(keyword in question_lower for keyword in ['vendedor', 'vendedores', 'seller', 'sellers', 'performance', 'rutas', 'routes']):
                logger.info("Question requires vendor/sales performance data")
                # Use parsed_months if available, else default to 3
                months_for_vendor_data = parsed_months if parsed_months is not None else 3
                sales_data = get_sales_analytics(date_months=months_for_vendor_data) # Re-fetch if not already fetched for this period, or use existing if months_for_vendor_data is same as months_for_sales_data
                
                # To avoid re-fetching, we could store sales_data if fetched with same period
                # For now, keeping it simple and potentially re-fetching.
                # A more advanced approach would be to fetch sales_data once with the determined months
                # and use it across different sections if the keywords match.

                if sales_data.get('vendor_performance'):
                    live_data_context += f"\n\nRendimiento por vendedores (últimos {months_for_vendor_data} {'mes' if months_for_vendor_data == 1 else 'meses'}):\n{sales_data['vendor_performance']}"
                # If sales_data was already fetched for 'productos', 'ventas' etc. with a different period, 
                # this might add duplicate or conflicting context.
                # Consider unifying sales_data fetching if multiple sales-related keywords are present.
                
                # Example of conditional addition if not already added for the same period:
                # This part is a bit complex due to potential overlaps and is simplified here.
                if 'Análisis de productos' not in live_data_context or f"(últimos {months_for_vendor_data}" not in live_data_context :
                    if sales_data.get('product_analysis'):
                         live_data_context += f"\n\nAnálisis de productos (últimos {months_for_vendor_data} {'mes' if months_for_vendor_data == 1 else 'meses'}):\\n{sales_data['product_analysis']}"
                if 'Rendimiento por categorías' not in live_data_context or f"(últimos {months_for_vendor_data}" not in live_data_context:
                    if sales_data.get('category_performance'):
                        live_data_context += f"\n\nRendimiento por categorías (últimos {months_for_vendor_data} {'mes' if months_for_vendor_data == 1 else 'meses'}):\\n{sales_data['category_performance']}"
            
            # Check if the question needs real-time inventory data
            if any(keyword in question_lower for keyword in ['inventario', 'stock', 'productos', 'bajo stock', 'sin stock', 'reposición']):
                logger.info("Question requires inventory analytics data")
                inventory_data = get_inventory_analytics()
                if inventory_data.get('low_stock'):
                    live_data_context += f"\n\nProductos con bajo stock:\n{inventory_data['low_stock']}"
                if inventory_data.get('abc_analysis'):
                    live_data_context += f"\n\nAnálisis ABC de productos:\n{inventory_data['abc_analysis']}"
                if inventory_data.get('brand_analysis'):
                    live_data_context += f"\n\nAnálisis por marcas:\n{inventory_data['brand_analysis']}"
            
            if live_data_context:
                logger.info(f"Live data context added, length: {len(live_data_context)}")
            else:
                logger.info("No specific live data context needed for this question based on keywords.")
                
        except Exception as live_data_error:
            logger.error(f"Error getting live data context: {str(live_data_error)}", exc_info=True)
            live_data_context = "\nError al obtener datos en tiempo real." # Keep it separate from RAG error
        
        # Construct the prompt using BOTH contexts
        prompt = f"""Eres Ariadna Neuman, asistente de IA experta para el panel de "Analytics Avanzados" de Veterinaria Neuman.

Personalidad y Estilo:
- Profesional pero accesible, siempre dispuesta a ayudar
- Usas frases como "Permíteme revisar los detalles para ti...", "Según la información del panel...", "Los datos muestran que..."
- Te enfocas en proporcionar insights útiles y accionables
- Cuando tienes datos reales, los presentas de manera clara y con recomendaciones

Tu propósito es ayudar al administrador a entender los datos y gráficos presentados.

IMPORTANTE: 
- Si tienes datos actuales disponibles en el contexto, úsalos para dar respuestas específicas y completas
- Si la pregunta es sobre productos más vendidos, clientes top, inventario, etc., proporciona los datos reales cuando estén disponibles
- Para consultas específicas de marcas: EDO = "Laboratorios EDO, S.A.S." y CHINFIELD = "CHINFIELD, S.A."
- Para consultas de productos específicos, busca nombres similares y diferentes presentaciones/tamaños
- Combina la explicación técnica con insights de negocio
- Sé concisa pero completa en tus respuestas

Contexto del Panel (Información de la Base de Conocimiento de Ariadna):
{rag_dynamic_context}

Datos Relevantes en Tiempo Real (si aplica a la pregunta):
{live_data_context}

Pregunta del Usuario:
"{user_question}"

Respuesta como Ariadna Neuman:
"""
        
        logger.info(f"Prompt generated for Gemini, length: {len(prompt)}")
        # logger.debug(f"Full prompt for Gemini:\n{prompt}") # Optional: log full prompt for debugging
        
        # Call Gemini model (your existing logic)
        try:
            logger.info("Calling Gemini model...")
            response = gemini_model.generate_content(prompt)
            logger.info("Gemini model responded successfully")
        except Exception as gemini_error:
            logger.error(f"Error calling Gemini model: {str(gemini_error)}", exc_info=True)
            return jsonify({"error": f"Error comunicándose con el modelo de IA: {str(gemini_error)}"}), 500
        
        # Process response
        ai_response_text = ""
        try:
            if response.candidates and response.candidates[0].content.parts:
                ai_response_text = response.candidates[0].content.parts[0].text
                logger.info(f"Extracted response text, length: {len(ai_response_text)}")
            else:
                logger.warning("Gemini response structure unexpected")
                ai_response_text = "No pude generar una respuesta. Intenta reformular tu pregunta."
        except Exception as parse_error:
            logger.error(f"Error parsing Gemini response: {str(parse_error)}", exc_info=True)
            ai_response_text = "Error procesando la respuesta del modelo de IA."
        
        if not ai_response_text:
            ai_response_text = "No pude generar una respuesta. Intenta reformular tu pregunta."
            logger.warning("Final response text was empty")
        
        logger.info(f"[REQUEST-{request_id}] AI Assistant response snippet: {ai_response_text[:200]}...")
        
        # Ensure proper UTF-8 encoding
        response = app.response_class(
            response=json.dumps({"response": ai_response_text}, ensure_ascii=False),
            status=200,
            mimetype='application/json; charset=utf-8'
        )
        return response
            
    except Exception as e:
        logger.error(f"Error in AI Assistant endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al procesar pregunta con IA: {str(e)}"}), 500

# --- Other Routes from User's new simple_dashboard.py ---
# (Excel upload, export, old AI endpoints, debug routes, etc.)
# These should be copied verbatim from the user's provided simple_dashboard.py
# For brevity, I am not re-listing all of them but ensuring key AI and core app routes are present.

@app.route('/api/upload/excel', methods=['POST'])
@login_required
def upload_excel():
    try:
        if 'excel_file' not in request.files:
            return jsonify({"success": False, "error": "No se encontró archivo en la solicitud"})
        file = request.files['excel_file']
        table_name = request.form.get('table_name', 'ventas')
        if file.filename == '': return jsonify({"success": False, "error": "No se seleccionó archivo"})
        logger.info(f"Processing Excel upload: {file.filename} for table: {table_name}")
        is_valid, validation_message = validate_excel_file(file)
        if not is_valid: return jsonify({"success": False, "error": validation_message})
        conn, db_message = get_db_connection()
        if not conn: return jsonify({"success": False, "error": f"Error de conexión a base de datos: {db_message}"})
        try:
            file_content = file.read()
            file.seek(0)
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl' if file.filename.lower().endswith('.xlsx') else None) # type: ignore
            if df.empty:
                conn.close()
                return jsonify({"success": False, "error": "El archivo Excel está vacío o no contiene datos válidos"})
            logger.info(f"Excel file loaded. Rows: {len(df)}, Columns: {len(df.columns)}")
            if table_name == 'ventas':
                processed_df, error_message = process_ventas_excel(df)
                if error_message: 
                    conn.close()
                    return jsonify({"success": False, "error": error_message})
                success, message = update_ventas_table(processed_df, conn) # type: ignore
            elif table_name == 'inventario':
                processed_df, error_message = process_inventario_excel(df)
                if error_message: 
                    conn.close()
                    return jsonify({"success": False, "error": error_message})
                success, message = update_inventario_table(processed_df, conn) # type: ignore
            else:
                conn.close()
                return jsonify({"success": False, "error": f"Tipo de tabla no soportado: {table_name}"})
            conn.close()
            if success: return jsonify({"success": True, "message": f"✅ Archivo '{file.filename}' procesado para {table_name}.\n{message}"}) # type: ignore
            else: return jsonify({"success": False, "error": message})
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error processing Excel file: {str(e)}", exc_info=True)
            return jsonify({"success": False, "error": f"Error procesando archivo: {str(e)}"})
    except Exception as e:
        logger.error(f"Error in upload_excel endpoint: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"})

@app.route('/api/export/excel') # From
@login_required
def export_excel():
    return jsonify({"error": "Funcionalidad de exportación pendiente"})

@app.route('/api/ai/question', methods=['POST']) # From
@login_required
def api_ai_question():
    logger.warning("Legacy /api/ai/question endpoint called. Use /api/ai/analytics_assistant.")
    return jsonify({"answer": "Este endpoint ha sido reemplazado. Utiliza el nuevo asistente de IA en Analytics Avanzados.", "summary": ""})

@app.route('/api/ai/sql', methods=['POST']) # From
@login_required
def api_ai_sql():
    logger.warning("Legacy /api/ai/sql endpoint called. SQL generation via chat is not fully implemented in analytics_assistant yet.")
    return jsonify({"sql": "-- SQL generation not available via this endpoint --", "data": [], "columns": [], "summary": "Utiliza el nuevo asistente de IA."})

@app.route('/api/check-columns') # From
@login_required
def check_columns():
    try:
        columns, error = check_view_columns()
        if error: return jsonify({"error": error})
        return jsonify({"columns": columns})
    except Exception as e: return jsonify({"error": str(e)})
        
@app.route('/health') # From
def health():
    return jsonify({"status": "healthy"})

@app.route('/debug-users') # From
def debug_users():
    try:
        conn, message = get_db_connection()
        if not conn: return jsonify({"error": f"Database connection failed: {message}"})
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'usuarios')")
        table_exists = cursor.fetchone()[0] # type: ignore
        result = {"table_exists": table_exists, "users": []}
        if table_exists:
            cursor.execute("SELECT id, username, email, role, is_active, created_at FROM usuarios")
            users_data = cursor.fetchall()
            result["users"] = [{'id': r[0], 'username': r[1], 'email': r[2], 'role': r[3], 'is_active': r[4], 'created_at': str(r[5]) if r[5] else None} for r in users_data] # type: ignore
            cursor.execute("SELECT id, username, password_hash FROM usuarios WHERE username = %s", ('aneuman',))
            admin_user_data = cursor.fetchone()
            if admin_user_data:
                result["admin_user_found"] = True # type: ignore
                result["password_test"] = bcrypt.checkpw('#Vetneuman4012'.encode('utf-8'), admin_user_data[2].encode('utf-8')) # type: ignore
            else: result["admin_user_found"] = False # type: ignore
        cursor.close(); conn.close()
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)})

@app.route('/admin/fix-brands') # From new simple_dashboard.py
@login_required
def fix_inventory_brands():
    if not current_user.is_admin(): return jsonify({'error': 'No autorizado'}), 403 # type: ignore
    try:
        conn, message = get_db_connection()
        if not conn: return jsonify({"error": f"Database connection failed: {message}"})
        cursor = conn.cursor()
        cursor.execute('SELECT "Item", "Description", marca FROM public."inventarioneuman"')
        items = cursor.fetchall()
        updated_count, chinfield_count, edo_count, other_count = 0, 0, 0, 0
        for item_id, _, current_marca in items:
            new_marca = 'CHINFIELD, S.A.' if 'ach' in item_id.lower() else ('Laboratorios EDO, S.A.S.' if 'edo' in item_id.lower() else 'otra')
            if new_marca == 'CHINFIELD, S.A.': chinfield_count +=1
            elif new_marca == 'Laboratorios EDO, S.A.S.': edo_count += 1
            else: other_count +=1
            if current_marca != new_marca:
                cursor.execute('UPDATE public."inventarioneuman" SET marca = %s WHERE "Item" = %s', (new_marca, item_id))
                updated_count += 1
        conn.commit(); cursor.close(); conn.close()
        return jsonify({'success': True, 'message': 'Brand fix completed', 'total_items': len(items), 'updated_items': updated_count,
                        'brand_distribution': {'CHINFIELD, S.A.': chinfield_count, 'Laboratorios EDO, S.A.S.': edo_count, 'otra': other_count}})
    except Exception as e:
        logger.error(f"Error fixing inventory brands: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Helper functions (validate_excel_file, process_ventas_excel, etc.)
# These should be the versions from your new simple_dashboard.py.
# For brevity, I am assuming they are correctly defined as in your provided file.
def validate_excel_file(file): # From
    filename = file.filename.lower() # type: ignore
    if not (filename.endswith('.xlsx') or filename.endswith('.xls')): return False, "El archivo debe ser un Excel (.xlsx o .xls)"
    file.seek(0, 2); file_size = file.tell(); file.seek(0)
    if file_size > 10 * 1024 * 1024: return False, "El archivo es demasiado grande (máximo 10MB)"
    if file_size == 0: return False, "El archivo está vacío"
    return True, "Archivo válido"

def process_ventas_excel(df):
    """Process sales Excel file with flexible column mapping"""
    try:
        # Column mapping for flexibility
        column_mapping = {
            'invoice_cm_': ['Invoice/CM #', 'Invoice/CM#', 'invoice', 'factura'],
            'date': ['Date', 'fecha', 'Fecha'],
            'customer_id': ['Customer ID', 'cliente_id', 'customer'],
            'name': ['Name', 'nombre', 'cliente'],
            'qty': ['Qty', 'cantidad', 'quantity'],
            'item_id': ['Item ID', 'item', 'codigo'],
            'item_description': ['Item Description', 'descripcion', 'description'],
            'unit_price': ['Unit Price', 'precio', 'price'],
            'vendedor': ['Vendedor', 'vendor', 'seller'],
            'provincia': ['Provincia', 'province'],
            'ruta': ['Ruta', 'route'],
            'tipo_cliente': ['Tipo Cliente', 'customer_type', 'tipo']
        }
        
        # Debug: Log actual Excel columns
        logger.info(f"Excel columns found: {list(df.columns)}")
        
        # Find actual column names
        actual_columns = {}
        for target_col, possible_names in column_mapping.items():
            found = False
            for possible_name in possible_names:
                if possible_name in df.columns:
                    actual_columns[target_col] = possible_name
                    logger.info(f"Mapped {target_col} -> {possible_name}")
                    found = True
                    break
            if not found:
                logger.warning(f"Column for {target_col} not found. Possible names: {possible_names}")
        
        logger.info(f"Actual columns mapped: {actual_columns}")
        
        # Check required columns
        required_columns = ['invoice_cm_', 'date', 'customer_id', 'qty', 'item_description', 'unit_price']
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        logger.info(f"Required columns: {required_columns}")
        logger.info(f"Missing columns: {missing_columns}")
        
        if missing_columns:
            error_msg = f"Columnas requeridas faltantes: {missing_columns}"
            logger.error(error_msg)
            return None, error_msg
        
        # Rename columns to standard names
        rename_dict = {v: k for k, v in actual_columns.items()}
        df_processed = df.rename(columns=rename_dict)
        
        # Standardize dates
        if 'date' in df_processed.columns:
            df_processed['date'] = df_processed['date'].apply(standardize_date_format)
        
        # Clean and validate data
        df_processed = df_processed.dropna(subset=['invoice_cm_', 'customer_id', 'qty', 'unit_price'])
        
        # Convert numeric columns (customer_id is text, not numeric!)
        numeric_columns = ['qty', 'unit_price']
        for col in numeric_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Remove rows with invalid numeric data
        df_processed = df_processed.dropna(subset=numeric_columns)
        
        # Apply customer ID decoding to extract vendedor, provincia, ruta, tipo_cliente
        if 'customer_id' in df_processed.columns:
            logger.info("Applying customer ID decoding rules...")
            customer_info = df_processed['customer_id'].apply(decodificar_customer_id)
            
            # Convert the series of dictionaries to separate columns
            for key in ['vendedor', 'provincia', 'ruta', 'tipo_cliente']:
                df_processed[key] = customer_info.apply(lambda x: x[key])
            
            logger.info(f"Customer ID decoding completed. Example values:")
            if len(df_processed) > 0:
                sample_row = df_processed.iloc[0]
                logger.info(f"  Customer ID: {sample_row['customer_id']}")
                logger.info(f"  Vendedor: {sample_row['vendedor']}")
                logger.info(f"  Provincia: {sample_row['provincia']}")
                logger.info(f"  Ruta: {sample_row['ruta']}")
                logger.info(f"  Tipo Cliente: {sample_row['tipo_cliente']}")
        
        logger.info(f"Processed {len(df_processed)} valid sales records")
        return df_processed, None
        
    except Exception as e:
        error_msg = f"Error processing sales Excel: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def process_inventario_excel(df):
    """Process inventory Excel file with flexible column mapping"""
    try:
        # Column mapping for flexibility
        column_mapping = {
            'Item': ['Item', 'item_id', 'codigo', 'Code'],
            'Description': ['Description', 'descripcion', 'Descripcion'],
            'Qty on Hand': ['Qty on Hand', 'stock', 'cantidad', 'Quantity'],
            'Unit Price': ['Unit Price', 'precio', 'price', 'Price']
        }
        
        # Find actual column names
        actual_columns = {}
        for target_col, possible_names in column_mapping.items():
            found = False
            for possible_name in possible_names:
                if possible_name in df.columns:
                    actual_columns[target_col] = possible_name
                    found = True
                    break
            if not found and target_col in ['Item', 'Description', 'Qty on Hand']:
                logger.warning(f"Required column for {target_col} not found. Possible names: {possible_names}")
        
        # Check required columns
        required_columns = ['Item', 'Description', 'Qty on Hand']
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        if missing_columns:
            return None, f"Columnas requeridas faltantes: {missing_columns}"
        
        # Rename columns to standard names
        rename_dict = {v: k for k, v in actual_columns.items()}
        df_processed = df.rename(columns=rename_dict)
        
        # Clean and validate data
        df_processed = df_processed.dropna(subset=['Item', 'Description'])
        
        # Convert numeric columns
        if 'Qty on Hand' in df_processed.columns:
            df_processed['Qty on Hand'] = pd.to_numeric(df_processed['Qty on Hand'], errors='coerce').fillna(0)
        
        if 'Unit Price' in df_processed.columns:
            df_processed['Unit Price'] = pd.to_numeric(df_processed['Unit Price'], errors='coerce')
        
        # Derive brand from item_id
        def get_brand(item_id):
            if pd.isna(item_id):
                return 'otra'
            item_str = str(item_id).lower()
            if 'ach' in item_str:
                return 'CHINFIELD, S.A.'
            elif 'edo' in item_str:
                return 'Laboratorios EDO, S.A.S.'
            else:
                return 'otra'
        
        df_processed['marca'] = df_processed['Item'].apply(get_brand)
        
        # Ensure Item is string and not empty
        df_processed['Item'] = df_processed['Item'].astype(str)
        df_processed = df_processed[df_processed['Item'].str.strip() != '']
        
        logger.info(f"Processed {len(df_processed)} valid inventory records")
        return df_processed, None
        
    except Exception as e:
        error_msg = f"Error processing inventory Excel: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def update_ventas_table(df, conn):
    """Update sales table with processed data"""
    try:
        cursor = conn.cursor()
        
        # Clear existing data (optional - you might want to append instead)
        # cursor.execute('DELETE FROM public."ventas_vet_neuman"')
        
        # Insert new data
        insert_count = 0
        skip_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Log first few rows for debugging
                if idx < 5:
                    app.logger.info(f"Row {idx} data: qty={row.get('qty')}, unit_price={row.get('unit_price')}, item_description='{row.get('item_description')}'")
                
                # Skip rows with missing critical data
                if pd.isna(row.get('qty')) or pd.isna(row.get('unit_price')) or not row.get('item_description'):
                    skip_count += 1
                    if idx < 10:  # Log why first 10 rows were skipped
                        app.logger.info(f"Skipping row {idx}: qty={row.get('qty')}, unit_price={row.get('unit_price')}, item_description='{row.get('item_description')}'")
                    continue
                
                cursor.execute('''
                    INSERT INTO public."ventas_vet_neuman" 
                    ("invoice_cm_", "date", "customer_id", "name", "qty", "item_id", 
                     "item_description", "unit_price", "vendedor", "provincia", "ruta", "tipo_cliente")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    row.get('invoice_cm_'),
                    row.get('date'),
                    row.get('customer_id'),
                    row.get('name'),
                    float(row.get('qty', 0)),
                    row.get('item_id'),
                    row.get('item_description'),
                    float(row.get('unit_price', 0)),
                    row.get('vendedor', 'SIN ASIGNAR'),  # Default value
                    row.get('provincia', 'SIN ASIGNAR'),  # Default value
                    row.get('ruta', 'SIN ASIGNAR'),  # Default value
                    row.get('tipo_cliente', 'SIN ASIGNAR')  # Default value
                ))
                insert_count += 1
                if idx < 5:  # Log first few successful inserts
                    app.logger.info(f"Successfully inserted row {idx}: {row.get('invoice_cm_')}")
            except Exception as e:
                logger.warning(f"Error inserting row {idx}: {e}")
                error_count += 1
                continue
        
        conn.commit()
        
        message = f"Successfully inserted {insert_count} sales records"
        if skip_count > 0:
            message += f" (skipped {skip_count} rows with missing data)"
        if error_count > 0:
            message += f" (failed to insert {error_count} rows)"
            
        return True, message
        
    except Exception as e:
        conn.rollback()
        error_msg = f"Error updating sales table: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def update_inventario_table(df, conn):
    """Update inventory table with processed data"""
    try:
        cursor = conn.cursor()
        
        # Use UPSERT (INSERT ... ON CONFLICT) to update existing items or insert new ones
        upsert_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO public."inventarioneuman" 
                    ("Item", "Description", "Qty on Hand", "Unit Price", "marca")
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ("Item") DO UPDATE SET
                        "Description" = EXCLUDED."Description",
                        "Qty on Hand" = EXCLUDED."Qty on Hand",
                        "Unit Price" = EXCLUDED."Unit Price",
                        "marca" = EXCLUDED."marca"
                ''', (
                    row.get('Item'),
                    row.get('Description'),
                    row.get('Qty on Hand'),
                    row.get('Unit Price'),
                    row.get('marca')
                ))
                upsert_count += 1
            except Exception as e:
                logger.warning(f"Error upserting inventory row: {e}")
                continue
        
        conn.commit()
        return True, f"Successfully upserted {upsert_count} inventory records"
        
    except Exception as e:
        conn.rollback()
        error_msg = f"Error updating inventory table: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def check_view_columns():
    """Check available columns in the sales view"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return None, f"Database connection failed: {message}"
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT column_name, data_type 
                    FROM information_schema.columns 
            WHERE table_name = 'vista_ventas_con_tipo_por_desc'
                    ORDER BY ordinal_position
        ''')
        
        columns = cursor.fetchall()
        cursor.close()
        conn.close()
        
        column_info = [{'name': col[0], 'type': col[1]} for col in columns]
        return column_info, None
        
    except Exception as e:
        error_msg = f"Error checking view columns: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

# Note: Admin user initialization moved to happen on first request to avoid Cloud Run startup issues

@app.route('/debug-upload') # Debug endpoint for upload issues
@login_required
def debug_upload():
    """Debug endpoint to check upload/view data sync"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return jsonify({"error": f"Database connection failed: {message}"})
        
        cursor = conn.cursor()
        
        # Check what's in the raw table
        cursor.execute('SELECT COUNT(*) FROM public."ventas_vet_neuman"')
        raw_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM public."vista_ventas_con_tipo_por_desc"')
        view_count = cursor.fetchone()[0]
        
        # Check recent records in raw table
        cursor.execute('''
            SELECT "invoice_cm_", "date", "customer_id", "name", "qty", "item_description", "unit_price"
            FROM public."ventas_vet_neuman" 
            ORDER BY "invoice_cm_" DESC 
            LIMIT 5
        ''')
        raw_recent = cursor.fetchall()
        
        # Check recent records in view
        cursor.execute('''
            SELECT "invoice_cm_", "date", "customer_id", "name", "qty", "item_description", "unit_price"
            FROM public."vista_ventas_con_tipo_por_desc" 
            ORDER BY "invoice_cm_" DESC 
            LIMIT 5
        ''')
        view_recent = cursor.fetchall()
        
        # Check column names
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ventas_vet_neuman' AND table_schema = 'public'
            ORDER BY ordinal_position
        ''')
        raw_columns = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vista_ventas_con_tipo_por_desc' AND table_schema = 'public'
            ORDER BY ordinal_position
        ''')
        view_columns = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "raw_table_count": raw_count,
            "view_count": view_count,
            "raw_columns": raw_columns,
            "view_columns": view_columns,
            "raw_recent_records": [list(r) for r in raw_recent],
            "view_recent_records": [list(r) for r in view_recent],
            "columns_missing_in_raw": [col for col in view_columns if col not in raw_columns],
            "columns_missing_in_view": [col for col in raw_columns if col not in view_columns]
        })
        
    except Exception as e:
        logger.error(f"Error in debug_upload: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)})

@app.route('/debug-ai') # Debug endpoint for AI status
def debug_ai():
    debug_info = {
        "vertex_ai_available": VERTEX_AI_AVAILABLE,
        "gemini_model_loaded": gemini_model is not None,
        "environment_vars": {
            "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT"),
            "GCP_PROJECT_ID": os.environ.get("GCP_PROJECT_ID"),
            "GOOGLE_CLOUD_LOCATION": os.environ.get("GOOGLE_CLOUD_LOCATION"),
            "GEMINI_MODEL_NAME": os.environ.get("GEMINI_MODEL_NAME"),
            "INSTANCE_CONNECTION_NAME": os.environ.get("INSTANCE_CONNECTION_NAME")[:50] + "..." if os.environ.get("INSTANCE_CONNECTION_NAME") else None
        }
    }
    
    if VERTEX_AI_AVAILABLE and gemini_model:
        try:
            # Test a simple prompt
            test_response = gemini_model.generate_content("Responde con: 'Test exitoso'")
            if test_response.candidates and test_response.candidates[0].content.parts:
                debug_info["test_result"] = "SUCCESS"
                debug_info["test_response"] = test_response.candidates[0].content.parts[0].text
            else:
                debug_info["test_result"] = "FAILED - No response parts"
        except Exception as e:
            debug_info["test_result"] = f"FAILED - {str(e)}"
    else:
        debug_info["test_result"] = "SKIPPED - AI not available"
    
    return jsonify(debug_info)

# Admin user initialization now happens on demand (lazy loading) to avoid Cloud Run startup issues

def load_filter_options():
    """Load filter options from the database"""
    try:
        conn, message = get_db_connection()
        if not conn:
            logger.error(f"Cannot connect to database: {message}")
            return None, message
        
        cursor = conn.cursor()
        
        # Get unique values for each filter
        filter_queries = {
            'provincias': 'SELECT DISTINCT "provincia" FROM public."vista_ventas_con_tipo_por_desc" WHERE "provincia" IS NOT NULL ORDER BY "provincia"',
            'rutas': 'SELECT DISTINCT "ruta" FROM public."vista_ventas_con_tipo_por_desc" WHERE "ruta" IS NOT NULL ORDER BY "ruta"',
            'vendedores': 'SELECT DISTINCT "vendedor" FROM public."vista_ventas_con_tipo_por_desc" WHERE "vendedor" IS NOT NULL ORDER BY "vendedor"',
            'tipos_producto': 'SELECT DISTINCT "tipo" FROM public."vista_ventas_con_tipo_por_desc" WHERE "tipo" IS NOT NULL ORDER BY "tipo"'
        }
        
        filter_options = {}
        
        for filter_name, query in filter_queries.items():
            logger.info(f"Loading {filter_name}...")
            cursor.execute(query)
            results = cursor.fetchall()
            values = [row[0] for row in results if row[0] and str(row[0]).strip()]
            filter_options[filter_name] = values
            logger.info(f"Found {len(values)} unique {filter_name}")
        
        # Get date range
        date_query = '''
        SELECT 
            MIN("date") as min_date,
            MAX("date") as max_date
        FROM public."vista_ventas_con_tipo_por_desc" 
        WHERE "date" IS NOT NULL
        '''
        
        cursor.execute(date_query)
        date_result = cursor.fetchone()
        
        if date_result and date_result[0] and date_result[1]:
            min_date = date_result[0]
            max_date = date_result[1]
            filter_options['date_range'] = {"min": min_date, "max": max_date}
        else:
            filter_options['date_range'] = {"min": "2024-01-01", "max": "2024-12-31"}
        
        cursor.close()
        conn.close()
        
        return filter_options, None
        
    except Exception as e:
        error_msg = f"Error loading filter options: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def load_filtered_data(filters=None):
    """Load detailed sales data with filtering"""
    try:
        conn, message = get_db_connection()
        if not conn:
            logger.error(f"Cannot connect to database: {message}")
            return None, message
        
        # Build the WHERE clause based on filters
        where_conditions = []
        params = []
        
        # Date filtering - handle different date formats
        if filters and filters.get('start_date'):
            try:
                from datetime import datetime
                start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                where_conditions.append('("date" >= %s OR "date" >= %s OR "date" >= %s)')
                params.extend([
                    start_date.strftime('%d/%m/%y'),
                    start_date.strftime('%d/%m/%Y'),
                    start_date.strftime('%Y-%m-%d')
                ])
            except:
                pass
        
        if filters and filters.get('end_date'):
            try:
                from datetime import datetime
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                where_conditions.append('("date" <= %s OR "date" <= %s OR "date" <= %s)')
                params.extend([
                    end_date.strftime('%d/%m/%y'),
                    end_date.strftime('%d/%m/%Y'),
                    end_date.strftime('%Y-%m-%d')
                ])
            except:
                pass
        
        # Multi-select filters
        if filters:
            filter_mappings = [
                ('provincia', 'provincia'),
                ('ruta', 'ruta'),
                ('vendedor', 'vendedor'),
                ('tipo', 'tipo')
            ]
            
            for filter_key, column_name in filter_mappings:
                filter_values = filters.get(filter_key, [])
                if filter_values and 'all' not in filter_values:
                    if isinstance(filter_values, str):
                        filter_values = [filter_values]
                    if filter_values:
                        placeholders = ','.join(['%s'] * len(filter_values))
                        where_conditions.append(f'"{column_name}" IN ({placeholders})')
                        params.extend(filter_values)
        
        # Build the complete query
        base_query = '''
        SELECT 
            "invoice_cm_" as "Invoice/CM #",
            "date" as "Date",
            "customer_id" as "Customer ID", 
            "name" as "Name",
            "qty" as "Qty",
            "item_description" as "Item Description",
            "unit_price" as "Unit Price",
            "vendedor" as "Vendedor",
            "provincia" as "Provincia", 
            "ruta" as "Ruta",
            "tipo_cliente" as "Tipo Cliente",
            "tipo" as "Tipo",
            ("qty" * "unit_price") as "Total"
        FROM public."vista_ventas_con_tipo_por_desc"
        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
        '''
        
        if where_conditions:
            base_query += ' AND (' + ' AND '.join(where_conditions) + ')'
        
        base_query += ' ORDER BY "date" DESC LIMIT 1000'
        
        logger.info(f"Executing filtered query with {len(params)} parameters")
        
        cursor = conn.cursor()
        cursor.execute(base_query, params)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch results
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            record = {}
            for i, column in enumerate(columns):
                value = row[i]
                if value is None:
                    record[column] = ''
                else:
                    record[column] = value
            data.append(record)
        
        logger.info(f"Returning {len(data)} filtered records")
        return data, None
            
    except Exception as e:
        error_msg = f"Error loading filtered data: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def calculate_filtered_kpis(filters=None):
    """Calculate KPIs based on filters"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return None, message
        
        # Build the same WHERE clause as in load_filtered_data
        where_conditions = []
        params = []
        
        # Date filtering
        if filters and filters.get('start_date'):
            try:
                from datetime import datetime
                start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                where_conditions.append('("date" >= %s OR "date" >= %s OR "date" >= %s)')
                params.extend([
                    start_date.strftime('%d/%m/%y'),
                    start_date.strftime('%d/%m/%Y'),
                    start_date.strftime('%Y-%m-%d')
                ])
            except:
                pass
        
        if filters and filters.get('end_date'):
            try:
                from datetime import datetime
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                where_conditions.append('("date" <= %s OR "date" <= %s OR "date" <= %s)')
                params.extend([
                    end_date.strftime('%d/%m/%y'),
                    end_date.strftime('%d/%m/%Y'),
                    end_date.strftime('%Y-%m-%d')
                ])
            except:
                pass
        
        # Multi-select filters
        if filters:
            filter_mappings = [
                ('provincia', 'provincia'),
                ('ruta', 'ruta'),
                ('vendedor', 'vendedor'),
                ('tipo', 'tipo')
            ]
            
            for filter_key, column_name in filter_mappings:
                filter_values = filters.get(filter_key, [])
                if filter_values and 'all' not in filter_values:
                    if isinstance(filter_values, str):
                        filter_values = [filter_values]
                    if filter_values:
                        placeholders = ','.join(['%s'] * len(filter_values))
                        where_conditions.append(f'"{column_name}" IN ({placeholders})')
                        params.extend(filter_values)
        
        # KPI query
        kpi_query = '''
        SELECT 
            COUNT(*) as total_records,
            SUM("qty" * "unit_price") as total_ventas,
            COUNT(DISTINCT "invoice_cm_") as cantidad_facturas,
            COUNT(DISTINCT "customer_id") as cantidad_clientes
        FROM public."vista_ventas_con_tipo_por_desc"
        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
        '''
        
        if where_conditions:
            kpi_query += ' AND (' + ' AND '.join(where_conditions) + ')'
        
        cursor = conn.cursor()
        cursor.execute(kpi_query, params)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            total_records, total_ventas, cantidad_facturas, cantidad_clientes = result
            ticket_promedio = total_ventas / cantidad_facturas if cantidad_facturas > 0 else 0
            
            return {
                "total_records": total_records or 0,
                "total_ventas": float(total_ventas or 0),
                "cantidad_facturas": int(cantidad_facturas or 0),
                "cantidad_clientes": int(cantidad_clientes or 0),
                "ticket_promedio": float(ticket_promedio)
            }, None
        else:
            return {
                "total_records": 0,
                "total_ventas": 0,
                "cantidad_facturas": 0,
                "cantidad_clientes": 0,
                "ticket_promedio": 0
            }, None
            
    except Exception as e:
        error_msg = f"Error calculating KPIs: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def get_inventory_analytics():
    """Get advanced inventory analytics"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return {"error": f"Database connection failed: {message}"}
        
        cursor = conn.cursor()
        analytics = {}
        
        # 1. Low Stock Analysis
        cursor.execute('''
            SELECT "Item", "Description", "Qty on Hand", marca
            FROM public."inventarioneuman"
            WHERE "Qty on Hand" < 10
            ORDER BY "Qty on Hand" ASC
            LIMIT 20
        ''')
        low_stock = cursor.fetchall()
        analytics['low_stock'] = [{
            'item_id': row[0],
            'description': row[1], 
            'stock': float(row[2]) if row[2] else 0,
            'brand': row[3]
        } for row in low_stock]
        
        # 2. ABC Analysis (based on sales)
        cursor.execute('''
            SELECT 
                v."item_id",
                v."item_description",
                SUM(v."qty" * v."unit_price") as total_sales,
                SUM(v."qty") as total_qty_sold,
                i."Qty on Hand" as current_stock
            FROM public."vista_ventas_con_tipo_por_desc" v
            LEFT JOIN public."inventarioneuman" i ON v."item_id" = i."Item"
            WHERE v."qty" IS NOT NULL AND v."unit_price" IS NOT NULL
            GROUP BY v."item_id", v."item_description", i."Qty on Hand"
            ORDER BY total_sales DESC
            LIMIT 50
        ''')
        abc_data = cursor.fetchall()
        analytics['abc_analysis'] = [{
            'item_id': row[0],
            'description': row[1],
            'total_sales': float(row[2]) if row[2] else 0,
            'qty_sold': float(row[3]) if row[3] else 0,
            'current_stock': float(row[4]) if row[4] else 0
        } for row in abc_data]
        
        # 3. Slow Moving Products (high stock, low sales)
        cursor.execute('''
            SELECT 
                i."Item",
                i."Description", 
                i."Qty on Hand",
                COALESCE(sales.total_qty_sold, 0) as qty_sold_last_period,
                i.marca
            FROM public."inventarioneuman" i
            LEFT JOIN (
                SELECT 
                    "item_id",
                    SUM("qty") as total_qty_sold
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL
                GROUP BY "item_id"
            ) sales ON i."Item" = sales."item_id"
            WHERE i."Qty on Hand" > 20
            AND COALESCE(sales.total_qty_sold, 0) < 5
            ORDER BY i."Qty on Hand" DESC
            LIMIT 30
        ''')
        slow_moving = cursor.fetchall()
        analytics['slow_moving'] = [{
            'item_id': row[0],
            'description': row[1],
            'stock': float(row[2]) if row[2] else 0,
            'sales': float(row[3]) if row[3] else 0,
            'brand': row[4]
        } for row in slow_moving]
        
        # 4. Stock vs Sales Comparison
        cursor.execute('''
            SELECT 
                i.marca,
                COUNT(i."Item") as products_count,
                SUM(i."Qty on Hand") as total_stock,
                COALESCE(SUM(sales.total_sales), 0) as total_sales
            FROM public."inventarioneuman" i
            LEFT JOIN (
                SELECT 
                    "item_id",
                    SUM("qty" * "unit_price") as total_sales
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                GROUP BY "item_id"
            ) sales ON i."Item" = sales."item_id"
            GROUP BY i.marca
            ORDER BY total_sales DESC
        ''')
        brand_analysis = cursor.fetchall()
        analytics['brand_analysis'] = [{
            'brand': row[0],
            'products_count': int(row[1]) if row[1] else 0,
            'total_stock': float(row[2]) if row[2] else 0,
            'total_sales': float(row[3]) if row[3] else 0
        } for row in brand_analysis]
        
        cursor.close()
        conn.close()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error in inventory analytics: {str(e)}")
        return {"error": str(e)}

def get_customer_analytics(date_months=3):
    """Get advanced customer analytics with date filtering"""
    try:
        from datetime import datetime, timedelta # MOVED IMPORT HERE
        conn, message = get_db_connection()
        if not conn:
            return {
                "top_customers": [],
                "date_range": {
                    "months": date_months,
                    "start_date": datetime.now().strftime("%d/%m/%y"),
                    "end_date": datetime.now().strftime("%d/%m/%y")
                },
                "error": f"Database connection failed: {message}"
            }
        
        cursor = conn.cursor()
        analytics = {
            "top_customers": [],
            "date_range": {
                "months": date_months,
                "start_date": datetime.now().strftime("%d/%m/%y"),
                "end_date": datetime.now().strftime("%d/%m/%y")
            }
        }
        
        # Calculate date filter based on months parameter
        # from datetime import datetime, timedelta # REMOVED FROM HERE
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_months * 30)
        
        # Create a date filter condition that works with DD/M/YY format
        date_filter_condition = f"""
            AND TO_DATE("date", 'DD/MM/YY') >= TO_DATE('{start_date.strftime("%d/%m/%y")}', 'DD/MM/YY')
            AND TO_DATE("date", 'DD/MM/YY') <= TO_DATE('{end_date.strftime("%d/%m/%y")}', 'DD/MM/YY')
        """
        
        # 1. Top Customers by Sales (fixed duplicates issue)
        top_customers_query = f'''
            WITH customer_aggregated AS (
                SELECT 
                    "customer_id",
                    MAX("name") as name,
                    COUNT(DISTINCT "invoice_cm_") as invoice_count,
                    SUM("qty" * "unit_price") as total_sales,
                    COUNT(*) as line_items,
                    MAX("date") as last_purchase,
                    MAX("provincia") as provincia,
                    MAX("vendedor") as vendedor
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                AND "date" IS NOT NULL
                {date_filter_condition}
                GROUP BY "customer_id"
            )
            SELECT 
                customer_id,
                name,
                invoice_count,
                total_sales,
                line_items,
                last_purchase,
                provincia,
                vendedor
            FROM customer_aggregated
            ORDER BY total_sales DESC
            LIMIT 30
        '''
        
        try:
            cursor.execute(top_customers_query)
            top_customers = cursor.fetchall()
        except Exception as e:
            # Fallback: If date parsing fails, use a simpler approach
            logger.warning(f"Customer date filtering failed, using fallback approach: {e}")
            cursor.execute('''
                WITH customer_aggregated AS (
                    SELECT 
                        "customer_id",
                        MAX("name") as name,
                        COUNT(DISTINCT "invoice_cm_") as invoice_count,
                        SUM("qty" * "unit_price") as total_sales,
                        COUNT(*) as line_items,
                        MAX("date") as last_purchase,
                        MAX("provincia") as provincia,
                        MAX("vendedor") as vendedor
                    FROM (
                        SELECT *
                        FROM public."vista_ventas_con_tipo_por_desc"
                        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                        AND "date" IS NOT NULL
                        ORDER BY "invoice_cm_" DESC
                        LIMIT CASE 
                            WHEN %s = 1 THEN 5000
                            WHEN %s = 3 THEN 15000  
                            WHEN %s = 6 THEN 30000
                            WHEN %s = 12 THEN 60000
                            ELSE 200000
                        END
                    ) recent_data
                    GROUP BY "customer_id"
                )
                SELECT 
                    customer_id,
                    name,
                    invoice_count,
                    total_sales,
                    line_items,
                    last_purchase,
                    provincia,
                    vendedor
                FROM customer_aggregated
                ORDER BY total_sales DESC
                LIMIT 30
            ''', [date_months, date_months, date_months, date_months])
            top_customers = cursor.fetchall()
            
        analytics['top_customers'] = [{
            'customer_id': row[0],
            'name': row[1],
            'invoice_count': int(row[2]) if row[2] else 0,
            'total_sales': float(row[3]) if row[3] else 0,
            'line_items': int(row[4]) if row[4] else 0,
            'last_purchase': row[5],
            'province': row[6],
            'vendor': row[7]
        } for row in top_customers]
        
        # Update date range info
        analytics['date_range'] = {
            'months': date_months,
            'start_date': start_date.strftime("%d/%m/%y"),
            'end_date': end_date.strftime("%d/%m/%y")
        }
        
        cursor.close()
        conn.close()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error in customer analytics: {str(e)}")
        # Return a valid data structure even in case of error
        return {
            "top_customers": [],
            "date_range": {
                "months": date_months,
                "start_date": datetime.now().strftime("%d/%m/%y"),
                "end_date": datetime.now().strftime("%d/%m/%y")
            },
            "error": str(e)
        }

def get_sales_analytics(date_months=3):
    """Get advanced sales analytics with date filtering"""
    try:
        from datetime import datetime, timedelta # MOVED IMPORT HERE
        conn, message = get_db_connection()
        if not conn:
            return {
                "error": f"Database connection failed: {message}",
                "product_analysis": [],
                "vendor_performance": [],
                "category_performance": [],
                "province_performance": [],
                "date_range": {
                    "months": date_months,
                    "start_date": datetime.now().strftime("%d/%m/%y"),
                    "end_date": datetime.now().strftime("%d/%m/%y")
                }
            }
        
        cursor = conn.cursor()
        analytics = {
            "product_analysis": [],
            "vendor_performance": [],
            "category_performance": [],
            "province_performance": [],
            "date_range": {
                "months": date_months,
                "start_date": datetime.now().strftime("%d/%m/%y"),
                "end_date": datetime.now().strftime("%d/%m/%y")
            }
        }
        
        # Calculate date filter based on months parameter
        # from datetime import datetime, timedelta # REMOVED FROM HERE
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_months * 30)
        
        # Create a date filter condition that works with DD/M/YY format
        date_filter_condition = f"""
            AND TO_DATE("date", 'DD/MM/YY') >= TO_DATE('{start_date.strftime("%d/%m/%y")}', 'DD/MM/YY')
            AND TO_DATE("date", 'DD/MM/YY') <= TO_DATE('{end_date.strftime("%d/%m/%y")}', 'DD/MM/YY')
        """
        
        # 1. Product Analysis - Top Selling Products
        try:
            product_query = f'''
                SELECT 
                    "item_id",
                    "item_description",
                    "tipo" as type,
                    SUM("qty") as total_qty_sold,
                    SUM("qty" * "unit_price") as total_sales,
                    COUNT(DISTINCT "customer_id") as unique_customers,
                    COUNT(DISTINCT "invoice_cm_") as total_invoices,
                    AVG("unit_price") as avg_price
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                AND "item_id" IS NOT NULL AND "item_description" IS NOT NULL
                AND "date" IS NOT NULL
                {date_filter_condition}
                GROUP BY "item_id", "item_description", "tipo"
                ORDER BY total_sales DESC
                LIMIT 30
            '''
            
            cursor.execute(product_query)
            product_analysis = cursor.fetchall()
            
            if product_analysis:
                analytics['product_analysis'] = [{
                    'item_id': row[0],
                    'description': row[1],
                    'type': row[2] or 'Sin categoría',
                    'qty_sold': float(row[3]) if row[3] else 0,
                    'total_sales': float(row[4]) if row[4] else 0,
                    'unique_customers': int(row[5]) if row[5] else 0,
                    'total_invoices': int(row[6]) if row[6] else 0,
                    'avg_price': float(row[7]) if row[7] else 0
                } for row in product_analysis]
            
        except Exception as e:
            logger.warning(f"Product date filtering failed, using fallback approach: {e}")
            try:
                cursor.execute('''
                    SELECT 
                        "item_id",
                        "item_description",
                        "tipo" as type,
                        SUM("qty") as total_qty_sold,
                        SUM("qty" * "unit_price") as total_sales,
                        COUNT(DISTINCT "customer_id") as unique_customers,
                        COUNT(DISTINCT "invoice_cm_") as total_invoices,
                        AVG("unit_price") as avg_price
                    FROM (
                        SELECT *
                        FROM public."vista_ventas_con_tipo_por_desc"
                        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                        AND "item_id" IS NOT NULL AND "item_description" IS NOT NULL
                        AND "date" IS NOT NULL
                        ORDER BY "invoice_cm_" DESC
                        LIMIT CASE 
                            WHEN %s = 1 THEN 5000
                            WHEN %s = 3 THEN 15000  
                            WHEN %s = 6 THEN 30000
                            WHEN %s = 12 THEN 60000
                            ELSE 200000
                        END
                    ) recent_data
                    GROUP BY "item_id", "item_description", "tipo"
                    ORDER BY total_sales DESC
                    LIMIT 30
                ''', [date_months, date_months, date_months, date_months])
                product_analysis = cursor.fetchall()
                
                if product_analysis:
                    analytics['product_analysis'] = [{
                        'item_id': row[0],
                        'description': row[1],
                        'type': row[2] or 'Sin categoría',
                        'qty_sold': float(row[3]) if row[3] else 0,
                        'total_sales': float(row[4]) if row[4] else 0,
                        'unique_customers': int(row[5]) if row[5] else 0,
                        'total_invoices': int(row[6]) if row[6] else 0,
                        'avg_price': float(row[7]) if row[7] else 0
                    } for row in product_analysis]
            except Exception as e2:
                logger.error(f"Both product analysis attempts failed: {e2}")
        
        # 2. Category Performance Analysis
        try:
            category_query = f'''
                SELECT 
                    "tipo",
                    COUNT(DISTINCT "item_id") as unique_products,
                    SUM("qty") as total_qty_sold,
                    SUM("qty" * "unit_price") as total_sales,
                    COUNT(DISTINCT "customer_id") as unique_customers,
                    AVG("qty" * "unit_price") as avg_line_value
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                AND "tipo" IS NOT NULL
                AND "date" IS NOT NULL
                {date_filter_condition}
                GROUP BY "tipo"
                ORDER BY total_sales DESC
            '''
            
            cursor.execute(category_query)
            category_performance = cursor.fetchall()
            
            if category_performance:
                analytics['category_performance'] = [{
                    'category': row[0] or 'Sin categoría',
                    'unique_products': int(row[1]) if row[1] else 0,
                    'total_qty_sold': float(row[2]) if row[2] else 0,
                    'total_sales': float(row[3]) if row[3] else 0,
                    'unique_customers': int(row[4]) if row[4] else 0,
                    'avg_line_value': float(row[5]) if row[5] else 0
                } for row in category_performance]
            
        except Exception as e:
            logger.warning(f"Category date filtering failed, using fallback approach: {e}")
            try:
                cursor.execute('''
                    SELECT 
                        "tipo",
                        COUNT(DISTINCT "item_id") as unique_products,
                        SUM("qty") as total_qty_sold,
                        SUM("qty" * "unit_price") as total_sales,
                        COUNT(DISTINCT "customer_id") as unique_customers,
                        AVG("qty" * "unit_price") as avg_line_value
                    FROM (
                        SELECT *
                        FROM public."vista_ventas_con_tipo_por_desc"
                        WHERE "qty" IS NOT NULL 
                        AND "unit_price" IS NOT NULL
                        AND "tipo" IS NOT NULL
                        AND "date" IS NOT NULL
                        ORDER BY "invoice_cm_" DESC
                        LIMIT CASE 
                            WHEN %s = 1 THEN 5000
                            WHEN %s = 3 THEN 15000  
                            WHEN %s = 6 THEN 30000
                            WHEN %s = 12 THEN 60000
                            ELSE 200000
                        END
                    ) recent_data
                    GROUP BY "tipo"
                    ORDER BY total_sales DESC
                ''', [date_months, date_months, date_months, date_months])
                category_performance = cursor.fetchall()
                
                if category_performance:
                    analytics['category_performance'] = [{
                        'category': row[0] or 'Sin categoría',
                        'unique_products': int(row[1]) if row[1] else 0,
                        'total_qty_sold': float(row[2]) if row[2] else 0,
                        'total_sales': float(row[3]) if row[3] else 0,
                        'unique_customers': int(row[4]) if row[4] else 0,
                        'avg_line_value': float(row[5]) if row[5] else 0
                    } for row in category_performance]
            except Exception as e2:
                logger.error(f"Both category analysis attempts failed: {e2}")
        
        # 3. Sales Performance by Vendor
        try:
            vendor_query = f'''
                SELECT 
                    "vendedor",
                    COUNT(DISTINCT "customer_id") as unique_customers,
                    COUNT(DISTINCT "invoice_cm_") as total_invoices,
                    SUM("qty" * "unit_price") as total_sales,
                    AVG("qty" * "unit_price") as avg_line_value,
                    COUNT(*) as total_line_items
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                AND "vendedor" IS NOT NULL
                AND "date" IS NOT NULL
                {date_filter_condition}
                GROUP BY "vendedor"
                ORDER BY total_sales DESC
            '''
            
            cursor.execute(vendor_query)
            vendor_performance = cursor.fetchall()
            
            if vendor_performance:
                analytics['vendor_performance'] = [{
                    'vendor': row[0] or 'Sin vendedor',
                    'unique_customers': int(row[1]) if row[1] else 0,
                    'total_invoices': int(row[2]) if row[2] else 0,
                    'total_sales': float(row[3]) if row[3] else 0,
                    'avg_line_value': float(row[4]) if row[4] else 0,
                    'total_lines': int(row[5]) if row[5] else 0
                } for row in vendor_performance]
            
        except Exception as e:
            logger.warning(f"Vendor date filtering failed, using fallback approach: {e}")
            try:
                cursor.execute('''
                    SELECT 
                        "vendedor",
                        COUNT(DISTINCT "customer_id") as unique_customers,
                        COUNT(DISTINCT "invoice_cm_") as total_invoices,
                        SUM("qty" * "unit_price") as total_sales,
                        AVG("qty" * "unit_price") as avg_line_value,
                        COUNT(*) as total_line_items
                    FROM (
                        SELECT *
                        FROM public."vista_ventas_con_tipo_por_desc"
                        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                        AND "vendedor" IS NOT NULL
                        AND "date" IS NOT NULL
                        ORDER BY "invoice_cm_" DESC
                        LIMIT CASE 
                            WHEN %s = 1 THEN 5000
                            WHEN %s = 3 THEN 15000  
                            WHEN %s = 6 THEN 30000
                            WHEN %s = 12 THEN 60000
                            ELSE 200000
                        END
                    ) recent_data
                    GROUP BY "vendedor"
                    ORDER BY total_sales DESC
                ''', [date_months, date_months, date_months, date_months])
                vendor_performance = cursor.fetchall()
                
                if vendor_performance:
                    analytics['vendor_performance'] = [{
                        'vendor': row[0] or 'Sin vendedor',
                        'unique_customers': int(row[1]) if row[1] else 0,
                        'total_invoices': int(row[2]) if row[2] else 0,
                        'total_sales': float(row[3]) if row[3] else 0,
                        'avg_line_value': float(row[4]) if row[4] else 0,
                        'total_lines': int(row[5]) if row[5] else 0
                    } for row in vendor_performance]
            except Exception as e2:
                logger.error(f"Both vendor analysis attempts failed: {e2}")
        
        # 4. Province Performance Analysis
        try:
            province_query = f'''
                SELECT 
                    "provincia",
                    COUNT(DISTINCT "customer_id") as unique_customers,
                    COUNT(DISTINCT "invoice_cm_") as total_invoices,
                    SUM("qty" * "unit_price") as total_sales,
                    AVG("qty" * "unit_price") as avg_line_value
                FROM public."vista_ventas_con_tipo_por_desc"
                WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                AND "provincia" IS NOT NULL
                AND "date" IS NOT NULL
                {date_filter_condition}
                GROUP BY "provincia"
                ORDER BY total_sales DESC
            '''
            
            cursor.execute(province_query)
            province_performance = cursor.fetchall()
            
            if province_performance:
                analytics['province_performance'] = [{
                    'province': row[0] or 'Sin provincia',
                    'unique_customers': int(row[1]) if row[1] else 0,
                    'total_invoices': int(row[2]) if row[2] else 0,
                    'total_sales': float(row[3]) if row[3] else 0,
                    'avg_line_value': float(row[4]) if row[4] else 0
                } for row in province_performance]
            
        except Exception as e:
            logger.warning(f"Province date filtering failed, using fallback approach: {e}")
            try:
                cursor.execute('''
                    SELECT 
                        "provincia",
                        COUNT(DISTINCT "customer_id") as unique_customers,
                        COUNT(DISTINCT "invoice_cm_") as total_invoices,
                        SUM("qty" * "unit_price") as total_sales,
                        AVG("qty" * "unit_price") as avg_line_value
                    FROM (
                        SELECT *
                        FROM public."vista_ventas_con_tipo_por_desc"
                        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
                        AND "provincia" IS NOT NULL
                        AND "date" IS NOT NULL
                        ORDER BY "invoice_cm_" DESC
                        LIMIT CASE 
                            WHEN %s = 1 THEN 5000
                            WHEN %s = 3 THEN 15000  
                            WHEN %s = 6 THEN 30000
                            WHEN %s = 12 THEN 60000
                            ELSE 200000
                        END
                    ) recent_data
                    GROUP BY "provincia"
                    ORDER BY total_sales DESC
                ''', [date_months, date_months, date_months, date_months])
                province_performance = cursor.fetchall()
                
                if province_performance:
                    analytics['province_performance'] = [{
                        'province': row[0] or 'Sin provincia',
                        'unique_customers': int(row[1]) if row[1] else 0,
                        'total_invoices': int(row[2]) if row[2] else 0,
                        'total_sales': float(row[3]) if row[3] else 0,
                        'avg_line_value': float(row[4]) if row[4] else 0
                    } for row in province_performance]
            except Exception as e2:
                logger.error(f"Both province analysis attempts failed: {e2}")
        
        # Update date range info
        analytics['date_range'] = {
            'months': date_months,
            'start_date': start_date.strftime("%d/%m/%y"),
            'end_date': end_date.strftime("%d/%m/%y")
        }
        
        cursor.close()
        conn.close()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error in sales analytics: {str(e)}")
        return {
            "error": str(e),
            "product_analysis": [],
            "vendor_performance": [],
            "category_performance": [],
            "province_performance": [],
            "date_range": {
                "months": date_months,
                "start_date": datetime.now().strftime("%d/%m/%y"),
                "end_date": datetime.now().strftime("%d/%m/%y")
            }
        }

def get_brand_specific_analytics(user_question):
    """Get analytics for specific brand queries"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return f"Error de conexión: {message}"
        
        cursor = conn.cursor()
        question_lower = user_question.lower()
        
        # Determine which brand is being asked about
        target_brand = None
        if any(brand in question_lower for brand in ['edo', 'laboratorios edo']):
            target_brand = 'Laboratorios EDO, S.A.S.'
            brand_filter = "edo"
        elif any(brand in question_lower for brand in ['chinfield', 'ach']):
            target_brand = 'CHINFIELD, S.A.'
            brand_filter = "ach"
        
        if not target_brand:
            return "No se pudo identificar la marca específica en la consulta."
        
        # Get top customers for this specific brand
        if any(keyword in question_lower for keyword in ['clientes', 'compradores', 'quien', 'quienes', 'más compraron']):
            customer_query = f'''
                WITH brand_sales AS (
                    SELECT 
                        v."customer_id",
                        v."name",
                        SUM(v."qty" * v."unit_price") as total_brand_sales,
                        COUNT(DISTINCT v."invoice_cm_") as invoices_count,
                        COUNT(DISTINCT v."item_id") as different_products,
                        SUM(v."qty") as total_qty,
                        MAX(v."date") as last_purchase,
                        MAX(v."provincia") as provincia
                    FROM public."vista_ventas_con_tipo_por_desc" v
                    INNER JOIN public."inventarioneuman" i ON v."item_id" = i."Item"
                    WHERE v."qty" IS NOT NULL AND v."unit_price" IS NOT NULL
                    AND i.marca = %s
                    GROUP BY v."customer_id", v."name"
                )
                SELECT 
                    customer_id,
                    name,
                    total_brand_sales,
                    invoices_count,
                    different_products,
                    total_qty,
                    last_purchase,
                    provincia
                FROM brand_sales
                ORDER BY total_brand_sales DESC
                LIMIT 10
            '''
            
            try:
                cursor.execute(customer_query, [target_brand])
                results = cursor.fetchall()
                
                if results:
                    response = f"Top clientes que más compraron productos de {target_brand}:\n\n"
                    for i, row in enumerate(results[:7], 1):  # Limit to 7 as requested
                        customer_id, name, total_sales, invoices, products, qty, last_purchase, provincia = row
                        response += f"{i}. **{name}** (ID: {customer_id})\n"
                        response += f"   - Total compras {target_brand}: ${total_sales:,.2f}\n"
                        response += f"   - Facturas: {invoices}, Productos diferentes: {products}\n"
                        response += f"   - Cantidad total: {qty} unidades\n"
                        response += f"   - Última compra: {last_purchase}, Provincia: {provincia}\n\n"
                    
                    cursor.close()
                    conn.close()
                    return response
                else:
                    cursor.close()
                    conn.close()
                    return f"No se encontraron ventas específicas para la marca {target_brand}."
                    
            except Exception as e:
                logger.warning(f"Brand-specific customer query failed: {e}")
                # Fallback: try with item_id pattern matching
                fallback_query = f'''
                    SELECT 
                        v."customer_id",
                        v."name",
                        SUM(v."qty" * v."unit_price") as total_brand_sales,
                        COUNT(DISTINCT v."invoice_cm_") as invoices_count,
                        COUNT(DISTINCT v."item_id") as different_products,
                        SUM(v."qty") as total_qty,
                        MAX(v."date") as last_purchase,
                        MAX(v."provincia") as provincia
                    FROM public."vista_ventas_con_tipo_por_desc" v
                    WHERE v."qty" IS NOT NULL AND v."unit_price" IS NOT NULL
                    AND LOWER(v."item_id") LIKE %s
                    GROUP BY v."customer_id", v."name"
                    ORDER BY total_brand_sales DESC
                    LIMIT 10
                '''
                
                cursor.execute(fallback_query, [f'%{brand_filter}%'])
                results = cursor.fetchall()
                
                if results:
                    response = f"Top clientes que más compraron productos de {target_brand} (basado en códigos de producto):\n\n"
                    for i, row in enumerate(results[:7], 1):
                        customer_id, name, total_sales, invoices, products, qty, last_purchase, provincia = row
                        response += f"{i}. **{name}** (ID: {customer_id})\n"
                        response += f"   - Total compras {target_brand}: ${total_sales:,.2f}\n"
                        response += f"   - Facturas: {invoices}, Productos diferentes: {products}\n"
                        response += f"   - Cantidad total: {qty} unidades\n"
                        response += f"   - Última compra: {last_purchase}, Provincia: {provincia}\n\n"
                    
                    cursor.close()
                    conn.close()
                    return response
                else:
                    cursor.close()
                    conn.close()
                    return f"No se encontraron ventas para productos con código que contenga '{brand_filter}'."
        
                cursor.close()
                conn.close()
                return f"Consulta de marca {target_brand} no completamente procesada."
                
            except Exception as e:
                logger.error(f"Error in brand-specific analytics: {str(e)}")
                return f"Error al analizar datos de marca: {str(e)}"
                
    except Exception as e:
        logger.error(f"Error in brand-specific analytics (outer): {str(e)}")
        return f"Error al procesar la consulta de marca: {str(e)}"

def get_product_name_analytics(user_question):
    """Get analytics for specific product name queries"""
    try:
        conn, message = get_db_connection()
        if not conn:
            return None, f"Error de conexión: {message}"
        
        cursor = conn.cursor()
        question_lower = user_question.lower()
        
        # Extract product name from question
        product_name = None
        edo_patterns = [
            r'edo\s+([a-zA-Z0-9-]+(?:\s+[x×]\s+\d+\s*(?:ml|g|mg|kg|l|cc))?)',
            r'edo\s+([^\s]+(?:\s+[x×]\s+\d+\s*(?:ml|g|mg|kg|l|cc))?)'
        ]
        
        for pattern in edo_patterns:
            match = re.search(pattern, question_lower)
            if match:
                product_name = match.group(1)
                break
        
        if not product_name:
            return None
        
        # Query for product analytics
        query = """
            SELECT 
                    v."item_id",
                    v."item_description",
                v."provincia",
                SUM(v."qty") as total_qty,
                    COUNT(DISTINCT v."invoice_cm_") as total_invoices,
                COUNT(DISTINCT v."customer_id") as unique_customers,
                SUM(v."qty" * v."unit_price") as total_sales,
                MAX(v."date") as last_sale
                FROM public."vista_ventas_con_tipo_por_desc" v
            WHERE v."qty" IS NOT NULL 
            AND v."unit_price" IS NOT NULL
                AND LOWER(v."item_description") LIKE %s
            GROUP BY v."item_id", v."item_description", v."provincia"
            ORDER BY total_qty DESC
        """
        
        cursor.execute(query, [f"%{product_name.upper()}%"])
        results = cursor.fetchall()
        
        if results:
            response = []
            for row in results:
                item_id, description, province, qty, invoices, customers, sales, last_sale = row
                response.append({
                    'item_id': item_id,
                    'description': description,
                    'province': province,
                    'total_qty': float(qty) if qty else 0,
                    'total_invoices': int(invoices) if invoices else 0,
                    'unique_customers': int(customers) if customers else 0,
                    'total_sales': float(sales) if sales else 0,
                    'last_sale': last_sale
                })
            
            # Format the response as text
            text_response = f"Análisis de ventas para {description}:\n\n"
            for data in response:
                text_response += f"En {data['province']}:\n"
                text_response += f"- Cantidad vendida: {data['total_qty']} unidades\n"
                text_response += f"- Facturas: {data['total_invoices']}\n"
                text_response += f"- Clientes únicos: {data['unique_customers']}\n"
                text_response += f"- Total ventas: ${data['total_sales']:,.2f}\n"
                text_response += f"- Última venta: {data['last_sale']}\n\n"
            
            cursor.close()
            conn.close()
            return text_response
        else:
            cursor.close()
            conn.close()
            return None
        
    except Exception as e:
        logger.error(f"Error in product name analytics: {str(e)}")
        return None

def load_sales_data_simple():
    """Load basic sales data from the view for testing"""
    try:
        conn, message = get_db_connection()
        if not conn:
            logger.error(f"Cannot connect to database: {message}")
            return None, message
        
        # Query using qty * unit_price to calculate totals
        query = '''
        SELECT 
            COUNT(*) as total_records,
            SUM("qty" * "unit_price") as total_ventas,
            COUNT(DISTINCT "invoice_cm_") as cantidad_facturas,
            COUNT(DISTINCT "customer_id") as cantidad_clientes
        FROM public."vista_ventas_con_tipo_por_desc"
        WHERE "qty" IS NOT NULL AND "unit_price" IS NOT NULL
        '''
        
        logger.info("Executing sales summary query with calculated totals...")
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            total_records, total_ventas, cantidad_facturas, cantidad_clientes = result
            ticket_promedio = total_ventas / cantidad_facturas if cantidad_facturas > 0 else 0
            
            logger.info(f"Loaded summary: {total_records} records, ${total_ventas} total sales")
            
            return {
                "total_records": total_records,
                "total_ventas": float(total_ventas or 0),
                "cantidad_facturas": int(cantidad_facturas or 0),
                "cantidad_clientes": int(cantidad_clientes or 0),
                "ticket_promedio": float(ticket_promedio)
            }, None
        else:
            return None, "No data returned from query"
        
    except Exception as e:
        error_msg = f"Error loading sales data: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

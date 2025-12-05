from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de MongoDB
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://admin:visitorguard2025@localhost:27017/visitorguard?authSource=admin')
DATABASE_NAME = 'visitorguard'

# Cliente de MongoDB (singleton)
_client: MongoClient = None
_database: Database = None

def get_mongodb_client() -> MongoClient:
    """Obtiene el cliente de MongoDB (singleton)"""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
    return _client

def get_database() -> Database:
    """Obtiene la base de datos de MongoDB"""
    global _database
    if _database is None:
        client = get_mongodb_client()
        _database = client[DATABASE_NAME]
    return _database

def get_collection(collection_name: str) -> Collection:
    """Obtiene una colección específica de MongoDB"""
    db = get_database()
    return db[collection_name]

def close_mongodb_connection():
    """Cierra la conexión a MongoDB"""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None

def init_db():
    """
    Inicializa la base de datos y crea índices necesarios
    """
    db = get_database()
    
    # Crear colecciones si no existen
    collections = db.list_collection_names()
    
    if 'visits' not in collections:
        db.create_collection('visits')
        # Crear índices para la colección visits
        visits_collection = db['visits']
        visits_collection.create_index('codigo', unique=True)
        visits_collection.create_index('id_usuario')
        visits_collection.create_index('id_persona')
        visits_collection.create_index('fecha_inicio')
        visits_collection.create_index('estatus')
        print("Colección 'visits' creada con índices")
    
    if 'users' not in collections:
        db.create_collection('users')
        users_collection = db['users']
        users_collection.create_index('username', unique=True)
        users_collection.create_index('email', unique=True)
        print("Colección 'users' creada con índices")
    
    print(f"Base de datos '{DATABASE_NAME}' inicializada correctamente")

# Para compatibilidad con código anterior (SQLAlchemy)
# Mantener estas funciones si se necesita transición gradual
def get_db():
    """Función de compatibilidad - devuelve la base de datos de MongoDB"""
    return get_database()
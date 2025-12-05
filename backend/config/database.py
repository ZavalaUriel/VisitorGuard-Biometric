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
    Inicializa la base de datos y elimina índices problemáticos
    """
    db = get_database()
    
    # Obtener colección visits
    visits_collection = db['visits']
    
    # Eliminar índice problemático 'codigo_1' si existe
    try:
        existing_indexes = visits_collection.index_information()
        if 'codigo_1' in existing_indexes:
            visits_collection.drop_index('codigo_1')
            print("✅ Índice 'codigo_1' eliminado")
    except Exception as e:
        print(f"⚠️ Error eliminando índice: {e}")
    
    # Asegurar que existe índice en _id (id_persona)
    try:
        # MongoDB ya tiene índice único en _id por defecto
        print("✅ Colección 'visits' configurada correctamente")
    except Exception as e:
        print(f"⚠️ Error configurando colección: {e}")
    
    print(f"✅ Base de datos '{DATABASE_NAME}' inicializada correctamente")

# Para compatibilidad con código anterior (SQLAlchemy)
# Mantener estas funciones si se necesita transición gradual
def get_db():
    """Función de compatibilidad - devuelve la base de datos de MongoDB"""
    return get_database()
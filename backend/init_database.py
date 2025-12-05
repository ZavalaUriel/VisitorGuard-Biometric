#!/usr/bin/env python3
"""
Script de inicialización de la base de datos MongoDB
Crea las colecciones e índices necesarios
"""

from config.database import init_db, get_database, get_collection
from datetime import datetime
import sys

def create_sample_data():
    """Crea datos de ejemplo para probar la base de datos"""
    
    print("\n🔧 Creando datos de ejemplo...")
    
    # Obtener colecciones
    users_collection = get_collection('users')
    visits_collection = get_collection('visits')
    
    # Limpiar datos existentes (solo para pruebas)
    users_collection.delete_many({})
    visits_collection.delete_many({})
    
    # Crear usuario de ejemplo
    sample_user = {
        "name": "Usuario Demo",
        "email": "demo@visitorguard.com",
        "username": "demo_user",
        "phone": "+52 123 456 7890",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    user_result = users_collection.insert_one(sample_user)
    print(f"✅ Usuario creado con ID: {user_result.inserted_id}")
    
    # Crear visita de ejemplo (estructura simplificada con 3 campos)
    sample_visit = {
        "_id": "PERSON-001",  # id_persona como _id
        "nombre": "Juan Pérez García",
        "foto_path": None,  # Sin foto inicialmente
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

        "fecha_fin": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    visit_result = visits_collection.insert_one(sample_visit)
    print(f"✅ Visita creada con ID: {visit_result.inserted_id}")
    
    print("\n📊 Estadísticas:")
    print(f"   Total usuarios: {users_collection.count_documents({})}")
    print(f"   Total visitas: {visits_collection.count_documents({})}")

def verify_connection():
    """Verifica la conexión a MongoDB"""
    try:
        db = get_database()
        # Hacer ping a la base de datos
        db.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con MongoDB: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 VisitorGuard - Inicialización de Base de Datos MongoDB")
    print("=" * 60)
    
    # Verificar conexión
    print("\n🔍 Verificando conexión a MongoDB...")
    if not verify_connection():
        print("\n❌ No se pudo conectar a MongoDB. Verifica que:")
        print("   1. MongoDB esté corriendo (docker-compose up mongodb)")
        print("   2. Las credenciales sean correctas")
        print("   3. La variable MONGODB_URL esté configurada correctamente")
        sys.exit(1)
    
    # Inicializar base de datos
    print("\n🗄️  Inicializando base de datos...")
    try:
        init_db()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        sys.exit(1)
    
    # Preguntar si crear datos de ejemplo
    response = input("\n¿Deseas crear datos de ejemplo? (s/n): ").lower()
    if response == 's':
        try:
            create_sample_data()
        except Exception as e:
            print(f"❌ Error al crear datos de ejemplo: {e}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ Inicialización completada exitosamente")
    print("=" * 60)
    print("\n💡 Próximos pasos:")
    print("   1. Ejecuta el backend: python app.py")
    print("   2. O ejecuta con Docker: docker-compose up")
    print("   3. Accede a la API en: http://localhost:5000")
    print()

if __name__ == "__main__":
    main()

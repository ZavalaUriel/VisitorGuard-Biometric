#!/usr/bin/env python3
"""
Script de prueba para la API de visitas
Prueba todos los endpoints REST de visitas (con y sin imágenes)
"""

import requests
from datetime import datetime
import sys
import os
from PIL import Image
import io

BASE_URL = "http://localhost:5000/api"

def print_separator():
    print("\n" + "="*70)

def print_result(title, response):
    print(f"\n{title}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")

def test_health_check():
    """Probar health check"""
    print_separator()
    print("🔍 TEST 1: Health Check")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/health")
    print_result("Health Check Result:", response)
    return response.status_code == 200

def create_test_image():
    """Crear una imagen de prueba"""
    img = Image.new('RGB', (200, 200), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_create_visit():
    """Probar creación de visita con imagen"""
    print_separator()
    print("📝 TEST 2: Crear Nueva Visita (CON IMAGEN)")
    print_separator()
    
    visit_data = {
        "motivo_visita": "Reunión de prueba API",
        "codigo": f"VIS-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "id_usuario": "USER-TEST-001",
        "id_persona": "PERSON-TEST-001",
        "id_tipo_pase": "TEMPORAL",
        "id_area": "AREA-PRUEBAS",
        "fecha_inicio": datetime.now().isoformat(),
        "comentario": "Esta es una visita de prueba de la API REST con imagen"
    }
    
    # Crear imagen de prueba
    test_image = create_test_image()
    files = {'foto': ('test_image.jpg', test_image, 'image/jpeg')}
    
    print(f"Datos enviados: {visit_data}")
    print("📷 Incluyendo imagen de prueba...")
    
    response = requests.post(f"{BASE_URL}/visits", data=visit_data, files=files)
    print_result("Crear Visita con Imagen Result:", response)
    
    if response.status_code == 201:
        result = response.json()
        visit_id = result.get('visit_id')
        codigo = visit_data['codigo']
        foto_path = result.get('foto_path')
        print(f"\n✅ Imagen guardada en: {foto_path}")
        return visit_id, codigo
    return None, None

def test_get_all_visits():
    """Probar obtener todas las visitas"""
    print_separator()
    print("📋 TEST 3: Obtener Todas las Visitas")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits?limit=5")
    print_result("Listar Visitas Result:", response)
    return response.status_code == 200

def test_get_visit_by_id(visit_id):
    """Probar obtener visita por ID"""
    print_separator()
    print(f"🔍 TEST 4: Obtener Visita por ID ({visit_id})")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/{visit_id}")
    print_result("Obtener Visita por ID Result:", response)
    return response.status_code == 200

def test_get_visit_by_code(codigo):
    """Probar obtener visita por código"""
    print_separator()
    print(f"🔢 TEST 5: Obtener Visita por Código ({codigo})")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/codigo/{codigo}")
    print_result("Obtener Visita por Código Result:", response)
    return response.status_code == 200

def test_update_visit(visit_id):
    """Probar actualizar visita con nueva imagen"""
    print_separator()
    print(f"✏️  TEST 6: Actualizar Visita con Nueva Imagen ({visit_id})")
    print_separator()
    
    update_data = {
        "comentario": "Comentario actualizado desde el script de prueba",
        "estatus": "Activa"
    }
    
    # Crear nueva imagen de prueba
    test_image = create_test_image()
    files = {'foto': ('updated_image.jpg', test_image, 'image/jpeg')}
    
    print(f"Datos a actualizar: {update_data}")
    print("📷 Incluyendo nueva imagen...")
    
    response = requests.put(f"{BASE_URL}/visits/{visit_id}", data=update_data, files=files)
    print_result("Actualizar Visita Result:", response)
    
    if response.status_code == 200:
        result = response.json()
        foto_path = result.get('foto_path')
        if foto_path:
            print(f"\n✅ Nueva imagen guardada en: {foto_path}")
    
    return response.status_code == 200

def test_get_visits_by_status():
    """Probar obtener visitas por estatus"""
    print_separator()
    print("🔎 TEST 7: Obtener Visitas por Estatus (Activa)")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/estatus/Activa")
    print_result("Obtener Visitas Activas Result:", response)
    return response.status_code == 200

def test_get_visits_by_user():
    """Probar obtener visitas por usuario"""
    print_separator()
    print("👤 TEST 8: Obtener Visitas por Usuario (USER-TEST-001)")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/usuario/USER-TEST-001")
    print_result("Obtener Visitas por Usuario Result:", response)
    return response.status_code == 200

def test_finalize_visit(visit_id):
    """Probar finalizar visita"""
    print_separator()
    print(f"🏁 TEST 9: Finalizar Visita ({visit_id})")
    print_separator()
    
    response = requests.post(f"{BASE_URL}/visits/{visit_id}/finalizar")
    print_result("Finalizar Visita Result:", response)
    return response.status_code == 200

def test_get_visit_photo(visit_id):
    """Probar obtener foto de visita por ID"""
    print_separator()
    print(f"📷 TEST 10: Obtener Foto por ID ({visit_id})")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/{visit_id}/foto")
    
    if response.status_code == 200:
        print(f"\n✅ Foto obtenida exitosamente")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Tamaño: {len(response.content)} bytes")
        
        # Guardar foto temporalmente
        temp_file = f"test_downloaded_{visit_id}.jpg"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        print(f"   Guardada temporalmente en: {temp_file}")
        
        # Limpiar
        try:
            os.remove(temp_file)
            print(f"   Archivo temporal eliminado")
        except:
            pass
        
        return True
    else:
        print_result("Obtener Foto Result:", response)
        return False

def test_get_visit_photo_by_code(codigo):
    """Probar obtener foto de visita por código"""
    print_separator()
    print(f"📷 TEST 11: Obtener Foto por Código ({codigo})")
    print_separator()
    
    response = requests.get(f"{BASE_URL}/visits/codigo/{codigo}/foto")
    
    if response.status_code == 200:
        print(f"\n✅ Foto obtenida exitosamente por código")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Tamaño: {len(response.content)} bytes")
        return True
    else:
        print_result("Obtener Foto por Código Result:", response)
        return False

def test_delete_visit(visit_id):
    """Probar eliminar visita"""
    print_separator()
    print(f"🗑️  TEST 12: Eliminar Visita ({visit_id})")
    print_separator()
    
    response = input(f"\n⚠️  ¿Deseas eliminar la visita de prueba? (s/n): ").lower()
    if response == 's':
        response = requests.delete(f"{BASE_URL}/visits/{visit_id}")
        print_result("Eliminar Visita Result:", response)
        return response.status_code == 200
    else:
        print("❌ Eliminación cancelada por el usuario")
        return True

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("🚀 VisitorGuard - Pruebas de API de Visitas")
    print("="*70)
    print("\n💡 Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Servidor respondiendo correctamente")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: No se puede conectar al servidor en {BASE_URL}")
        print("   Verifica que el servidor esté corriendo:")
        print("   - Con Docker: docker-compose up")
        print("   - Local: cd backend && python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
    
    results = []
    visit_id = None
    codigo = None
    
    try:
        # Test 1: Health Check
        results.append(("Health Check", test_health_check()))
        
        # Test 2: Crear visita
        visit_id, codigo = test_create_visit()
        results.append(("Crear Visita", visit_id is not None))
        
        if not visit_id:
            print("\n❌ No se pudo crear la visita. Deteniendo pruebas.")
            sys.exit(1)
        
        # Test 3: Listar visitas
        results.append(("Listar Visitas", test_get_all_visits()))
        
        # Test 4: Obtener por ID
        results.append(("Obtener por ID", test_get_visit_by_id(visit_id)))
        
        # Test 5: Obtener por código
        results.append(("Obtener por Código", test_get_visit_by_code(codigo)))
        
        # Test 6: Actualizar visita
        results.append(("Actualizar Visita", test_update_visit(visit_id)))
        
        # Test 7: Filtrar por estatus
        results.append(("Filtrar por Estatus", test_get_visits_by_status()))
        
        # Test 8: Filtrar por usuario
        results.append(("Filtrar por Usuario", test_get_visits_by_user()))
        
        # Test 9: Finalizar visita
        results.append(("Finalizar Visita", test_finalize_visit(visit_id)))
        
        # Test 10: Obtener foto por ID
        results.append(("Obtener Foto por ID", test_get_visit_photo(visit_id)))
        
        # Test 11: Obtener foto por código
        results.append(("Obtener Foto por Código", test_get_visit_photo_by_code(codigo)))
        
        # Test 12: Eliminar visita (opcional)
        results.append(("Eliminar Visita", test_delete_visit(visit_id)))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Resumen de resultados
    print_separator()
    print("📊 RESUMEN DE PRUEBAS")
    print_separator()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{'Test':<30} {'Resultado':<10}")
    print("-" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status:<10}")
    
    print("-" * 40)
    print(f"Total: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")
    
    print_separator()
    print("\n💡 Información de la visita de prueba:")
    print(f"   ID: {visit_id}")
    print(f"   Código: {codigo}")
    print("\n📚 Ver más en: API_VISITS.md")
    print()

if __name__ == "__main__":
    main()

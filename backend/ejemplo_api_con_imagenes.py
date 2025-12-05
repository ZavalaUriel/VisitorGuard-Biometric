#!/usr/bin/env python3
"""
Ejemplo completo de uso de la API de visitas con imágenes
Muestra cómo crear, actualizar y obtener visitas con fotos desde otro servidor
"""

import requests
from datetime import datetime
import os

# URL base de la API
BASE_URL = "http://localhost:5000/api"

def ejemplo_1_crear_visita_con_imagen():
    """
    Ejemplo 1: Crear una visita con imagen
    """
    print("\n" + "="*70)
    print("📝 EJEMPLO 1: Crear Visita con Imagen")
    print("="*70)
    
    # Datos de la visita (solo 3 campos)
    visit_data = {
        "id_persona": f"PERSON-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "nombre": "Juan Pérez García"
    }
    
    # Ruta de la imagen (ajusta según tu archivo)
    image_path = "foto_visitante.jpg"
    
    # Si no existe la imagen, crear una de prueba
    if not os.path.exists(image_path):
        from PIL import Image
        img = Image.new('RGB', (400, 400), color='blue')
        img.save(image_path)
        print(f"✅ Imagen de prueba creada: {image_path}")
    
    # Enviar datos con imagen
    with open(image_path, 'rb') as foto:
        files = {'foto': foto}
        response = requests.post(f"{BASE_URL}/visits", data=visit_data, files=files)
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✅ Visita creada exitosamente")
        print(f"   ID Persona: {result['id_persona']}")
        print(f"   Nombre: {visit_data['nombre']}")
        print(f"   Foto guardada en: {result.get('foto_path')}")
        return result['id_persona']
    else:
        print(f"\n❌ Error: {response.json()}")
        return None

def ejemplo_2_obtener_visita_y_foto(id_persona):
    """
    Ejemplo 2: Obtener datos de la visita y su foto
    """
    print("\n" + "="*70)
    print(f"🔍 EJEMPLO 2: Obtener Visita y Foto (ID Persona: {id_persona})")
    print("="*70)
    
    # Obtener datos de la visita
    response = requests.get(f"{BASE_URL}/visits/{id_persona}")
    
    if response.status_code == 200:
        visit = response.json()['visit']
        print(f"\n✅ Visita encontrada:")
        print(f"   ID Persona: {visit['id_persona']}")
        print(f"   Nombre: {visit['nombre']}")
        print(f"   Foto path: {visit.get('foto_path')}")
        print(f"   Creada: {visit.get('created_at')}")
        
        # Obtener la foto
        foto_response = requests.get(f"{BASE_URL}/visits/{id_persona}/foto")
        
        if foto_response.status_code == 200:
            # Guardar foto descargada
            output_file = f"foto_descargada_{id_persona}.jpg"
            with open(output_file, 'wb') as f:
                f.write(foto_response.content)
            print(f"\n✅ Foto descargada: {output_file}")
            print(f"   Tamaño: {len(foto_response.content)} bytes")
            return output_file
        else:
            print(f"\n⚠️  No se pudo obtener la foto")
    else:
        print(f"\n❌ Error: {response.json()}")
    
    return None

def ejemplo_3_actualizar_visita_con_nueva_imagen(id_persona):
    """
    Ejemplo 3: Actualizar visita con nueva imagen
    """
    print("\n" + "="*70)
    print(f"✏️  EJEMPLO 3: Actualizar Visita con Nueva Imagen (ID: {visit_id})")
    print("="*70)
    
    # Datos a actualizar
    print("\n" + "="*70)
    print(f"🔄 EJEMPLO 3: Actualizar Visita (ID Persona: {id_persona})")
    print("="*70)
    
    # Actualizar solo el nombre
    update_data = {
        "nombre": "Juan Pérez González - Actualizado"
    }
    
    # Nueva imagen (crear una diferente)
    new_image_path = "foto_actualizada.jpg"
    if not os.path.exists(new_image_path):
        from PIL import Image
        img = Image.new('RGB', (400, 400), color='red')
        img.save(new_image_path)
        print(f"✅ Nueva imagen creada: {new_image_path}")
    
    # Enviar actualización con nueva imagen
    with open(new_image_path, 'rb') as foto:
        files = {'foto': foto}
        response = requests.put(f"{BASE_URL}/visits/{id_persona}", data=update_data, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Visita actualizada exitosamente")
        print(f"   Nueva foto guardada en: {result.get('foto_path')}")
    else:
        print(f"\n❌ Error: {response.json()}")

def ejemplo_4_buscar_por_nombre(nombre):
    """
    Ejemplo 4: Buscar visitas por nombre
    """
    print("\n" + "="*70)
    print(f"🔍 EJEMPLO 4: Buscar por Nombre ({nombre})")
    print("="*70)
    
    # Buscar por nombre
    response = requests.get(f"{BASE_URL}/visits/search/{nombre}")
    
    if response.status_code == 200:
        visits = response.json()['visits']
        print(f"\n✅ Resultados encontrados: {len(visits)}")
        
        for visit in visits:
            print(f"\n   ID Persona: {visit['id_persona']}")
            print(f"   Nombre: {visit['nombre']}")
            print(f"   Foto: {visit.get('foto_path', 'Sin foto')}")
            print(f"   URL foto: {BASE_URL}/visits/{visit['id_persona']}/foto")
    else:
        print(f"\n❌ Error: {response.json()}")

def ejemplo_5_listar_visitas_con_fotos():
    """
    Ejemplo 5: Listar todas las visitas y mostrar cuáles tienen foto
    """
    print("\n" + "="*70)
    print("📋 EJEMPLO 5: Listar Visitas con Fotos")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/visits?limit=10")
    
    if response.status_code == 200:
        visits = response.json()['visits']
        print(f"\n✅ Total de visitas: {len(visits)}")
        
        print("\nVisitas encontradas:")
        for visit in visits:
            print(f"\n   ID Persona: {visit['id_persona']}")
            print(f"   Nombre: {visit['nombre']}")
            if visit.get('foto_path'):
                print(f"   Foto: ✅ Disponible")
                print(f"   URL: {BASE_URL}/visits/{visit['id_persona']}/foto")
            else:
                print(f"   Foto: ❌ Sin foto")
    else:
        print(f"\n❌ Error: {response.json()}")

def ejemplo_6_eliminar_visita(id_persona):
    """
    Ejemplo 6: Eliminar una visita
    """
    print("\n" + "="*70)
    print(f"🗑️  EJEMPLO 6: Eliminar Visita (ID Persona: {id_persona})")
    print("="*70)
    
    response = requests.delete(f"{BASE_URL}/visits/{id_persona}")
    
    if response.status_code == 200:
        print(f"\n✅ Visita eliminada exitosamente")
    else:
        print(f"\n❌ Error: {response.json()}")

def limpiar_archivos_temporales():
    """Limpiar archivos de prueba"""
    archivos = [
        "foto_visitante.jpg",
        "foto_actualizada.jpg"
    ]
    
    for archivo in archivos:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
        except:
            pass

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🚀 Ejemplos de API de Visitas con Imágenes")
    print("   Consumo desde Otro Servidor")
    print("="*70)
    
    print("\n💡 Este script muestra cómo consumir la API desde otro servidor")
    print("   incluyendo el envío y obtención de imágenes.")
    print("   La estructura simplificada usa solo 3 campos:")
    print("   - id_persona (proporcionado por el cliente)")
    print("   - nombre")
    print("   - foto")
    
    try:
        # Verificar que el servidor esté corriendo
        response = requests.get(f"http://localhost:5000/health", timeout=5)
        print(f"\n✅ Servidor activo: {response.json()['service']}")
    except:
        print(f"\n❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo.")
        return
    
    try:
        # Ejemplo 1: Crear visita con imagen
        id_persona = ejemplo_1_crear_visita_con_imagen()
        
        if not id_persona:
            print("\n❌ No se pudo crear la visita. Terminando ejemplos.")
            return
        
        # Ejemplo 2: Obtener visita y su foto
        ejemplo_2_obtener_visita_y_foto(id_persona)
        
        # Ejemplo 3: Actualizar con nueva imagen
        ejemplo_3_actualizar_visita_con_nueva_imagen(id_persona)
        
        # Ejemplo 4: Buscar por nombre
        ejemplo_4_buscar_por_nombre("Juan")
        
        # Ejemplo 5: Listar visitas con fotos
        ejemplo_5_listar_visitas_con_fotos()
        
        # Ejemplo 6: Eliminar visita (opcional)
        respuesta = input("\n❓ ¿Deseas eliminar la visita de prueba? (s/n): ").lower()
        if respuesta == 's':
            ejemplo_6_eliminar_visita(id_persona)
        
        print("\n" + "="*70)
        print("✨ Todos los ejemplos completados")
        print("="*70)
        
        print(f"\n💾 Información de la visita creada:")
        print(f"   ID Persona: {id_persona}")
        print(f"\n🌐 URLs útiles para tu frontend:")
        print(f"   Datos: GET {BASE_URL}/visits/{id_persona}")
        print(f"   Foto: GET {BASE_URL}/visits/{id_persona}/foto")
        print(f"   Buscar: GET {BASE_URL}/visits/search/nombre")
        
        # Preguntar si limpiar archivos
        respuesta = input("\n🗑️  ¿Deseas limpiar los archivos de prueba? (s/n): ").lower()
        if respuesta == 's':
            limpiar_archivos_temporales()
            print("✅ Archivos temporales eliminados")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

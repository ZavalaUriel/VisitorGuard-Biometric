# /backend/tests/test_facial_recognition.py

import os
import sys
# Añadir la carpeta backend al path para importar el módulo
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from recognition.facial_manager import verify_face 

# Define las rutas de las imágenes de prueba (Asegúrate de tenerlas)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
REFERENCE_IMG = os.path.join(BASE_PATH, 'test_reference.jpg')
CAMERA_IMG = os.path.join(BASE_PATH, 'test_camera.jpg')
STRANGER_IMG = os.path.join(BASE_PATH, 'test_stranger.jpg')

print("--- Prueba de Coincidencia (Misma Persona) ---")
# Debe retornar 'verified': True
result_same = verify_face(CAMERA_IMG, REFERENCE_IMG)
print(f"Resultado: {result_same['verified']}") 
print("-" * 40)

print("--- Prueba de No Coincidencia (Persona Diferente) ---")
# Debe retornar 'verified': False
result_different = verify_face(CAMERA_IMG, STRANGER_IMG)
print(f"Resultado: {result_different['verified']}")
print("-" * 40)

if result_same['verified'] and not result_different['verified']:
    print("✅ PRUEBA HU3 EXITOSA: La verificación facial funciona correctamente.")
else:
    print("❌ PRUEBA HU3 FALLIDA: Revisa las imágenes y la configuración de DeepFace.")
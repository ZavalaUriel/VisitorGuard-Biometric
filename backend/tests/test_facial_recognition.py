import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from recognition.facial_manager import verify_faces

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
REFERENCE_IMG = os.path.join(BASE_PATH, 'test_reference.jpg')
CAMERA_IMG = os.path.join(BASE_PATH, 'test_camera.jpg')
STRANGER_IMG = os.path.join(BASE_PATH, 'test_stranger.jpg')

def test_same_person():
    """Test: Verificar que dos fotos de la misma persona coincidan"""
    if not os.path.exists(REFERENCE_IMG) or not os.path.exists(CAMERA_IMG):
        print("⚠️ Imágenes de prueba no encontradas, saltando test")
        return
    
    result = verify_faces(REFERENCE_IMG, CAMERA_IMG)
    print(f"--- Test Misma Persona ---")
    print(f"Resultado: {result}")
    assert result is not None
    assert result.get('verified') == True

def test_different_person():
    """Test: Verificar que dos fotos de diferentes personas NO coincidan"""
    if not os.path.exists(CAMERA_IMG) or not os.path.exists(STRANGER_IMG):
        print("⚠️ Imágenes de prueba no encontradas, saltando test")
        return
    
    result = verify_faces(CAMERA_IMG, STRANGER_IMG)
    print(f"--- Test Diferente Persona ---")
    print(f"Resultado: {result}")
    assert result is not None
    assert result.get('verified') == False
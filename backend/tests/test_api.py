import requests
import os
import pytest

API_URL = "http://localhost:5000"

def test_health():
    """Test del endpoint de salud"""
    print("🔍 Probando endpoint de salud...")
    response = requests.get(f"{API_URL}/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    print("✅ Health check passed")

# Este test requiere que el servidor esté corriendo y que tengas imágenes de prueba
# Por ahora lo marcamos como skip
@pytest.mark.skip(reason="Requiere imágenes de prueba y servidor corriendo")
def test_verify_face_with_images():
    """Test de verificación facial - requiere imágenes"""
    ref_image_path = "path/to/reference.jpg"
    ver_image_path = "path/to/verification.jpg"
    
    if not os.path.exists(ref_image_path) or not os.path.exists(ver_image_path):
        pytest.skip("Imágenes de prueba no disponibles")
    
    files = {
        'reference_image': open(ref_image_path, 'rb'),
        'verification_image': open(ver_image_path, 'rb')
    }
    
    try:
        response = requests.post(f"{API_URL}/api/verify-face", files=files)
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            result = response.json()
            assert 'verified' in result
            assert 'distance' in result
            print(f"✅ Verificación: {result.get('verified')}")
    finally:
        files['reference_image'].close()
        files['verification_image'].close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBAS DE API - VISITORGUARD BIOMETRIC")
    print("=" * 60)
    print()
    
    # Para ejecutar manualmente sin pytest
    try:
        response = requests.get(f"{API_URL}/api/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            print(f"   {response.json()}")
        else:
            print(f"❌ Servidor no responde: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("   Asegúrate de que el servidor esté corriendo: python backend/app.py")
    
    
    print("📝 Para probar verificación facial, proporciona dos imágenes:")
    print("   - test_verify_face('ruta/imagen1.jpg', 'ruta/imagen2.jpg')")
    print()
    print("Ejemplo:")
    print("   test_verify_face('temp/person1.jpg', 'temp/person1_2.jpg')")
    print()

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv

from services.visit_service import VisitService
from config.database import init_db
from recognition.facial_manager import verify_faces, generate_vector, compare_embeddings

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max para imágenes

CORS(app, resources={r"/api/*": {"origins": "*"}})

TEMP_FOLDER = 'temp'
UPLOADS_FOLDER = 'uploads/visits'
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

with app.app_context():
    init_db()

# ==================== ENDPOINTS PRINCIPALES ====================

@app.route('/', methods=['GET'])
def index():
    """Ruta raíz - Información de la API"""
    return jsonify({
        'service': 'VisitorGuard Biometric API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'visits': '/api/visits',
            'face_recognition': '/api/face-recognition/verify'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'VisitorGuard Biometric API'
    })

# ==================== CRUD DE VISITAS ====================

@app.route('/api/visits', methods=['POST'])
def create_visit():
    """
    Crear o actualizar una visita
    Campos: id_persona (requerido), nombre (requerido), foto (opcional)
    """
    try:
        id_persona = request.form.get('id_persona')
        nombre = request.form.get('nombre')
        
        if not id_persona or not nombre:
            return jsonify({'error': 'id_persona and nombre are required'}), 400
        
        foto_path = None
        
        # Procesar foto si existe
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                # Generar nombre único para la foto
                file_ext = os.path.splitext(foto.filename)[1]
                filename = f"{id_persona}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                foto_path = os.path.join(UPLOADS_FOLDER, filename)
                foto.save(foto_path)
        
        # Crear/actualizar visita
        visit_service = VisitService()
        visit_data = {
            'id_persona': id_persona,
            'nombre': nombre,
            'foto_path': foto_path
        }
        
        visit_id = visit_service.create_visit(visit_data)
        
        return jsonify({
            'success': True,
            'message': 'Visit created/updated successfully',
            'id_persona': visit_id,
            'nombre': nombre,
            'foto_path': foto_path
        }), 201
    
    except Exception as e:
        # Limpiar foto si hubo error
        if foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits', methods=['GET'])
def get_all_visits():
    """Obtener todas las visitas"""
    try:
        visit_service = VisitService()
        visits = visit_service.get_all_visits()
        
        return jsonify({
            'success': True,
            'count': len(visits),
            'visits': visits
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['GET'])
def get_visit(id_persona):
    """Obtener una visita por ID"""
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        return jsonify(visit), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['PUT'])
def update_visit(id_persona):
    """Actualizar una visita existente"""
    try:
        visit_service = VisitService()
        
        # Verificar que existe
        existing_visit = visit_service.get_visit_by_id(id_persona)
        if not existing_visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        update_data = {}
        
        # Actualizar nombre si se proporciona
        if 'nombre' in request.form:
            update_data['nombre'] = request.form['nombre']
        
        # Actualizar foto si se proporciona
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                # Eliminar foto anterior si existe
                if existing_visit.get('foto_path') and os.path.exists(existing_visit['foto_path']):
                    os.remove(existing_visit['foto_path'])
                
                # Guardar nueva foto
                file_ext = os.path.splitext(foto.filename)[1]
                filename = f"{id_persona}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                foto_path = os.path.join(UPLOADS_FOLDER, filename)
                foto.save(foto_path)
                update_data['foto_path'] = foto_path
        
        if not update_data:
            return jsonify({'error': 'No data to update'}), 400
        
        success = visit_service.update_visit(id_persona, update_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Visit updated successfully',
                'id_persona': id_persona
            }), 200
        else:
            return jsonify({'error': 'Update failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['DELETE'])
def delete_visit(id_persona):
    """Eliminar una visita"""
    try:
        visit_service = VisitService()
        
        # Obtener la visita antes de eliminar para borrar la foto
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        # Eliminar foto si existe
        if visit.get('foto_path') and os.path.exists(visit['foto_path']):
            os.remove(visit['foto_path'])
        
        # Eliminar de la base de datos
        success = visit_service.delete_visit(id_persona)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Visit deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Delete failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>/foto', methods=['GET'])
def get_visit_photo(id_persona):
    """Descargar la foto de una visita"""
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        foto_path = visit.get('foto_path')
        
        if not foto_path or not os.path.exists(foto_path):
            return jsonify({'error': 'Photo not found'}), 404
        
        return send_file(foto_path, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/search/<nombre>', methods=['GET'])
def search_visits(nombre):
    """Buscar visitas por nombre"""
    try:
        visit_service = VisitService()
        visits = visit_service.search_by_name(nombre)
        
        return jsonify({
            'success': True,
            'count': len(visits),
            'visits': visits
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>/landmarks', methods=['GET'])
def get_visit_landmarks(id_persona):
    """
    Obtener los landmarks faciales de una visita específica
    Retorna datos biométricos y coordenadas faciales guardadas
    """
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        if not visit.get('landmarks'):
            return jsonify({
                'error': 'No landmarks available for this visit',
                'message': 'The visit exists but facial landmarks were not extracted'
            }), 404
        
        return jsonify({
            'success': True,
            'id_persona': visit['id_persona'],
            'nombre': visit['nombre'],
            'landmarks': visit['landmarks'],
            'biometric_data': visit['landmarks'].get('biometric_data', {}),
            'facial_area': visit['landmarks'].get('facial_area', {}),
            'has_embedding': visit.get('embedding') is not None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== RECONOCIMIENTO FACIAL ====================

@app.route('/api/face-recognition/verify', methods=['POST'])
def verify_face_recognition():
    """
    Endpoint para reconocimiento facial OPTIMIZADO con análisis de landmarks
    Compara embeddings y extrae landmarks faciales
    Mucho más rápido que la comparación de imágenes
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Guardar imagen temporal
        temp_filename = f"verify_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        temp_path = os.path.join(TEMP_FOLDER, temp_filename)
        image_file.save(temp_path)
        
        try:
            # Generar embedding y landmarks de la imagen capturada
            from recognition.facial_manager import generate_vector_with_landmarks
            
            result_data = generate_vector_with_landmarks(temp_path)
            
            if result_data is None:
                # Limpiar imagen temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                return jsonify({
                    'error': 'No face detected in image',
                    'message': 'Please ensure your face is clearly visible and well-lit',
                    'match': False
                }), 200  # Cambiar a 200 en lugar de 400 para que el frontend lo maneje mejor
            
            captured_embedding = result_data['embedding']
            captured_landmarks = result_data['landmarks']
            
            # Obtener todos los embeddings de la base de datos
            visit_service = VisitService()
            all_visits = visit_service.get_all_embeddings()
            
            if not all_visits:
                return jsonify({
                    'match': False,
                    'message': 'No embeddings found in database',
                    'captured_landmarks': captured_landmarks,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            best_match = None
            best_distance = float('inf')
            threshold = 0.40  # Threshold para Facenet con cosine distance
            
            # 3. Comparar embedding capturado con todos los embeddings de BD
            for visit in all_visits:
                if not visit.get('embedding'):
                    continue
                
                try:
                    # Comparar embeddings directamente
                    result = compare_embeddings(
                        captured_embedding.tolist(), 
                        visit['embedding'],
                        distance_metric='cosine'
                    )
                    
                    if result and result['verified']:
                        distance = result['distance']
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_match = visit
                
                except Exception as e:
                    continue
            
            # Limpiar imagen temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # 4. Retornar resultado con landmarks
            if best_match and best_distance < threshold:
                similarity = 1 - best_distance  # Convertir distancia a similitud
                
                response_data = {
                    'match': True,
                    'id_persona': best_match['id_persona'],
                    'nombre': best_match['nombre'],
                    'distance': round(best_distance, 4),
                    'similarity': round(similarity, 4),
                    'threshold': threshold,
                    'confidence': 'high' if best_distance < 0.25 else 'medium',
                    'timestamp': datetime.now().isoformat(),
                    # Datos faciales capturados
                    'captured_facial_data': {
                        'landmarks': captured_landmarks,
                        'biometric_info': captured_landmarks.get('biometric_data', {})
                    }
                }
                
                # Incluir landmarks guardados si existen
                if best_match.get('landmarks'):
                    response_data['stored_facial_data'] = {
                        'landmarks': best_match['landmarks'],
                        'biometric_info': best_match['landmarks'].get('biometric_data', {})
                    }
                
                return jsonify(response_data), 200
            else:
                return jsonify({
                    'match': False,
                    'message': 'No match found in database',
                    'best_distance': round(best_distance, 4) if best_distance != float('inf') else None,
                    'threshold': threshold,
                    'captured_facial_data': {
                        'landmarks': captured_landmarks,
                        'biometric_info': captured_landmarks.get('biometric_data', {})
                    },
                    'timestamp': datetime.now().isoformat()
                }), 200
        
        finally:
            # Asegurar limpieza de archivo temporal
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    except Exception as e:
        return jsonify({'error': str(e), 'match': False}), 500


# ==================== INICIO DE LA APLICACIÓN ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from models.user import User
from recognition.facial_manager import generate_vector

import os
from datetime import datetime
from dotenv import load_dotenv

from services.notification_service import NotificationService
from services.visit_service import VisitService
from config.database import init_db, get_db
from recognition.facial_manager import verify_faces
from recognition.socket_events import register_socket_events

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

# Configuramos Email (Flask-Mail)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

register_socket_events(socketio)

TEMP_FOLDER = 'temp'
UPLOADS_FOLDER = 'uploads/visits'
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

with app.app_context():
    init_db()
    print("✅ Database initialized")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'VisitorGuard Biometric API'
    })




@app.route('/api/verify-face', methods=['POST'])
def verify_face_endpoint():
    """
    Endpoint para verificar si dos rostros coinciden
    Espera: reference_image y verification_image como archivos
    """
    try:
        if 'reference_image' not in request.files:
            return jsonify({'error': 'Missing reference_image'}), 400
        
        if 'verification_image' not in request.files:
            return jsonify({'error': 'Missing verification_image'}), 400
        
        

        ref_img = request.files['reference_image']
        ver_img = request.files['verification_image']
        
        if ref_img.filename == '' or ver_img.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        ref_path = os.path.join(TEMP_FOLDER, f"ref_{ref_img.filename}")
        ver_path = os.path.join(TEMP_FOLDER, f"ver_{ver_img.filename}")
        
        ref_img.save(ref_path)
        ver_img.save(ver_path)
        
        result = verify_faces(ref_path, ver_path)
        
        try:
            os.remove(ref_path)
            os.remove(ver_path)
        except:
            pass 
        
        if result is None:
            return jsonify({
                'error': 'Face verification failed - No face detected or processing error'
            }), 422
        
        return jsonify({
            'verified': result.get('verified', False),
            'distance': result.get('distance', 0),
            'threshold': result.get('threshold', 0),
            'model': result.get('model', 'Facenet'),
            'similarity_metric': result.get('distance_metric', 'cosine')
        })
        
    except Exception as e:
        try:
            if 'ref_path' in locals():
                os.remove(ref_path)
            if 'ver_path' in locals():
                os.remove(ver_path)
        except:
            pass
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/register-face', methods=['POST'])
def register_face_endpoint():
    """
    Endpoint para registrar un nuevo rostro
    Espera: image (archivo), name, email, role
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Missing image file'}), 400
        
        image = request.files['image']
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role', 'visitor')
        
        if not name or not email:
            return jsonify({'error': 'Missing required fields: name, email'}), 400
        
        if image.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Guardar temporalmente
        temp_path = os.path.join(TEMP_FOLDER, image.filename)
        image.save(temp_path)
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'message': 'Face registered successfully',
            'name': name,
            'email': email,
            'role': role
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/pre-register', methods=['POST'])
def send_verification_email():
    data = request.json
    email = data.get('email')
    name = data.get('name')

    db = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:   
        return jsonify({'error': 'Email already registered'}), 400
    
    new_user = User(name=name, email=email, role='visitor', verified=False)
    db.add(new_user)
    db.commit()

    token = serializer.dumps(email, salt='email-verify')

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    send = NotificationService.send_verification_email(email, name, token, frontend_url)
    

    if send:
        return jsonify({'success': True, 'message': 'Verification email sent'})
    else:
        return jsonify({'error': 'Failed to send verification email'}), 500
    

@app.route('/api/complete-registration', methods=['POST'])
def complete_registration():
    image = request.files.get('image')
    token = request.form.get('token')

    if not image or not token:
        return jsonify({'error': 'Missing image or token'}), 400
    
    try: 
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except:
        return jsonify({'error': 'Invalid or expired token'}), 400  
        

    temp_path = os.path.join(TEMP_FOLDER, image.filename)
    image.save(temp_path)

    try:
        vector = generate_vector(temp_path)
    
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.photo_path = f"uploads/{user.id}.jpg"
        user.face_encoding = vector.tobytes() if vector is not None else None
        user.verified = True

        db.commit()

        return jsonify({'success': True, 'message': 'Registration completed successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)






    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except:
        return jsonify({'error': 'Invalid or expired token'}), 400

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.verified = True
    db.commit()

    return jsonify({'success': True, 'message': 'Registration completed successfully'}) 


# ==================== ENDPOINTS DE VISITAS ====================

@app.route('/api/visits', methods=['POST'])
def create_visit():
    """
    Crear o actualizar una visita con foto
    Acepta multipart/form-data
    
    Campos requeridos:
    - id_persona: ID de la persona (proporcionado por el cliente)
    - nombre: Nombre de la persona
    - foto: Archivo de imagen (.jpg, .jpeg, .png)
    """
    try:
        # Validar que sea multipart/form-data
        if not request.content_type or 'multipart/form-data' not in request.content_type:
            return jsonify({'error': 'Content-Type must be multipart/form-data'}), 400
        
        # Obtener datos del formulario
        id_persona = request.form.get('id_persona')
        nombre = request.form.get('nombre')
        
        # Validar campos requeridos
        if not id_persona or not nombre:
            return jsonify({'error': 'Missing required fields: id_persona, nombre'}), 400
        
        # Procesar imagen (requerida)
        if 'foto' not in request.files:
            return jsonify({'error': 'Missing required field: foto'}), 400
        
        foto = request.files['foto']
        if foto.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Validar extensión
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext = os.path.splitext(foto.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed'}), 400
        
        # Generar nombre único para la imagen
        filename = f"{id_persona}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        foto_path = os.path.join(UPLOADS_FOLDER, filename)
        
        # Si ya existe una visita con este id_persona, eliminar foto anterior
        visit_service = VisitService()
        existing_visit = visit_service.get_visit_by_id(id_persona)
        if existing_visit and existing_visit.get('foto_path'):
            old_foto_path = existing_visit['foto_path']
            if os.path.exists(old_foto_path):
                os.remove(old_foto_path)
        
        # Guardar nueva imagen
        foto.save(foto_path)
        
        # Crear/actualizar visita
        visit_data = {
            'id_persona': id_persona,
            'nombre': nombre,
            'foto_path': foto_path
        }
        
        result_id = visit_service.create_visit(visit_data)
        
        return jsonify({
            'success': True,
            'message': 'Visit created/updated successfully',
            'id_persona': result_id,
            'nombre': nombre,
            'foto_path': foto_path
        }), 201
        
    except Exception as e:
        # Limpiar imagen si hubo error
        if 'foto_path' in locals() and foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits', methods=['GET'])
def get_visits():
    """
    Obtener todas las visitas con paginación
    Query params: skip (default: 0), limit (default: 100)
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        visit_service = VisitService()
        visits = visit_service.get_all_visits(skip=skip, limit=limit)
        
        return jsonify({
            'success': True,
            'visits': visits,
            'count': len(visits)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['GET'])
def get_visit(id_persona):
    """
    Obtener una visita por id_persona
    """
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        return jsonify({
            'success': True,
            'visit': visit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['PUT'])
def update_visit(id_persona):
    """
    Actualizar una visita (nombre y/o foto)
    Acepta multipart/form-data
    """
    try:
        visit_service = VisitService()
        
        # Verificar que la visita existe
        existing_visit = visit_service.get_visit_by_id(id_persona)
        if not existing_visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        update_data = {}
        
        # Actualizar nombre si viene
        if 'nombre' in request.form:
            update_data['nombre'] = request.form.get('nombre')
        
        # Procesar nueva imagen si existe
        foto_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                # Validar extensión
                allowed_extensions = {'.jpg', '.jpeg', '.png'}
                file_ext = os.path.splitext(foto.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed'}), 400
                
                # Eliminar foto anterior
                if existing_visit.get('foto_path'):
                    old_foto_path = existing_visit['foto_path']
                    if os.path.exists(old_foto_path):
                        os.remove(old_foto_path)
                
                # Generar nombre único para la nueva imagen
                filename = f"{id_persona}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                foto_path = os.path.join(UPLOADS_FOLDER, filename)
                
                # Guardar nueva imagen
                foto.save(foto_path)
                update_data['foto_path'] = foto_path
        
        if not update_data:
            return jsonify({'error': 'No data to update'}), 400
        
        success = visit_service.update_visit(id_persona, update_data)
        
        if not success:
            # Limpiar imagen si hubo error
            if foto_path and os.path.exists(foto_path):
                os.remove(foto_path)
            return jsonify({'error': 'Could not update visit'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Visit updated successfully',
            'foto_path': foto_path
        })
        
    except Exception as e:
        # Limpiar imagen si hubo error
        if 'foto_path' in locals() and foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>', methods=['DELETE'])
def delete_visit(id_persona):
    """
    Eliminar una visita y su foto
    """
    try:
        visit_service = VisitService()
        
        # Obtener visita para eliminar foto
        visit = visit_service.get_visit_by_id(id_persona)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        # Eliminar foto si existe
        if visit.get('foto_path') and os.path.exists(visit['foto_path']):
            os.remove(visit['foto_path'])
        
        # Eliminar registro de la base de datos
        success = visit_service.delete_visit(id_persona)
        
        if not success:
            return jsonify({'error': 'Could not delete visit'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Visit deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<id_persona>/foto', methods=['GET'])
def get_visit_photo(id_persona):
    """
    Obtener la foto de una visita
    Retorna la imagen directamente
    """
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


@app.route('/api/visits/search', methods=['GET'])
def search_visits():
    """
    Buscar visitas por nombre
    Query param: nombre
    """
    try:
        nombre = request.args.get('nombre')
        
        if not nombre:
            return jsonify({'error': 'Missing query parameter: nombre'}), 400
        
        visit_service = VisitService()
        visits = visit_service.search_by_nombre(nombre)
        
        return jsonify({
            'success': True,
            'visits': visits,
            'count': len(visits)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FIN ENDPOINTS DE VISITAS ====================
    """
    Crear una nueva visita con imagen opcional
    Acepta multipart/form-data o application/json
    
    Campos requeridos:
    - motivo_visita, codigo, id_usuario, id_persona, id_tipo_pase, id_area
    
    Campos opcionales:
    - foto (archivo de imagen)
    - fecha_inicio, fecha_fin, comentario
    """
    try:
        # Determinar si es multipart (con imagen) o JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Obtener datos del formulario
            data = {
                'motivo_visita': request.form.get('motivo_visita'),
                'codigo': request.form.get('codigo'),
                'id_usuario': request.form.get('id_usuario'),
                'id_persona': request.form.get('id_persona'),
                'id_tipo_pase': request.form.get('id_tipo_pase'),
                'id_area': request.form.get('id_area'),
                'comentario': request.form.get('comentario'),
                'fecha_inicio': request.form.get('fecha_inicio'),
                'fecha_fin': request.form.get('fecha_fin'),
            }
        else:
            # JSON tradicional
            data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['motivo_visita', 'codigo', 'id_usuario', 'id_persona', 'id_tipo_pase', 'id_area']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Procesar imagen si existe
        foto_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                # Validar extensión
                allowed_extensions = {'.jpg', '.jpeg', '.png'}
                file_ext = os.path.splitext(foto.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed'}), 400
                
                # Generar nombre único para la imagen
                codigo = data['codigo']
                filename = f"{codigo}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                foto_path = os.path.join(UPLOADS_FOLDER, filename)
                
                # Guardar imagen
                foto.save(foto_path)
                data['foto_path'] = foto_path
        
        # Convertir fecha_inicio a datetime si viene como string
        if 'fecha_inicio' in data and data['fecha_inicio'] and isinstance(data['fecha_inicio'], str):
            data['fecha_inicio'] = datetime.fromisoformat(data['fecha_inicio'].replace('Z', '+00:00'))
        else:
            data['fecha_inicio'] = datetime.now()
        
        # Convertir fecha_fin si existe
        if 'fecha_fin' in data and data['fecha_fin'] and isinstance(data['fecha_fin'], str):
            data['fecha_fin'] = datetime.fromisoformat(data['fecha_fin'].replace('Z', '+00:00'))
        
        visit_service = VisitService()
        visit_id = visit_service.create_visit(data)
        
        return jsonify({
            'success': True,
            'message': 'Visit created successfully',
            'visit_id': visit_id,
            'foto_path': foto_path
        }), 201
        
    except Exception as e:
        # Limpiar imagen si hubo error
        if 'foto_path' in locals() and foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/visits/<visit_id>', methods=['GET'])
def get_visit(visit_id):
    """
    Obtener una visita por ID
    """
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(visit_id)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        return jsonify({
            'success': True,
            'visit': visit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/visits/<visit_id>', methods=['PUT'])
def update_visit(visit_id):
    """
    Actualizar una visita con imagen opcional
    Acepta multipart/form-data o application/json
    """
    try:
        # Determinar si es multipart (con imagen) o JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Obtener datos del formulario
            data = {}
            for key in request.form.keys():
                data[key] = request.form.get(key)
        else:
            # JSON tradicional
            data = request.get_json()
        
        # Procesar nueva imagen si existe
        foto_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                # Validar extensión
                allowed_extensions = {'.jpg', '.jpeg', '.png'}
                file_ext = os.path.splitext(foto.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed'}), 400
                
                # Obtener visita actual para eliminar foto anterior si existe
                visit_service = VisitService()
                current_visit = visit_service.get_visit_by_id(visit_id)
                
                if current_visit and current_visit.get('foto_path'):
                    old_foto_path = current_visit['foto_path']
                    if os.path.exists(old_foto_path):
                        os.remove(old_foto_path)
                
                # Generar nombre único para la nueva imagen
                codigo = current_visit.get('codigo', visit_id) if current_visit else visit_id
                filename = f"{codigo}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                foto_path = os.path.join(UPLOADS_FOLDER, filename)
                
                # Guardar nueva imagen
                foto.save(foto_path)
                data['foto_path'] = foto_path
        
        # Convertir fechas si vienen como strings
        if 'fecha_inicio' in data and isinstance(data['fecha_inicio'], str):
            data['fecha_inicio'] = datetime.fromisoformat(data['fecha_inicio'].replace('Z', '+00:00'))
        
        if 'fecha_fin' in data and isinstance(data['fecha_fin'], str):
            data['fecha_fin'] = datetime.fromisoformat(data['fecha_fin'].replace('Z', '+00:00'))
        
        visit_service = VisitService()
        success = visit_service.update_visit(visit_id, data)
        
        if not success:
            # Limpiar imagen si hubo error
            if foto_path and os.path.exists(foto_path):
                os.remove(foto_path)
            return jsonify({'error': 'Visit not found or not updated'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Visit updated successfully',
            'foto_path': foto_path
        })
        
    except Exception as e:
        # Limpiar imagen si hubo error
        if 'foto_path' in locals() and foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'error': str(e)}), 500



@app.route('/api/visits/<visit_id>', methods=['DELETE'])
def delete_visit(visit_id):
    """
    Eliminar una visita
    """
    try:
        visit_service = VisitService()
        success = visit_service.delete_visit(visit_id)
        
        if not success:
            return jsonify({'error': 'Visit not found or could not be deleted'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Visit deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/visits/<visit_id>/foto', methods=['GET'])
def get_visit_photo(visit_id):
    """
    Obtener la foto de una visita
    Retorna la imagen directamente
    """
    try:
        visit_service = VisitService()
        visit = visit_service.get_visit_by_id(visit_id)
        
        if not visit:
            return jsonify({'error': 'Visit not found'}), 404
        
        foto_path = visit.get('foto_path')
        
        if not foto_path or not os.path.exists(foto_path):
            return jsonify({'error': 'Photo not found'}), 404
        
        return send_file(foto_path, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ==================== FIN ENDPOINTS DE VISITAS ====================
    print("🚀 Starting VisitorGuard Biometric Server...")
    print(f"📂 Temp folder: {os.path.abspath(TEMP_FOLDER)}")
    print("🌐 Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)



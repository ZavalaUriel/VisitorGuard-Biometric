from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv

from config.database import init_db, get_db
from recognition.facial_manager import verify_faces
from recognition.socket_events import register_socket_events

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

register_socket_events(socketio)

TEMP_FOLDER = 'temp'
os.makedirs(TEMP_FOLDER, exist_ok=True)

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

if __name__ == '__main__':
    print("🚀 Starting VisitorGuard Biometric Server...")
    print(f"📂 Temp folder: {os.path.abspath(TEMP_FOLDER)}")
    print("🌐 Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
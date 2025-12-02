# VisitorGuard-Biometric

Sistema de control de acceso con reconocimiento facial biométrico para la gestión de visitantes.

## 🚀 Características

- Reconocimiento facial con DeepFace
- Gestión de usuarios y visitantes
- Sistema de roles y permisos
- Agenda de visitas
- Comunicación en tiempo real con WebSockets

## 📋 Requisitos

- Python 3.8+
- OpenCV
- DeepFace

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/ZavalaUriel/VisitorGuard-Biometric.git
cd VisitorGuard-Biometric
```

### 2. Crear entorno virtual e instalar dependencias

**Windows PowerShell:**
```powershell
# Todo en uno
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt

# O paso por paso
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

**Git Bash (Windows):**
```bash
# Todo en uno
python -m venv venv && source venv/Scripts/activate && pip install -r backend/requirements.txt

# O paso por paso
python -m venv venv
source venv/Scripts/activate
pip install -r backend/requirements.txt
```

**Linux/Mac:**
```bash
# Todo en uno
python3 -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt

# O paso por paso
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Windows CMD:**
```cmd
python -m venv venv && venv\Scripts\activate.bat && pip install -r backend/requirements.txt
```

### 3. Configurar variables de entorno

**Linux/Mac/Git Bash:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
nano .env
```

**Windows PowerShell:**
```powershell
copy .env.example .env
# Editar .env con tus configuraciones
notepad .env
```

## 🏃‍♂️ Uso

### Iniciar el servidor

**Asegúrate de activar el entorno virtual primero:**

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Git Bash / Linux / Mac
source venv/bin/activate

# Windows CMD
venv\Scripts\activate.bat
```

**Luego ejecuta el servidor:**
```bash
python backend/app.py
```

El servidor estará disponible en `http://localhost:5000`

### Endpoints disponibles

#### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

#### 2. Verificar rostro
```bash
curl -X POST http://localhost:5000/api/verify-face \
  -F "reference_image=@/path/to/reference.jpg" \
  -F "verification_image=@/path/to/verify.jpg"
```

**Respuesta:**
```json
{
  "verified": true,
  "distance": 0.23,
  "threshold": 0.4,
  "model": "Facenet",
  "similarity_metric": "cosine"
}
```

#### 3. Registrar rostro
```bash
curl -X POST http://localhost:5000/api/register-face \
  -F "image=@/path/to/photo.jpg" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "role=visitor"
```

**Respuesta:**
```json
{
  "success": true,
  "user_id": 123,
  "message": "Face registered successfully"
}
```

### WebSocket Events

El servidor soporta comunicación en tiempo real vía Socket.IO:

- `connect` - Conectar cliente
- `join` - Unirse a sala
- `face_verification_request` - Solicitar verificación
- `visitor_check_in` - Check-in de visitante
- `visitor_check_out` - Check-out de visitante
- `alert` - Alertas de seguridad

### Probar la API

```bash
# Asegúrate que el servidor esté corriendo en otra terminal
python backend/tests/test_api.py
```

## 📁 Estructura del Proyecto

```
VisitorGuard-Biometric/
├── venv/                  # Entorno virtual (no incluido en git)
├── backend/
│   ├── app.py              # Punto de entrada
│   ├── requirements.txt    # Dependencias
│   ├── config/            # Configuración
│   │   └── database.py
│   ├── models/            # Modelos de datos
│   │   ├── user.py
│   │   └── visit.py
│   ├── services/          # Lógica de negocio
│   │   ├── agenda_service.py
│   │   └── role_service.py
│   ├── recognition/       # Reconocimiento facial
│   │   ├── facial_manager.py
│   │   └── socket_events.py
│   └── tests/            # Pruebas
│       └── test_api.py
├── .env                   # Variables de entorno (no incluido en git)
├── .env.example          # Plantilla de variables de entorno
├── .gitignore
└── README.md
```

## 🧪 Tests

```bash
# Ejecutar todas las pruebas
pytest backend/tests/

# Ejecutar con verbose
pytest backend/tests/ -v

# Ejecutar archivo específico
pytest backend/tests/test_facial_recognition.py
```

## 🔧 Tecnologías

- **Backend**: Flask
- **Base de datos**: SQLAlchemy
- **Reconocimiento facial**: DeepFace, OpenCV
- **WebSockets**: Flask-SocketIO
- **Testing**: pytest

## 🐛 Troubleshooting

### Error: "No module named 'flask'"
Asegúrate de activar el entorno virtual:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Git Bash / Linux / Mac
source venv/bin/activate
```

### Error: TensorFlow DLL issues
Instala Microsoft Visual C++ Redistributable o usa opencv backend:
```bash
pip install tf-keras
# O
pip uninstall tensorflow && pip install tensorflow==2.15.0
```

### Puerto 5000 en uso
Cambia el puerto en `backend/app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Autores

- ZavalaUriel

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
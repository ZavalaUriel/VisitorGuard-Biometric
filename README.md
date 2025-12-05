# VisitorGuard-Biometric

Sistema de control de acceso con reconocimiento facial biométrico para la gestión de visitantes.

## 🚀 Características

- Reconocimiento facial con DeepFace
- Gestión de usuarios y visitantes
- Sistema de roles y permisos
- Agenda de visitas
- Comunicación en tiempo real con WebSockets
- Base de datos MongoDB para almacenamiento escalable
- Despliegue con Docker y Docker Compose

## 📋 Requisitos

### Opción 1: Docker (Recomendado)
- Docker
- Docker Compose

### Opción 2: Instalación Local
- Python 3.12+
- MongoDB 7.0+
- OpenCV
- DeepFace

## 🛠️ Instalación

### Opción A: Con Docker (Recomendado) 🐳

Esta es la forma más rápida y sencilla de iniciar el proyecto.

```bash
# 1. Clonar el repositorio
git clone https://github.com/ZavalaUriel/VisitorGuard-Biometric.git
cd VisitorGuard-Biometric

# 2. Construir y levantar los contenedores
docker-compose up --build

# O en segundo plano
docker-compose up -d --build
```

¡Eso es todo! El sistema estará disponible en:
- Backend: `http://localhost:5000`
- MongoDB: `localhost:27017`

**Ver logs:**
```bash
docker-compose logs -f
```

**Detener servicios:**
```bash
docker-compose down
```

📚 **Más información:** Ver [DOCKER_MONGODB_GUIDE.md](DOCKER_MONGODB_GUIDE.md) para documentación completa de Docker y MongoDB.

### Opción B: Instalación Local

### Opción B: Instalación Local

#### 1. Instalar y configurar MongoDB

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb-org

# Iniciar MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
Descarga e instala desde [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

#### 2. Clonar el repositorio
```bash
git clone https://github.com/ZavalaUriel/VisitorGuard-Biometric.git
cd VisitorGuard-Biometric
```

#### 3. Crear entorno virtual e instalar dependencias

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

#### 4. Configurar variables de entorno

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

#### 5. Inicializar la base de datos

```bash
# Activar entorno virtual primero (ver paso 3)
cd backend
python init_database.py
```

## 🏃‍♂️ Uso

### Con Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose stop
```

### Sin Docker

### Sin Docker

**Asegúrate de tener MongoDB corriendo y activar el entorno virtual primero:**

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
cd backend
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 📊 Gestión de Visitas

### Estructura del Documento de Visita en MongoDB

```javascript
{
  "_id": ObjectId("..."),           // ID único de MongoDB
  "hora_visita": ISODate("..."),    // Hora de registro
  "motivo_visita": "string",        // Razón de la visita
  "codigo": "VIS-2025-001",         // Código único (índice único)
  "estatus": "Activa",              // Activa, Finalizada, Cancelada
  "id_usuario": "USER-001",         // ID del usuario que registra
  "id_persona": "PERSON-123",       // ID de la persona visitante
  "id_tipo_pase": "TEMPORAL",       // ID del tipo de pase
  "comentario": "string",           // Comentarios opcionales
  "id_area": "AREA-001",            // ID del área a visitar
  "fecha_inicio": ISODate("..."),   // Fecha y hora de inicio
  "fecha_fin": ISODate("..."),      // Fecha y hora de fin (opcional)
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

### Ejemplos de Uso

Ver ejemplos completos en:
- [backend/ejemplo_visit_service.py](backend/ejemplo_visit_service.py)

```python
from services.visit_service import VisitService
from datetime import datetime

visit_service = VisitService()

# Crear visita
visit_data = {
    "hora_visita": datetime.now(),
    "motivo_visita": "Reunión de negocios",
    "codigo": "VIS-2025-001",
    "estatus": "Activa",
    "id_usuario": "USER-001",
    "id_persona": "PERSON-123",
    "id_tipo_pase": "TEMPORAL",
    "id_area": "AREA-OFICINAS",
    "fecha_inicio": datetime.now(),
    "comentario": "Visitante autorizado"
}

visit_id = visit_service.create_visit(visit_data)

# Consultar visita
visit = visit_service.get_visit_by_id(visit_id)

# Finalizar visita
visit_service.finalizar_visita(visit_id)
```

### Comandos MongoDB Útiles

Ver [MONGODB_COMMANDS.md](MONGODB_COMMANDS.md) para lista completa de comandos.

```bash
# Conectarse a MongoDB
docker exec -it visitorguard-mongodb mongosh

# Ver todas las visitas
use visitorguard
db.visits.find().pretty()

# Buscar visitas activas
db.visits.find({estatus: "Activa"}).pretty()
```
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

#### 4. Gestión de Visitas (CRUD Completo)

**Crear Visita:**
```bash
curl -X POST http://localhost:5000/api/visits \
  -H "Content-Type: application/json" \
  -d '{
    "motivo_visita": "Reunión de trabajo",
    "codigo": "VIS-2025-001",
    "id_usuario": "USER-001",
    "id_persona": "PERSON-123",
    "id_tipo_pase": "TEMPORAL",
    "id_area": "AREA-OFICINAS",
    "comentario": "Visitante autorizado"
  }'
```

**Obtener todas las visitas:**
```bash
curl http://localhost:5000/api/visits
```

**Obtener visita por ID:**
```bash
curl http://localhost:5000/api/visits/{visit_id}
```

**Finalizar visita:**
```bash
curl -X POST http://localhost:5000/api/visits/{visit_id}/finalizar
```

📚 **Documentación completa de la API de Visitas:** Ver [API_VISITS.md](API_VISITS.md)

### WebSocket Events

El servidor soporta comunicación en tiempo real vía Socket.IO:

- `connect` - Conectar cliente
- `join` - Unirse a sala
- `face_verification_request` - Solicitar verificación
- `visitor_check_in` - Check-in de visitante
- `visitor_check_out` - Check-out de visitante
- `alert` - Alertas de seguridad

### Probar la API

**Probar reconocimiento facial:**
```bash
# Asegúrate que el servidor esté corriendo en otra terminal
python backend/tests/test_api.py
```

**Probar API de Visitas:**
```bash
python backend/tests/test_visits_api.py
```

```bash
# Asegúrate que el servidor esté corriendo en otra terminal
python backend/tests/test_api.py
```

## 📁 Estructura del Proyecto

```
VisitorGuard-Biometric/
├── venv/                     # Entorno virtual (no incluido en git)
├── backend/
│   ├── app.py                # Punto de entrada
│   ├── requirements.txt      # Dependencias
│   ├── init_database.py      # Script de inicialización de MongoDB
│   ├── ejemplo_visit_service.py  # Ejemplos de uso
│   ├── config/               # Configuración
│   │   └── database.py       # Configuración de MongoDB
│   ├── models/               # Modelos de datos
│   │   ├── user.py           # Modelo de Usuario
│   │   └── visit.py          # Modelo de Visita
│   ├── services/             # Lógica de negocio
│   │   ├── agenda_service.py
│   │   ├── role_service.py
│   │   ├── visit_service.py  # Servicio de visitas MongoDB
│   │   └── notification_service.py
│   ├── recognition/          # Reconocimiento facial
│   │   ├── facial_manager.py
│   │   └── socket_events.py
│   └── tests/                # Pruebas
│       ├── test_api.py
│       └── test_facial_recognition.py
├── temp/                     # Archivos temporales
├── docker-compose.yml        # Configuración de Docker Compose
├── Dockerfile                # Dockerfile del backend
├── .dockerignore             # Archivos ignorados por Docker
├── .env                      # Variables de entorno (no incluido en git)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore
├── README.md                 # Este archivo
├── DOCKER_MONGODB_GUIDE.md   # Guía completa de Docker y MongoDB
└── MONGODB_COMMANDS.md       # Comandos útiles de MongoDB
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
- **Base de datos**: MongoDB con PyMongo
- **Reconocimiento facial**: DeepFace, OpenCV
- **WebSockets**: Flask-SocketIO
- **Containerización**: Docker, Docker Compose
- **Testing**: pytest

## 🐛 Troubleshooting

### Docker

#### Contenedor no inicia
```bash
# Ver logs
docker-compose logs -f

# Reconstruir contenedores
docker-compose down
docker-compose up --build
```

#### Puerto en uso
Edita `docker-compose.yml` y cambia los puertos:
```yaml
ports:
  - "5001:5000"  # Para backend
  - "27018:27017"  # Para MongoDB
```

#### Error de conexión a MongoDB
Verifica que MongoDB esté corriendo:
```bash
docker-compose ps
```

### Instalación Local

### Error: "No module named 'flask'"
Asegúrate de activar el entorno virtual:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Git Bash / Linux / Mac
source venv/bin/activate
```

### Error: "No module named 'pymongo'"
Instala las dependencias actualizadas:
```bash
pip install -r backend/requirements.txt
```

### Error: TensorFlow DLL issues
Instala Microsoft Visual C++ Redistributable o usa opencv backend:
```bash
pip install tf-keras
# O
pip uninstall tensorflow && pip install tensorflow==2.15.0
```

### Error de conexión a MongoDB
Verifica que MongoDB esté corriendo:
```bash
# Linux/Mac
sudo systemctl status mongod

# Windows - verifica el servicio de MongoDB en Servicios
```

## 📚 Documentación Adicional

- [Guía completa de Docker y MongoDB](DOCKER_MONGODB_GUIDE.md)
- [Comandos útiles de MongoDB](MONGODB_COMMANDS.md)
- [Ejemplos de uso del servicio de visitas](backend/ejemplo_visit_service.py)

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
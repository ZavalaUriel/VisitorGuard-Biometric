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

1. **Clonar el repositorio**
```bash
git clone https://github.com/ZavalaUriel/VisitorGuard-Biometric.git
cd VisitorGuard-Biometric
```

2. **Crear entorno virtual e instalar dependencias**

```powershell
# Windows PowerShell (dos comandos en uno)
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt
```

**O paso por paso:**

```powershell
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r backend/requirements.txt
```

**Para otros sistemas:**
```bash
3. **Configurar variables de entorno**
python -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt

# Windows CMD
python -m venv venv && venv\Scripts\activate.bat && pip install -r backend/requirements.txt
```

5. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.dev .env

# Editar .env con tus configuraciones
```

## 🏃‍♂️ Uso

```bash
# Ejecutar servidor de desarrollo
python backend/app.py
```

## 📁 Estructura del Proyecto

```
VisitorGuard-Biometric/
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
│       └── test_facial_recognition.py
├── .env                   # Variables de entorno
├── .gitignore
└── README.md
```

## 🧪 Tests

```bash
pytest backend/tests/
```

## 🔧 Tecnologías

- **Backend**: Flask
- **Base de datos**: SQLAlchemy
- **Reconocimiento facial**: DeepFace, OpenCV
- **WebSockets**: Flask-SocketIO

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

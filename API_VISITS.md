# API de Visitas - VisitorGuard

Documentación de los endpoints para gestionar visitas.

## Base URL
```
http://localhost:5000/api
```

---

## 📝 Crear o Actualizar Visita

**POST** `/api/visits`

Crea o actualiza una visita en el sistema con imagen. Si el `id_persona` ya existe, se actualiza la visita.

### Request (multipart/form-data)

```bash
curl -X POST http://localhost:5000/api/visits \
  -F "id_persona=PERSON-123" \
  -F "nombre=Juan Pérez" \
  -F "foto=@/ruta/a/foto.jpg"
```

### Campos Requeridos
- `id_persona` (string): ID único de la persona (proporcionado por el cliente)
- `nombre` (string): Nombre completo del visitante
- `foto` (file): Imagen de la visita (.jpg, .jpeg, .png)

### Response (201 Created)
```json
{
  "success": true,
  "message": "Visit created successfully",
  "id_persona": "PERSON-123",
  "foto_path": "uploads/visits/PERSON-123_20251204103045.jpg"
}
```

### Ejemplo con curl
```bash
curl -X POST http://localhost:5000/api/visits \
  -F "id_persona=PERSON-123" \
  -F "nombre=Juan Pérez" \
  -F "foto=@./foto_visitante.jpg"
```

### Ejemplo con Python
```python
import requests

url = 'http://localhost:5000/api/visits'

data = {
    'id_persona': 'PERSON-123',
    'nombre': 'Juan Pérez'
}

files = {
    'foto': open('foto_visitante.jpg', 'rb')
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

---

## 🔍 Obtener Todas las Visitas

**GET** `/api/visits`

Obtiene todas las visitas registradas con paginación.

### Query Parameters
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 100)

### Response (200 OK)
```json
{
  "success": true,
  "visits": [
    {
      "id_persona": "PERSON-123",
      "nombre": "Juan Pérez",
      "foto_path": "uploads/visits/PERSON-123_20251204103045.jpg",
      "created_at": "2025-12-04T10:30:45",
      "updated_at": "2025-12-04T10:30:45"
    }
  ],
  "count": 1
}
```

### Ejemplo con curl
```bash
curl http://localhost:5000/api/visits?skip=0&limit=10
```

---

## 🔎 Obtener Visita por ID

**GET** `/api/visits/<id_persona>`

Obtiene una visita específica por su ID de persona.

### Response (200 OK)
```json
{
  "success": true,
  "visit": {
    "id_persona": "PERSON-123",
    "nombre": "Juan Pérez",
    "foto_path": "uploads/visits/PERSON-123_20251204103045.jpg",
    "created_at": "2025-12-04T10:30:45",
    "updated_at": "2025-12-04T10:30:45"
  }
}
```

### Ejemplo con curl
```bash
curl http://localhost:5000/api/visits/PERSON-123
```

---

## 🔍 Buscar Visitas por Nombre

**GET** `/api/visits/search/<nombre>`

Busca visitas por nombre (búsqueda parcial, case-insensitive).

### Response (200 OK)
```json
{
  "success": true,
  "visits": [
    {
      "id_persona": "PERSON-123",
      "nombre": "Juan Pérez",
      "foto_path": "uploads/visits/PERSON-123_20251204103045.jpg",
      "created_at": "2025-12-04T10:30:45",
      "updated_at": "2025-12-04T10:30:45"
    }
  ],
  "count": 1
}
```

### Ejemplo con curl
```bash
curl http://localhost:5000/api/visits/search/Juan
```

---

## 📸 Obtener Foto de Visita

**GET** `/api/visits/<id_persona>/foto`

Obtiene la imagen de una visita específica.

### Response (200 OK)
Retorna directamente el archivo de imagen (JPEG/PNG).

### Ejemplo con curl
```bash
curl http://localhost:5000/api/visits/PERSON-123/foto -o foto_descargada.jpg
```

### Ejemplo con Python
```python
import requests

response = requests.get('http://localhost:5000/api/visits/PERSON-123/foto')

if response.status_code == 200:
    with open('foto_descargada.jpg', 'wb') as f:
        f.write(response.content)
```

---

## 🔄 Actualizar Visita

**PUT** `/api/visits/<id_persona>`

Actualiza una visita existente. Puede actualizar solo el nombre, solo la foto, o ambos.

### Request (multipart/form-data)

```bash
curl -X PUT http://localhost:5000/api/visits/PERSON-123 \
  -F "nombre=Juan Pérez González" \
  -F "foto=@/ruta/a/nueva_foto.jpg"
```

### Campos Opcionales
- `nombre` (string): Nuevo nombre
- `foto` (file): Nueva imagen

### Response (200 OK)
```json
{
  "success": true,
  "message": "Visit updated successfully",
  "foto_path": "uploads/visits/PERSON-123_20251204120000.jpg"
}
```

---

## ❌ Eliminar Visita

**DELETE** `/api/visits/<id_persona>`

Elimina una visita y su imagen asociada.

### Response (200 OK)
```json
{
  "success": true,
  "message": "Visit deleted successfully"
}
```

### Ejemplo con curl
```bash
curl -X DELETE http://localhost:5000/api/visits/PERSON-123
```

---

## 📊 Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200    | Operación exitosa |
| 201    | Recurso creado exitosamente |
| 400    | Solicitud incorrecta (datos faltantes o inválidos) |
| 404    | Recurso no encontrado |
| 500    | Error interno del servidor |

---

## 🚨 Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "error": "Descripción del error"
}
```

### Ejemplos de Errores

**400 Bad Request - Campos faltantes:**
```json
{
  "error": "Missing required fields: id_persona, nombre, foto"
}
```

**400 Bad Request - Tipo de archivo inválido:**
```json
{
  "error": "Invalid file type. Only JPG, JPEG, and PNG are allowed"
}
```

**404 Not Found - Visita no encontrada:**
```json
{
  "error": "Visit not found"
}
```

---

## 💡 Notas Importantes

1. **ID de Persona**: El `id_persona` NO se genera automáticamente. Debe ser proporcionado por el cliente.

2. **Imágenes**: 
   - Se guardan físicamente en `uploads/visits/`
   - Solo se almacena la ruta en MongoDB
   - Formatos permitidos: JPG, JPEG, PNG
   - Al actualizar, la imagen anterior se elimina automáticamente

3. **Upsert**: El endpoint POST crea o actualiza según si el `id_persona` ya existe.

4. **Paginación**: Por defecto, GET `/api/visits` retorna máximo 100 registros.

5. **Búsqueda**: La búsqueda por nombre es case-insensitive y permite coincidencias parciales.
```

### Ejemplo con curl
```bash
curl http://localhost:5000/api/visits/usuario/USER-001
```

---

## 📷 Obtener Foto de Visita por ID

**GET** `/api/visits/:visit_id/foto`

Obtiene la imagen asociada a una visita específica. Retorna la imagen directamente.

### Response (200 OK)
Retorna el archivo de imagen (image/jpeg)

### Response (404 Not Found)
```json
{
  "error": "Visit not found"
}
```
o
```json
{
  "error": "Photo not found"
}
```

### Ejemplo con curl
```bash
# Descargar la foto
curl http://localhost:5000/api/visits/675035a8e8f9c123456789ab/foto -o foto_visita.jpg

# Ver en el navegador
# http://localhost:5000/api/visits/675035a8e8f9c123456789ab/foto
```

### Ejemplo con Python
```python
import requests

visit_id = "675035a8e8f9c123456789ab"
response = requests.get(f'http://localhost:5000/api/visits/{visit_id}/foto')

if response.status_code == 200:
    with open('foto_descargada.jpg', 'wb') as f:
        f.write(response.content)
    print("Foto descargada exitosamente")
else:
    print(f"Error: {response.json()}")
```

---

## 📷 Obtener Foto de Visita por Código

**GET** `/api/visits/codigo/:codigo/foto`

Obtiene la imagen asociada a una visita por su código único. Retorna la imagen directamente.

### Response (200 OK)
Retorna el archivo de imagen (image/jpeg)

### Ejemplo con curl
```bash
# Descargar la foto
curl http://localhost:5000/api/visits/codigo/VIS-2025-001/foto -o foto_visita.jpg

# Ver en HTML
# <img src="http://localhost:5000/api/visits/codigo/VIS-2025-001/foto" />
```

### Ejemplo con JavaScript (Frontend)
```javascript
// Mostrar foto en una página web
const codigo = "VIS-2025-001";
const imgElement = document.createElement('img');
imgElement.src = `http://localhost:5000/api/visits/codigo/${codigo}/foto`;
document.body.appendChild(imgElement);

// Descargar foto
fetch(`http://localhost:5000/api/visits/codigo/${codigo}/foto`)
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${codigo}.jpg`;
    a.click();
  });
```

---

## 🧪 Probar la API

### Script de Prueba Completo (Python)

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# 1. Crear visita
print("1. Creando visita...")
visit_data = {
    "motivo_visita": "Reunión de prueba",
    "codigo": f"VIS-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "id_usuario": "USER-TEST",
    "id_persona": "PERSON-TEST",
    "id_tipo_pase": "TEMPORAL",
    "id_area": "AREA-TEST",
    "fecha_inicio": datetime.now().isoformat(),
    "comentario": "Visita de prueba de API"
}

response = requests.post(f"{BASE_URL}/visits", json=visit_data)
result = response.json()
print(f"   Resultado: {result}")

if result.get('success'):
    visit_id = result['visit_id']
    
    # 2. Obtener visita por ID
    print(f"\n2. Obteniendo visita por ID: {visit_id}")
    response = requests.get(f"{BASE_URL}/visits/{visit_id}")
    print(f"   Resultado: {response.json()}")
    
    # 3. Actualizar visita
    print(f"\n3. Actualizando visita...")
    update_data = {"comentario": "Comentario actualizado"}
    response = requests.put(f"{BASE_URL}/visits/{visit_id}", json=update_data)
    print(f"   Resultado: {response.json()}")
    
    # 4. Finalizar visita
    print(f"\n4. Finalizando visita...")
    response = requests.post(f"{BASE_URL}/visits/{visit_id}/finalizar")
    print(f"   Resultado: {response.json()}")
    
    # 5. Listar todas las visitas
    print(f"\n5. Listando todas las visitas...")
    response = requests.get(f"{BASE_URL}/visits?limit=5")
    print(f"   Total: {response.json()['count']} visitas")

print("\n✅ Pruebas completadas")
```

### Guardar como script
```bash
# Guardar el script anterior como test_visits_api.py
python test_visits_api.py
```

---

## 🔒 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos o incompletos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 📊 Estructura del Documento de Visita

```javascript
{
  "_id": ObjectId("..."),           // ID único de MongoDB
  "hora_visita": ISODate("..."),    // Hora de registro
  "motivo_visita": "string",        // Razón de la visita
  "codigo": "VIS-2025-001",         // Código único (índice único)
  "estatus": "Activa",              // Activa | Finalizada | Cancelada
  "id_usuario": "USER-001",         // ID del usuario que registra
  "id_persona": "PERSON-123",       // ID de la persona visitante
  "id_tipo_pase": "TEMPORAL",       // ID del tipo de pase
  "comentario": "string",           // Comentarios opcionales
  "id_area": "AREA-001",            // ID del área a visitar
  "fecha_inicio": ISODate("..."),   // Fecha y hora de inicio
  "fecha_fin": ISODate("..."),      // Fecha y hora de fin (opcional)
  "created_at": ISODate("..."),     // Fecha de creación
  "updated_at": ISODate("...")      // Fecha de actualización
}
```

---

## 🔗 Ver También

- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido del proyecto
- [MONGODB_COMMANDS.md](MONGODB_COMMANDS.md) - Comandos de MongoDB
- [README.md](README.md) - Documentación principal

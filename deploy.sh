#!/bin/bash

# Script de Despliegue Rápido - VisitorGuard Biometric

set -e

echo "🚀 Iniciando despliegue de VisitorGuard Biometric..."

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml no encontrado"
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env con tus credenciales"
    echo "   nano .env"
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p backend/uploads/visits
mkdir -p backend/temp
mkdir -p temp

# Construir e iniciar contenedores
echo "🐳 Construyendo contenedores..."
docker compose build

echo "🚀 Iniciando servicios..."
docker compose up -d

# Esperar a que MongoDB esté listo
echo "⏳ Esperando MongoDB..."
sleep 10

# Verificar servicios
echo "✅ Verificando servicios..."
docker compose ps

# Health check
echo "🏥 Verificando backend..."
sleep 5
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Backend funcionando correctamente"
else
    echo "⚠️  Backend aún iniciando..."
fi

echo ""
echo "✅ Despliegue completado!"
echo ""
echo "📍 URLs disponibles:"
echo "   - API Backend: http://localhost:5000"
echo "   - Health Check: http://localhost:5000/health"
echo "   - Mongo Express: http://localhost:8081"
echo "   - Scanner: Abre facial-scanner.html"
echo ""
echo "📋 Comandos útiles:"
echo "   - Ver logs: docker compose logs -f"
echo "   - Reiniciar: docker compose restart"
echo "   - Detener: docker compose down"
echo ""
echo "📖 Ver DEPLOY.md para más información"

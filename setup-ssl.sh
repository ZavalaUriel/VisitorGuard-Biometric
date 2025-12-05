#!/bin/bash

# Script para configurar SSL con Let's Encrypt para deepface.zukdev.com
# Uso: ./setup-ssl.sh

set -e

DOMAIN="deepface.zukdev.com"
EMAIL="tu-email@ejemplo.com"  # ⚠️ CAMBIAR POR TU EMAIL REAL

echo "🔧 Configurando SSL para $DOMAIN"

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx/conf.d

# Verificar que el dominio apunta a este servidor
echo "🌐 Verificando DNS..."
echo "Por favor, asegúrate de que $DOMAIN apunta a la IP de este servidor"
read -p "¿El dominio está configurado correctamente? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Por favor, configura tu DNS antes de continuar"
    exit 1
fi

# Detener servicios si están corriendo
echo "🛑 Deteniendo servicios existentes..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Crear configuración temporal de Nginx para el desafío HTTP-01
echo "📝 Creando configuración temporal de Nginx..."
cat > nginx/conf.d/temp.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name deepface.zukdev.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Server is ready for SSL setup\n';
        add_header Content-Type text/plain;
    }
}
EOF

# Iniciar Nginx temporalmente
echo "🚀 Iniciando Nginx temporal..."
docker compose -f docker-compose.prod.yml up -d nginx

# Esperar a que Nginx esté listo
echo "⏳ Esperando a que Nginx inicie..."
sleep 5

# Obtener certificado SSL
echo "🔐 Solicitando certificado SSL..."
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL obtenido exitosamente"
    
    # Eliminar configuración temporal
    rm nginx/conf.d/temp.conf
    
    # Detener Nginx temporal
    docker compose -f docker-compose.prod.yml down
    
    # Iniciar todos los servicios con SSL
    echo "🚀 Iniciando todos los servicios..."
    docker compose -f docker-compose.prod.yml up -d
    
    echo ""
    echo "✅ ¡Configuración completada!"
    echo "🌐 Tu API está disponible en: https://$DOMAIN"
    echo "📊 Endpoints disponibles:"
    echo "   - https://$DOMAIN/api/visits"
    echo "   - https://$DOMAIN/health"
    echo ""
    echo "📝 Para ver los logs: docker compose -f docker-compose.prod.yml logs -f"
    echo "🔄 El certificado se renovará automáticamente cada 12 horas"
else
    echo "❌ Error al obtener el certificado SSL"
    echo "Por favor, verifica:"
    echo "1. Que el dominio $DOMAIN apunta a este servidor"
    echo "2. Que los puertos 80 y 443 están abiertos en el firewall"
    echo "3. Que no hay otro servicio usando esos puertos"
    exit 1
fi

#!/bin/bash

# Script de gestión para VisitorGuard con SSL
# Uso: ./manage.sh [comando]

set -e

COMPOSE_FILE="docker-compose.prod.yml"

show_help() {
    echo "🔧 VisitorGuard - Script de Gestión"
    echo ""
    echo "Uso: ./manage.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup         - Configurar SSL por primera vez"
    echo "  start         - Iniciar todos los servicios"
    echo "  stop          - Detener todos los servicios"
    echo "  restart       - Reiniciar todos los servicios"
    echo "  logs          - Ver logs de todos los servicios"
    echo "  logs-backend  - Ver logs solo del backend"
    echo "  logs-nginx    - Ver logs solo de Nginx"
    echo "  status        - Ver estado de los servicios"
    echo "  rebuild       - Reconstruir y reiniciar el backend"
    echo "  renew-ssl     - Renovar certificado SSL manualmente"
    echo "  backup-db     - Crear backup de MongoDB"
    echo "  restore-db    - Restaurar backup de MongoDB"
    echo "  clean         - Limpiar contenedores y volúmenes"
    echo "  help          - Mostrar esta ayuda"
    echo ""
}

case "${1}" in
    setup)
        echo "🔧 Configurando SSL..."
        ./setup-ssl.sh
        ;;
    
    start)
        echo "🚀 Iniciando servicios..."
        docker compose -f $COMPOSE_FILE up -d
        echo "✅ Servicios iniciados"
        docker compose -f $COMPOSE_FILE ps
        ;;
    
    stop)
        echo "🛑 Deteniendo servicios..."
        docker compose -f $COMPOSE_FILE down
        echo "✅ Servicios detenidos"
        ;;
    
    restart)
        echo "🔄 Reiniciando servicios..."
        docker compose -f $COMPOSE_FILE restart
        echo "✅ Servicios reiniciados"
        docker compose -f $COMPOSE_FILE ps
        ;;
    
    logs)
        echo "📋 Mostrando logs (Ctrl+C para salir)..."
        docker compose -f $COMPOSE_FILE logs -f --tail=100
        ;;
    
    logs-backend)
        echo "📋 Mostrando logs del backend (Ctrl+C para salir)..."
        docker compose -f $COMPOSE_FILE logs -f --tail=100 backend
        ;;
    
    logs-nginx)
        echo "📋 Mostrando logs de Nginx (Ctrl+C para salir)..."
        docker compose -f $COMPOSE_FILE logs -f --tail=100 nginx
        ;;
    
    status)
        echo "📊 Estado de los servicios:"
        docker compose -f $COMPOSE_FILE ps
        echo ""
        echo "🔍 Verificando conectividad..."
        echo ""
        if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200"; then
            echo "✅ HTTP (puerto 80): OK"
        else
            echo "❌ HTTP (puerto 80): ERROR"
        fi
        
        if curl -k -s -o /dev/null -w "%{http_code}" https://localhost/health | grep -q "200"; then
            echo "✅ HTTPS (puerto 443): OK"
        else
            echo "❌ HTTPS (puerto 443): ERROR o certificado no configurado"
        fi
        ;;
    
    rebuild)
        echo "🔨 Reconstruyendo backend..."
        docker compose -f $COMPOSE_FILE stop backend
        docker compose -f $COMPOSE_FILE build --no-cache backend
        docker compose -f $COMPOSE_FILE up -d backend
        echo "✅ Backend reconstruido"
        docker compose -f $COMPOSE_FILE logs -f --tail=50 backend
        ;;
    
    renew-ssl)
        echo "🔐 Renovando certificado SSL..."
        docker compose -f $COMPOSE_FILE run --rm certbot renew
        docker compose -f $COMPOSE_FILE exec nginx nginx -s reload
        echo "✅ Certificado renovado"
        ;;
    
    backup-db)
        BACKUP_DIR="./backups"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="mongodb_backup_$TIMESTAMP"
        
        echo "💾 Creando backup de MongoDB..."
        mkdir -p $BACKUP_DIR
        
        docker compose -f $COMPOSE_FILE exec -T mongodb mongodump \
            --username=${MONGO_ROOT_USERNAME:-admin} \
            --password=${MONGO_ROOT_PASSWORD:-admin123} \
            --authenticationDatabase=admin \
            --db=${MONGO_DATABASE:-visitorguard} \
            --archive=/data/$BACKUP_FILE.archive
        
        docker cp visitorguard-mongodb:/data/$BACKUP_FILE.archive $BACKUP_DIR/$BACKUP_FILE.archive
        
        docker compose -f $COMPOSE_FILE exec mongodb rm /data/$BACKUP_FILE.archive
        
        echo "✅ Backup creado: $BACKUP_DIR/$BACKUP_FILE.archive"
        ;;
    
    restore-db)
        BACKUP_DIR="./backups"
        
        if [ -z "$2" ]; then
            echo "❌ Error: Especifica el archivo de backup"
            echo "Uso: ./manage.sh restore-db <archivo_backup>"
            echo ""
            echo "Backups disponibles:"
            ls -lh $BACKUP_DIR/*.archive 2>/dev/null || echo "No hay backups disponibles"
            exit 1
        fi
        
        BACKUP_FILE="$2"
        
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "❌ Error: El archivo $BACKUP_FILE no existe"
            exit 1
        fi
        
        echo "⚠️  ADVERTENCIA: Esto sobrescribirá la base de datos actual"
        read -p "¿Continuar? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "❌ Restauración cancelada"
            exit 1
        fi
        
        echo "📥 Restaurando backup..."
        
        BACKUP_NAME=$(basename $BACKUP_FILE)
        docker cp $BACKUP_FILE visitorguard-mongodb:/data/$BACKUP_NAME
        
        docker compose -f $COMPOSE_FILE exec -T mongodb mongorestore \
            --username=${MONGO_ROOT_USERNAME:-admin} \
            --password=${MONGO_ROOT_PASSWORD:-admin123} \
            --authenticationDatabase=admin \
            --db=${MONGO_DATABASE:-visitorguard} \
            --archive=/data/$BACKUP_NAME \
            --drop
        
        docker compose -f $COMPOSE_FILE exec mongodb rm /data/$BACKUP_NAME
        
        echo "✅ Backup restaurado exitosamente"
        ;;
    
    clean)
        echo "⚠️  ADVERTENCIA: Esto eliminará todos los contenedores, volúmenes y datos"
        read -p "¿Continuar? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "❌ Limpieza cancelada"
            exit 1
        fi
        
        echo "🧹 Limpiando..."
        docker compose -f $COMPOSE_FILE down -v
        docker system prune -f
        echo "✅ Limpieza completada"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo "❌ Comando no reconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

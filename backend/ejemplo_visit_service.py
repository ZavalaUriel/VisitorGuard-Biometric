#!/usr/bin/env python3
"""
Script de ejemplo para demostrar el uso del servicio de visitas
"""

from services.visit_service import VisitService
from datetime import datetime, timedelta
import sys

def ejemplo_crear_visita():
    """Ejemplo de cómo crear una nueva visita"""
    print("\n" + "="*60)
    print("📝 Ejemplo 1: Crear una nueva visita")
    print("="*60)
    
    visit_service = VisitService()
    
    visit_data = {
        "hora_visita": datetime.now(),
        "motivo_visita": "Reunión con el equipo de desarrollo",
        "codigo": f"VIS-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "estatus": "Activa",
        "id_usuario": "USER-001",
        "id_persona": "PERSON-123",
        "id_tipo_pase": "TEMPORAL",
        "id_area": "AREA-DESARROLLO",
        "fecha_inicio": datetime.now(),
        "comentario": "Visitante autorizado por el director de tecnología"
    }
    
    try:
        visit_id = visit_service.create_visit(visit_data)
        print(f"\n✅ Visita creada exitosamente")
        print(f"   ID: {visit_id}")
        print(f"   Código: {visit_data['codigo']}")
        return visit_id
    except Exception as e:
        print(f"\n❌ Error al crear visita: {e}")
        return None

def ejemplo_consultar_visita(visit_id):
    """Ejemplo de cómo consultar una visita"""
    print("\n" + "="*60)
    print("🔍 Ejemplo 2: Consultar una visita por ID")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        visit = visit_service.get_visit_by_id(visit_id)
        if visit:
            print(f"\n✅ Visita encontrada:")
            print(f"   Código: {visit['codigo']}")
            print(f"   Motivo: {visit['motivo_visita']}")
            print(f"   Estatus: {visit['estatus']}")
            print(f"   Fecha inicio: {visit['fecha_inicio']}")
            print(f"   ID Usuario: {visit['id_usuario']}")
            print(f"   ID Persona: {visit['id_persona']}")
            return visit
        else:
            print(f"\n❌ Visita no encontrada")
            return None
    except Exception as e:
        print(f"\n❌ Error al consultar visita: {e}")
        return None

def ejemplo_listar_visitas():
    """Ejemplo de cómo listar todas las visitas"""
    print("\n" + "="*60)
    print("📋 Ejemplo 3: Listar todas las visitas")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        visits = visit_service.get_all_visits(limit=10)
        print(f"\n✅ Total de visitas encontradas: {len(visits)}")
        
        if visits:
            print("\nPrimeras visitas:")
            for i, visit in enumerate(visits, 1):
                print(f"\n   {i}. Código: {visit['codigo']}")
                print(f"      Estatus: {visit['estatus']}")
                print(f"      Motivo: {visit['motivo_visita']}")
                print(f"      Fecha: {visit['fecha_inicio']}")
    except Exception as e:
        print(f"\n❌ Error al listar visitas: {e}")

def ejemplo_actualizar_visita(visit_id):
    """Ejemplo de cómo actualizar una visita"""
    print("\n" + "="*60)
    print("✏️  Ejemplo 4: Actualizar una visita")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        # Actualizar comentario
        update_data = {
            "comentario": "Visita actualizada - Reunión finalizada exitosamente"
        }
        
        success = visit_service.update_visit(visit_id, update_data)
        
        if success:
            print(f"\n✅ Visita actualizada correctamente")
            # Mostrar datos actualizados
            visit = visit_service.get_visit_by_id(visit_id)
            print(f"   Nuevo comentario: {visit['comentario']}")
        else:
            print(f"\n❌ No se pudo actualizar la visita")
    except Exception as e:
        print(f"\n❌ Error al actualizar visita: {e}")

def ejemplo_finalizar_visita(visit_id):
    """Ejemplo de cómo finalizar una visita"""
    print("\n" + "="*60)
    print("🏁 Ejemplo 5: Finalizar una visita")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        success = visit_service.finalizar_visita(visit_id)
        
        if success:
            print(f"\n✅ Visita finalizada correctamente")
            # Mostrar datos actualizados
            visit = visit_service.get_visit_by_id(visit_id)
            print(f"   Estatus: {visit['estatus']}")
            print(f"   Fecha fin: {visit['fecha_fin']}")
        else:
            print(f"\n❌ No se pudo finalizar la visita")
    except Exception as e:
        print(f"\n❌ Error al finalizar visita: {e}")

def ejemplo_filtrar_por_estatus():
    """Ejemplo de cómo filtrar visitas por estatus"""
    print("\n" + "="*60)
    print("🔎 Ejemplo 6: Filtrar visitas por estatus")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        # Buscar visitas activas
        activas = visit_service.get_visits_by_estatus("Activa")
        print(f"\n✅ Visitas activas: {len(activas)}")
        
        # Buscar visitas finalizadas
        finalizadas = visit_service.get_visits_by_estatus("Finalizada")
        print(f"✅ Visitas finalizadas: {len(finalizadas)}")
        
        if activas:
            print(f"\nVisitas activas:")
            for visit in activas[:5]:  # Mostrar solo las primeras 5
                print(f"   - {visit['codigo']}: {visit['motivo_visita']}")
    except Exception as e:
        print(f"\n❌ Error al filtrar visitas: {e}")

def ejemplo_buscar_por_rango_fechas():
    """Ejemplo de cómo buscar visitas por rango de fechas"""
    print("\n" + "="*60)
    print("📅 Ejemplo 7: Buscar visitas por rango de fechas")
    print("="*60)
    
    visit_service = VisitService()
    
    try:
        # Buscar visitas del último día
        fecha_inicio = datetime.now() - timedelta(days=1)
        fecha_fin = datetime.now()
        
        visits = visit_service.get_visits_by_date_range(fecha_inicio, fecha_fin)
        print(f"\n✅ Visitas en las últimas 24 horas: {len(visits)}")
        
        if visits:
            for visit in visits[:5]:
                print(f"   - {visit['codigo']} ({visit['fecha_inicio']})")
    except Exception as e:
        print(f"\n❌ Error al buscar por rango de fechas: {e}")

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("\n" + "="*70)
    print("🚀 VisitorGuard - Ejemplos de Uso del Servicio de Visitas")
    print("="*70)
    
    try:
        # Ejemplo 1: Crear visita
        visit_id = ejemplo_crear_visita()
        
        if not visit_id:
            print("\n❌ No se pudo crear la visita. Verifica la conexión a MongoDB.")
            sys.exit(1)
        
        # Ejemplo 2: Consultar visita
        ejemplo_consultar_visita(visit_id)
        
        # Ejemplo 3: Listar visitas
        ejemplo_listar_visitas()
        
        # Ejemplo 4: Actualizar visita
        ejemplo_actualizar_visita(visit_id)
        
        # Ejemplo 5: Finalizar visita
        ejemplo_finalizar_visita(visit_id)
        
        # Ejemplo 6: Filtrar por estatus
        ejemplo_filtrar_por_estatus()
        
        # Ejemplo 7: Buscar por rango de fechas
        ejemplo_buscar_por_rango_fechas()
        
        print("\n" + "="*70)
        print("✨ Todos los ejemplos se ejecutaron correctamente")
        print("="*70)
        print("\n💡 Revisa el código en 'ejemplo_visit_service.py' para ver")
        print("   cómo implementar estas funcionalidades en tu aplicación.")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

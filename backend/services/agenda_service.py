from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.visit import Visit
from models.user import User

class AgendaService:
    """Servicio para gestionar la agenda de visitas"""
    
    @staticmethod
    def create_visit(db: Session, user_id: int, visit_data: dict):
        """
        Crear una nueva visita programada
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario/visitante
            visit_data: Datos de la visita (purpose, host_name, scheduled_time, etc.)
        """
        visit = Visit(
            user_id=user_id,
            purpose=visit_data.get('purpose'),
            host_name=visit_data.get('host_name'),
            location=visit_data.get('location'),
            scheduled_time=visit_data.get('scheduled_time'),
            notes=visit_data.get('notes')
        )
        
        db.add(visit)
        db.commit()
        db.refresh(visit)
        
        return visit
    
    @staticmethod
    def check_in_visit(db: Session, visit_id: int, verification_data: dict):
        """
        Registrar entrada de una visita
        
        Args:
            db: Sesión de base de datos
            visit_id: ID de la visita
            verification_data: Datos de verificación biométrica
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()
        
        if not visit:
            return None
        
        visit.check_in = datetime.utcnow()
        visit.is_verified = verification_data.get('verified', False)
        visit.verification_score = str(verification_data.get('distance', 0))
        visit.verification_photo = verification_data.get('photo_path')
        
        db.commit()
        db.refresh(visit)
        
        return visit
    
    @staticmethod
    def check_out_visit(db: Session, visit_id: int):
        """
        Registrar salida de una visita
        
        Args:
            db: Sesión de base de datos
            visit_id: ID de la visita
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()
        
        if not visit:
            return None
        
        visit.check_out = datetime.utcnow()
        
        db.commit()
        db.refresh(visit)
        
        return visit
    
    @staticmethod
    def get_active_visits(db: Session):
        """
        Obtener todas las visitas activas (sin check_out)
        
        Args:
            db: Sesión de base de datos
        """
        return db.query(Visit).filter(Visit.check_out == None).all()
    
    @staticmethod
    def get_scheduled_visits(db: Session, date=None):
        """
        Obtener visitas programadas para una fecha específica
        
        Args:
            db: Sesión de base de datos
            date: Fecha a consultar (default: hoy)
        """
        if date is None:
            date = datetime.utcnow().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        return db.query(Visit).filter(
            Visit.scheduled_time >= start_of_day,
            Visit.scheduled_time <= end_of_day
        ).all()
    
    @staticmethod
    def get_visit_history(db: Session, user_id: int, limit=10):
        """
        Obtener historial de visitas de un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            limit: Número máximo de resultados
        """
        return db.query(Visit).filter(
            Visit.user_id == user_id
        ).order_by(Visit.check_in.desc()).limit(limit).all()
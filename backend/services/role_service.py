from sqlalchemy.orm import Session
from models.user import User
from typing import List, Dict

class RoleService:
    """Servicio para gestionar roles y permisos de usuarios"""
    
    # Definir roles y sus permisos
    ROLES = {
        'admin': {
            'permissions': [
                'manage_users',
                'view_all_visits',
                'manage_visits',
                'view_reports',
                'manage_settings'
            ],
            'description': 'Administrador con acceso completo'
        },
        'employee': {
            'permissions': [
                'check_in',
                'check_out',
                'view_own_visits',
                'schedule_visits'
            ],
            'description': 'Empleado con acceso regular'
        },
        'visitor': {
            'permissions': [
                'check_in',
                'check_out',
                'view_own_visits'
            ],
            'description': 'Visitante con acceso limitado'
        },
        'security': {
            'permissions': [
                'verify_faces',
                'view_all_visits',
                'check_in_visitors',
                'check_out_visitors'
            ],
            'description': 'Personal de seguridad'
        }
    }
    
    @staticmethod
    def get_user_role(db: Session, user_id: int) -> str:
        """
        Obtener rol de un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Rol del usuario o None
        """
        user = db.query(User).filter(User.id == user_id).first()
        return user.role if user else None
    
    @staticmethod
    def has_permission(db: Session, user_id: int, permission: str) -> bool:
        """
        Verificar si un usuario tiene un permiso específico
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            permission: Permiso a verificar
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        role = RoleService.get_user_role(db, user_id)
        
        if not role or role not in RoleService.ROLES:
            return False
        
        return permission in RoleService.ROLES[role]['permissions']
    
    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """
        Obtener lista de permisos de un rol
        
        Args:
            role: Nombre del rol
            
        Returns:
            Lista de permisos o lista vacía
        """
        if role not in RoleService.ROLES:
            return []
        
        return RoleService.ROLES[role]['permissions']
    
    @staticmethod
    def assign_role(db: Session, user_id: int, role: str) -> bool:
        """
        Asignar un rol a un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            role: Rol a asignar
            
        Returns:
            True si se asignó correctamente, False en caso contrario
        """
        if role not in RoleService.ROLES:
            return False
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        user.role = role
        db.commit()
        
        return True
    
    @staticmethod
    def get_all_roles() -> Dict[str, Dict]:
        """
        Obtener todos los roles disponibles con sus descripciones
        
        Returns:
            Diccionario con roles y su información
        """
        return RoleService.ROLES
    
    @staticmethod
    def validate_role(role: str) -> bool:
        """
        Validar si un rol existe
        
        Args:
            role: Nombre del rol
            
        Returns:
            True si el rol existe, False en caso contrario
        """
        return role in RoleService.ROLES
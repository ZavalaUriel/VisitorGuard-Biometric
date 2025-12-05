from datetime import datetime
from typing import Optional

class Visit:
    """
    Modelo simplificado de documento MongoDB para Visitas
    
    Estructura del documento:
    - id_persona: ID de la persona (enviado por el cliente, no autogenerado)
    - nombre: Nombre de la persona visitante
    - foto_path: Ruta de la foto guardada
    """
    
    def __init__(
        self,
        id_persona: str,
        nombre: str,
        foto_path: Optional[str] = None
    ):
        self.id_persona = id_persona
        self.nombre = nombre
        self.foto_path = foto_path
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario para MongoDB"""
        return {
            "id_persona": self.id_persona,
            "nombre": self.nombre,
            "foto_path": self.foto_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Visit':
        """Crea un objeto Visit desde un diccionario de MongoDB"""
        return Visit(
            id_persona=data.get("id_persona"),
            nombre=data.get("nombre"),
            foto_path=data.get("foto_path")
        )
    
    def __repr__(self):
        return f"<Visit(id_persona={self.id_persona}, nombre={self.nombre})>"
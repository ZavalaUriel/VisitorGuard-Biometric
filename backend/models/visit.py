from datetime import datetime
from typing import Optional, Dict

class Visit:
    
    def __init__(
        self,
        id_persona: str,
        nombre: str,
        foto_path: Optional[str] = None,
        embedding: Optional[list] = None,
        landmarks: Optional[Dict] = None
    ):
        self.id_persona = id_persona
        self.nombre = nombre
        self.foto_path = foto_path
        self.embedding = embedding
        self.landmarks = landmarks
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id_persona": self.id_persona,
            "nombre": self.nombre,
            "foto_path": self.foto_path,
            "embedding": self.embedding,
            "landmarks": self.landmarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Visit':
        return Visit(
            id_persona=data.get("id_persona"),
            nombre=data.get("nombre"),
            foto_path=data.get("foto_path"),
            embedding=data.get("embedding"),
            landmarks=data.get("landmarks")
        )
    
    def __repr__(self):
        return f"<Visit(id_persona={self.id_persona}, nombre={self.nombre})>"
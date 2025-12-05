from datetime import datetime
from typing import Optional
from bson import ObjectId

class User:
    """
    Modelo de documento MongoDB para Usuarios
    """
    
    def __init__(
        self,
        name: str,
        email: str,
        username: str,
        phone: Optional[str] = None,
        role: str = 'visitor',
        face_encoding: Optional[bytes] = None,
        photo_path: Optional[str] = None,
        is_active: bool = True,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.email = email
        self.username = username
        self.phone = phone
        self.role = role
        self.face_encoding = face_encoding
        self.photo_path = photo_path
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario para MongoDB"""
        return {
            "_id": self._id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "phone": self.phone,
            "role": self.role,
            "face_encoding": self.face_encoding,
            "photo_path": self.photo_path,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Crea un objeto User desde un diccionario de MongoDB"""
        return User(
            _id=data.get("_id"),
            name=data.get("name"),
            email=data.get("email"),
            username=data.get("username"),
            phone=data.get("phone"),
            role=data.get("role", "visitor"),
            face_encoding=data.get("face_encoding"),
            photo_path=data.get("photo_path"),
            is_active=data.get("is_active", True)
        )
    
    def __repr__(self):
        return f"<User(id={self._id}, name={self.name}, role={self.role})>"
"""
Servicio para gestionar las visitas en MongoDB
"""
from datetime import datetime
from typing import List, Optional, Dict
from config.database import get_collection
from models.visit import Visit
from recognition.facial_manager import generate_vector
import os


class VisitService:
    
    def __init__(self):
        self.collection = get_collection('visits')
    
    def create_visit(self, visit_data: Dict) -> str:
        """
        Crea una nueva visita en la base de datos
        
        Args:
            visit_data: Diccionario con id_persona, nombre y opcionalmente foto_path
            
        Returns:
            id_persona de la visita creada
        """
        # Generar embedding si hay foto
        embedding = None
        if visit_data.get('foto_path') and os.path.exists(visit_data['foto_path']):
            try:
                vector = generate_vector(visit_data['foto_path'])
                if vector is not None:
                    embedding = vector.tolist()  # Convertir numpy array a lista
                    print(f"✅ Embedding generado: {len(embedding)} dimensiones")
            except Exception as e:
                print(f"⚠️ Error al generar embedding: {e}")
        
        visit = Visit(
            id_persona=visit_data['id_persona'],
            nombre=visit_data['nombre'],
            foto_path=visit_data.get('foto_path'),
            embedding=embedding
        )
        
        # Usar id_persona como _id en MongoDB
        visit_dict = visit.to_dict()
        visit_dict['_id'] = visit_data['id_persona']
        
        # Insertar o actualizar si ya existe
        self.collection.replace_one(
            {'_id': visit_data['id_persona']},
            visit_dict,
            upsert=True
        )
        
        return visit_data['id_persona']
    
    def get_visit_by_id(self, id_persona: str) -> Optional[Dict]:
        """
        Obtiene una visita por su id_persona
        
        Args:
            id_persona: ID de la persona
            
        Returns:
            Diccionario con los datos de la visita o None
        """
        try:
            visit = self.collection.find_one({'_id': id_persona})
            if visit:
                visit['id_persona'] = visit.pop('_id')
            return visit
        except Exception as e:
            print(f"Error al obtener visita: {e}")
            return None
    
    def get_all_visits(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Obtiene todas las visitas con paginación
        
        Args:
            skip: Número de documentos a saltar
            limit: Número máximo de documentos a retornar
            
        Returns:
            Lista de visitas
        """
        visits = list(self.collection.find().skip(skip).limit(limit))
        for visit in visits:
            visit['id_persona'] = visit.pop('_id')
        return visits
    
    def update_visit(self, id_persona: str, update_data: Dict) -> bool:
        """
        Actualiza una visita existente
        
        Args:
            id_persona: ID de la persona
            update_data: Diccionario con los datos a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': id_persona},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar visita: {e}")
            return False
    
    def delete_visit(self, id_persona: str) -> bool:
        """
        Elimina una visita
        
        Args:
            id_persona: ID de la persona
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            result = self.collection.delete_one({'_id': id_persona})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar visita: {e}")
            return False
    
    def search_by_nombre(self, nombre: str) -> List[Dict]:
        """
        Busca visitas por nombre (búsqueda parcial)
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            
        Returns:
            Lista de visitas que coinciden
        """
        visits = list(self.collection.find({
            'nombre': {'$regex': nombre, '$options': 'i'}
        }))
        for visit in visits:
            visit['id_persona'] = visit.pop('_id')
        return visits
    
    def search_by_name(self, nombre: str) -> List[Dict]:
        """Alias para search_by_nombre"""
        return self.search_by_nombre(nombre)
    
    def get_all_embeddings(self) -> List[Dict]:
        """
        Obtiene todos los embeddings de la base de datos
        
        Returns:
            Lista de diccionarios con id_persona, nombre y embedding
        """
        visits = list(self.collection.find(
            {'embedding': {'$exists': True, '$ne': None}},
            {'_id': 1, 'nombre': 1, 'embedding': 1}
        ))
        for visit in visits:
            visit['id_persona'] = visit.pop('_id')
        return visits


from deepface import DeepFace
import numpy as np
import cv2

def generate_vector(image_path, model_name='Facenet'):
    detectors = ['opencv', 'ssd', 'retinaface']
    
    for detector in detectors:
        try:
            embedding = DeepFace.represent(
                img_path=image_path, 
                model_name=model_name, 
                enforce_detection=False,
                detector_backend=detector
            )
            if embedding and len(embedding) > 0:
                vector_facial = embedding[0]["embedding"]
                return np.array(vector_facial)
        except Exception as e:
            continue
    
    return None


def generate_vector_with_landmarks(image_path, model_name='Facenet'):
    """
    Genera embedding y extrae landmarks faciales completos
    
    Returns:
        dict con 'embedding' y 'landmarks' o None si falla
    """
    detectors = ['opencv', 'ssd', 'retinaface']
    
    for detector in detectors:
        try:
            # Generar embedding con detector actual
            embedding_result = DeepFace.represent(
                img_path=image_path, 
                model_name=model_name, 
                enforce_detection=False,
                detector_backend=detector
            )
            
            if not embedding_result or len(embedding_result) == 0:
                continue
        
            embedding = embedding_result[0]["embedding"]
            facial_area = embedding_result[0].get("facial_area", {})
            
            # NO extraer análisis facial adicional (muy lento, descarga modelos de 500MB+)
            # Omitimos age, gender, race, emotion para mejor rendimiento
            analysis_data = {}
        
            # Construir estructura de landmarks
            landmarks = {
                # Región facial (bounding box)
                'facial_area': {
                    'x': facial_area.get('x', 0),
                    'y': facial_area.get('y', 0),
                    'w': facial_area.get('w', 0),
                    'h': facial_area.get('h', 0)
                },
                # Datos biométricos adicionales
                'biometric_data': {
                    'age': analysis_data.get('age'),
                    'gender': analysis_data.get('dominant_gender'),
                    'race': analysis_data.get('dominant_race'),
                    'emotion': analysis_data.get('dominant_emotion')
                },
                # Coordenadas faciales (calculadas del bounding box)
                'face_coordinates': {
                    'center_x': facial_area.get('x', 0) + facial_area.get('w', 0) // 2,
                    'center_y': facial_area.get('y', 0) + facial_area.get('h', 0) // 2,
                    'top': facial_area.get('y', 0),
                    'bottom': facial_area.get('y', 0) + facial_area.get('h', 0),
                    'left': facial_area.get('x', 0),
                    'right': facial_area.get('x', 0) + facial_area.get('w', 0)
                },
                # Metadata
                'detection_confidence': facial_area.get('confidence', 1.0),
                'model_used': model_name,
                'detector_backend': detector
            }
            
            return {
                'embedding': np.array(embedding),
                'landmarks': landmarks
            }
            
        except Exception as e:
            continue
    
    # Si todos los detectores fallaron
    return None


def verify_faces(image_path1, image_path2, model_name='Facenet', distance_metric='cosine'):
    try:
        result = DeepFace.verify(img1_path=image_path1, img2_path=image_path2, model_name=model_name, distance_metric=distance_metric, enforce_detection=True)
        return result
    except ValueError as ve:
        print("ValueError:", ve) 
        return None
    except Exception as e:
        print(f"Error verificando rostros: {e}")
        return None


def compare_embeddings(embedding1, embedding2, distance_metric='cosine'):
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        if distance_metric == 'cosine':
            distance = 1 - np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            threshold = 0.40
        elif distance_metric == 'euclidean':
            distance = np.linalg.norm(vec1 - vec2)
            threshold = 10.0
        else:
            distance = np.linalg.norm(vec1 - vec2)
            threshold = 10.0
        
        verified = distance < threshold
        
        return {
            'distance': float(distance),
            'threshold': float(threshold),
            'verified': bool(verified),
            'distance_metric': distance_metric
        }
    except Exception as e:
        print(f"Error comparando embeddings: {e}")
        return None

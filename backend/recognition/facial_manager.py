from deepface import DeepFace
import numpy as np

def generate_vector(image_path, model_name='Facenet'):

    try :

        embedding = DeepFace.represent(img_path = image_path, model_name = model_name, enforce_detection=True)
        vector_facial = embedding[0]["embedding"]

        return np.array(vector_facial)
    
    except ValueError as ve:
        print("ValueError:", ve)
        return None
    

def verify_faces(image_path1, image_path2, model_name='Facenet', distance_metric='cosine'):

    try:
        result = DeepFace.verify(img1_path = image_path1, img2_path = image_path2, model_name = model_name, distance_metric=distance_metric, enforce_detection=True)
        return result
    
    except ValueError as ve:
        print("ValueError:", ve)
        return None
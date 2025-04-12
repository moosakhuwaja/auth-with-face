import bcrypt
import secrets
from datetime import datetime, timedelta
from .models import User, Session

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_session(user):
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=1)
    Session.objects.create(user=user, session_token=token, expires_at=expires)
    return token



# face recog 
import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO
import base64
def extract_face_encoding(image_data):
    img_bytes = base64.b64decode(image_data.split(';base64,')[1])
    img = Image.open(BytesIO(img_bytes))
    img_np = np.array(img)

    face_locations = face_recognition.face_locations(img_np)
    if face_locations:
        face_encodings = face_recognition.face_encodings(img_np, face_locations)
        return face_encodings[0].tolist()  # Return first face's encoding
    return None


def find_user_by_face(image_data, users):
    # Decode the base64 image
    image_data = image_data.split(',')[1]  # Remove header if present
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    image_np = np.array(image)

    # Get encoding for the current captured face
    current_encodings = face_recognition.face_encodings(image_np)
    if not current_encodings:
        return None  # No face found

    current_encoding = current_encodings[0]  # Only one face expected

    for user in users:
        if user.face_encoding:
            # Ensure face_embedding is converted to a numpy array
            user_encoding = np.array(user.face_encoding)

            # face_distance expects a list of encodings and one to compare
            distance = face_recognition.face_distance([user_encoding], current_encoding)[0]

            if distance < 0.5:  # Adjust threshold if needed
                return user

    return None  # No match


def detect_face_in_image(image_data):
    # Convert the base64 image data to bytes
    import base64
    from io import BytesIO
    from PIL import Image

    # Remove the prefix from base64 data
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)

    # Load the image
    image = Image.open(BytesIO(image_bytes))
    image = np.array(image)

    # Find all face locations
    face_locations = face_recognition.face_locations(image)
    return len(face_locations) > 0 
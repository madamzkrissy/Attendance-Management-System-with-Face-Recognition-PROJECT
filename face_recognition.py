"""
Face Recognition Module for Attendance System
Handles encoding generation and face matching
"""

import os
import pickle
import numpy as np
import cv2
import face_recognition
from datetime import datetime

class FaceRecognitionEngine:
    """Face recognition engine for attendance system"""
    
    def __init__(self, encodings_dir='encodings'):
        """Initialize the face recognition engine"""
        self.encodings_dir = encodings_dir
        self.tolerance = 0.6
        self.known_encodings = {}
        self.known_sr_codes = {}
        
        # Create encodings directory if it doesn't exist
        os.makedirs(encodings_dir, exist_ok=True)
        
        # Load all known encodings
        self.load_known_encodings()
    
    def load_known_encodings(self):
        """Load all known face encodings from disk"""
        try:
            for filename in os.listdir(self.encodings_dir):
                if filename.endswith('.pkl'):
                    sr_code = filename.replace('.pkl', '')
                    filepath = os.path.join(self.encodings_dir, filename)
                    
                    with open(filepath, 'rb') as f:
                        encoding = pickle.load(f)
                        self.known_encodings[sr_code] = encoding
                        self.known_sr_codes[sr_code] = sr_code
            
            print(f"Loaded {len(self.known_encodings)} face encodings")
        except Exception as e:
            print(f"Error loading encodings: {e}")
    
    def save_face_encoding(self, image, sr_code):
        """
        Extract and save face encoding for a student
        
        Args:
            image: Image file or numpy array
            sr_code: Student SR code
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read image if file path is provided
            if isinstance(image, str):
                img = cv2.imread(image)
                if img is None:
                    return False
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img = image
            
            # Detect faces
            face_locations = face_recognition.face_locations(img)
            
            if not face_locations:
                return False
            
            if len(face_locations) > 1:
                print("Multiple faces detected. Using the first one.")
            
            # Generate encoding for the first face
            face_encodings = face_recognition.face_encodings(img, face_locations)
            
            if not face_encodings:
                return False
            
            # Save encoding
            encoding_path = os.path.join(self.encodings_dir, f"{sr_code}.pkl")
            
            with open(encoding_path, 'wb') as f:
                pickle.dump(face_encodings[0], f)
            
            # Update in-memory cache
            self.known_encodings[sr_code] = face_encodings[0]
            self.known_sr_codes[sr_code] = sr_code
            
            print(f"Face encoding saved for {sr_code}")
            return True
        
        except Exception as e:
            print(f"Error saving face encoding: {e}")
            return False
    
    def recognize_face(self, image, known_sr_codes=None):
        """
        Recognize faces in an image
        
        Args:
            image: Image file path or numpy array
            known_sr_codes: List of specific SR codes to match against (optional)
            
        Returns:
            list: List of tuples (sr_code, confidence) for recognized faces
        """
        try:
            # Read image if file path is provided
            if isinstance(image, str):
                img = cv2.imread(image)
                if img is None:
                    return []
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img = image
            
            # Detect faces
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            
            if not face_encodings:
                return []
            
            results = []
            
            # Use specific SR codes or all known codes
            sr_codes_to_check = known_sr_codes if known_sr_codes else list(self.known_encodings.keys())
            
            for face_encoding in face_encodings:
                matches = {}
                
                for sr_code in sr_codes_to_check:
                    if sr_code in self.known_encodings:
                        known_encoding = self.known_encodings[sr_code]
                        
                        # Compare faces
                        face_distances = face_recognition.face_distance([known_encoding], face_encoding)
                        
                        if face_distances[0] < self.tolerance:
                            confidence = 1 - face_distances[0]
                            matches[sr_code] = confidence
                
                # Find best match
                if matches:
                    best_match = max(matches, key=matches.get)
                    results.append((best_match, matches[best_match]))
            
            return results
        
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return []
    
    def recognize_face_in_section(self, image, section_sr_codes):
        """
        Recognize a face from a specific section's students
        
        Args:
            image: Image file path or numpy array
            section_sr_codes: List of SR codes in the section
            
        Returns:
            tuple: (sr_code, confidence) if recognized, None otherwise
        """
        results = self.recognize_face(image, section_sr_codes)
        
        if results:
            return results[0]  # Return best match
        
        return None
    
    def delete_encoding(self, sr_code):
        """Delete face encoding for a student"""
        try:
            encoding_path = os.path.join(self.encodings_dir, f"{sr_code}.pkl")
            
            if os.path.exists(encoding_path):
                os.remove(encoding_path)
                
                # Remove from cache
                if sr_code in self.known_encodings:
                    del self.known_encodings[sr_code]
                if sr_code in self.known_sr_codes:
                    del self.known_sr_codes[sr_code]
                
                print(f"Face encoding deleted for {sr_code}")
                return True
            
            return False
        
        except Exception as e:
            print(f"Error deleting face encoding: {e}")
            return False
    
    def update_tolerance(self, tolerance):
        """Update face recognition tolerance (0-1)"""
        if 0 <= tolerance <= 1:
            self.tolerance = tolerance
            return True
        return False

# Initialize global face recognition engine
face_engine = FaceRecognitionEngine()

def extract_face_from_frame(frame):
    """Extract face from a video frame"""
    try:
        if frame is None:
            return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            # Return the first face location
            top, right, bottom, left = face_locations[0]
            return rgb_frame[top:bottom, left:right]
        
        return None
    
    except Exception as e:
        print(f"Error extracting face: {e}")
        return None

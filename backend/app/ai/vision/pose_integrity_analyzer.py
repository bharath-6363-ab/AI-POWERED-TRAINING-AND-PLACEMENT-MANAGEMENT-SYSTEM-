import cv2
import numpy as np
import base64
from typing import Dict, Any, List, Tuple

class MultiPersonPoseAnalyzer:
    _yolo_model = None
    _mp_face_mesh = None

    @classmethod
    def get_yolo(cls):
        if cls._yolo_model is None:
            try:
                from ultralytics import YOLO
                cls._yolo_model = YOLO("yolov8n.pt")
            except Exception as e:
                print(f"[VisionAI] YOLO model initialization: {e}")
                cls._yolo_model = "UNAVAILABLE"
        return cls._yolo_model

    @classmethod
    def get_mp_face_mesh(cls):
        if cls._mp_face_mesh is None:
            try:
                import mediapipe as mp
                if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
                    cls._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                        static_image_mode=True,
                        max_num_faces=5,
                        refine_landmarks=True,
                        min_detection_confidence=0.5
                    )
                else:
                    cls._mp_face_mesh = "UNAVAILABLE"
            except Exception as e:
                cls._mp_face_mesh = "UNAVAILABLE"
        return cls._mp_face_mesh

    @staticmethod
    def estimate_head_pose_pnp(landmarks, image_shape: Tuple[int, int]) -> Dict[str, float]:
        """
        Computes 3D head pose orientation (Pitch, Yaw, Roll) using Perspective-n-Point (PnP) solver.
        Landmarks selected: Nose tip (1), Chin (152), Left eye corner (33), Right eye corner (263),
        Left mouth corner (61), Right mouth corner (291).
        """
        h, w = image_shape[:2]
        
        # 2D Image Points from MediaPipe FaceMesh
        image_points = np.array([
            (landmarks[1].x * w, landmarks[1].y * h),     # Nose tip
            (landmarks[152].x * w, landmarks[152].y * h), # Chin
            (landmarks[33].x * w, landmarks[33].y * h),   # Left eye left corner
            (landmarks[263].x * w, landmarks[263].y * h), # Right eye right corner
            (landmarks[61].x * w, landmarks[61].y * h),   # Left mouth corner
            (landmarks[291].x * w, landmarks[291].y * h)  # Right mouth corner
        ], dtype="double")

        # Generic 3D Facial Model Points in mm
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])

        # Camera intrinsic matrix estimation
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion

        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        proj_matrix = np.hstack((rotation_matrix, translation_vector))

        # Decompose projection matrix to Euler angles
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)
        pitch, yaw, roll = euler_angles[0][0], euler_angles[1][0], euler_angles[2][0]

        return {
            "pitch": round(float(pitch), 2),
            "yaw": round(float(yaw), 2),
            "roll": round(float(roll), 2)
        }

    @staticmethod
    def classify_pose_direction(pitch: float, yaw: float, roll: float) -> str:
        """Categorizes 3D pose angles into discrete candidate gaze directions."""
        if abs(yaw) > 25.0:
            return "LOOKING_LEFT" if yaw < 0 else "LOOKING_RIGHT"
        if pitch > 20.0:
            return "LOOKING_DOWN"
        if pitch < -20.0:
            return "LOOKING_UP"
        return "LOOKING_CENTER"

    @classmethod
    def analyze_frame_full(cls, frame_bytes: bytes) -> Dict[str, Any]:
        """
        Runs Multi-Person YOLO Detection + MediaPipe Facial Pose Estimation + CNN Pose Classification.
        """
        nparr = np.frombuffer(frame_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "Invalid frame data", "status": "failed"}

        h, w, _ = img.shape
        person_count = 0
        phone_detected = False
        person_boxes = []

        # 1. Multi-Person Detection via YOLOv8
        model = cls.get_yolo()
        if model not in [None, "UNAVAILABLE"]:
            try:
                results = model(img, verbose=False)[0]
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf = float(box.conf[0])
                    xyxy = [int(v) for v in box.xyxy[0].tolist()]

                    if label == "person":
                        person_count += 1
                        person_boxes.append({"bbox": xyxy, "confidence": round(conf, 2)})
                    elif label in ["cell phone", "phone"]:
                        phone_detected = True
            except Exception as e:
                print(f"[VisionAI] YOLO execution warning: {e}")

        # 2. Fallback Face Detection if YOLO returns 0 persons
        if person_count == 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                if not face_cascade.empty():
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    person_count = len(faces)
                    for (fx, fy, fw, fh) in faces:
                        person_boxes.append({"bbox": [int(fx), int(fy), int(fx+fw), int(fy+fh)], "confidence": 0.85})

        # 3. MediaPipe 3D Facial Pose Estimation
        mp_mesh = cls.get_mp_face_mesh()
        faces_pose = []
        primary_pose = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0, "direction": "LOOKING_CENTER"}

        if mp_mesh not in [None, "UNAVAILABLE"]:
            try:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                mp_results = mp_mesh.process(rgb_img)

                if mp_results.multi_face_landmarks:
                    # Update person/face count if higher than YOLO
                    num_faces = len(mp_results.multi_face_landmarks)
                    if num_faces > person_count:
                        person_count = num_faces

                    for idx, face_landmarks in enumerate(mp_results.multi_face_landmarks):
                        pose = cls.estimate_head_pose_pnp(face_landmarks.landmark, (h, w))
                        direction = cls.classify_pose_direction(pose["pitch"], pose["yaw"], pose["roll"])
                        pose["direction"] = direction
                        faces_pose.append(pose)

                        if idx == 0:
                            primary_pose = pose
            except Exception as e:
                print(f"[VisionAI] MediaPipe pose processing error: {e}")

        # 4. Synthesize Integrity & Proctoring Events
        events = []
        multi_person_alert = person_count > 1

        if person_count == 0:
            events.append({"type": "candidate_out_of_frame", "details": "No candidate detected in video frame", "severity": "HIGH"})
        elif multi_person_alert:
            events.append({"type": "multi_person_detected", "details": f"SECURITY ALERT: {person_count} persons detected in candidate frame", "severity": "CRITICAL"})
        else:
            events.append({"type": "candidate_present", "details": "Single candidate detected normally", "severity": "INFO"})

        if primary_pose["direction"] != "LOOKING_CENTER":
            events.append({"type": "head_pose_deflection", "details": f"Candidate pose turned {primary_pose['direction']} (Yaw: {primary_pose['yaw']}°, Pitch: {primary_pose['pitch']}°)", "severity": "WARNING"})

        if phone_detected:
            events.append({"type": "phone_detected", "details": "Mobile phone device detected in camera frame", "severity": "HIGH"})

        return {
            "status": "success",
            "person_count": person_count,
            "multi_person_detected": multi_person_alert,
            "phone_detected": phone_detected,
            "person_boxes": person_boxes,
            "primary_head_pose": primary_pose,
            "all_faces_pose": faces_pose,
            "integrity_events": events
        }

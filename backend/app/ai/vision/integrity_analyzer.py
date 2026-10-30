import cv2
import numpy as np
import base64
from typing import Dict, Any, List
from backend.app.ai.vision.pose_integrity_analyzer import MultiPersonPoseAnalyzer

class VisionIntegrityAnalyzer:
    @staticmethod
    def analyze_frame_bytes(frame_bytes: bytes) -> Dict[str, Any]:
        """
        Delegates frame analysis to MultiPersonPoseAnalyzer to return YOLO detection,
        MediaPipe 3D head pose (Pitch, Yaw, Roll), person count, and integrity events.
        """
        return MultiPersonPoseAnalyzer.analyze_frame_full(frame_bytes)

    @staticmethod
    def analyze_frame_base64(base64_str: str) -> Dict[str, Any]:
        """Processes base64 encoded JPEG/PNG frame sent from HTML5 webcam canvas."""
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            frame_bytes = base64.b64decode(base64_str)
            return MultiPersonPoseAnalyzer.analyze_frame_full(frame_bytes)
        except Exception as e:
            return {"status": "failed", "error": f"Base64 decoding failed: {str(e)}"}


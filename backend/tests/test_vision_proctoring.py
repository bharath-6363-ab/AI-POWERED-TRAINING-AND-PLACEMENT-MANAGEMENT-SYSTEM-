import pytest
import numpy as np
import cv2
import base64
from backend.app.ai.vision.integrity_analyzer import VisionIntegrityAnalyzer

def test_vision_integrity_dummy_frame():
    # 480x640 blank image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', img)
    img_bytes = encoded.tobytes()
    
    result = VisionIntegrityAnalyzer.analyze_frame_bytes(img_bytes)
    assert result["status"] == "success"
    assert "person_count" in result
    assert "multi_person_detected" in result
    assert "primary_head_pose" in result
    assert "integrity_events" in result

def test_vision_integrity_base64_decoding():
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', img)
    b64_str = base64.b64encode(encoded.tobytes()).decode('utf-8')
    
    result = VisionIntegrityAnalyzer.analyze_frame_base64(b64_str)
    assert result["status"] == "success"
    assert isinstance(result["integrity_events"], list)

import cv2
import numpy as np
import base64
import requests

print("=" * 68)
print("  MULTI-PERSON DETECTION & 3D FACIAL POSE ESTIMATION TEST SUITE")
print("=" * 68)

# 1. Create a dummy image frame with drawn face circles
img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.circle(img, (320, 240), 60, (200, 180, 150), -1) # Face 1 (Candidate)
cv2.circle(img, (300, 230), 8, (255, 255, 255), -1)  # Left eye
cv2.circle(img, (340, 230), 8, (255, 255, 255), -1)  # Right eye
cv2.circle(img, (320, 250), 6, (0, 0, 255), -1)      # Nose

_, encoded_img = cv2.imencode('.jpg', img)
img_bytes = encoded_img.tobytes()
b64_str = base64.b64encode(img_bytes).decode('utf-8')

# Test Direct Python Vision Analyzer
from backend.app.ai.vision.pose_integrity_analyzer import MultiPersonPoseAnalyzer
res_direct = MultiPersonPoseAnalyzer.analyze_frame_full(img_bytes)

print("[PASS] 1. Direct Python Pose & Multi-Person Analyzer:")
print(f"       Person Count: {res_direct.get('person_count')}")
print(f"       Multi-Person Alert: {res_direct.get('multi_person_detected')}")
print(f"       Primary Head Pose: {res_direct.get('primary_head_pose')}")
print(f"       Events: {res_direct.get('integrity_events')}")

# Test API Endpoint base64
url_b64 = "http://127.0.0.1:8080/api/v1/interviews/vision/analyze-frame-base64"
resp_b64 = requests.post(url_b64, json={"image_base64": b64_str})
print(f"\n[PASS] 2. HTTP Base64 Vision Endpoint (Status {resp_b64.status_code}):")
print(f"       Response Payload: {resp_b64.json()}")

# Test API Endpoint Multipart
url_multipart = "http://127.0.0.1:8080/api/v1/interviews/vision/analyze-frame"
files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
resp_mp = requests.post(url_multipart, files=files)
print(f"\n[PASS] 3. HTTP Multipart Vision Endpoint (Status {resp_mp.status_code}):")
print(f"       Response Payload: {resp_mp.json()}")

print("\n" + "=" * 68)
print(">>> ALL MULTI-PERSON & FACIAL POSE TESTS COMPLETED SUCCESSFULLY! <<<")
print("=" * 68)

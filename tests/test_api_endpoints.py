"""
API Entegrasyon Testleri (FastAPI Server Endpoints)
MRT Güç Sistemleri & Harran Üniversitesi
"""

import unittest
import threading
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path
import cv2
import numpy as np

import uvicorn
import config
from server import app


class TestServerEndpoints(unittest.TestCase):
    server_thread = None
    server_port = 8765

    @classmethod
    def setUpClass(cls):
        # Bağımsız bir test portunda FastAPI sunucusunu thread olarak başlat
        config_obj = uvicorn.Config(app, host="127.0.0.1", port=cls.server_port, log_level="warning")
        cls.server = uvicorn.Server(config_obj)
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()
        time.sleep(1.0)  # Sunucunun dinlemeye geçmesini bekle

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        time.sleep(0.5)

    def _get(self, path: str):
        url = f"http://127.0.0.1:{self.server_port}{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data)

    def _post(self, path: str, payload: dict):
        url = f"http://127.0.0.1:{self.server_port}{path}"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data)

    def _delete(self, path: str):
        url = f"http://127.0.0.1:{self.server_port}{path}"
        req = urllib.request.Request(url, method="DELETE")
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data)

    def test_01_api_status(self):
        status, data = self._get("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("Muhammed Emin", data["student"])

    def test_02_api_samples(self):
        status, data = self._get("/api/samples")
        self.assertEqual(status, 200)
        self.assertIn("images", data)
        self.assertIn("videos", data)
        self.assertTrue(len(data["images"]) > 0)
        self.assertTrue(len(data["videos"]) > 0)

    def test_03_api_simulate(self):
        payload = {
            "scenario": "DUST_STORM",
            "base_image": "panel_clean.jpg",
            "dust": 0.5,
            "noise": 0.0,
            "brightness": 0.0,
            "arc": 0.0,
            "panel_id": "MRT-TEST-PANO"
        }
        status, data = self._post("/api/simulate", payload)
        self.assertEqual(status, 200)
        self.assertIn("metrics", data)
        self.assertIn("images", data)
        self.assertIn("heatmap", data["images"])

    def test_04_api_extract_video_frame(self):
        payload = {"video_name": "video_arc_fault.mp4"}
        status, data = self._post("/api/extract-video-frame", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("filename", data)
        self.assertTrue(data["filename"].startswith("video_frame_"))

        # Test sonrası üretilen frame'i sil
        img_name = data["filename"]
        del_status, del_data = self._delete(f"/api/samples/image/{img_name}")
        self.assertEqual(del_status, 200)
        self.assertTrue(del_data["success"])

    def test_05_api_generate_pdf(self):
        payload = {
            "scenario": "NORMAL",
            "base_image": "panel_clean.jpg",
            "dust": 0.0,
            "noise": 0.0,
            "brightness": 0.0,
            "arc": 0.0,
            "panel_id": "MRT-TEST-PDF"
        }
        status, data = self._post("/api/generate-pdf", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("download_url", data)

    def test_06_api_generate_video_pdf(self):
        payload = {
            "video_name": "video_normal_panel.mp4",
            "panel_id": "MRT-VIDEO-TEST"
        }
        status, data = self._post("/api/generate-video-pdf", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("download_url", data)

    def test_07_api_records_and_delete(self):
        # Kayıtları oku
        status, data = self._get("/api/records")
        self.assertEqual(status, 200)
        records = data["records"]
        self.assertTrue(len(records) > 0)

        # İlk kaydı sil
        rec_id = records[0]["id"]
        del_status, del_data = self._delete(f"/api/records/{rec_id}")
        self.assertEqual(del_status, 200)
        self.assertTrue(del_data["success"])

    def test_08_api_photo_upload_and_delete(self):
        # Sentetik resim oluştur ve multipart/form-data ile yükle
        img = np.full((100, 100, 3), 120, dtype=np.uint8)
        _, img_buf = cv2.imencode(".jpg", img)
        file_bytes = img_buf.tobytes()

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="unit_test_photo.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8") + file_bytes + (
            f"\r\n--{boundary}\r\n"
            f'Content-Disposition: form-data; name="panel_id"\r\n\r\n'
            f"MRT-TEST-PANO\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        url = f"http://127.0.0.1:{self.server_port}/api/upload-photo"
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertTrue(data["success"])
            filename = data["filename"]

        # Yüklenen fotoğrafı sil
        del_status, del_data = self._delete(f"/api/samples/image/{filename}")
        self.assertEqual(del_status, 200)
        self.assertTrue(del_data["success"])


if __name__ == "__main__":
    unittest.main()

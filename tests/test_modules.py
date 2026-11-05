"""
Sistem Birim ve Entegrasyon Testleri (Unit & Integration Tests)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi
"""

import os
import unittest
import numpy as np
import cv2
from pathlib import Path

import config
from modules.data_acquisition import ImageLoader, VideoFileReader
from modules.metrics_engine import QualityMetricsEngine
from modules.simulator import FieldConditionSimulator
from modules.dynamic_analysis import FPSMeter, VibrationAnalyzer
from modules.database import DatabaseManager
from modules.report_generator import QualityReportGenerator


class TestCameraQualitySystem(unittest.TestCase):

    def setUp(self):
        # 300x300 sentetik temiz kare oluştur
        self.sample_img = np.full((300, 300, 3), 100, dtype=np.uint8)
        cv2.rectangle(self.sample_img, (50, 50), (250, 250), (200, 200, 200), -1)
        cv2.putText(self.sample_img, 'TEST MRT', (60, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    def test_01_image_loader(self):
        """Örnek pano görselinin doğru yüklendiğini test eder."""
        test_path = config.SAMPLE_IMAGES_DIR / "panel_clean.jpg"
        success, img, msg = ImageLoader.load(test_path)
        self.assertTrue(success, f"Görsel yüklenemedi: {msg}")
        self.assertIsNotNone(img)
        self.assertEqual(len(img.shape), 3)

    def test_02_metrics_engine(self):
        """Metrik hesaplama motorunun tüm çıktılarını doğrular."""
        results = QualityMetricsEngine.evaluate_frame(self.sample_img)
        self.assertIn("sharpness", results)
        self.assertIn("noise_sigma", results)
        self.assertIn("brightness", results)
        self.assertIn("contrast", results)
        self.assertIn("overall_score", results)
        self.assertIn("final_verdict", results)
        self.assertTrue(0 <= results["overall_score"] <= 100)

    def test_03_field_simulator(self):
        """Saha simülatörünün senaryolarını test eder."""
        dusty = FieldConditionSimulator.apply_dust_and_blur(self.sample_img, 0.8)
        self.assertEqual(dusty.shape, self.sample_img.shape)

        res_clean = QualityMetricsEngine.evaluate_frame(self.sample_img)
        res_dusty = QualityMetricsEngine.evaluate_frame(dusty)
        self.assertLess(res_dusty["sharpness"], res_clean["sharpness"])

        arc_img = FieldConditionSimulator.apply_electrical_arc(self.sample_img, 0.9)
        res_arc = QualityMetricsEngine.evaluate_frame(arc_img)
        self.assertTrue(res_arc["has_arc"])

    def test_04_vibration_analyzer(self):
        """Optik akış titreşim analizörünü test eder."""
        analyzer = VibrationAnalyzer()
        res1 = analyzer.process_frame(self.sample_img)
        self.assertIn("mean_vibration", res1)

        M = np.float32([[1, 0, 10], [0, 1, 0]])
        shifted = cv2.warpAffine(self.sample_img, M, (300, 300))
        res2 = analyzer.process_frame(shifted)
        self.assertGreater(res2["mean_vibration"], 0.0)

    def test_05_database_manager_crud(self):
        """SQLite veritabanına kayıt yazma, okuma ve SİLME işlemlerini test eder."""
        db = DatabaseManager()
        data = {
            "source_type": "UNIT_TEST",
            "panel_id": "MRT-TEST-CRUD",
            "sharpness": 165.2,
            "sharpness_status": "NORMAL",
            "noise_sigma": 5.4,
            "noise_status": "NORMAL",
            "brightness": 120.0,
            "contrast": 45.0,
            "has_arc": False,
            "arc_ratio": 0.0,
            "vibration": 0.5,
            "overall_score": 92.5,
            "final_verdict": "ONAYLANDI",
            "report_path": "outputs/reports/test_crud.pdf"
        }
        # 1. Ekle
        rec_id = db.insert_record(data)
        self.assertGreater(rec_id, 0)

        # 2. Oku
        rec = db.get_record(rec_id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["panel_id"], "MRT-TEST-CRUD")

        # 3. Sil
        deleted = db.delete_record(rec_id)
        self.assertTrue(deleted)
        self.assertIsNone(db.get_record(rec_id))

    def test_06_report_generator_turkish_unicode(self):
        """ReportLab ile Türkçe karakterlerin bozulmadan PDF oluşturulduğunu test eder."""
        metrics = QualityMetricsEngine.evaluate_frame(self.sample_img)
        metrics["final_verdict"] = "ONAYLANDI: ŞANLIURFA TRAFO HÜCRESİ IŞIK ŞARTLARI UYGUNDUR"
        pdf_path = QualityReportGenerator.generate_pdf(
            frame_bgr=self.sample_img,
            metrics=metrics,
            panel_id="MRT-ŞALTER-01",
            source_type="TÜRKÇE_TESTİ"
        )
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 5000)


if __name__ == "__main__":
    unittest.main()

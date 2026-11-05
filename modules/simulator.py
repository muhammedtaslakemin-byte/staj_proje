"""
Modül 4: Web Tabanlı Saha ve Anormallik Simülatörü (Field Simulator)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi

Jüri sunumunda ve saha testlerinde fiziksel toz/ark gerektirmeden
tüm arıza koşullarını canlı olarak simüle eden çekirdek modüldür.
"""

import math
import random
import cv2
import numpy as np
from typing import Tuple, Dict, Any


class FieldConditionSimulator:
    """
    Şanlıurfa ve endüstriyel saha şartlarını (Toz fırtınası, 45°C termal gürültü,
    şalter arkı, jeneratör titreşimi, gece karanlığı) matematiksel modellerle simüle eder.
    """

    @staticmethod
    def apply_dust_and_blur(image_bgr: np.ndarray, dust_level: float) -> np.ndarray:
        """
        Tozlanma ve odak kaybı simülasyonu.
        dust_level: 0.0 (Temiz) - 1.0 (Şiddetli Toz Fırtınası)
        """
        if dust_level <= 0.01:
            return image_bgr.copy()

        result = image_bgr.astype(np.float32)

        # 1. Gauss Bulanıklığı (Odak Kaybı / Mercek Kirliği)
        k_size = int(dust_level * 30) * 2 + 1  # 1 ile 61 arası tek sayı
        blurred = cv2.GaussianBlur(result, (k_size, k_size), sigmaX=dust_level * 15.0)

        # 2. Toz Perdesi Rengi (Toprak / Kum Sarısı rengi katmanı)
        dust_overlay = np.full_like(result, (120, 150, 190), dtype=np.float32)  # BGR Kum rengi
        alpha = dust_level * 0.45  # Kontrast zayıflatma oranı

        blended = (1.0 - alpha) * blurred + alpha * dust_overlay
        return np.clip(blended, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_sensor_noise(image_bgr: np.ndarray, noise_level: float) -> np.ndarray:
        """
        Yüksek sıcaklık (45°C) ve düşük ışık kaynaklı sensör termal gürültüsü.
        noise_level: 0.0 (Temiz) - 1.0 (Kritik Gren)
        """
        if noise_level <= 0.01:
            return image_bgr.copy()

        h, w, c = image_bgr.shape
        sigma = noise_level * 50.0  # Standart sapma
        gauss = np.random.normal(0, sigma, (h, w, c)).astype(np.float32)

        noisy = image_bgr.astype(np.float32) + gauss

        # Tuz & Biber (Salt and Pepper) paraziti
        if noise_level > 0.4:
            sp_prob = (noise_level - 0.4) * 0.05
            num_sp = int(sp_prob * h * w)
            for _ in range(num_sp):
                y = random.randint(0, h - 1)
                x = random.randint(0, w - 1)
                color = 255 if random.random() > 0.5 else 0
                noisy[y, x] = [color, color, color]

        return np.clip(noisy, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_lighting_adjustment(image_bgr: np.ndarray, brightness_factor: float) -> np.ndarray:
        """
        Işık ayarı.
        brightness_factor: -100 (Tam Karanlık) ile +100 (Aşırı Aydınlık)
        """
        if abs(brightness_factor) < 1.0:
            return image_bgr.copy()

        # cv2.convertScaleAbs ile güvenli parlaklık ayarı
        adjusted = cv2.convertScaleAbs(image_bgr, alpha=1.0, beta=brightness_factor)
        return adjusted

    @staticmethod
    def apply_electrical_arc(image_bgr: np.ndarray, arc_intensity: float, center: Tuple[int, int] = None) -> np.ndarray:
        """
        Elektriksel ark patlaması ve doygunluk simülasyonu.
        arc_intensity: 0.0 (Yok) - 1.0 (Şiddetli Ark Parlaması)
        """
        if arc_intensity <= 0.01:
            return image_bgr.copy()

        h, w, c = image_bgr.shape
        if center is None:
            center = (w // 2, h // 2)

        result = image_bgr.astype(np.float32)

        # 1. Genel sahne parlaması (Flash)
        flash = np.full_like(result, (230, 240, 255), dtype=np.float32)
        scene_alpha = arc_intensity * 0.6
        result = (1.0 - scene_alpha) * result + scene_alpha * flash

        # 2. Ark merkezinde aşırı parlak çekirdek ve radyal halesi
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        radius = int(min(h, w) * (0.35 + arc_intensity * 0.3))

        mask = np.clip(1.0 - (dist_from_center / radius), 0.0, 1.0)
        mask = (mask ** 1.8) * arc_intensity * 255.0

        for ch in range(3):
            result[:, :, ch] += mask

        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_vibration(image_bgr: np.ndarray, vibration_level: float, step: int = 0) -> np.ndarray:
        """
        Mekanik titreşim simülasyonu (Afif dönüşüm matrisi ile piksel kaydırma).
        vibration_level: 0.0 (Sabit) - 1.0 (Şiddetli Sarsıntı)
        step: Sinüzoidal hareket için zaman adımı.
        """
        if vibration_level <= 0.01:
            return image_bgr.copy()

        h, w = image_bgr.shape[:2]
        max_shift = vibration_level * 25.0

        # Sinüs dalgası + rastgele mikro titreme
        dx = max_shift * math.sin(step * 0.8) + (random.random() - 0.5) * max_shift * 0.3
        dy = max_shift * math.cos(step * 1.1) + (random.random() - 0.5) * max_shift * 0.3

        M = np.float32([[1, 0, dx], [0, 1, dy]])
        shifted = cv2.warpAffine(image_bgr, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        return shifted

    @classmethod
    def apply_scenario(cls, base_image: np.ndarray, scenario_name: str, step: int = 0) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Jüri sunumunda tek tıkla çalıştırılabilecek 5 hazır endüstriyel senaryo.
        """
        params = {
            "dust": 0.0,
            "noise": 0.0,
            "brightness": 0.0,
            "arc": 0.0,
            "vibration": 0.0,
            "title": "Normal Çalışma",
            "description": "Herhangi bir anormallik bulunmuyor."
        }

        if scenario_name == "NORMAL":
            params.update({
                "title": "Normal Pano (Yeşil Onay)",
                "description": "Tüm parametreler ISO standartlarında, keskinlik yüksek, gürültü minimum seviyede."
            })

        elif scenario_name == "DUST_STORM":
            params.update({
                "dust": 0.75,
                "brightness": -15.0,
                "title": "Şanlıurfa Toz Fırtınası",
                "description": "Mercek üzerinde aşırı toz tabakası birikti. Odak varyansı <80 altına düştü, temizlik alarmı tetiklendi."
            })

        elif scenario_name == "NIGHT_NOISE":
            params.update({
                "brightness": -75.0,
                "noise": 0.65,
                "title": "Gece Vardiyası / Yetersiz Işık",
                "description": "Aydınlatma yetersizliği nedeniyle sensör kazancı (gain) arttı, yüksek termal gren ve gürültü oluştu."
            })

        elif scenario_name == "ELECTRICAL_ARC":
            params.update({
                "arc": 0.90,
                "title": "Şalter Açma / Elektriksel Ark",
                "description": "Pano hücresinde ani elektriksel ark parlaması oluştu. Doygun piksel oranı >%15'i aşarak kritik acil durum alarmı verdi."
            })

        elif scenario_name == "GENERATOR_VIBRATION":
            params.update({
                "vibration": 0.85,
                "title": "Jeneratör Mekanik Titreşimi",
                "description": "Dizel jeneratör ünitesinde mekanik rezonans ve sarsıntı başladı. Optik akış vektörleri sınır değerleri aştı."
            })

        # Parametreleri sırayla uygula
        out = base_image.copy()
        if params["vibration"] > 0:
            out = cls.apply_vibration(out, params["vibration"], step)
        if params["dust"] > 0:
            out = cls.apply_dust_and_blur(out, params["dust"])
        if params["noise"] > 0:
            out = cls.apply_sensor_noise(out, params["noise"])
        if abs(params["brightness"]) > 0:
            out = cls.apply_lighting_adjustment(out, params["brightness"])
        if params["arc"] > 0:
            out = cls.apply_electrical_arc(out, params["arc"])

        return out, params


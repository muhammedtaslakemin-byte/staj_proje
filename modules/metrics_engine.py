"""
Modül 2: Görüntü Kalite Değerlendirme ve Analiz Motoru (Metrics Engine)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
from skimage.metrics import structural_similarity as ssim_func
import config


class QualityMetricsEngine:
    """
    Endüstriyel kamera görüntülerinin kalite parametrelerini (keskinlik, gürültü,
    parlaklık, kontrast, ark parlaması, PSNR, SSIM) matematiksel olarak hesaplar.
    """

    @staticmethod
    def calculate_sharpness(gray_frame: np.ndarray) -> float:
        """
        Laplacian operatörünün varyansını hesaplayarak odak/keskinlik derecesini belirler.
        Yüksek varyans = Net kenarlar ve yüksek odak.
        Düşük varyans = Tozlanmış mercek, kir veya bulanıklık.
        """
        laplacian = cv2.Laplacian(gray_frame, cv2.CV_64F)
        score = float(laplacian.var())
        return round(score, 2)

    @staticmethod
    def calculate_noise(gray_frame: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Medyan filtre farkı üzerinden yüksek frekanslı sensör gürültüsünü hesaplar.
        Döner: (gürültü_standart_sapması, gürültü_fark_matrisi)
        """
        # 3x3 medyan filtre ile pürüzsüzleştir
        filtered = cv2.medianBlur(gray_frame, 3)
        # Orijinal ile filtrelenmiş arasındaki artık fark
        diff = np.abs(gray_frame.astype(np.float64) - filtered.astype(np.float64))
        noise_sigma = float(np.std(diff))
        return round(noise_sigma, 2), diff.astype(np.uint8)

    @staticmethod
    def generate_noise_heatmap(diff_matrix: np.ndarray) -> np.ndarray:
        """
        Sensör gürültüsü artık fark matrisini renkli JET Isı Haritasına (Heatmap) dönüştürür.
        Jüri sunumunda ve resmi PDF raporunda görsel arıza kanıtı olarak kullanılır.
        """
        # Fark matrisini 0-255 arasına dinamik ger
        norm_diff = cv2.normalize(diff_matrix, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmap = cv2.applyColorMap(norm_diff, cv2.COLORMAP_JET)
        return heatmap

    @staticmethod
    def generate_edge_map(gray_frame: np.ndarray) -> np.ndarray:
        """
        Laplacian kenar haritasını renklendirerek odak ve netlik dağılımını gösterir.
        """
        lap = cv2.Laplacian(gray_frame, cv2.CV_64F)
        lap_abs = np.uint8(np.absolute(lap))
        norm_lap = cv2.normalize(lap_abs, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        edge_map = cv2.applyColorMap(norm_lap, cv2.COLORMAP_CYAN if hasattr(cv2, 'COLORMAP_CYAN') else cv2.COLORMAP_OCEAN)
        return edge_map

    @staticmethod
    def calculate_brightness_and_contrast(gray_frame: np.ndarray) -> Tuple[float, float]:
        """
        Parlaklık (ortalama piksel yoğunluğu) ve RMS Kontrast (standart sapma) hesaplar.
        """
        brightness = float(np.mean(gray_frame))
        contrast = float(np.std(gray_frame))
        return round(brightness, 2), round(contrast, 2)

    @staticmethod
    def detect_electrical_arc(gray_frame: np.ndarray) -> Tuple[bool, float]:
        """
        Elektriksel ark veya patlama anında oluşan tepe aşırı pozlamayı (histogram doyumu) tespit eder.
        Döner: (ark_var_mı, doymuş_piksel_yüzdesi)
        """
        threshold = config.ARC_DETECTION["SATURATION_PIXEL_THRESHOLD"]
        saturated_pixels = np.count_nonzero(gray_frame >= threshold)
        total_pixels = gray_frame.size
        ratio = (saturated_pixels / total_pixels) * 100.0
        is_arc = ratio >= config.ARC_DETECTION["ALARM_PERCENTAGE"]
        return is_arc, round(ratio, 2)

    @staticmethod
    def calculate_full_reference_metrics(reference_bgr: np.ndarray, current_bgr: np.ndarray) -> Dict[str, float]:
        """
        Eğer referans altın görüntü (temiz pano) mevcutsa PSNR ve SSIM hesaplar.
        """
        # Boyutları eşitle
        if reference_bgr.shape != current_bgr.shape:
            ref_resized = cv2.resize(reference_bgr, (current_bgr.shape[1], current_bgr.shape[0]))
        else:
            ref_resized = reference_bgr

        # PSNR Hesaplama
        try:
            psnr_val = cv2.PSNR(ref_resized, current_bgr)
            if np.isinf(psnr_val) or psnr_val > 100:
                psnr_val = 100.0
        except Exception:
            psnr_val = 0.0

        # SSIM Hesaplama (Gri tonlamada)
        try:
            ref_gray = cv2.cvtColor(ref_resized, cv2.COLOR_BGR2GRAY)
            cur_gray = cv2.cvtColor(current_bgr, cv2.COLOR_BGR2GRAY)
            ssim_val = ssim_func(ref_gray, cur_gray)
        except Exception:
            ssim_val = 0.0

        return {
            "psnr_db": round(float(psnr_val), 2),
            "ssim": round(float(ssim_val), 4)
        }

    @classmethod
    def evaluate_frame(cls, frame_bgr: np.ndarray, reference_bgr: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Bir kamera karesi için tüm metrikleri bütünsel olarak çalıştırır ve 0-100 Genel Kalite Endeksi üretir.
        """
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # 1. Metrikleri hesapla
        sharpness = cls.calculate_sharpness(gray)
        noise_sigma, diff_matrix = cls.calculate_noise(gray)
        brightness, contrast = cls.calculate_brightness_and_contrast(gray)
        has_arc, arc_ratio = cls.detect_electrical_arc(gray)

        # 2. Durum Sınıflandırması (Normal, Uyarı, Kritik)
        if sharpness >= config.SHARPNESS_THRESHOLDS["NORMAL"]:
            sharpness_status = "NORMAL"
        elif sharpness >= config.SHARPNESS_THRESHOLDS["WARNING"]:
            sharpness_status = "UYARI"
        else:
            sharpness_status = "KRİTİK"

        if noise_sigma <= config.NOISE_THRESHOLDS["NORMAL"]:
            noise_status = "NORMAL"
        elif noise_sigma <= config.NOISE_THRESHOLDS["WARNING"]:
            noise_status = "UYARI"
        else:
            noise_status = "KRİTİK"

        if (brightness < config.BRIGHTNESS_LIMITS["MIN_ACCEPTABLE"] or
            brightness > config.BRIGHTNESS_LIMITS["MAX_ACCEPTABLE"]):
            brightness_status = "KRİTİK"
        elif (brightness < config.BRIGHTNESS_LIMITS["OPTIMAL_MIN"] or
              brightness > config.BRIGHTNESS_LIMITS["OPTIMAL_MAX"]):
            brightness_status = "UYARI"
        else:
            brightness_status = "NORMAL"

        # 3. 0-100 Genel Kalite Endeksi (Overall Quality Score)
        # Keskinlik katkısı (0-100 normalize, 250 varyans = 100 puan)
        sharpness_norm = min(100.0, (sharpness / 200.0) * 100.0)
        # Gürültü cezası (gürültü 0 ise 100, 30 ve üstü ise 0)
        noise_norm = max(0.0, 100.0 - (noise_sigma / 30.0) * 100.0)
        # Parlaklık uygunluk puanı
        if 80.0 <= brightness <= 180.0:
            bright_norm = 100.0
        else:
            dist = min(abs(brightness - 80.0), abs(brightness - 180.0))
            bright_norm = max(0.0, 100.0 - dist * 1.2)

        # Ağırlıklı genel skor
        overall_score = (sharpness_norm * 0.40) + (noise_norm * 0.35) + (bright_norm * 0.25)

        # Eğer elektriksel ark varsa veya keskinlik kritik seviyedeyse skor düşürülür
        if has_arc:
            overall_score = min(overall_score, 25.0)
        if sharpness_status == "KRİTİK":
            overall_score = min(overall_score, 45.0)

        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Nihai Karar
        if has_arc:
            final_verdict = "KRİTİK: ELEKTRİKSEL ARK TESPİT EDİLDİ!"
            verdict_color = "DANGER_RED"
        elif overall_score >= 80.0 and sharpness_status == "NORMAL" and noise_status == "NORMAL":
            final_verdict = "ONAYLANDI: STANDARTLARA UYGUN (KALİTELİ)"
            verdict_color = "SUCCESS_GREEN"
        elif overall_score >= 55.0 and sharpness_status != "KRİTİK":
            final_verdict = "DİKKAT: BAKIM / TEMİZLİK ÖNERİLİR"
            verdict_color = "WARNING_YELLOW"
        else:
            final_verdict = "KRİTİK HATA: GÖRÜNTÜ İZLENEBİLİRLİĞİ KAYBEDİLDİ"
            verdict_color = "DANGER_RED"

        # 4. Spesifik Arıza / Hata Türü Belirleme (Yangın, Titreşim, Tozlanma, Gürültü vb.)
        if has_arc:
            fault_type = "ELEKTRİKSEL ARK & YANGIN TEHLİKESİ"
            fault_desc = f"Ani plazma parlaması ve alev doyumu saptandı (Doyum: %{arc_ratio:.1f}). Yangın koruma devresi devreye alınmalıdır."
        elif sharpness_status == "KRİTİK":
            fault_type = "ŞİDDETLİ TOZLANMA / ODAK KAYBI"
            fault_desc = f"Laplacian odak varyansı ({sharpness}) kritik eşiğin altına düştü. Mercek temizliği gereklidir."
        elif noise_status == "KRİTİK":
            fault_type = "AŞIRI TERMAL SENSÖR GÜRÜLTÜSÜ (GREN)"
            fault_desc = f"Sensör gürültüsü ({noise_sigma:.1f} sigma) kritik düzeyde. Aşırı ortam sıcaklığı veya yetersiz aydınlatma."
        elif brightness_status == "KRİTİK":
            fault_type = "KRİTİK AYDINLATMA KUSURU"
            fault_desc = f"Lüminans değeri ({brightness:.1f}) kabul edilebilir sınırlar dışındadır."
        elif overall_score >= 80.0:
            fault_type = "NORMAL ÇALIŞMA (ARIZA YOK)"
            fault_desc = "Kamera kalite ve görünürlük parametreleri standart toleranslar içerisindedir."
        else:
            fault_type = "PERİYODİK BAKIM / KONTROL GEREKLİ"
            fault_desc = "Görüntü kalitesinde kısmi bozulma saptandı, rutin kontrol önerilir."

        # 5. Referanslı metrikler (varsa)
        ref_metrics = None
        if reference_bgr is not None:
            ref_metrics = cls.calculate_full_reference_metrics(reference_bgr, frame_bgr)

        return {
            "sharpness": sharpness,
            "sharpness_status": sharpness_status,
            "noise_sigma": noise_sigma,
            "noise_status": noise_status,
            "brightness": brightness,
            "brightness_status": brightness_status,
            "contrast": contrast,
            "has_arc": has_arc,
            "arc_ratio": arc_ratio,
            "overall_score": overall_score,
            "final_verdict": final_verdict,
            "fault_type": fault_type,
            "fault_desc": fault_desc,
            "verdict_color": verdict_color,
            "diff_matrix": diff_matrix,
            "reference_metrics": ref_metrics
        }


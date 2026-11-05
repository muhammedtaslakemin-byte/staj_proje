"""
Endüstriyel Kamera Görüntü Kalite Değerlendirme ve Raporlama Sistemi
Sistem Yapılandırması, ROC Kalibrasyon Eşik Değerleri ve Kurumsal Ayarlar
MRT Güç Sistemleri & Harran Üniversitesi Staj Projesi
"""

import os
from pathlib import Path

# ==========================================
# 1. DİZİN VE YOL YAPILANDIRMASI
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_IMAGES_DIR = DATA_DIR / "sample_images"
SAMPLE_VIDEOS_DIR = DATA_DIR / "sample_videos"
DATABASE_PATH = DATA_DIR / "database.sqlite"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Klasörlerin varlığını garantiye al
SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. KURUMSAL VE RAPORLAMA BİLGİLERİ
# ==========================================
COMPANY_NAME = "MRT GÜÇ SİSTEMLERİ MÜH. SAN. VE TİC. LTD. ŞTİ."
COMPANY_LOCATION = "Haliliye / ŞANLIURFA"
SUPERVISOR_NAME = "Murat Tartış"
SUPERVISOR_TITLE = "Mühendis (Oda Sicil No: 59501)"
STUDENT_NAME = "Muhammed Emin Taslak"
STUDENT_ID = "230517037"
PROJECT_TITLE = "Endüstriyel Güç Sistemleri Otomatik Kamera Kalite Değerlendirme Sistemi"
ISO_STANDARD = "ISO/IEC 25010 & ISO 12233 Standartlarına Uygun Kalite Sertifikasyonu"

# ==========================================
# 3. METRİK EŞİK DEĞERLERİ (ROC KALİBRASYONU)
# Harran Üniversitesi Staj Defteri ve Saha Şartları
# ==========================================

# Keskinlik (Laplacian Varyansı - Focus / Sharpness)
SHARPNESS_THRESHOLDS = {
    "NORMAL": 150.0,   # >= 150: Yüksek Netlik / Odak Mükemmel
    "WARNING": 80.0,   # 80 - 149.9: Tozlanma Başlangıcı / Hafif Odak Kaybı
    "CRITICAL": 0.0    # < 80: Şiddetli Toz Fırtınası / Kritik Odak Kaybı
}

# Gürültü (Medyan Filtre Farkı Standart Sapması - Noise Sigma)
NOISE_THRESHOLDS = {
    "NORMAL": 10.0,    # <= 10: Temiz Sensör / Düşük Gürültü
    "WARNING": 25.0,   # 10.1 - 25: Yüksek Sıcaklık (45°C) / Termal Gren
    "CRITICAL": 45.0   # > 25: Gece Düşük Işık / Kritik Sensör Paraziti
}

# Parlaklık (Luminance Ortalama Değeri: 0 - 255)
BRIGHTNESS_LIMITS = {
    "MIN_ACCEPTABLE": 40.0,   # < 40: Aşırı Karanlık Pano Hücresi
    "OPTIMAL_MIN": 70.0,
    "OPTIMAL_MAX": 190.0,
    "MAX_ACCEPTABLE": 230.0   # > 230: Aşırı Pozlama / Doyum
}

# Kontrast (RMS Kontrast Standart Sapması: 0 - 128)
CONTRAST_LIMITS = {
    "CRITICAL_LOW": 20.0,     # < 20: Sisli, Tozlu, Detaysız
    "ACCEPTABLE_MIN": 40.0
}

# Elektriksel Ark Tespiti (250-255 Doygunluk Alan Oranı - Yüzde)
ARC_DETECTION = {
    "SATURATION_PIXEL_THRESHOLD": 250, # Doygun piksel değeri
    "ALARM_PERCENTAGE": 15.0           # Görüntünün %15'inden fazlası doymuşsa ARK ALARMI
}

# Titreşim Tespiti (Lucas-Kanade Ortalama Piksel Hareketi - Piksel/Kare)
VIBRATION_LIMITS = {
    "STABLE": 1.2,    # <= 1.2 px: Normal Sabit Montaj
    "WARNING": 3.0,   # 1.2 - 3.0 px: Hafif Titreşim
    "CRITICAL": 5.0   # > 3.0 px: Jeneratör Şiddetli Mekanik Titreşim Alarmı
}

# Referans Kalite Karşılaştırma Eşikleri (Full-Reference)
FULL_REFERENCE_THRESHOLDS = {
    "PSNR_OPTIMAL_DB": 30.0,    # >= 30 dB Kabul edilebilir kalite
    "SSIM_OPTIMAL": 0.85        # >= 0.85 Yüksek yapısal benzerlik
}

# ==========================================
# 4. GÖRSELLEŞTİRME VE RENK PALETİ
# ==========================================
COLORS = {
    "PRIMARY_NAVY": "#0F172A",
    "SECONDARY_BLUE": "#1E293B",
    "ACCENT_CYAN": "#06B6D4",
    "SUCCESS_GREEN": "#10B981",
    "WARNING_YELLOW": "#F59E0B",
    "DANGER_RED": "#EF4444",
    "TEXT_LIGHT": "#F8FAFC",
    "CARD_BG": "#1E293B"
}


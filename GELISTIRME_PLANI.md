# Endüstriyel Kamera Görüntü Kalite Değerlendirme ve Raporlama Sistemi
## Adım Adım Proje Geliştirme ve Simülasyon Planı

Bu plan, **Masaüstü'ndeki `staj_proje`** klasöründe sıfırdan çalışan, uçtan uca test edilmiş ve jüri önünde etkileyici bir **Web Tabanlı Simülasyon** ile sunulabilir bir sistem kurmak için tasarlanmıştır.

---

### Proje Dizin Yapısı (Masaüstü / `staj_proje`)

```
C:\Users\LENOVO\Desktop\staj_proje\
│
├── .venv/                              # Python izole sanal ortamı
├── requirements.txt                    # Gerekli Python kütüphaneleri
├── PROJE_RAPORU_...pdf                 # 4 sayfalık resmi proje mühendislik raporu (Hazır)
├── README.md                           # Kurulum ve jüri sunum kullanım kılavuzu
├── app.py                              # Ana Streamlit Web Uygulaması ve Simülasyon Kontrol Paneli
├── config.py                           # Sistem eşik değerleri (ROC kalibrasyonları) ve kurumsal renkler
│
├── modules/                            # 5 Temel Mühendislik Katmanı
│   ├── __init__.py
│   ├── data_acquisition.py            # Modül 1: ImageLoader, VideoFileReader, LiveStreamCapture, RobustStream
│   ├── metrics_engine.py              # Modül 2: Laplacian Keskinlik, Medyan Gürültüsü, Parlaklık, Ark/Histogram, PSNR, SSIM
│   ├── dynamic_analysis.py            # Modül 3: FPSMeter, Lucas-Kanade Optik Akış (Titreşim), ThreadedCamera (30 FPS)
│   ├── simulator.py                   # YENİ: Web Tabanlı Saha ve Anormallik Simülatörü (Toz, Gürültü, Ark, Titreşim)
│   ├── database.py                    # Modül 5: SQLite DatabaseManager (test_records tablosu ve indeksleme)
│   └── report_generator.py            # Modül 5: ReportLab ISO formatlı otomatik resmi PDF sertifikası üreticisi
│
├── data/
│   ├── sample_images/                 # Simülasyon ve test için sentetik/gerçek trafo ve pano görselleri
│   └── database.sqlite                # SQLite test kayıt veritabanı
│
├── outputs/
│   └── reports/                       # Sistem tarafından otomatik üretilen resmi PDF test raporları
│
└── tests/
    └── test_modules.py                # unittest birim ve bellek testleri
```

---

### Adım Adım Geliştirme Aşamaları

1. **1. Aşama: Altyapı, Yapılandırma ve Test Verileri**
   * Sanal ortamda kütüphanelerin doğrulanması.
   * `config.py` içinde staj defterindeki ROC eşiklerinin tanımlanması (Normal >150, Uyarı 80-150, Kritik <80; Ark oranı %15; PSNR 30 dB; SSIM 0.85).
   * Jüri önünde anında çalıştırılabilmesi için `data/sample_images/` altına yüksek çözünürlüklü endüstriyel elektrik panosu ve trafo test görsellerinin eklenmesi.

2. **2. Aşama: Görüntü İşleme ve Analiz Katmanları (Modül 1, 2, 3)**
   * `data_acquisition.py`: Resim, video ve RTSP kamera okuyucu sınıfları.
   * `metrics_engine.py`: Laplacian varyansı, medyan farkı standart sapması, parlaklık, kontrast, histogram doygunluğu, PSNR ve SSIM hesaplayıcıları; 0-100 Genel Kalite İndeksi.
   * `dynamic_analysis.py`: `ThreadedCamera` ile canlı yayında 30 FPS optimizasyonu ve Lucas-Kanade Optik Akışı ile mekanik titreşim tespiti.

3. **3. Aşama: Web Tabanlı Saha Koşulları Simülatörü (`simulator.py`)**
   Jüriye projeyi anlatırken fiziksel toz veya ark oluşturamayacağımız için arayüze ekleyeceğimiz **"Saha Simülatörü"**:
   * Tozlanma / Odak Kaybı Simülasyonu (Gauss bulanıklığı ve kontrast zayıflatması)
   * Sensör Gürültüsü Simülasyonu (Düşük ışık simülasyonu, tuz-biber ve Gauss paraziti)
   * Elektriksel Ark Parlaması Simülasyonu (Bölgesel aşırı pozlama ve tepe doyum)
   * Jeneratör Mekanik Titreşimi (Ardışık karelerde sinüzoidal titreşim)
   * 5 Hazır Demo Senaryosu Butonu: Normal, Toz Fırtınası, Gece Greni, Ark Parlaması, Motor Titreşimi.

4. **4. Aşama: Veritabanı ve Otomatik PDF Raporlama (Modül 5)**
   * `database.py`: Yapılan tüm testleri SQLite veritabanına indeksli olarak kaydeder.
   * `report_generator.py`: Test anındaki görseli, gürültü ısı haritasını, metrik tablosunu ve onay durumunu içeren resmi A4 PDF sertifikasını saniyeler içinde üretir.

5. **5. Aşama: Streamlit Web Dashboard (`app.py`) ve Canlı Demo**
   * Modern, koyu lacivert temalı, endüstriyel operatör paneli.
   * Sol menüden mod seçimi: Canlı RTSP / Webcam, Video Dosyası, Statik Fotoğraf veya Saha Simülasyon Modu.
   * Canlı metrik sayaçları, anlık durum rozetleri (Yeşil / Sarı / Kırmızı), zaman serisi grafikleri ve tek tıkla resmi PDF raporu indirme butonu.

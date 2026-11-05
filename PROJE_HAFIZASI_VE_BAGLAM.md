# ENDÜSTRİYEL KAMERA GÖRÜNTÜ KALİTE DEĞERLENDİRME VE RAPORLAMA SİSTEMİ
## Proje Hafızası, Bağlam Aktarımı ve Geliştirme Durumu (Context Transfer)

> **DİKKAT (YENİ OTURUM İÇİN TALİMAT):**  
> Bu belge, önceki sohbet oturumunun tüm teknik hafızasını, staj defteri gereksinimlerini, mimari kararları ve geliştirme adımlarını içerir. Yeni oturumda projeye devam ederken doğrudan bu dosyayı referans alarak sıradaki adımdan devam ediniz.

---

### 1. Proje ve Staj Künyesi
* **Öğrenci:** Muhammed Emin Taslak (Öğrenci No: 230517037)
* **Bölüm:** Harran Üniversitesi Mühendislik Fakültesi - Yazılım Mühendisliği (2023 Giriş)
* **Staj Devresi:** 1. Devre Pratik Çalışması / 35 İş Günü (280 Saat)
* **Tarih Aralığı:** 20.07.2026 - 04.09.2026
* **Firma:** MRT GÜÇ SİSTEMLERİ MÜHENDİSLİK SANAYİ VE TİCARET LİMİTED ŞİRKETİ (Haliliye / Şanlıurfa)
* **İşyeri Amiri:** Murat Tartış (Mühendis, Oda Sicil No: 59501)
* **Proje Konusu:** *Endüstriyel Güç Sistemleri İçin Otomatik Kamera Görüntü Kalite Değerlendirme ve Raporlama Sistemi*
* **Çalışma Dizini:** `C:\Users\LENOVO\Desktop\staj_proje`

---

### 2. Dosya Uyumluluk ve Analiz Özeti
Kullanıcının sağladığı iki temel kaynak (DeepSeek Proje Taslağı ve Harran Üniversitesi 35 Günlük Staj Defteri) ayrıntılı incelenmiş ve aralarında **%100 tam uyum** olduğu doğrulanmıştır:
* Staj defteri, taslaktaki teorik 5 modülü almış ve **MRT Güç Sistemleri'nin saha gerçeklerine (Şanlıurfa yaz toz fırtınaları, 45°C sıcaklık, trafo ark parlamaları, jeneratör titreşimleri ve karanlık pano hücreleri)** uyarlamıştır.
* 4 sayfalık resmi proje mühendislik raporu ReportLab ile derlenmiş ve `PROJE_RAPORU_Kamera_Kalite_Degerlendirme.pdf` olarak klasöre kaydedilmiştir.

---

### 3. Çok Katmanlı Sistem Mimarisi (5 Ana Modül + Simülatör)

```
C:\Users\LENOVO\Desktop\staj_proje\
├── .venv/                      # Python sanal ortamı
├── requirements.txt            # Bağımlılıklar (OpenCV, Streamlit, NumPy, Scikit-image, ReportLab, Pandas)
├── PROJE_RAPORU_...pdf         # Hazır resmi PDF raporu
├── app.py                      # Ana Streamlit Web Uygulaması ve Dashboard
├── config.py                   # Eşik değerler (ROC kalibrasyonu) ve kurumsal ayarlar
│
├── modules/
│   ├── data_acquisition.py    # Modül 1: ImageLoader, VideoFileReader, LiveStreamCapture (buffer=1, Exponential Backoff)
│   ├── metrics_engine.py      # Modül 2: Laplacian Keskinlik, Medyan Gürültüsü, Parlaklık/Kontrast, Histogram Arkı, PSNR, SSIM
│   ├── dynamic_analysis.py    # Modül 3: FPSMeter, Lucas-Kanade Optik Akışı (Titreşim), ThreadedCamera (30 FPS)
│   ├── simulator.py           # KRİTİK YENİLİK: Web Tabanlı Saha Simülatörü (Toz, Gürültü, Ark, Titreşim)
│   ├── database.py            # Modül 5: SQLite DatabaseManager (test_records tablosu ve indeksleme)
│   └── report_generator.py    # Modül 5: ReportLab ISO formatlı otomatik resmi PDF sertifikası üreticisi
│
├── data/sample_images/         # Test ve simülasyon panosu görselleri
└── outputs/reports/           # Otomatik üretilen test PDF raporları
```

---

### 4. Jüri Sunumu İçin "Web Tabanlı Saha Simülatörü" Mantığı
Kullanıcının talebi doğrultusunda, jüri önünde canlı donanım veya fiziksel toz/ark gerektirmeden tam işlevselliği sergilemek üzere arayüze bir **Saha Simülasyonu** eklenecektir:
* **Canlı Kaydırıcılar (Sliders):** Tozlanma/Bulanıklık seviyesi, Sensör Gürültüsü, Ortam Işığı, Titreşim.
* **5 Hazır Demo Senaryosu Butonu:**
  1. *Normal Pano (Yeşil Onay, Keskinlik >150)*
  2. *Şanlıurfa Toz Fırtınası (Keskinlik <80, Kırmızı Kritik Alarm)*
  3. *Gece Vardiyası / Yetersiz Işık (Gürültü artışı ve Renkli Isı Haritası - Jet Heatmap)*
  4. *Şalter Açma / Elektriksel Ark (Histogram doyumu >%15, Ark Uyarısı)*
  5. *Jeneratör Titreşimi (Optik Akış zaman serisinde ani pikler)*
* **Otomatik Rapor Butonu:** Arıza anında tek tıkla resmi PDF raporunu basma ve indirme.

---

### 5. Mevcut Durum ve Tamamlanan Aşamalar

* [x] Python sanal ortamı (`.venv`) yapılandırıldı ve tüm kütüphaneler kuruldu (`opencv-python`, `numpy`, `scikit-image`, `streamlit`, `reportlab`, `pandas`, `pillow`, `matplotlib`, `psutil`, `plotly`, `fastapi`, `uvicorn`).
* [x] **PDF Türkçe Karakter Desteği:** ReportLab için `ArialTR` ve `ArialTR-Bold` TrueType fontları kaydedildi. Türkçe karakterler (`ş, ğ, ı, İ, ö, ü, ç`) sembolleşmeden, kusursuz A4 ISO sertifikası üretiliyor.
* [x] **Fotoğraf ve Video Yükleme Entegrasyonu:**
  * Backend: `POST /api/upload-photo` ve `POST /api/upload-video` endpointleri eklendi.
  * Frontend: Fotoğraf sekmesinde anında analiz eden dosya yükleyici, Video sekmesinde yüklenen videoyu anında oynatıcıya bağlayan uploader eklendi.
* [x] **Veritabanı Silme ve Temizleme (Efektif Yönetim):**
  * Backend: `DELETE /api/records/{id}` ve `DELETE /api/records` endpointleri ile `DatabaseManager.delete_record` ve `clear_all_records` fonksiyonları yazıldı.
  * Frontend: Her satıra kırmızı çöp kutusu silme butonu ve üst panele "Tümünü Temizle" butonu eklendi.
* [x] **React 19 + Tailwind CSS Frontend Yeniden Derlendi:** `frontend/dist` klasörüne hatasız paketlendi (780ms).
* [x] **Birim ve Entegrasyon Testleri (`tests/test_modules.py`):** 6/6 test başarıyla geçti.

#### 👉 Uygulamayı Çalıştırma Komutu:
```powershell
.\.venv\Scripts\python.exe start_system.py
```
*(veya klasördeki `baslat.bat` dosyasına çift tıklayın)*

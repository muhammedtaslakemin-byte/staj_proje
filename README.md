# Endüstriyel Kamera Görüntü Kalite Değerlendirme ve Raporlama Sistemi
**Harran Üniversitesi Yazılım Mühendisliği & MRT Güç Sistemleri Staj Projesi**

Bu proje, trafo, elektrik panosu ve jeneratör izleme kameralarının görüntü kalitesini (keskinlik, gürültü, parlaklık, ark parlamaları, titreşim) otomatik olarak değerlendiren, **React + Tailwind CSS** ve **FastAPI** mimarisiyle canlı web arayüzünde sunan ve resmi PDF kalite sertifikası üreten bir mühendislik sistemidir.

---

## 🚀 Proje Dokümantasyonu ve Hızlı Erişim
* **Proje Hafızası ve Bağlam:** [PROJE_HAFIZASI_VE_BAGLAM.md](PROJE_HAFIZASI_VE_BAGLAM.md)
* **Geliştirme Planı:** [GELISTIRME_PLANI.md](GELISTIRME_PLANI.md)
* **Resmi Mühendislik Raporu (PDF):** [PROJE_RAPORU_Kamera_Kalite_Degerlendirme.pdf](PROJE_RAPORU_Kamera_Kalite_Degerlendirme.pdf)

---

## 🛠️ Nasıl Çalıştırılır?

### Yöntem 1: Tek Tıkla Başlatma (Önerilen - React + Tailwind Arayüzü)
Klasör içindeki **`baslat.bat`** dosyasına çift tıklayabilir veya terminalde şu komutu çalıştırabilirsiniz:

```powershell
.\.venv\Scripts\python.exe start_system.py
```
> Otomatik olarak tarayıcınızda `http://localhost:8000` adresinde **Ana Menü (Launchpad)** açılacaktır.

### Yöntem 2: Streamlit Python Arayüzü (Alternatif)
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

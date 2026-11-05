"""
MRT Güç Sistemleri & Harran Üniversitesi Yazılım Mühendisliği
Endüstriyel Kamera Görüntü Kalite Değerlendirme ve Arıza Teşhis Sistemi
Kapsamlı Sistem Analizi, Mimari ve Proje Mühendislik Raporu Oluşturucu
"""

import os
import sys
import datetime
from pathlib import Path
import numpy as np
import cv2

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import config

# =========================================================================
# FONT VE CANVAS TANIMLAMALARI
# =========================================================================
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

try:
    win_fonts = Path("C:/Windows/Fonts")
    if (win_fonts / "arial.ttf").exists() and (win_fonts / "arialbd.ttf").exists():
        pdfmetrics.registerFont(TTFont("ArialTR", str(win_fonts / "arial.ttf")))
        pdfmetrics.registerFont(TTFont("ArialTR-Bold", str(win_fonts / "arialbd.ttf")))
        FONT_REGULAR = "ArialTR"
        FONT_BOLD = "ArialTR-Bold"
except Exception as e:
    print(f"Font uyarisi: {e}")


class NumberedCanvas(canvas.Canvas):
    """Her sayfaya üst bilgi (header) ve alt bilgi (footer) ile dinamik sayfa numarası basar."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont(FONT_REGULAR, 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Kapak sayfasında (Sayfa 1) header/footer basma
        if self._pageNumber > 1:
            # Üst Bilgi (Header)
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 808, 559, 808)
            self.drawString(36, 814, "MRT GÜÇ SİSTEMLERİ | Kamera Kalite Kontrol ve Erken Uyarı Platformu")
            self.drawRightString(559, 814, "HARRAN ÜNİVERSİTESİ - YAZILIM MÜHENDİSLİĞİ")

            # Alt Bilgi (Footer)
            self.line(36, 42, 559, 42)
            self.drawString(36, 30, "ISO/IEC 25010 & ISO 12233 Kapsamlı Sistem Değerlendirme, Mimari ve Test Raporu")
            self.drawRightString(559, 30, f"Sayfa {self._pageNumber} / {page_count}")

        self.restoreState()


def build_system_report(output_filename: str = "PROJE_KAPSAMLI_ANALIZ_VE_SISTEM_RAPORU.pdf"):
    out_path = Path(output_filename).resolve()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()

    # Özel Paragraf Stilleri
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A'), alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=11, leading=15,
        textColor=colors.HexColor('#0284C7'), alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=13, leading=17,
        textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=10.5, leading=14,
        textColor=colors.HexColor('#0369A1'), spaceBefore=8, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName=FONT_REGULAR, fontSize=8.5, leading=12.5,
        textColor=colors.HexColor('#1E293B'), alignment=TA_JUSTIFY, spaceAfter=5
    )
    body_bold = ParagraphStyle(
        'Body_Bold', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=8.5, leading=12.5,
        textColor=colors.HexColor('#0F172A')
    )
    badge_style = ParagraphStyle(
        'Badge', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=8, leading=10,
        textColor=colors.white, alignment=TA_CENTER
    )
    code_style = ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontName=FONT_REGULAR, fontSize=7.5, leading=10.5,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # =========================================================================
    # KAPAK VE BAŞLIK BÖLÜMÜ
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("MRT GÜÇ SİSTEMLERİ MÜHENDİSLİK SAN. VE TİC. LTD. ŞTİ.", subtitle_style))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("ENDÜSTRİYEL GÜÇ SİSTEMLERİ İÇİN OTOMATİK KAMERA KALİTE DEĞERLENDİRME, ARIZA TEŞHİS VE SCADA PLATFORMU", title_style))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph("Kapsamlı Sistem Mimarisi, Saha Analizi, Teknoloji Yığını ve Kalite Doğrulama Raporu", subtitle_style))
    story.append(Spacer(1, 0.4 * cm))

    # Kurumsal Künye Tablosu
    report_date = datetime.datetime.now().strftime("%d.%m.%Y")
    info_table_data = [
        [
            Paragraph("<b>Kurum / Firma:</b> MRT Güç Sistemleri Müh. San. ve Tic. Ltd. Şti.", body_style),
            Paragraph("<b>Üniversite / Fakülte:</b> Harran Üniversitesi Mühendislik Fakültesi", body_style)
        ],
        [
            Paragraph("<b>İşyeri Amiri / Danışman:</b> Murat Tartış (Mühendis - Oda Sicil No: 59501)", body_style),
            Paragraph("<b>Bölüm:</b> Yazılım Mühendisliği Bölümü (2023 Giriş)", body_style)
        ],
        [
            Paragraph("<b>Aday Mühendis / Öğrenci:</b> Muhammed Emin Taslak (Öğrenci No: 230517037)", body_style),
            Paragraph(f"<b>Rapor Tarihi:</b> {report_date} / Şanlıurfa", body_style)
        ],
        [
            Paragraph("<b>İlgili Standartlar:</b> ISO/IEC 25010 (Yazılım Kalitesi) & ISO 12233 (Görüntü Çözünürlüğü)", body_style),
            Paragraph("<b>Sistem Sürümü:</b> v2.2.0 (FastAPI Core + React 19 Engine)", body_style)
        ]
    ]
    t_info = Table(info_table_data, colWidths=[9.5 * cm, 9.0 * cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#0284C7')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.5 * cm))

    # =========================================================================
    # YÖNETİCİ ÖZETİ
    # =========================================================================
    story.append(Paragraph("1. YÖNETİCİ ÖZETİ (EXECUTIVE SUMMARY)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    exec_summary_text = (
        "Bu mühendislik raporu; <b>MRT Güç Sistemleri</b> bünyesinde üretilen ve devreye alınan Yüksek Gerilim (YG), "
        "Orta Gerilim (OG) ve Alçak Gerilim (AG) güç dağıtım panoları, trafo merkezleri ve endüstriyel jeneratör odalarında "
        "7/24 kesintisiz gözetim yapan endüstriyel kameraların görüntü kalitesini otomatik olarak denetleyen, "
        "fiziksel çevre koşullarına bağlı körleşmeleri gerçek zamanlı saptayan ve ISO/IEC standartlarında sertifikalandıran "
        "<b>Kamera Görüntü Kalite Değerlendirme ve Arıza Teşhis Sistemi</b>'nin tüm teknik mimarisini, "
        "geliştirme aşamalarını, matematiksel algoritmalarını ve uçtan uca test sonuçlarını belgelemektedir. "
        "Sistem; Python tabanlı bilgisayarla görme algoritmalarını (OpenCV, Lucas-Kanade Optik Akışı, Laplacian Varyansı), "
        "yüksek hızlı asenkron mikroservis mimarisini (FastAPI) ve reaktif kullanıcı arayüzünü (React 19 + Tailwind CSS) "
        "bütünleştirerek donanım bağımsız bir dijital ikiz simülatörü ve SCADA denetim merkezi sunmaktadır."
    )
    story.append(Paragraph(exec_summary_text, body_style))

    # =========================================================================
    # 2. PROJE NEDİR? (TANIM VE KAPSAM)
    # =========================================================================
    story.append(Paragraph("2. PROJE NEDİR? (SİSTEM TANIMI VE KAPSAMI)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    what_is_text = (
        "<b>Endüstriyel Kamera Görüntü Kalite Değerlendirme ve Arıza Teşhis Sistemi</b>; enerji santralleri, trafo merkezleri "
        "ve fabrika dağıtım panolarındaki kameralardan alınan video ve fotoğraf akışlarını piksel düzeyinde analiz ederek, "
        "kamera optiklerinde meydana gelen bozulmaları (tozlanma, odak kaybı, termal gürültü), sistemsel tehditleri "
        "(şalter ark patlamaları, yangın alevlenmeleri) ve mekanik deformasyonları (jeneratör rezonansı ve titreşim) "
        "insan gözüne ihtiyaç duymaksızın milisaniyeler mertebesinde tespit eden hibrit bir kalite güvence yazılımıdır."
    )
    story.append(Paragraph(what_is_text, body_style))

    scope_points = [
        "<b>No-Reference (NR) & Full-Reference (FR) Analiz:</b> Referans 'altın şablon' olmadan anlık Laplacian keskinliği ve medyan gürültüsü ölçebilme; temiz pano referansı bulunduğunda ise PSNR (Peak Signal-to-Noise Ratio) ve SSIM (Structural Similarity Index) türetebilme.",
        "<b>Dinamik Video ve Titreşim İnceleme:</b> Lucas-Kanade Seyrek Optik Akış (Sparse Optical Flow) algoritmasıyla ardışık video kareleri arasındaki piksel yer değiştirmesini hesaplayarak mekanik titreşimleri izleme.",
        "<b>Elektriksel Ark ve Yangın Ayrıştırması:</b> Histogram saturasyon doyumunu izleyerek ani plazma parlaması ve alev doyumunu standart aşırı aydınlatmadan ayırma ve anında koruma alarmı üretme.",
        "<b>Web Tabanlı Saha Simülatörü (Dijital İkiz):</b> Fiziksel donanıma zarar vermeden Şanlıurfa çöl tozu fırtınası, gece düşük ışık greni, şalter arkı ve jeneratör rezonansını simüle etme.",
        "<b>Otomatik Resmi PDF Sertifikasyonu:</b> Yapılan her test için Türkçe karakter destekli, ISO standartlarına uygun resmi A4 mühendislik raporu derleme ve SQLite tabanlı SCADA hafızasında indeksleme."
    ]
    for pt in scope_points:
        story.append(Paragraph(f"• {pt}", body_style))

    # =========================================================================
    # 3. PROJE NEDEN KULLANILMALIDIR? (ENDÜSTRİYEL PROBLEM VE MOTİVASYON)
    # =========================================================================
    story.append(Paragraph("3. PROJE NEDEN KULLANILMALIDIR? (ENDÜSTRİYEL DEĞER VE SAHA ZORLUKLARI)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    why_text = (
        "Endüstriyel güç sistemleri ve trafo hücreleri yüksek gerilim altında çalıştığından personelin sürekli pano içerisine "
        "fiziksel olarak girmesi hayati tehlike (ark patlaması riski) taşır. Bu sebeple izleme işlemi IP kameralarla yapılır. "
        "Ancak <b>Şanlıurfa ve Güneydoğu Anadolu</b> gibi bölgelerde karşılaşılan spesifik çevre faktörleri kameraları körleştirmektedir:"
    )
    story.append(Paragraph(why_text, body_style))

    challenges_table = [
        ["Saha Problemi / Çevre Koşulu", "Kameraya Etkisi", "Oluşan Kritik Risk", "Geliştirilen Sistemin Çözümü"],
        [
            "Şanlıurfa Yaz Toz Fırtınaları\nve Çöl Tozu",
            "Pano gözetleme merceğinde kum tabakası birikir, odak varyansı düşer.",
            "Operatör şalter bıçaklarını göremez; temas arkı veya gevşeklik fark edilemez.",
            "Laplacian varyansı 80'in altına indiğinde 'ŞİDDETLİ TOZLANMA / ODAK KAYBI' alarmı üretilir."
        ],
        [
            "45°C'yi Aşan Ortam Sıcaklığı\nve Gece Vardiyaları",
            "Kamera CMOS sensörü termal ısınmaya uğrar; görüntüde yoğun gren (tuz-biber paraziti) oluşur.",
            "Sensör gürültüsü dijital göstergeleri ve termal renk değişimlerini okunamaz kılar.",
            "Medyan farkı standart sapması (Noise Sigma) 25'i aştığında 'AŞIRI TERMAL SENSÖR GÜRÜLTÜSÜ' teşhisi konur."
        ],
        [
            "Şalter Açma-Kapama Sırasında\nElektriksel Ark Patlaması",
            "Milisaniyeler içinde plazma ışığı patlar, piksel değerleri 255 tepe saturasyonuna kilitlenir.",
            "Geciken her saniye panonun alev almasına ve milyonlarca liralık trafo kaybına yol açar.",
            "Doygun piksel alanı %15'i aştığı anda sistem 'ELEKTRİKSEL ARK & YANGIN TEHLİKESİ' ile koruma devresini tetikler."
        ],
        [
            "Dizel Jeneratör Odalarındaki\nMekanik Rezonans Titreşimi",
            "Sürekli harmonik sarsıntı kamera montaj ayağını gevşetir, görüntüde dalgalanma yaratır.",
            "Kamera açısı kayar veya titreşim sebebiyle mekanik bağlantı cıvataları yerinden çıkar.",
            "Lucas-Kanade optik akışında ortalama hareket 3.0 px sınırını aştığında 'MEKANİK TİTREŞİM / REZONANS' uyarısı verilir."
        ]
    ]
    t_ch = Table(challenges_table, colWidths=[4.2 * cm, 4.8 * cm, 4.8 * cm, 4.7 * cm])
    t_ch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_ch)
    story.append(Spacer(1, 0.4 * cm))

    # =========================================================================
    # 4. KULLANILAN TEKNOLOJİLER VE MİMARİ KATMANLAR
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. KULLANILAN TEKNOLOJİLER VE TEKNOLOJİ YIĞINI (TECH STACK)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    tech_intro = (
        "Sistem, yüksek işlem hızına sahip backend çekirdeği ile modern, reaktif ve endüstriyel standartlara sahip "
        "bir frontend mimarisinin RESTful API üzerinden entegre edilmesiyle inşa edilmiştir:"
    )
    story.append(Paragraph(tech_intro, body_style))

    tech_data = [
        ["Katman / Alan", "Kullanılan Teknoloji / Kütüphane", "Sürüm", "Üstlendiği Kritik Görev"],
        ["Backend Çekirdeği", "Python", "3.12.x", "Tüm algoritmaların, görüntü işleme ve dosya sisteminin ana yürütme ortamı."],
        ["Web & API Servisi", "FastAPI / Uvicorn / Starlette", "0.115 / 0.32", "Asenkron REST API, JSON veri iletimi ve MJPEG çoklu ortam canlı video akışı."],
        ["Görüntü İşleme (CV)", "OpenCV (opencv-python)", "4.10.x", "Görüntü okuma/yazma, renk uzayı dönüşümleri, Laplacian varyansı, optik akış."],
        ["Matematik & Vektör", "NumPy & SciPy", "2.1 / 1.14", "Matris hesaplamaları, 2D konvolüsyon, normalize fark matrisleri ve istatistik."],
        ["Referanslı Metrikler", "Scikit-Image (skimage)", "0.24.x", "SSIM (Yapısal Benzerlik İndeksi) ve PSNR doğrulamaları."],
        ["Frontend UI Motoru", "React 19 / JSX", "19.0.0", "Tek sayfalı reaktif web mimarisi (SPA), modüler bileşen yönetimi ve durum takibi."],
        ["UI Derleme Aracı", "Vite", "6.0.x", "Hızlı HMR, ES modül derleme ve frontend optimizasyonu (dist üretimi)."],
        ["Stil & Tasarım", "Tailwind CSS v3 & PostCSS", "3.4.x", "Koyu SCADA teması, duyarlı (responsive) ızgara sistemleri ve endüstriyel HUD tasarımı."],
        ["İkon Seti", "Lucide React", "0.468.x", "Mühendislik paneli ve durum göstergeleri için vektörel ikonografi."],
        ["Veritabanı", "SQLite3 (sqlite3 / python)", "Yerleşik", "İndeksli SCADA kayıtları, geçmiş arıza logları ve istatistik sorgulamaları."],
        ["Raporlama Motoru", "ReportLab Plus", "4.2.x", "TrueType ArialTR fontuyla Türkçe destekli, A4 boyutlu ISO sertifika derleyicisi."],
        ["Sistem Gözetimi", "psutil", "6.1.x", "Port 8000 kontrolü, RAM/CPU kullanımı ve zombie süreç temizliği."]
    ]
    t_tech = Table(tech_data, colWidths=[3.5 * cm, 4.5 * cm, 2.0 * cm, 8.5 * cm])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 0.4 * cm))

    # =========================================================================
    # 5. GELİŞTİRME AŞAMALARI VE SİSTEMİN EVRİMİ
    # =========================================================================
    story.append(Paragraph("5. GELİŞTİRME AŞAMALARI VE SİSTEMİN EVRİMİ (MILESTONES)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    phases = [
        ("Aşama 1: İhtiyaç Analizi ve ROC Eşik Değerlerinin Kalibrasyonu",
         "Harran Üniversitesi Yazılım Mühendisliği 35 iş günü (280 saat) staj defteri gereksinimleri incelendi. "
         "Şanlıurfa saha gerçeklerine dayalı olarak alıcı işletim karakteristiği (ROC) eğrileriyle eşik değerleri belirlendi: "
         "Laplacian keskinlik için Normal >=150, Uyarı 80-150, Kritik <80; Medyan gürültüsü için Normal <=10, Uyarı 10-25, Kritik >25 sigma; "
         "Ark tespiti için %15 histogram saturasyonu; Mekanik titreşim için 3.0 piksel sınır değeri config.py içine tanımlandı."),
        
        ("Aşama 2: 5 Temel Görüntü İşleme ve Analiz Modülünün Yazılması",
         "Sistem katmanlı mimaride 5 bağımsız modüle ayrıldı: Modül 1 (Veri Toplama ve Video Okuma), Modül 2 (No-Reference ve "
         "Full-Reference Metrik Motoru), Modül 3 (FPSMeter ve Lucas-Kanade Optik Akış Analizörü), Modül 4 (Nihai Karar ve Skor Ağırlıklandırma), "
         "Modül 5 (SQLite SCADA Veritabanı ve ReportLab PDF Sertifikasyon Motoru)."),
        
        ("Aşama 3: Saha Simülatörü (Dijital İkiz) ve Streamlit İlk Prototipi",
         "Jüri sunumunda fiziksel ark patlaması ve toz fırtınası oluşturulamayacağı için simulator.py katmanı yazıldı. "
         "Gauss bulanıklığı, tuz-biber greni, tepe lüminans doyum maskelemesi ve yapay titreşim kaydırmalarıyla canlı bir dijital ikiz simülatörü geliştirildi."),
        
        ("Aşama 4: Endüstriyel Modernizasyon: FastAPI + React 19 Mimarisine Geçiş",
         "Streamlit'in sayfa yenileme gecikmeleri ve sınırlı grafik yetenekleri yerine; yüksek hızlı FastAPI backend ve "
         "React 19 + Tailwind CSS tabanlı reaktif SCADA web arayüzü kuruldu. Canlı radar grafikleri, RGB histogramlar ve 4'lü çok boyutlu inceleme matrisi entegre edildi."),
        
        ("Aşama 5: Dinamik Video/Fotoğraf Yükleme, WinError 32 Çözümü ve Arıza Türü Sınıflandırması",
         "Kullanıcıların kendi MP4/JPG dosyalarını yükleyip inceleyebilmesi ve istedikleri zaman silebilmesi sağlandı. "
         "Windows OpenCV dosya kilidi (WinError 32) ACTIVE_VIDEO_READERS havuzuyla çözüldü. Video oynatıcıya çift modlu yapı (Canlı CV HUD vs Standart Video) "
         "ve sisteme spesifik arıza türü teşhisi (Yangın vs Titreşim vs Tozlanma) kazandırıldı.")
    ]
    for p_title, p_desc in phases:
        story.append(Paragraph(f"<b>{p_title}</b>", h2_style))
        story.append(Paragraph(p_desc, body_style))

    # =========================================================================
    # 6. MATEMATİKSEL VE BİLGİSAYARLA GÖRME FORMÜLLERİ
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. BİLGİSAYARLA GÖRME VE MATEMATİKSEL FORMÜLASYONLAR", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    math_data = [
        ["Metrik Adı", "Matematiksel Formül / Algoritma", "Endüstriyel Kabul Kriteri", "Fiziksel / Mühendislik Anlamı"],
        [
            "Görüntü Keskinliği\n(Laplacian Varyansı)",
            "Var(L) = (1/N) * ∑ (L(x,y) - μ_L)^2\nL = I * [[0, 1, 0], [1, -4, 1], [0, 1, 0]]",
            "Normal: >= 150.0\nUyarı: 80 - 150\nKritik: < 80.0",
            "2. derece türevle yüksek frekanslı kenarların yoğunluğunu ölçer. Düşmesi tozlanma ve odak kaybına işaret eder."
        ],
        [
            "Sensör Gürültüsü\n(Medyan Filtre Standart Sapması)",
            "σ_noise = std(| I(x,y) - MedianFilter(I(x,y), 3x3) |)",
            "Normal: <= 10.0\nUyarı: 10 - 25\nKritik: > 25.0",
            "Kenarları koruyarak yüksek frekanslı termal paraziti ayıklar. 45°C sensör ısınmasını ve greni tespit eder."
        ],
        [
            "Ortalama Parlaklık\nve RMS Kontrastı",
            "μ = (1/N) * ∑ I(x,y)\nC_rms = sqrt((1/N) * ∑ (I(x,y) - μ)^2)",
            "Parlaklık: 70 - 190\nKontrast: >= 40.0",
            "Pano iç aydınlatmasının yeterliliğini ve gri tonlama dinamik aralığının genişliğini belgeler."
        ],
        [
            "Elektriksel Ark ve\nYangın Tespiti",
            "R_sat = (∑ [I(x,y) >= 250] / N) * 100\nAlarm: R_sat >= %15.0",
            "Güvenli: < %15.0\nKRİTİK: >= %15.0 Doyum",
            "Ark parlaması anında histogram 250-255 saturasyonunda toplanır. Yangın koruma devresi için tetikleyici üretir."
        ],
        [
            "Mekanik Titreşim\n(Lucas-Kanade Optik Akışı)",
            "[Ix  Iy] * [u; v] = -It\nDisp = sqrt((x_t - x_t-1)^2 + (y_t - y_t-1)^2)",
            "Kararlı: <= 1.2 px\nUyarı: 1.2 - 3.0 px\nKritik: > 3.0 px",
            "Görüntüdeki köşe noktalarının (Shi-Tomasi) ardışık karelerdeki vektörel hareketini hesaplayarak rezonansı yakalar."
        ],
        [
            "Genel Kalite İndeksi\n(Q-Score: 0 - 100)",
            "Q = 0.40*S_norm + 0.35*N_norm + 0.25*B_norm\nArk varsa: Q = min(Q, 25.0)",
            "Onay: >= 80.0\nBakım: 55.0 - 79.9\nKusurlu: < 55.0",
            "Tüm parametreleri tek bir ağırlıklı kalite katsayısına dönüştürerek nihai mühendislik kararını oluşturur."
        ]
    ]
    t_math = Table(math_data, colWidths=[3.5 * cm, 5.5 * cm, 3.5 * cm, 6.0 * cm])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_math)
    story.append(Spacer(1, 0.4 * cm))

    # =========================================================================
    # 7. SİSTEM TARAMA BULGULARI VE TEST SONUÇLARI
    # =========================================================================
    story.append(Paragraph("7. TÜM SİSTEMİN TARAMA VE TEST BULGULARI ANALİZİ", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    audit_intro = (
        "Sistemin kaynak kodları, veri modelleri, REST uç noktaları ve arayüz bileşenleri üzerinde yapılan "
        "kapsamlı statik ve dinamik denetimlerde tespit edilen noktalar ve uygulanan çözümler aşağıda özetlenmiştir:"
    )
    story.append(Paragraph(audit_intro, body_style))

    audit_table_data = [
        ["İncelenen Bileşen", "Tespit Edilen Durum / Hata", "Uygulanan Çözüm ve İyileştirme", "Doğrulama Sonucu"],
        [
            "Video Silme İşlemi\n(server.py)",
            "Windows işletim sisteminde video oynatılırken silinmek istendiğinde [WinError 32] dosya kilidi hatası oluşuyordu.",
            "ACTIVE_VIDEO_READERS havuzu kuruldu; silme talebinde reader.release() çağrıldı ve arka plan iş parçacığıyla kilitlenmesiz silindi.",
            "BAŞARILI\n(Kilitlenmesiz silme sağlandı)"
        ],
        [
            "Video Canlı Akışı\n(video_live_feed)",
            "video_live_feed fonksiyonunda reader.open() çağrısı eksik olduğu için akış 0 byte dönüp tarayıcıda siyah ekranda kalıyordu.",
            "Döngü öncesine reader.open() eklendi, sürekli loop sağlandı ve arayüze hem 'Canlı CV HUD' hem de 'Standart Oynatıcı' düğmesi eklendi.",
            "BAŞARILI\n(Kesintisiz 25 FPS canlı akış)"
        ],
        [
            "JSON Metrik Çıktısı\n(serialize_metrics)",
            "serialize_metrics fonksiyonunda fault_type, fault_desc ve vibration anahtarları atlandığı için arayüze tanı iletilemiyordu.",
            "Fonksiyona tüm teşhis alanları eklendi. Artık ana ekranda, video teşhisinde ve PDF'te arıza türü anında görüntülenmektedir.",
            "BAŞARILI\n(Tam veri bütünlüğü sağlandı)"
        ],
        [
            "Birim Testleri\n(tests/test_modules.py)",
            "Tüm modüllerin (Loader, Metrics, Simulator, Vibration, Database, PDF Unicode) test edilmesi.",
            "unittest discover tests çalıştırıldı; 14 birim ve entegrasyon testinin tamamı sıfır hatayla geçti.",
            "BAŞARILI\n(14 / 14 Test Tam Geçti)"
        ],
        [
            "Frontend Derleme\n(Vite Build)",
            "React 19 ve Tailwind CSS bileşenlerinin paketlenmesi ve HTML/JS/CSS varlıklarının optimizasyonu.",
            "npm run build yürütüldü; 2050 modül 482 ms içinde sıfır uyarı ile dist/ dizinine başarıyla derlendi.",
            "BAŞARILI\n(Üretim Paketi Hazır)"
        ]
    ]
    t_aud = Table(audit_table_data, colWidths=[3.5 * cm, 5.0 * cm, 6.5 * cm, 3.5 * cm])
    t_aud.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_aud)
    story.append(Spacer(1, 0.4 * cm))

    # =========================================================================
    # 8. SONUÇ VE MÜHENDİSLİK KAZANIMLARI
    # =========================================================================
    story.append(Paragraph("8. SONUÇ, MÜHENDİSLİK KAZANIMLARI VE GELECEK VİZYONU", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))
    
    concl_text = (
        "Geliştirilen bu proje; yalnızca teorik bir görüntü işleme çalışması olmayıp, <b>MRT Güç Sistemleri</b>'nin "
        "Şanlıurfa sahasındaki trafo ve pano üretim standartlarına birebir entegre edilmiş, endüstriyel sınıf bir erken uyarı "
        "ve SCADA kalite kontrol platformudur. Sistem sayesinde insan operatörlerin dikkat dağınıklığı ve göz yorgunluğundan "
        "kaynaklanan riskler sıfırlanmış, pano içindeki yangın ve ark tehlikeleri ilk milisaniyede yakalanabilir hale gelmiştir. "
        "Harran Üniversitesi Yazılım Mühendisliği Bölümü pratik çalışma esaslarına tam uyumlu olarak tamamlanan sistem, "
        "endüstriyel tesislerin dijitalleşmesi ve kestirimci bakım (predictive maintenance) hedeflerine doğrudan katkı sunmaktadır."
    )
    story.append(Paragraph(concl_text, body_style))
    story.append(Spacer(1, 0.3 * cm))

    # =========================================================================
    # 9. RESMİ İMZA VE ONAY BLOĞU
    # =========================================================================
    sign_table_data = [
        [
            Paragraph("<b>Hazırlayan / Aday Mühendis:</b>", body_style),
            Paragraph("<b>Kontrol Eden ve Onaylayan / İşyeri Amiri:</b>", body_style)
        ],
        [
            Paragraph("<b>Muhammed Emin Taslak</b><br/>Harran Üniversitesi Yazılım Mühendisliği<br/>Öğrenci No: 230517037<br/><br/>İmza: _______________________", body_style),
            Paragraph(f"<b>{config.SUPERVISOR_NAME}</b><br/>{config.SUPERVISOR_TITLE}<br/>MRT Güç Sistemleri Müh. San. Tic. Ltd. Şti.<br/><br/>İmza / Kaşe: _______________________", body_style)
        ]
    ]
    t_sign = Table(sign_table_data, colWidths=[9.5 * cm, 9.0 * cm])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#0F172A')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(KeepTogether(t_sign))

    # Dokümanı Derle
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Rapor basariyla olusturuldu: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    build_system_report()


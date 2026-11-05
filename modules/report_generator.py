"""
Modül 5: Resmi Kalite Değerlendirme Raporu ve Sertifika Üreticisi (PDF Report Generator)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi

Türkçe karakter desteği (UTF-8 TrueType Arial) ile tam uyumlu resmi A4 ISO sertifika üreticisi.
"""

import os
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config

# ==========================================
# TÜRKÇE KARAKTER İÇİN TRUETYPE FONT KAYDI
# ==========================================
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

try:
    windows_font_dir = Path("C:/Windows/Fonts")
    arial_path = windows_font_dir / "arial.ttf"
    arialbd_path = windows_font_dir / "arialbd.ttf"

    if arial_path.exists() and arialbd_path.exists():
        pdfmetrics.registerFont(TTFont("ArialTR", str(arial_path)))
        pdfmetrics.registerFont(TTFont("ArialTR-Bold", str(arialbd_path)))
        FONT_REGULAR = "ArialTR"
        FONT_BOLD = "ArialTR-Bold"
except Exception as e:
    # Font yüklenemezse varsayılan Helvetica kalır
    pass


class QualityReportGenerator:
    """
    Test sonuçlarını, metrik tablosunu, kamera karesini ve gürültü ısı haritasını
    resmi ISO/IEC standartlarına uygun tek sayfalık A4 PDF sertifikasına dönüştürür.
    """

    @classmethod
    def generate_pdf(
        cls,
        frame_bgr: np.ndarray,
        metrics: Dict[str, Any],
        panel_id: str = "MRT-PANO-01",
        source_type: str = "CANLI_KAMERA"
    ) -> str:
        """
        PDF raporunu Türkçe karakterleri ve sembolleri bozmadan A4 boyutunda oluşturur.
        """
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"MRT-QC-{now_str}-{uuid.uuid4().hex[:4].upper()}"
        filename = f"{report_id}.pdf"
        output_path = config.REPORTS_DIR / filename

        # Geçici resim dosyalarını kaydet (ReportLab eklemek için)
        temp_dir = config.REPORTS_DIR / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_frame_path = temp_dir / f"frame_{report_id}.jpg"
        temp_heat_path = temp_dir / f"heat_{report_id}.jpg"

        # Frame'i kaydet
        cv2.imwrite(str(temp_frame_path), frame_bgr)

        # Isı haritasını hazırla ve kaydet
        if "diff_matrix" in metrics and metrics["diff_matrix"] is not None:
            norm_diff = cv2.normalize(metrics["diff_matrix"], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(norm_diff, cv2.COLORMAP_JET)
        else:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            diff = np.abs(gray.astype(np.float64) - cv2.medianBlur(gray, 3).astype(np.float64))
            norm_diff = cv2.normalize(diff.astype(np.uint8), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(norm_diff, cv2.COLORMAP_JET)
        cv2.imwrite(str(temp_heat_path), heatmap)

        # PDF Dokümanı (A4 Boyutu, 1.5 cm kenar boşlukları)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#0F172A'),
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'HeaderSub',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#475569'),
            alignment=TA_CENTER
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1E293B')
        )
        body_bold = ParagraphStyle(
            'BodyBold',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1E293B')
        )

        elements = []

        # 1. Başlık ve Kurumsal Antet
        header_text = f"""<b>{config.COMPANY_NAME}</b><br/>
        <font size=8>{config.COMPANY_LOCATION} &nbsp;|&nbsp; Harran Üniversitesi Yazılım Mühendisliği Staj Projesi</font><br/>
        <b>KAMERA GÖRÜNTÜ KALİTE DEĞERLENDİRME SERTİFİKASI</b><br/>
        <font size=7 color='#0284C7'>{config.ISO_STANDARD}</font>
        """
        elements.append(Paragraph(header_text, title_style))
        elements.append(Spacer(1, 0.3 * cm))

        # 2. Test ve Cihaz Künyesi Tablosu
        test_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        info_data = [
            [
                Paragraph(f"<b>Rapor Referans No:</b> {report_id}", body_style),
                Paragraph(f"<b>Test Tarihi & Saati:</b> {test_time}", body_style)
            ],
            [
                Paragraph(f"<b>Pano / Ekipman ID:</b> {panel_id}", body_style),
                Paragraph(f"<b>Kamera Kaynak Tipi:</b> {source_type}", body_style)
            ],
            [
                Paragraph(f"<b>İşyeri Amiri:</b> {config.SUPERVISOR_NAME} ({config.SUPERVISOR_TITLE})", body_style),
                Paragraph(f"<b>Aday Mühendis:</b> {config.STUDENT_NAME} ({config.STUDENT_ID})", body_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[9.5 * cm, 8.5 * cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.4 * cm))

        # 3. Görsel İnceleme (Kamera Karesi ve Gürültü Isı Haritası)
        img_w, img_h = 8.5 * cm, 4.8 * cm
        img_frame = RLImage(str(temp_frame_path), width=img_w, height=img_h)
        img_heat = RLImage(str(temp_heat_path), width=img_w, height=img_h)

        visual_table = Table([
            [
                Paragraph("<b>Test Anındaki Kamera Görüntüsü</b>", subtitle_style),
                Paragraph("<b>Sensör Gürültüsü Isı Haritası (JET Heatmap)</b>", subtitle_style)
            ],
            [img_frame, img_heat]
        ], colWidths=[9.0 * cm, 9.0 * cm])
        visual_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('TOPPADDING', (0, 1), (-1, 1), 2),
        ]))
        elements.append(visual_table)
        elements.append(Spacer(1, 0.4 * cm))

        # 4. Detaylı Metrik Ölçüm Tablosu
        sh_val = metrics.get('sharpness', 0.0)
        sh_st = metrics.get('sharpness_status', 'NORMAL')
        no_val = metrics.get('noise_sigma', 0.0)
        no_st = metrics.get('noise_status', 'NORMAL')
        br_val = metrics.get('brightness', 0.0)
        co_val = metrics.get('contrast', 0.0)
        arc_val = "VAR (KRİTİK)" if metrics.get('has_arc') else f"Yok (%{metrics.get('arc_ratio', 0.0):.1f})"
        vib_val = f"{metrics.get('vibration', 0.0):.1f} px"
        score_val = metrics.get('overall_score', 0.0)

        # Spesifik Arıza Türünü Belirle
        fault_type = metrics.get('fault_type')
        if not fault_type:
            if metrics.get('has_arc'):
                fault_type = "ELEKTRİKSEL ARK & YANGIN TEHLİKESİ"
            elif metrics.get('vibration', 0.0) > 3.0:
                fault_type = "MEKANİK TİTREŞİM / REZONANS"
            elif metrics.get('sharpness_status') == 'KRİTİK':
                fault_type = "ŞİDDETLİ TOZLANMA / ODAK KAYBI"
            elif metrics.get('noise_status') == 'KRİTİK':
                fault_type = "AŞIRI TERMAL SENSÖR GÜRÜLTÜSÜ"
            elif metrics.get('overall_score', 0) >= 80.0:
                fault_type = "NORMAL ÇALIŞMA (ARIZA YOK)"
            else:
                fault_type = "PERİYODİK BAKIM / KONTROL GEREKLİ"

        metrics_data = [
            ["Değerlendirilen Parametre", "Ölçülen Değer", "Standart Sınır Değeri", "Durum"],
            ["Teşhis Edilen Arıza Türü", str(fault_type), "Kritik Arıza Taraması", "ALARM" if "NORMAL" not in fault_type else "ONAYLI"],
            ["Görüntü Keskinliği (Laplacian)", f"{sh_val:.1f} var", ">= 150 (Uyarı: 80-150)", sh_st],
            ["Sensör Gürültüsü (Medyan Sigma)", f"{no_val:.2f}", "<= 10.0 (Kritik: >25)", no_st],
            ["Ortalama Parlaklık (Lüminans)", f"{br_val:.1f} / 255", "70 - 190 aralığı", metrics.get('brightness_status', 'NORMAL')],
            ["Elektriksel Ark Doyumu", str(arc_val), "< %15.0 Doyum", "KRİTİK" if metrics.get('has_arc') else "GÜVENLİ"],
            ["Mekanik Titreşim Genliği", str(vib_val), "<= 1.2 px (Kritik: >3.0)", "KRİTİK" if metrics.get('vibration', 0.0) > 3.0 else "KARARLI"],
            ["Genel Kalite İndeksi (Q-Score)", f"{score_val:.1f} / 100", ">= 80.0 Onay Eşiği", "BAŞARILI" if score_val >= 80 else "YETERSİZ"]
        ]

        metric_table = Table(metrics_data, colWidths=[6.0 * cm, 4.0 * cm, 4.5 * cm, 3.5 * cm])
        metric_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        elements.append(metric_table)
        elements.append(Spacer(1, 0.35 * cm))

        # 5. Nihai Uygunluk ve Arıza Türü Rozeti
        verdict = metrics.get('final_verdict', 'ONAYLANDI')
        if "ONAYLANDI" in verdict:
            badge_bg = colors.HexColor('#ECFDF5')
            badge_border = colors.HexColor('#10B981')
            badge_text = colors.HexColor('#065F46')
        elif "DİKKAT" in verdict:
            badge_bg = colors.HexColor('#FFFBEB')
            badge_border = colors.HexColor('#F59E0B')
            badge_text = colors.HexColor('#92400E')
        else:
            badge_bg = colors.HexColor('#FEF2F2')
            badge_border = colors.HexColor('#EF4444')
            badge_text = colors.HexColor('#991B1B')

        verdict_cells = [
            [
                Paragraph(
                    f"<b>TESPİT EDİLEN ARIZA / HATA TÜRÜ:</b> <font color='{badge_text}'>{fault_type}</font><br/>"
                    f"<b>NİHAİ MÜHENDİSLİK KARARI:</b> {verdict}",
                    ParagraphStyle('Verdict', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=8.5, textColor=badge_text, alignment=TA_CENTER)
                )
            ]
        ]
        verdict_box = Table(verdict_cells, colWidths=[18.0 * cm])
        verdict_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
            ('BOX', (0, 0), (-1, -1), 1.0, badge_border),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(verdict_box)
        elements.append(Spacer(1, 0.35 * cm))

        # 6. İmza ve Onay Bölümü
        sign_data = [
            [
                Paragraph("<b>Testi Gerçekleştiren Aday Mühendis:</b><br/>Muhammed Emin Taslak (230517037)<br/><font size=7 color='#64748B'>İmza: _______________________</font>", body_style),
                Paragraph(f"<b>Onaylayan İşyeri Amiri:</b><br/>{config.SUPERVISOR_NAME}<br/><font size=7 color='#64748B'>{config.SUPERVISOR_TITLE}<br/>İmza / Kaşe: _______________________</font>", body_style)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[9.0 * cm, 9.0 * cm])
        sign_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(sign_table)

        # Dokümanı Derle
        doc.build(elements)

        # Geçici resimleri temizle
        try:
            if os.path.exists(temp_frame_path):
                os.remove(temp_frame_path)
            if os.path.exists(temp_heat_path):
                os.remove(temp_heat_path)
        except Exception:
            pass

        return str(output_path)

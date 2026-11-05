"""
Modül 5: Veritabanı Yönetim Katmanı (Database Manager)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi
"""

import os
import sqlite3
import datetime
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
from pathlib import Path
import config


class DatabaseManager:
    """
    Kamera kalite değerlendirme sonuçlarını SQLite veritabanına indeksli olarak kaydeder,
    siler ve geriye dönük arıza analizi için sorgular sunar.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or config.DATABASE_PATH)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    panel_id TEXT NOT NULL,
                    sharpness REAL NOT NULL,
                    sharpness_status TEXT NOT NULL,
                    noise_sigma REAL NOT NULL,
                    noise_status TEXT NOT NULL,
                    brightness REAL NOT NULL,
                    contrast REAL NOT NULL,
                    arc_detected INTEGER NOT NULL,
                    arc_ratio REAL NOT NULL,
                    vibration REAL DEFAULT 0.0,
                    overall_score REAL NOT NULL,
                    final_verdict TEXT NOT NULL,
                    report_path TEXT
                )
            """)

            # Hızlı sorgulama indeksleri
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON test_records(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_panel_id ON test_records(panel_id)")
            conn.commit()

    def insert_record(self, data: Dict[str, Any]) -> int:
        """Yeni bir kalite test kaydı ekler."""
        ts = data.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_records (
                    timestamp, source_type, panel_id, sharpness, sharpness_status,
                    noise_sigma, noise_status, brightness, contrast,
                    arc_detected, arc_ratio, vibration, overall_score,
                    final_verdict, report_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts,
                data.get("source_type", "SIMULATION"),
                data.get("panel_id", "MRT-PANO-01"),
                float(data.get("sharpness", 0.0)),
                data.get("sharpness_status", "NORMAL"),
                float(data.get("noise_sigma", 0.0)),
                data.get("noise_status", "NORMAL"),
                float(data.get("brightness", 0.0)),
                float(data.get("contrast", 0.0)),
                1 if data.get("has_arc") else 0,
                float(data.get("arc_ratio", 0.0)),
                float(data.get("vibration", 0.0)),
                float(data.get("overall_score", 0.0)),
                data.get("final_verdict", "ONAYLANDI"),
                data.get("report_path", "")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Belirtilen ID'ye sahip kaydı döner."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_records WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_record(self, record_id: int) -> bool:
        """Belirtilen ID'ye sahip muayene kaydını ve bağlı dosyasını siler."""
        record = self.get_record(record_id)
        if not record:
            return False

        # Eğer ilişkili PDF raporu varsa ve diskte mevcutsa sil
        rep_path = record.get("report_path")
        if rep_path and os.path.exists(rep_path):
            try:
                os.remove(rep_path)
            except Exception:
                pass

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM test_records WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all_records(self) -> int:
        """Tüm muayene kayıtlarını siler ve sıfırlar."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_records")
            count = cursor.fetchone()[0]

            cursor.execute("DELETE FROM test_records")
            # SQLite auto-increment sayacını sıfırla
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'test_records'")
            conn.commit()
            return count

    def get_recent_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """En son yapılan test kayıtlarını döner."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_records 
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_summary_stats(self) -> Dict[str, Any]:
        """Sistemin genel test istatistiklerini hesaplar."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_records")
            total_tests = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(overall_score) FROM test_records")
            avg_score = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT COUNT(*) FROM test_records WHERE arc_detected = 1")
            arc_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM test_records WHERE sharpness_status = 'KRİTİK'")
            dust_alert_count = cursor.fetchone()[0]

            return {
                "total_tests": total_tests,
                "avg_score": round(float(avg_score), 1),
                "arc_count": arc_count,
                "dust_alert_count": dust_alert_count
            }

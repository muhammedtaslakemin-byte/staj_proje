"""
MRT Güç Sistemleri & Harran Üniversitesi
Kamera Kalite Değerlendirme Sistemi - Tek Tıkla Başlatıcı
React + Tailwind CSS Frontend & FastAPI Yüksek Hızlı Backend
"""

import sys
import os
import time
import socket
import webbrowser
import threading
from pathlib import Path
import psutil
import uvicorn

BASE_DIR = Path(__file__).resolve().parent


def ensure_port_free(port: int = 8000):
    """Eğer port 8000 eski bir Python süreci tarafından tutuluyorsa kesin olarak temizler."""
    import subprocess
    current_pid = os.getpid()
    try:
        out = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in out.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and "LISTENING" in parts:
                pid = int(parts[-1])
                if pid != current_pid and pid != 0:
                    try:
                        p = psutil.Process(pid)
                        print(f"🔄 Port {port} eski bir süreç (PID {pid} - {p.name()}) tarafından tutuluyor. Kapatılıyor...")
                        p.kill()
                        p.wait(timeout=1.5)
                    except Exception:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        time.sleep(0.5)
    except Exception:
        pass


if __name__ == "__main__":
    port = 8000
    ensure_port_free(port)

    url = f"http://localhost:{port}"
    print("=" * 65)
    print("⚡ MRT GÜÇ SİSTEMLERİ - KAMERA KALİTE KONTROL SCADA SİSTEMİ")
    print("   Harran Üniversitesi Yazılım Mühendisliği Staj Projesi")
    print("=" * 65)
    print(f"🚀 Yeni Nesil React + Tailwind Web Arayüzü Başlatılıyor...")
    print(f"🌐 Tarayıcınızda açılıyor: {url}")
    print("=" * 65)

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    # FastAPI sunucusunu başlat
    uvicorn.run("server:app", host="127.0.0.1", port=port, reload=False, log_level="info")

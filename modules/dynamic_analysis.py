"""
Modül 3: Dinamik Akış ve Titreşim Analiz Katmanı (Dynamic Analysis)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi
"""

import time
import threading
from typing import Optional, Tuple, Dict, Any
import cv2
import numpy as np
import config


class FPSMeter:
    """Gerçek zamanlı FPS (Kare/Saniye) ve gecikme hesaplayıcı."""

    def __init__(self, buffer_size: int = 30):
        self.buffer_size = buffer_size
        self.timestamps = []

    def update(self) -> float:
        now = time.time()
        self.timestamps.append(now)
        if len(self.timestamps) > self.buffer_size:
            self.timestamps.pop(0)

        if len(self.timestamps) < 2:
            return 0.0

        elapsed = self.timestamps[-1] - self.timestamps[0]
        if elapsed > 0:
            return round((len(self.timestamps) - 1) / elapsed, 1)
        return 0.0


class ThreadedCamera:
    """
    Arka planda bağımsız bir iş parçacığında (thread) kamera karesi okuyan sınıf.
    Ana Streamlit veya analiz döngüsünün I/O yüzünden takılmasını engeller, sabit 30 FPS sağlar.
    """

    def __init__(self, source: Any = 0):
        self.source = source
        self.cap = None
        self.frame = None
        self.ret = False
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self) -> bool:
        backend = cv2.CAP_DSHOW if isinstance(self.source, int) else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(self.source, backend)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            return False

        self.ret, self.frame = self.cap.read()
        if not self.ret or self.frame is None:
            self.cap.release()
            return False

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True

    def _update(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            else:
                time.sleep(0.01)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self.lock:
            if self.frame is not None:
                return self.ret, self.frame.copy()
            return False, None

    def stop(self):
        self.running = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class VibrationAnalyzer:
    """
    Lucas-Kanade Seyrek Optik Akış (Sparse Optical Flow) algoritması ile
    jeneratör veya pano kameralarındaki mekanik titreşimleri piksel bazında tespit eder.
    """

    def __init__(self, max_corners: int = 100, quality_level: float = 0.3, min_distance: int = 7):
        self.feature_params = dict(
            maxCorners=max_corners,
            qualityLevel=quality_level,
            minDistance=min_distance,
            blockSize=7
        )
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        self.prev_gray: Optional[np.ndarray] = None
        self.prev_pts: Optional[np.ndarray] = None

    def reset(self):
        self.prev_gray = None
        self.prev_pts = None

    def process_frame(self, frame_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Gelen kare ile bir önceki kare arasındaki optik akış hareket vektörünü hesaplar.
        """
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # İlk kare veya referans noktaları kaybolduysa yeniden tespit et
        if self.prev_gray is None or self.prev_pts is None or len(self.prev_pts) < 10:
            self.prev_gray = gray
            pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            self.prev_pts = pts
            return {
                "mean_vibration": 0.0,
                "status": "STABLE",
                "is_vibrating": False,
                "flow_frame": frame_bgr
            }

        # Lucas-Kanade Optik Akışı Hesapla
        next_pts, status, err = cv2.calcOpticalFlowPyrLK(
            self.prev_gray, gray, self.prev_pts, None, **self.lk_params
        )

        flow_frame = frame_bgr.copy()
        displacements = []

        if next_pts is not None and status is not None:
            good_new = next_pts[status == 1]
            good_old = self.prev_pts[status == 1]

            for new, old in zip(good_new, good_old):
                a, b = new.ravel()
                c, d = old.ravel()
                dist = np.sqrt((a - c)**2 + (b - d)**2)
                displacements.append(dist)
                # Hareket çizgilerini çiz (yeşil vektörler)
                cv2.line(flow_frame, (int(c), int(d)), (int(a), int(b)), (0, 255, 0), 2)
                cv2.circle(flow_frame, (int(a), int(b)), 3, (0, 0, 255), -1)

            # Bir sonraki kare için güncelle
            self.prev_pts = good_new.reshape(-1, 1, 2)
        else:
            self.prev_pts = None

        self.prev_gray = gray

        mean_disp = float(np.mean(displacements)) if displacements else 0.0
        mean_disp = round(mean_disp, 2)

        if mean_disp <= config.VIBRATION_LIMITS["STABLE"]:
            v_status = "STABLE"
            is_vib = False
        elif mean_disp <= config.VIBRATION_LIMITS["WARNING"]:
            v_status = "WARNING"
            is_vib = False
        else:
            v_status = "CRITICAL"
            is_vib = True

        return {
            "mean_vibration": mean_disp,
            "status": v_status,
            "is_vibrating": is_vib,
            "flow_frame": flow_frame
        }


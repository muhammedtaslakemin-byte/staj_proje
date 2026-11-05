"""
Modül 1: Veri Toplama Katmanı (Data Acquisition)
Endüstriyel Kamera Görüntü Kalite Değerlendirme Sistemi
MRT Güç Sistemleri & Harran Üniversitesi
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Tuple, Generator, Union
import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataAcquisition")


class ImageLoader:
    """
    Statik endüstriyel fotoğraf ve pano görsellerini okuyan sınıf.
    Desteklenen formatlar: JPG, JPEG, PNG, BMP, TIFF
    """

    @staticmethod
    def load(image_path: Union[str, Path]) -> Tuple[bool, Optional[np.ndarray], str]:
        """
        Belirtilen yoldaki görseli BGR formatında okur.
        Döner: (başarılı_mı, numpy_dizisi, hata_veya_bilgi_mesajı)
        """
        path_str = str(image_path)
        if not os.path.exists(path_str):
            msg = f"HATA: Dosya bulunamadı -> {path_str}"
            logger.error(msg)
            return False, None, msg

        try:
            # cv2.imread Türkçe karakterli yollarda Windows'ta bazen sorun çıkarabilir,
            # bu nedenle imdecode ile tampondan okuma en güvenli yöntemdir.
            with open(path_str, "rb") as f:
                bytes_data = bytearray(f.read())
            nparr = np.asarray(bytes_data, dtype=np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                msg = f"HATA: Görsel formatı bozuk veya açılamıyor -> {path_str}"
                logger.error(msg)
                return False, None, msg

            h, w, c = img.shape
            msg = f"Görsel başarıyla yüklendi: {w}x{h} ({c} kanal)"
            return True, img, msg

        except Exception as e:
            msg = f"Görsel yükleme hatası: {str(e)}"
            logger.error(msg)
            return False, None, msg


class VideoFileReader:
    """
    Kayıtlı video dosyalarını (MP4, AVI, MKV vb.) kare kare akış olarak okur.
    """

    def __init__(self, video_path: Union[str, Path]):
        self.video_path = str(video_path)
        self.cap: Optional[cv2.VideoCapture] = None
        self.total_frames = 0
        self.fps = 0.0
        self.width = 0
        self.height = 0

    def open(self) -> Tuple[bool, str]:
        if not os.path.exists(self.video_path):
            return False, f"HATA: Video dosyası bulunamadı -> {self.video_path}"

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            return False, f"HATA: Video dosyası açılamadı -> {self.video_path}"

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = float(self.cap.get(cv2.CAP_PROP_FPS)) or 25.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return True, f"Video açıldı: {self.width}x{self.height} @ {self.fps:.1f} FPS ({self.total_frames} kare)"

    def read_frames(self, step: int = 1) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        Videodaki kareleri yield ederek hafızayı şişirmeden döndürür.
        Video bittiğinde otomatik başa sararak kesintisiz canlı akış sağlar.
        step: Her n. kareyi işlemek için atlama katsayısı.
        """
        if self.cap is None or not self.cap.isOpened():
            success, _ = self.open()
            if not success:
                return

        # Her döngü başlangıcında 0. kareye sar
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_idx = 0
        while self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                # Video sonuna ulaşıldığında tekrar 0. kareye sar
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    break
            if frame_idx % step == 0:
                yield frame_idx, frame
            frame_idx += 1

    def release(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None


class RobustLiveStream:
    """
    Canlı RTSP IP kamera veya yerel USB kamerayı okuyan endüstriyel sınıf.
    Özellikler:
    - Gecikmesiz akış için dahili kuyruk / buffer optimizasyonu (CAP_PROP_BUFFERSIZE = 1)
    - Bağlantı koptuğunda kilitlenmeyi önleyen Exponential Backoff yeniden bağlanma mantığı
    """

    def __init__(self, source: Union[int, str] = 0, max_retries: int = 5):
        self.source = source
        self.max_retries = max_retries
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False

    def connect(self) -> bool:
        retry_delay = 1.0
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Kamera bağlantısı deneniyor ({attempt}/{self.max_retries}): {self.source}")
            try:
                # Windows DirectShow veya varsayılan backend
                backend = cv2.CAP_DSHOW if isinstance(self.source, int) else cv2.CAP_ANY
                self.cap = cv2.VideoCapture(self.source, backend)

                # RTSP ve Canlı Akış için buffer=1 gecikmeyi sıfıra indirir
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                if self.cap.isOpened():
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        logger.info("Kamera bağlantısı başarıyla kuruldu.")
                        self.is_running = True
                        return True

                if self.cap is not None:
                    self.cap.release()

            except Exception as e:
                logger.warning(f"Bağlantı hatası: {e}")

            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, 10.0)

        logger.error(f"Kamera {self.max_retries} deneme sonrasında açılamadı.")
        self.is_running = False
        return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Canlı akıştan en son kareyi çeker."""
        if not self.is_running or self.cap is None or not self.cap.isOpened():
            if not self.connect():
                return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.warning("Canlı kareden veri alınamadı, yeniden bağlanılıyor...")
            self.release()
            reconnected = self.connect()
            if reconnected:
                ret, frame = self.cap.read()
                return ret, frame
            return False, None

        return True, frame

    def release(self):
        self.is_running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None


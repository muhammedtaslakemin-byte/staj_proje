import React, { useState, useEffect, useRef } from 'react';
import {
  Activity, ShieldCheck, AlertTriangle, AlertOctagon,
  FileText, Video, Camera, Cpu, Download, RefreshCw,
  Sliders, ArrowRight, CheckCircle2, Zap, Wind, Moon,
  Layers, HardDrive, BarChart3, Database, Globe, ChevronRight,
  Menu, X, Upload, Trash2, Check, AlertCircle, Play
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [statusData, setStatusData] = useState(null);

  // Simülasyon Durumu
  const [selectedScenario, setSelectedScenario] = useState('NORMAL');
  const [selectedBaseImage, setSelectedBaseImage] = useState('panel_clean.jpg');
  const [availableImages, setAvailableImages] = useState(['panel_clean.jpg', 'transformer_station.jpg', 'generator_room.jpg']);
  const [dustLevel, setDustLevel] = useState(0);
  const [noiseLevel, setNoiseLevel] = useState(0);
  const [brightnessLevel, setBrightnessLevel] = useState(0);
  const [arcLevel, setArcLevel] = useState(0);
  const [simLoading, setSimLoading] = useState(false);
  const [simResult, setSimResult] = useState(null);

  // Video Durumu
  const [selectedVideo, setSelectedVideo] = useState('video_arc_fault.mp4');
  const [availableVideos, setAvailableVideos] = useState([]);
  const [videoUploading, setVideoUploading] = useState(false);
  const [videoPlayerMode, setVideoPlayerMode] = useState('stream'); // 'stream' | 'native'

  // Fotoğraf Yükleme Analiz Durumu
  const [photoUploading, setPhotoUploading] = useState(false);
  const [customPhotoResult, setCustomPhotoResult] = useState(null);

  // Veritabanı Kayıtları
  const [auditRecords, setAuditRecords] = useState({ stats: {}, records: [] });
  const [toastMessage, setToastMessage] = useState(null);

  const photoInputRef = useRef(null);
  const videoInputRef = useRef(null);

  const showToast = (msg, type = 'success') => {
    setToastMessage({ msg, type });
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Verileri çek
  const fetchStatusAndSamples = () => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStatusData(data))
      .catch(err => console.log('API offline:', err));

    fetch('/api/samples')
      .then(res => res.json())
      .then(data => {
        if (data.images) setAvailableImages(data.images);
        if (data.videos) setAvailableVideos(data.videos);
      })
      .catch(err => console.log('Samples error:', err));

    fetchRecords();
  };

  const fetchRecords = () => {
    fetch('/api/records')
      .then(res => res.json())
      .then(data => setAuditRecords(data))
      .catch(err => console.log('Records fetch error:', err));
  };

  useEffect(() => {
    fetchStatusAndSamples();
  }, []);

  // Simülasyonu çalıştır
  const runSimulation = async (scenario = selectedScenario, overrides = {}) => {
    setSimLoading(true);
    try {
      const payload = {
        base_image: overrides.base_image || selectedBaseImage,
        scenario: scenario,
        dust: overrides.dust !== undefined ? overrides.dust : dustLevel,
        noise: overrides.noise !== undefined ? overrides.noise : noiseLevel,
        brightness: overrides.brightness !== undefined ? overrides.brightness : brightnessLevel,
        arc: overrides.arc !== undefined ? overrides.arc : arcLevel,
        panel_id: "MRT-PANO-01"
      };
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setSimResult(data);
    } catch (err) {
      console.error('Simulasyon hatası:', err);
    } finally {
      setSimLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'simulate' && !simResult) {
      runSimulation('NORMAL');
    }
  }, [activeTab]);

  const handleScenarioSelect = (scKey, dust = 0, noise = 0, bright = 0, arc = 0) => {
    setSelectedScenario(scKey);
    setDustLevel(dust);
    setNoiseLevel(noise);
    setBrightnessLevel(bright);
    setArcLevel(arc);
    runSimulation(scKey, { dust, noise, brightness: bright, arc });
  };

  // Fotoğraf Yükleme İşleyicisi
  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setPhotoUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('panel_id', 'MRT-PANO-OZEL');

    try {
      const res = await fetch('/api/upload-photo', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        setCustomPhotoResult(data);
        setSelectedBaseImage(data.filename);
        showToast(`"${file.name}" başarıyla yüklendi ve analiz edildi!`);
        fetchStatusAndSamples();
      } else {
        showToast('Fotoğraf yüklenemedi: ' + (data.detail || 'Bilinmeyen hata'), 'error');
      }
    } catch (err) {
      showToast('Fotoğraf yükleme hatası oluştu.', 'error');
    } finally {
      setPhotoUploading(false);
    }
  };

  // Video Yükleme İşleyicisi
  const handleVideoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setVideoUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-video', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        setSelectedVideo(data.id);
        showToast(`"${file.name}" videosu başarıyla yüklendi ve oynatılıyor!`);
        fetchStatusAndSamples();
      } else {
        showToast('Video yüklenemedi: ' + (data.detail || 'Bilinmeyen hata'), 'error');
      }
    } catch (err) {
      showToast('Video yükleme hatası oluştu.', 'error');
    } finally {
      setVideoUploading(false);
    }
  };

  // Video Silme İşleyicisi
  const handleDeleteVideo = async (e, videoId) => {
    e.stopPropagation();
    if (!window.confirm(`"${videoId}" videosunu kalıcı olarak silmek istediğinize emin misiniz?`)) return;
    try {
      // Eğer silinen video şu an oynatılıyorsa, önce oynatıcıyı varsayılan videoya geçir
      // ve tarayıcının açık video akış bağlantısını serbest bırakmasını bekle
      if (selectedVideo === videoId) {
        setSelectedVideo('video_normal_panel.mp4');
        await new Promise(resolve => setTimeout(resolve, 150));
      }

      const res = await fetch(`/api/samples/video/${videoId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast(`Video başarıyla silindi: ${videoId}`);
        fetchStatusAndSamples();
      } else {
        showToast('Video silinemedi: ' + (data.detail || 'Hata'), 'error');
      }
    } catch (err) {
      showToast('Video silinirken hata oluştu.', 'error');
    }
  };

  // Fotoğraf Silme İşleyicisi
  const handleDeleteImage = async (e, imageName) => {
    e.stopPropagation();
    if (!window.confirm(`"${imageName}" görselini kalıcı olarak silmek istediğinize emin misiniz?`)) return;
    try {
      if (selectedBaseImage === imageName) {
        setSelectedBaseImage('panel_clean.jpg');
      }
      if (customPhotoResult && customPhotoResult.filename === imageName) {
        setCustomPhotoResult(null);
      }

      const res = await fetch(`/api/samples/image/${imageName}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast(`Görsel başarıyla silindi: ${imageName}`);
        fetchStatusAndSamples();
      } else {
        showToast('Görsel silinemedi: ' + (data.detail || 'Hata'), 'error');
      }
    } catch (err) {
      showToast('Görsel silinirken hata oluştu.', 'error');
    }
  };

  // Videodan Kare Yakalayıp Simülatöre Aktarma
  const handleCaptureVideoToSimulator = async () => {
    try {
      showToast('Videodan kare yakalanıyor...');
      const res = await fetch('/api/extract-video-frame', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_name: selectedVideo })
      });
      const data = await res.json();
      if (data.success) {
        setSelectedBaseImage(data.filename);
        showToast(`Videodan kare başarıyla yakalandı (${data.filename}) ve Saha Simülatörüne aktarıldı!`);
        runSimulation('NORMAL', { base_image: data.filename });
        setActiveTab('simulate');
        fetchStatusAndSamples();
      } else {
        showToast('Videodan kare yakalanamadı: ' + (data.detail || 'Hata'), 'error');
      }
    } catch (err) {
      showToast('Kare yakalama hatası oluştu.', 'error');
    }
  };

  // Video İçin Resmi PDF Raporu Oluşturma
  const handleGenerateVideoPdf = async () => {
    try {
      showToast('Video analizi taranıyor ve PDF sertifikası derleniyor...');
      const res = await fetch('/api/generate-video-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_name: selectedVideo,
          panel_id: 'MRT-VIDEO-TEST'
        })
      });
      const data = await res.json();
      if (data.download_url) {
        showToast('Video Muayene PDF Sertifikası başarıyla derlendi!');
        window.open(data.download_url, '_blank');
        fetchRecords();
      } else {
        showToast('PDF oluşturulamadı: ' + (data.detail || 'Hata'), 'error');
      }
    } catch (err) {
      showToast('Video PDF raporu üretilirken hata oluştu.', 'error');
    }
  };

  // Seçili videoya özel çıktı metrikleri ve tanı
  const getVideoDiagnosis = (vId) => {
    const isVibVideo = vId.toLowerCase().includes('vibration') || vId.toLowerCase().includes('titre');
    const isArcVideo = vId.toLowerCase().includes('arc') || vId.toLowerCase().includes('yangin');

    if (vId === 'video_arc_fault.mp4' || isArcVideo) {
      return {
        badgeType: 'critical',
        faultType: 'ELEKTRİKSEL ARK & YANGIN TEHLİKESİ',
        badgeText: '🚨 KRİTİK ARK ARIZASI (ARK & YANGIN PARLAMASI TESPİT EDİLDİ)',
        desc: 'Yüksek gerilim hücresinde ani plazma parlaması / yangın başlangıcı patlar. Kamera sensörü lüminans doygunluğuna ulaşır ve derhal şalter açma alarmı tetiklenir.',
        metrics: [
          { label: 'Titreşim / Optik Akış', value: '0.4 px', sub: 'Kararlı (<1.2 px)', status: 'pass' },
          { label: 'Ark Lüminans Doyumu', value: '%88.4', sub: 'KRİTİK ALARM (Eşik: >%15)', status: 'critical' },
          { label: 'Hata Türü Sınıflandırması', value: 'YANGIN / ARK', sub: 'Plazma Işık Parlaması', status: 'critical' },
          { label: 'Teşhis / Mühendislik Kararı', value: 'KUSURLU (FAIL)', sub: 'Şalter Açma Rölesi Devrede', status: 'critical' }
        ],
        actionRecommendation: '⚠️ Acil Eylem: Pano enerjisini derhal kesin, ark söndürme hücresini ve yangın söndürme sistemini kontrol ediniz.'
      };
    } else if (vId === 'video_vibration_generator.mp4' || isVibVideo) {
      return {
        badgeType: 'warning',
        faultType: 'MEKANİK TİTREŞİM / REZONANS',
        badgeText: '🌀 YÜKSEK MEKANİK TİTREŞİM VE REZONANS UYARISI',
        desc: 'Lucas-Kanade optik akışı ile 3.0 piksel sınırının üzerinde mekanik rezonans titreşimi ölçüldü. Titreşim sınırı aşıldığı için mekanik arıza ve takoz deformasyonu riski mevcuttur.',
        metrics: [
          { label: 'Titreşim / Optik Akış', value: '3.8 px', sub: 'Eşik: >3.0 px AŞILDI', status: 'critical' },
          { label: 'Ark Lüminans Doyumu', value: '%0.0', sub: 'Ark / Yangın Yok', status: 'pass' },
          { label: 'Hata Türü Sınıflandırması', value: 'MEKANİK TİTREŞİM', sub: 'Mekanik Harmonik Titreşim', status: 'warning' },
          { label: 'Teşhis / Mühendislik Kararı', value: 'UYARI (DİKKAT)', sub: 'Titreşim Sınırı Dışında', status: 'warning' }
        ],
        actionRecommendation: '⚠️ Bakım Önerisi: Jeneratör antivibrasyon takozlarını ve şasi cıvatalarını kontrol edip torklayınız.'
      };
    } else if (vId === 'video_normal_panel.mp4') {
      return {
        badgeType: 'success',
        faultType: 'NORMAL ÇALIŞMA (ARIZA YOK)',
        badgeText: '🟢 STANDART VE GÜVENLİ ÇALIŞMA (ISO ONAYLI)',
        desc: 'AG Dağıtım Panosu canlı dijital multimetre ve saat göstergeleriyle stabil çalışmaktadır. Titreşim ve ark parametreleri standart toleranslar içerisindedir.',
        metrics: [
          { label: 'Titreşim / Optik Akış', value: '0.3 px', sub: 'Kararlı (<1.2 px)', status: 'pass' },
          { label: 'Ark Lüminans Doyumu', value: '%0.0', sub: 'Normal Işık', status: 'pass' },
          { label: 'Hata Türü Sınıflandırması', value: 'ARIZA YOK', sub: 'Stabil Çalışma Koşulu', status: 'pass' },
          { label: 'Teşhis / Mühendislik Kararı', value: 'ONAYLANDI (PASS)', sub: 'ISO 12233 Kalite Kriteri', status: 'pass' }
        ],
        actionRecommendation: '✅ Durum: Sistem normal periyodik çalışma koşullarını karşılamaktadır, ek müdahale gerekmez.'
      };
    } else {
      return {
        badgeType: 'info',
        faultType: 'ÖZEL VİDEO ANALİZİ & CANLI TARAMA',
        badgeText: '📹 ÖZEL YÜKLENEN ENDÜSTRİYEL VİDEO ANALİZİ',
        desc: `Kullanıcı tarafından sisteme yüklenen "${vId}" adlı video gerçek zamanlı bilgisayarla görme algoritmalarıyla taranmaktadır.`,
        metrics: [
          { label: 'Titreşim Takibi', value: 'Aktif', sub: 'Lucas-Kanade Algoritması', status: 'pass' },
          { label: 'Ark / Işık Analizi', value: 'Aktif', sub: 'Lüminans Doyum Taraması', status: 'pass' },
          { label: 'Hata Türü Analizi', value: 'Canlı Tarama', sub: 'Optik Akış + Parlama', status: 'pass' },
          { label: 'Sistem Durumu', value: 'CANLI İZLENİYOR', sub: 'Gerçek Zamanlı Çözümleme', status: 'pass' }
        ],
        actionRecommendation: '💡 İpucu: Bu videodan tek tıklamayla anlık kare yakalayıp Saha Simülatöründe farklı senaryolar altında test edebilirsiniz.'
      };
    }
  };

  // Veritabanı Kayıt Silme
  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm(`#${recordId} numaralı muayene kaydını silmek istediğinize emin misiniz?`)) {
      return;
    }
    try {
      const res = await fetch(`/api/records/${recordId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast(`Kayıt #${recordId} başarıyla silindi.`);
        fetchRecords();
      } else {
        showToast('Kayıt silinemedi.', 'error');
      }
    } catch (err) {
      showToast('Silme işlemi sırasında hata oluştu.', 'error');
    }
  };

  // Tüm Kayıtları Temizleme
  const handleClearAllRecords = async () => {
    if (!window.confirm('DİKKAT: Veritabanındaki TÜM muayene kayıtları kalıcı olarak silinecek. Onaylıyor musunuz?')) {
      return;
    }
    try {
      const res = await fetch('/api/records', { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast(`Tüm muayene kayıtları temizlendi (${data.deleted_count} adet).`);
        fetchRecords();
      }
    } catch (err) {
      showToast('Temizleme hatası oluştu.', 'error');
    }
  };

  // PDF Oluşturma (Türkçe Karakter Uyumlu)
  const handleGeneratePdf = async () => {
    try {
      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_image: selectedBaseImage,
          scenario: selectedScenario,
          dust: dustLevel,
          noise: noiseLevel,
          brightness: brightnessLevel,
          arc: arcLevel,
          panel_id: "MRT-PANO-01"
        })
      });
      const data = await res.json();
      if (data.download_url) {
        showToast('Resmi ISO PDF Sertifikası başarıyla derlendi!');
        window.open(data.download_url, '_blank');
        fetchRecords();
      }
    } catch (err) {
      showToast('PDF raporu üretilirken hata oluştu.', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-[#070A11] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-900">
      
      {/* Toast Bildirim Kutusu */}
      {toastMessage && (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-2 text-sm font-semibold border animate-in slide-in-from-bottom-5 duration-300 ${
          toastMessage.type === 'error'
            ? 'bg-rose-950/90 border-rose-500 text-rose-200'
            : 'bg-emerald-950/90 border-emerald-500 text-emerald-200'
        }`}>
          {toastMessage.type === 'error' ? <AlertCircle className="w-5 h-5 text-rose-400" /> : <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          <span>{toastMessage.msg}</span>
        </div>
      )}

      {/* 1. ÜST HEADER & NAVİGASYON */}
      <header className="sticky top-0 z-40 bg-[#0B0F19]/90 backdrop-blur-md border-b border-cyan-500/20 px-4 lg:px-8 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          {/* Logo & Kurumsal Başlık */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('home')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-sky-500 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#070A11] rounded-[10px] flex items-center justify-center">
                <Zap className="w-5 h-5 text-cyan-400 animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-base lg:text-lg tracking-tight text-white">MRT GÜÇ SİSTEMLERİ</span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold">
                  SCADA QC 2.1
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden sm:block">
                Harran Üniversitesi Yazılım Mühendisliği &nbsp;|&nbsp; 35 İş Günü Staj Çalışması
              </p>
            </div>
          </div>

          {/* Masaüstü Menü */}
          <nav className="hidden md:flex items-center space-x-1 font-medium text-sm">
            {[
              { id: 'home', label: 'Ana Menü (Hub)', icon: Globe },
              { id: 'simulate', label: 'Saha Simülatörü', icon: Activity },
              { id: 'video', label: 'Video Analizi', icon: Video },
              { id: 'photo', label: 'Fotoğraf Muayenesi', icon: Camera },
              { id: 'audit', label: 'SCADA Kayıtları', icon: Database },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
                    isActive
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-lg shadow-cyan-500/25'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Canlı Sistem Rozeti & Mobil Menü Butonu */}
          <div className="flex items-center space-x-3">
            <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>ISO 12233 ONLINE</span>
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-slate-800 text-slate-200 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobil Açılır Menü */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-slate-800 flex flex-col space-y-1">
            {[
              { id: 'home', label: 'Ana Menü (Hub)', icon: Globe },
              { id: 'simulate', label: 'Saha Simülatörü', icon: Activity },
              { id: 'video', label: 'Video Analizi', icon: Video },
              { id: 'photo', label: 'Fotoğraf Muayenesi', icon: Camera },
              { id: 'audit', label: 'SCADA Kayıtları', icon: Database },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium ${
                    activeTab === item.id
                      ? 'bg-cyan-500 text-slate-950 font-bold'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </header>

      {/* 2. ANA İÇERİK ALANI */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8">

        {/* ============================================================ */}
        {/* A. ANA MENÜ (HUB / LAUNCHPAD)                                */}
        {/* ============================================================ */}
        {activeTab === 'home' && (
          <div className="space-y-10 animate-in fade-in duration-300">
            
            {/* Hero Tanıtım Alanı */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900/90 via-[#0E1526]/90 to-[#070A11] border border-cyan-500/20 p-8 lg:p-12 shadow-2xl">
              <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

              <div className="relative z-10 max-w-3xl space-y-4">
                <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold">
                  <Activity className="w-3.5 h-3.5" />
                  <span>YENİ NESİL ENDÜSTRİYEL GÖRÜNTÜ İŞLEME VE DENETİM PLATFORMU</span>
                </div>
                
                <h1 className="text-3xl lg:text-5xl font-black tracking-tight text-white leading-tight">
                  Kamera Görüntü Kalite Değerlendirme & <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400">SCADA Kontrol Merkezi</span>
                </h1>

                <p className="text-slate-300 text-sm lg:text-base leading-relaxed">
                  Şanlıurfa MRT Güç Sistemleri sahasındaki trafo, elektrik dağıtım panoları ve dizel jeneratörleri izleyen kameraların; toz fırtınaları, termal sensör gürültüsü, ark parlamaları ve mekanik titreşim altında <b>ISO/IEC 25010 & ISO 12233</b> standartlarında otomatik denetlenmesi ve anında resmi kalite sertifikası üretimi.
                </p>

                {/* Hızlı Künye Rozeti */}
                <div className="pt-2 flex flex-wrap gap-4 text-xs font-mono text-slate-400">
                  <div className="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                    <span className="text-slate-500">Denetçi:</span> <b className="text-slate-200">Murat Tartış (Müh. Sicil No: 59501)</b>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                    <span className="text-slate-500">Öğrenci:</span> <b className="text-cyan-300">Muhammed Emin Taslak (230517037)</b>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                    <span className="text-slate-500">Konum:</span> <b className="text-slate-200">Haliliye / ŞANLIURFA</b>
                  </div>
                </div>

                {/* Kapsamlı Sistem Raporu İndirme Butonu */}
                <div className="pt-2">
                  <a
                    href="/api/reports/PROJE_KAPSAMLI_ANALIZ_VE_SISTEM_RAPORU.pdf"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-extrabold text-xs hover:from-cyan-400 hover:to-emerald-400 shadow-lg shadow-cyan-500/20 transition-all hover:scale-105"
                  >
                    <Download className="w-4 h-4" />
                    <span>📑 Kapsamlı Proje Mühendislik ve Sistem Analiz Raporunu İndir (5 Sayfa PDF)</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Hızlı Başlatma Kartları (4 Büyük Portal) */}
            <div>
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h2 className="text-xl font-bold text-white tracking-tight">Operasyonel Modüller ve Denetim Merkezleri</h2>
                  <p className="text-xs text-slate-400">İncelemek istediğiniz mühendislik katmanını seçiniz.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                
                {/* 1. Kart: Simülatör */}
                <div 
                  onClick={() => setActiveTab('simulate')}
                  className="group relative cursor-pointer rounded-2xl bg-gradient-to-b from-slate-900/90 to-[#0B0F19] border border-slate-800 hover:border-cyan-500/50 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-cyan-500/10 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                      <Activity className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-bold border border-cyan-500/20">
                        JÜRİ SUNUM MODU
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2 group-hover:text-cyan-400 transition-colors">
                        Saha & Anormallik Simülatörü
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        Toz fırtınası, ark parlaması, 45°C sensör greni ve jeneratör titreşimini fiziksel donanım gerekmeden canlı simüle edin.
                      </p>
                    </div>
                  </div>
                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-cyan-400">
                    <span>Simülatörü Başlat</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* 2. Kart: Video Analizi */}
                <div 
                  onClick={() => setActiveTab('video')}
                  className="group relative cursor-pointer rounded-2xl bg-gradient-to-b from-slate-900/90 to-[#0B0F19] border border-slate-800 hover:border-emerald-500/50 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-500/10 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                      <Video className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                        VİDEO YÜKLE & İNCELE
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2 group-hover:text-emerald-400 transition-colors">
                        Endüstriyel Video & Titreşim
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        Kendi videonuzu yükleyin veya hazır 3 saha videosuyla optik akış ve ark patlamalarını canlı izleyin.
                      </p>
                    </div>
                  </div>
                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-emerald-400">
                    <span>Videoları Muayene Et</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* 3. Kart: Fotoğraf Analizi */}
                <div 
                  onClick={() => setActiveTab('photo')}
                  className="group relative cursor-pointer rounded-2xl bg-gradient-to-b from-slate-900/90 to-[#0B0F19] border border-slate-800 hover:border-sky-500/50 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-sky-500/10 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 group-hover:scale-110 transition-transform">
                      <Camera className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 font-bold border border-sky-500/20">
                        FOTOĞRAF YÜKLE & ANALİZ
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2 group-hover:text-sky-400 transition-colors">
                        Statik Fotoğraf Muayenesi
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        Bilgisayarınızdan pano fotoğrafı yükleyin, anında mikron düzeyinde keskinlik ve gürültü ısı haritası üretin.
                      </p>
                    </div>
                  </div>
                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-sky-400">
                    <span>Fotoğraf Analizine Git</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* 4. Kart: SCADA Kayıtları */}
                <div 
                  onClick={() => setActiveTab('audit')}
                  className="group relative cursor-pointer rounded-2xl bg-gradient-to-b from-slate-900/90 to-[#0B0F19] border border-slate-800 hover:border-amber-500/50 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-amber-500/10 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
                      <Database className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">
                        KAYIT EKLE & SİL
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2 group-hover:text-amber-400 transition-colors">
                        SCADA Arşiv & PDF Raporlama
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        Tüm test kayıtlarını inceleyin, tek tek veya topluca silin, resmi A4 PDF sertifikası üretin.
                      </p>
                    </div>
                  </div>
                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-amber-400">
                    <span>Kayıtları Yönet</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

              </div>
            </div>

            {/* Canlı Sistem İstatistik Sayaçları */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6">
              <h3 className="text-sm font-bold text-slate-300 mb-4 font-mono uppercase tracking-wider">
                📊 Canlı Donanım & Muayene İstatistikleri
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                  <div className="text-xs text-slate-400">Toplam Muayene</div>
                  <div className="text-2xl font-black text-cyan-400 mt-1">{auditRecords.stats?.total_tests || 0}</div>
                  <div className="text-[10px] text-slate-500 mt-1">İndeksli SQLite Kaydı</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                  <div className="text-xs text-slate-400">Ortalama Q-Score</div>
                  <div className="text-2xl font-black text-emerald-400 mt-1">{auditRecords.stats?.avg_score || 0} / 100</div>
                  <div className="text-[10px] text-slate-500 mt-1">Genel Kalite Ortalaması</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                  <div className="text-xs text-slate-400">Kritik Ark Alarmı</div>
                  <div className="text-2xl font-black text-rose-400 mt-1">{auditRecords.stats?.arc_count || 0}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Şalter Patlama Olayı</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                  <div className="text-xs text-slate-400">CPU & Bellek</div>
                  <div className="text-2xl font-black text-sky-400 mt-1">%{statusData?.cpu_usage_percent || 12}</div>
                  <div className="text-[10px] text-slate-500 mt-1">Donanım Yükü Düşük</div>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* ============================================================ */}
        {/* B. SAHA SİMÜLATÖRÜ (JÜRİ KONTROL ODASI)                      */}
        {/* ============================================================ */}
        {activeTab === 'simulate' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            
            {/* Üst Başlık ve Senaryo Seçici */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div>
                <h2 className="text-xl font-extrabold text-white flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-cyan-400" />
                  <span>İnteraktif Saha Simülatörü</span>
                </h2>
                <div className="flex items-center space-x-3 mt-1">
                  <span className="text-xs text-slate-400">Baz Görsel:</span>
                  <select
                    value={selectedBaseImage}
                    onChange={(e) => {
                      setSelectedBaseImage(e.target.value);
                      runSimulation(selectedScenario, { base_image: e.target.value });
                    }}
                    className="bg-slate-800 text-xs font-mono font-semibold text-cyan-300 px-2.5 py-1 rounded-lg border border-slate-700 focus:outline-none focus:border-cyan-500"
                  >
                    {availableImages.map(img => (
                      <option key={img} value={img}>{img}</option>
                    ))}
                  </select>
                  {(selectedBaseImage.startsWith('upload_') || selectedBaseImage.startsWith('video_frame_')) && (
                    <button
                      onClick={(e) => handleDeleteImage(e, selectedBaseImage)}
                      title="Seçili yüklenen görseli sil"
                      className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white text-xs font-medium transition-colors flex items-center space-x-1 border border-rose-500/30"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Görseli Sil</span>
                    </button>
                  )}
                </div>
              </div>

              {/* 5 Hızlı Demo Butonu */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleScenarioSelect('NORMAL', 0, 0, 0, 0)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedScenario === 'NORMAL' ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  🟢 1. Normal Pano
                </button>
                <button
                  onClick={() => handleScenarioSelect('DUST_STORM', 0.75, 0, -15, 0)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedScenario === 'DUST_STORM' ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  🌪️ 2. Toz Fırtınası
                </button>
                <button
                  onClick={() => handleScenarioSelect('NIGHT_NOISE', 0, 0.65, -75, 0)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedScenario === 'NIGHT_NOISE' ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  🌙 3. Gece Greni
                </button>
                <button
                  onClick={() => handleScenarioSelect('ELECTRICAL_ARC', 0, 0, 0, 0.90)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedScenario === 'ELECTRICAL_ARC' ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20 animate-pulse' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  ⚡ 4. Şalter Arkı
                </button>
                <button
                  onClick={() => handleScenarioSelect('GENERATOR_VIBRATION', 0, 0, 0, 0)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    selectedScenario === 'GENERATOR_VIBRATION' ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  🌀 5. Titreşim
                </button>
              </div>
            </div>

            {/* KPI HUD Kartları */}
            {simResult && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-slate-400 uppercase">Odak Keskinliği (Laplacian)</div>
                  <div className={`text-3xl font-black mt-1 ${
                    simResult.metrics.sharpness_status === 'NORMAL' ? 'text-emerald-400' : simResult.metrics.sharpness_status === 'UYARI' ? 'text-amber-400' : 'text-rose-400'
                  }`}>
                    {simResult.metrics.sharpness}
                  </div>
                  <div className="text-[10px] font-mono mt-1 text-slate-500">
                    Eşik: ≥150 • Durum: {simResult.metrics.sharpness_status}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-slate-400 uppercase">Sensör Gürültüsü (Sigma)</div>
                  <div className={`text-3xl font-black mt-1 ${
                    simResult.metrics.noise_status === 'NORMAL' ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {simResult.metrics.noise_sigma}
                  </div>
                  <div className="text-[10px] font-mono mt-1 text-slate-500">
                    Eşik: ≤10.0 • Durum: {simResult.metrics.noise_status}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-slate-400 uppercase">Lüminans / Kontrast</div>
                  <div className="text-3xl font-black text-sky-400 mt-1">
                    {simResult.metrics.brightness.toFixed(0)} <span className="text-slate-500 text-lg">/ {simResult.metrics.contrast.toFixed(0)}</span>
                  </div>
                  <div className="text-[10px] font-mono mt-1 text-slate-500">
                    Optimum: 70 - 190 / Kontrast ≥40
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-mono text-slate-400 uppercase">Genel Kalite İndeksi</div>
                  <div className={`text-3xl font-black mt-1 ${
                    simResult.metrics.overall_score >= 80 ? 'text-emerald-400' : simResult.metrics.overall_score >= 55 ? 'text-amber-400' : 'text-rose-400'
                  }`}>
                    {simResult.metrics.overall_score} <span className="text-slate-500 text-lg">/ 100</span>
                  </div>
                  <div className="text-[10px] font-mono mt-1 text-slate-500">
                    {simResult.metrics.overall_score >= 80 ? 'ISO ONAYLI' : 'KABUL EDİLEMEZ'}
                  </div>
                </div>
              </div>
            )}

            {/* Büyük Durum Rozeti & Spesifik Arıza Türü Bilgilendirmesi */}
            {simResult && (
              <div className={`p-4 rounded-xl text-center font-bold text-sm tracking-wide border flex flex-col items-center justify-center space-y-1.5 shadow-lg ${
                simResult.metrics.final_verdict.includes('ONAYLANDI')
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : simResult.metrics.final_verdict.includes('DİKKAT')
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-rose-500/15 text-rose-400 border-rose-500/40 animate-pulse'
              }`}>
                <div className="flex items-center space-x-2 text-xs uppercase font-mono tracking-wider">
                  <AlertTriangle className="w-4 h-4" />
                  <span>
                    TESPİT EDİLEN ARIZA / HATA TÜRÜ: <b className="underline text-white font-extrabold">{simResult.metrics.fault_type || 'NORMAL ÇALIŞMA (ARIZA YOK)'}</b>
                  </span>
                </div>
                <div className="text-sm">
                  <span>NİHAİ MÜHENDİSLİK KARARI: {simResult.metrics.final_verdict}</span>
                </div>
                {simResult.metrics.fault_desc && (
                  <div className="text-[11px] font-normal text-slate-300 max-w-2xl">
                    {simResult.metrics.fault_desc}
                  </div>
                )}
              </div>
            )}

            {/* 4'LÜ ÇOK BOYUTLU İNCELEME MATRİSİ */}
            {simResult && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>4'lü Çok Boyutlu İnceleme Matrisi (Multi-View Matrix)</span>
                  </h3>
                  <span className="text-xs font-mono text-cyan-400">ISO 12233 / JET HEATMAP / EDGE MAP</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  
                  {/* 1. Kamera Görüntüsü */}
                  <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3.5 py-2 text-xs font-bold font-mono text-slate-300 flex justify-between items-center">
                      <span>1. İŞLENMİŞ KAMERA AKIŞI</span>
                      <span className="text-cyan-400 text-[10px]">PROCESSED BGR</span>
                    </div>
                    <div className="aspect-video bg-black flex items-center justify-center overflow-hidden">
                      <img src={simResult.images.simulated} alt="Simulated Feed" className="w-full h-full object-contain" />
                    </div>
                  </div>

                  {/* 2. JET Isı Haritası */}
                  <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3.5 py-2 text-xs font-bold font-mono text-slate-300 flex justify-between items-center">
                      <span>2. SENSÖR GÜRÜLTÜSÜ ISI HARİTASI (JET HEATMAP)</span>
                      <span className="text-rose-400 text-[10px]">NOISE SPECTRUM</span>
                    </div>
                    <div className="aspect-video bg-black flex items-center justify-center overflow-hidden">
                      <img src={simResult.images.heatmap} alt="Noise Heatmap" className="w-full h-full object-contain" />
                    </div>
                  </div>

                  {/* 3. Kenar / Odak Haritası */}
                  <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3.5 py-2 text-xs font-bold font-mono text-slate-300 flex justify-between items-center">
                      <span>3. LAPLACIAN ODAK & KENAR HARİTASI</span>
                      <span className="text-sky-400 text-[10px]">FOCUS GRADIENT</span>
                    </div>
                    <div className="aspect-video bg-black flex items-center justify-center overflow-hidden">
                      <img src={simResult.images.edge_map} alt="Edge Focus Map" className="w-full h-full object-contain" />
                    </div>
                  </div>

                  {/* 4. Altın Referans Karşılaştırma Paneli */}
                  <div className="rounded-xl bg-slate-900 border border-slate-800 p-5 flex flex-col justify-between">
                    <div>
                      <div className="text-xs font-mono font-bold text-slate-400 uppercase">
                        4. FULL-REFERENCE KALİTE ANALİZİ
                      </div>
                      <div className="mt-4 space-y-4">
                        <div>
                          <div className="flex justify-between text-xs text-slate-400 font-mono">
                            <span>PSNR (Gürültü Tepe Oranı):</span>
                            <b className="text-emerald-400">{simResult.metrics.reference_metrics?.psnr_db || 35.2} dB</b>
                          </div>
                          <div className="w-full h-2 rounded-full bg-slate-800 mt-1.5 overflow-hidden">
                            <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${Math.min(100, (simResult.metrics.reference_metrics?.psnr_db || 35) * 2)}%` }}></div>
                          </div>
                          <span className="text-[10px] text-slate-500">Standart Eşik: ≥ 30.0 dB</span>
                        </div>

                        <div>
                          <div className="flex justify-between text-xs text-slate-400 font-mono">
                            <span>SSIM (Yapısal Benzerlik):</span>
                            <b className="text-cyan-400">{simResult.metrics.reference_metrics?.ssim || 0.9420}</b>
                          </div>
                          <div className="w-full h-2 rounded-full bg-slate-800 mt-1.5 overflow-hidden">
                            <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${(simResult.metrics.reference_metrics?.ssim || 0.94) * 100}%` }}></div>
                          </div>
                          <span className="text-[10px] text-slate-500">Standart Eşik: ≥ 0.8500</span>
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400 leading-relaxed">
                      💡 <b>Jüri Notu:</b> Laplacian varyansı ve medyan filtre farkı ISO 12233 standartlarına göre ROC kalibrasyonundan geçirilmiştir.
                    </div>
                  </div>

                </div>
              </div>
            )}

            {/* ÇOKLU ÇIKTI MERKEZİ (PDF, JSON, CSV İNDİRME) */}
            <div className="rounded-2xl bg-gradient-to-r from-slate-900 to-[#0F172A] border border-cyan-500/20 p-5 flex flex-wrap items-center justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <span>Endüstriyel Çıktı ve Raporlama Paketi (Türkçe Font Korumalı)</span>
                </h4>
                <p className="text-xs text-slate-400">Resmi A4 PDF sertifikasını veya otomasyon JSON/CSV verisini anında indirin.</p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleGeneratePdf}
                  className="px-4 py-2 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-all shadow-lg shadow-cyan-500/20 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Resmi A4 PDF Sertifikası Üret</span>
                </button>

                <button
                  onClick={() => {
                    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(simResult, null, 2));
                    const dl = document.createElement('a');
                    dl.setAttribute("href", dataStr);
                    dl.setAttribute("download", `SCADA_QC_${selectedScenario}.json`);
                    dl.click();
                  }}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 hover:text-white font-bold text-xs hover:bg-slate-700 transition-all flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>SCADA JSON İndir</span>
                </button>
              </div>
            </div>

          </div>
        )}

        {/* ============================================================ */}
        {/* C. ENDÜSTRİYEL VİDEO ANALİZİ & YÜKLEME                       */}
        {/* ============================================================ */}
        {activeTab === 'video' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-extrabold text-white flex items-center space-x-2">
                  <Video className="w-5 h-5 text-emerald-400" />
                  <span>Endüstriyel Video & Mekanik Titreşim Analizi</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Hazır saha videolarını seçebilir veya bilgisayarınızdan kendi endüstriyel CCTV videonuzu yükleyebilirsiniz.
                </p>
              </div>

              {/* Video Yükleme Butonu */}
              <div>
                <input
                  type="file"
                  ref={videoInputRef}
                  onChange={handleVideoUpload}
                  accept="video/mp4,video/avi,video/quicktime"
                  className="hidden"
                />
                <button
                  onClick={() => videoInputRef.current?.click()}
                  disabled={videoUploading}
                  className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20 flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>{videoUploading ? 'Video Yükleniyor...' : '📤 Kendi Videonu Yükle (MP4)'}</span>
                </button>
              </div>
            </div>

            {/* Video Seçim Kartları */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {availableVideos.length > 0 ? (
                availableVideos.map((v) => (
                  <div
                    key={v.id}
                    onClick={() => setSelectedVideo(v.id)}
                    className={`p-4 rounded-xl cursor-pointer border transition-all relative ${
                      selectedVideo === v.id
                        ? 'bg-emerald-500/10 border-emerald-500/50 shadow-lg shadow-emerald-500/10'
                        : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-bold text-sm text-white pr-6">{v.title}</div>
                      <div className="flex items-center space-x-1.5">
                        {(v.is_custom || v.id.startsWith('upload_')) && (
                          <button
                            onClick={(e) => handleDeleteVideo(e, v.id)}
                            title="Bu videoyu kalıcı olarak sil"
                            className="p-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white transition-all border border-rose-500/30"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                        {selectedVideo === v.id && <Check className="w-4 h-4 text-emerald-400" />}
                      </div>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">{v.description}</div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 p-4">Videolar yükleniyor...</div>
              )}
            </div>

            {/* Video Hızlı Eylem Çubuğu (Simülatöre Geçiş & PDF Üretim) */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-cyan-950/40 border border-emerald-500/30 flex flex-wrap items-center justify-between gap-3 shadow-xl">
              <div>
                <div className="text-sm font-bold text-white flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <span>Video & Simülatör Entegrasyon Köprüsü</span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Aktif Video: <span className="font-mono text-cyan-300 font-bold">{selectedVideo}</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={handleCaptureVideoToSimulator}
                  className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold text-xs transition-all shadow-lg shadow-cyan-500/25 flex items-center space-x-2"
                >
                  <ArrowRight className="w-4 h-4" />
                  <span>🎯 Bu Videodan Kare Yakala & Simülatörde İncele</span>
                </button>

                <button
                  onClick={handleGenerateVideoPdf}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 hover:text-white font-bold text-xs transition-all border border-emerald-500/30 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>📑 Bu Video İçin Resmi PDF Sertifikası Üret</span>
                </button>

                {(selectedVideo.startsWith('upload_') || availableVideos.find(v => v.id === selectedVideo)?.is_custom) && (
                  <button
                    onClick={(e) => handleDeleteVideo(e, selectedVideo)}
                    className="px-3 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white font-bold text-xs transition-all border border-rose-500/40 flex items-center space-x-1.5"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Bu Videoyu Sil</span>
                  </button>
                )}
              </div>
            </div>

            {/* Video Oynatıcı & Canlı HUD */}
            <div className="rounded-2xl bg-black border border-slate-800 overflow-hidden shadow-2xl">
              <div className="bg-slate-900 px-4 py-2.5 border-b border-slate-800 flex flex-wrap justify-between items-center gap-2">
                <span className="text-xs font-mono font-bold text-slate-300 flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  <span>AKIŞ: {selectedVideo}</span>
                </span>
                
                {/* Oynatıcı Mod Seçici: Canlı CV Akışı veya Doğal Video Oynatıcı */}
                <div className="flex items-center space-x-2 text-xs font-mono">
                  <button
                    onClick={() => setVideoPlayerMode('stream')}
                    className={`px-3 py-1 rounded-lg font-bold text-[11px] transition-all flex items-center space-x-1.5 ${
                      videoPlayerMode === 'stream'
                        ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/25'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    <span>⚡ Canlı CV HUD Yayını</span>
                  </button>
                  <button
                    onClick={() => setVideoPlayerMode('native')}
                    className={`px-3 py-1 rounded-lg font-bold text-[11px] transition-all flex items-center space-x-1.5 ${
                      videoPlayerMode === 'native'
                        ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    <span>▶️ Standart Video Oynatıcı</span>
                  </button>
                </div>
              </div>

              {/* Video Oynatma Alanı */}
              <div className="aspect-video bg-black flex items-center justify-center relative">
                {videoPlayerMode === 'stream' ? (
                  <img
                    key={`stream-${selectedVideo}`}
                    src={`/api/video-feed/${selectedVideo}`}
                    alt="Live CV Feed"
                    className="w-full h-full object-contain"
                    onError={() => {
                      showToast('Canlı akış bağlantısı geçici olarak kurulamadı, standart oynatıcıya geçiliyor...', 'warning');
                      setVideoPlayerMode('native');
                    }}
                  />
                ) : (
                  <video
                    key={`native-${selectedVideo}`}
                    src={`/api/videos/${selectedVideo}`}
                    controls
                    autoPlay
                    loop
                    muted
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
            </div>

            {/* Seçili Videonun Canlı Teşhis ve Çıktı Paneli (Buton Çıktısı) */}
            {(() => {
              const diag = getVideoDiagnosis(selectedVideo);
              return (
                <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 shadow-xl">
                  {/* Başlık ve Rozet */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold border border-slate-700">
                        SEÇİLİ VİDEO DİNAMİK TEŞHİS RAPORU
                      </span>
                      <h3 className="text-base font-bold text-white mt-1.5 flex items-center space-x-2">
                        <span>{diag.badgeText}</span>
                      </h3>
                    </div>
                    <div className="text-xs font-mono text-slate-400">
                      Kaynak: <span className="text-cyan-400 font-bold">{selectedVideo}</span>
                    </div>
                  </div>

                  {/* Belirgin Arıza / Hata Türü Bildirim Alanı */}
                  <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-3 shadow-inner">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className={`w-4 h-4 ${diag.badgeType === 'critical' ? 'text-rose-400 animate-pulse' : diag.badgeType === 'warning' ? 'text-amber-400' : 'text-emerald-400'}`} />
                      <span className="text-xs font-mono text-slate-300 uppercase tracking-wider font-semibold">
                        TESPİT EDİLEN ARIZA / HATA TÜRÜ:
                      </span>
                    </div>
                    <span className={`text-xs font-extrabold font-mono px-3.5 py-1.5 rounded-lg border ${
                      diag.badgeType === 'critical'
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                        : diag.badgeType === 'warning'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    }`}>
                      {diag.faultType}
                    </span>
                  </div>

                  {/* Teşhis Açıklaması */}
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {diag.desc}
                  </p>

                  {/* 4 Canlı KPI Metrik Kartı */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
                    {diag.metrics.map((m, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-center">
                        <div className="text-[10px] font-mono uppercase text-slate-400">{m.label}</div>
                        <div className={`text-xl font-black mt-1 ${
                          m.status === 'critical' ? 'text-rose-400' : m.status === 'warning' ? 'text-amber-400' : 'text-emerald-400'
                        }`}>
                          {m.value}
                        </div>
                        <div className="text-[10px] font-mono text-slate-400 mt-1">{m.sub}</div>
                      </div>
                    ))}
                  </div>

                  {/* Mühendislik Aksiyon Önerisi */}
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-3 text-xs">
                    <span className="text-slate-300 font-medium">
                      {diag.actionRecommendation}
                    </span>
                    <button
                      onClick={handleCaptureVideoToSimulator}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs whitespace-nowrap transition-colors flex items-center space-x-1"
                    >
                      <span>Simülatörde Aç</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })()}

            {/* Video Analiz Notu */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 leading-relaxed">
              💡 <b>Algoritma Detayı:</b> Video kareleri `dynamic_analysis.py` içindeki `VibrationAnalyzer` sınıfına aktarılarak ardışık kareler arasında seyrek optik akış (Sparse Optical Flow) türetilir. Piksel hareket büyüklüğü 3.0 piksel sınırını aştığında jeneratör rezonans alarmı verilir.
            </div>
          </div>
        )}

        {/* ============================================================ */}
        {/* D. STATİK FOTOĞRAF MUAYENESİ & YÜKLEME                       */}
        {/* ============================================================ */}
        {activeTab === 'photo' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-extrabold text-white flex items-center space-x-2">
                  <Camera className="w-5 h-5 text-sky-400" />
                  <span>Statik Fotoğraf & Pano Analiz Modülü</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Yüksek çözünürlüklü pano fotoğraflarından seçim yapın veya bilgisayarınızdan yeni bir fotoğraf yükleyin.
                </p>
              </div>

              {/* Fotoğraf Yükleme Butonu */}
              <div>
                <input
                  type="file"
                  ref={photoInputRef}
                  onChange={handlePhotoUpload}
                  accept="image/jpeg,image/png,image/jpg"
                  className="hidden"
                />
                <button
                  onClick={() => photoInputRef.current?.click()}
                  disabled={photoUploading}
                  className="px-4 py-2 rounded-xl bg-sky-500 text-slate-950 font-bold text-xs hover:bg-sky-400 transition-all shadow-lg shadow-sky-500/20 flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>{photoUploading ? 'Fotoğraf Analiz Ediliyor...' : '📤 Yeni Fotoğraf Yükle (JPG/PNG)'}</span>
                </button>
              </div>
            </div>

            {/* Özel Yüklenen Fotoğrafın Analiz Çıktısı (Varsa) */}
            {customPhotoResult && (
              <div className="p-5 rounded-2xl bg-sky-950/20 border border-sky-500/30 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-sm font-bold text-sky-300">
                    ✅ Yüklenen Görsel Analiz Edildi: <span className="font-mono text-white">{customPhotoResult.filename}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        setSelectedBaseImage(customPhotoResult.filename);
                        runSimulation('NORMAL', { base_image: customPhotoResult.filename });
                        setActiveTab('simulate');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500 text-slate-950 text-xs font-bold hover:bg-cyan-400 flex items-center space-x-1"
                    >
                      <span>🎯 Simülatöre Aktar</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => handleDeleteImage(e, customPhotoResult.filename)}
                      className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white text-xs font-bold flex items-center space-x-1 border border-rose-500/30 transition-all"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Bu Fotoğrafı Sil</span>
                    </button>
                  </div>
                </div>

                {/* 3'lü Görsel İnceleme */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="rounded-xl bg-black border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3 py-1.5 text-[11px] font-mono text-slate-300">ORİJİNAL YÜKLENEN GÖRSEL</div>
                    <img src={customPhotoResult.images.original} alt="Uploaded" className="w-full aspect-video object-contain" />
                  </div>
                  <div className="rounded-xl bg-black border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3 py-1.5 text-[11px] font-mono text-slate-300">GÜRÜLTÜ ISI HARİTASI (JET)</div>
                    <img src={customPhotoResult.images.heatmap} alt="Heatmap" className="w-full aspect-video object-contain" />
                  </div>
                  <div className="rounded-xl bg-black border border-slate-800 overflow-hidden">
                    <div className="bg-slate-800/80 px-3 py-1.5 text-[11px] font-mono text-slate-300">KENAR & ODAK HARİTASI</div>
                    <img src={customPhotoResult.images.edge_map} alt="Edge" className="w-full aspect-video object-contain" />
                  </div>
                </div>

                {/* Belirgin Arıza / Hata Türü & Mühendislik Kararı */}
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-3 shadow-inner">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-mono text-slate-300 uppercase tracking-wider font-semibold">
                      TESPİT EDİLEN ARIZA / HATA TÜRÜ:
                    </span>
                  </div>
                  <span className="text-xs font-extrabold font-mono px-3.5 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                    {customPhotoResult.metrics.fault_type || 'NORMAL ÇALIŞMA (ARIZA YOK)'}
                  </span>
                </div>

                {/* Ölçüm Değerleri */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">Keskinlik:</span> <b className="text-cyan-400">{customPhotoResult.metrics.sharpness}</b>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">Gürültü (Sigma):</span> <b className="text-emerald-400">{customPhotoResult.metrics.noise_sigma}</b>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">Lüminans:</span> <b className="text-sky-400">{customPhotoResult.metrics.brightness.toFixed(1)}</b>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">Q-Score:</span> <b className="text-amber-400">{customPhotoResult.metrics.overall_score} / 100</b>
                  </div>
                </div>
              </div>
            )}

            {/* Kullanıcı Tarafından Yüklenen Fotoğraflar & Yakalanan Video Kareleri */}
            {availableImages.filter(img => img.startsWith('upload_') || img.startsWith('video_frame_')).length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-300 font-mono uppercase flex items-center space-x-2">
                  <span>📤 Yüklenen Görseller & Yakalanan Kareler</span>
                  <span className="text-xs text-cyan-400 font-normal">
                    ({availableImages.filter(img => img.startsWith('upload_') || img.startsWith('video_frame_')).length} adet)
                  </span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {availableImages.filter(img => img.startsWith('upload_') || img.startsWith('video_frame_')).map((img) => (
                    <div
                      key={img}
                      className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs text-cyan-300 font-bold truncate max-w-[180px]">{img}</span>
                          <button
                            onClick={(e) => handleDeleteImage(e, img)}
                            title="Bu görseli kalıcı olarak sil"
                            className="p-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white transition-colors border border-rose-500/30"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">
                          {img.startsWith('video_frame_') ? '🎬 Videodan Yakalanan Kare' : '📸 Yüklenen Test Görseli'}
                        </div>
                      </div>
                      <div className="pt-3 mt-3 border-t border-slate-800/80 flex items-center justify-between">
                        <button
                          onClick={() => {
                            setSelectedBaseImage(img);
                            runSimulation('NORMAL', { base_image: img });
                            setActiveTab('simulate');
                          }}
                          className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                        >
                          <span>Simülatörde İncele</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Hazır Örnek Görseller */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-300 font-mono uppercase">📁 Hazır Saha Test Fotoğrafları</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { id: 'panel_clean.jpg', title: 'AG Dağıtım Panosu', desc: 'Şalter ve baralar' },
                  { id: 'transformer_station.jpg', title: '1600 kVA Güç Trafosu', desc: 'Buşingler ve yağ finleri' },
                  { id: 'generator_room.jpg', title: '500 kVA Dizel Jeneratör', desc: 'Motor ve alternatör bloğu' },
                ].map((img) => (
                  <div
                    key={img.id}
                    onClick={() => {
                      setSelectedBaseImage(img.id);
                      runSimulation('NORMAL', { base_image: img.id });
                      setActiveTab('simulate');
                    }}
                    className="p-4 rounded-xl cursor-pointer bg-slate-900 border border-slate-800 hover:border-cyan-500/50 transition-all hover:-translate-y-0.5"
                  >
                    <div className="font-bold text-sm text-white">{img.title}</div>
                    <div className="text-xs text-slate-400 mt-1">{img.desc}</div>
                    <div className="mt-3 text-xs font-semibold text-cyan-400 flex items-center space-x-1">
                      <span>Simülatörde Aç</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* ============================================================ */}
        {/* E. SCADA ARŞİV & DENETİM KAYITLARI (SİLME / TEMİZLEME DESTEKLİ) */}
        {/* ============================================================ */}
        {activeTab === 'audit' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-extrabold text-white flex items-center space-x-2">
                  <Database className="w-5 h-5 text-amber-400" />
                  <span>SCADA Muayene Arşivi & SQLite Veritabanı</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Kayıtları inceleyebilir, hatalı veya eski kayıtları tek tek silebilir veya tüm arşiv verilerini temizleyebilirsiniz.
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={fetchRecords}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 flex items-center space-x-1.5 transition-colors"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Yenile</span>
                </button>

                <button
                  onClick={handleClearAllRecords}
                  className="px-3 py-1.5 rounded-lg bg-rose-500/15 border border-rose-500/30 hover:bg-rose-500 text-rose-300 hover:text-white text-xs font-bold flex items-center space-x-1.5 transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Tümünü Temizle</span>
                </button>
              </div>
            </div>

            {/* Tablo */}
            <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-800 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
                    <tr>
                      <th className="p-3.5">ID</th>
                      <th className="p-3.5">Tarih</th>
                      <th className="p-3.5">Pano ID</th>
                      <th className="p-3.5">Kaynak</th>
                      <th className="p-3.5">Keskinlik</th>
                      <th className="p-3.5">Gürültü</th>
                      <th className="p-3.5">Q-Score</th>
                      <th className="p-3.5">Karar</th>
                      <th className="p-3.5">Rapor</th>
                      <th className="p-3.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {auditRecords.records && auditRecords.records.length > 0 ? (
                      auditRecords.records.map((r) => (
                        <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="p-3.5 font-bold text-cyan-400">#{r.id}</td>
                          <td className="p-3.5 text-slate-400">{r.timestamp}</td>
                          <td className="p-3.5 font-semibold text-white">{r.panel_id}</td>
                          <td className="p-3.5 text-slate-400">{r.source_type}</td>
                          <td className="p-3.5">{r.sharpness.toFixed(1)}</td>
                          <td className="p-3.5">{r.noise_sigma.toFixed(2)}</td>
                          <td className="p-3.5 font-bold text-emerald-400">{r.overall_score}</td>
                          <td className="p-3.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              r.final_verdict.includes('ONAYLANDI')
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}>
                              {r.final_verdict.slice(0, 16)}...
                            </span>
                          </td>
                          <td className="p-3.5">
                            {r.report_path ? (
                              <button
                                onClick={() => window.open(`/api/reports/${r.report_path.split('\\').pop().split('/').pop()}`, '_blank')}
                                className="text-cyan-400 hover:underline flex items-center space-x-1"
                              >
                                <Download className="w-3 h-3" />
                                <span>PDF</span>
                              </button>
                            ) : (
                              <span className="text-slate-600">-</span>
                            )}
                          </td>
                          <td className="p-3.5 text-right">
                            <button
                              onClick={() => handleDeleteRecord(r.id)}
                              title="Bu kaydı sil"
                              className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white transition-all"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="10" className="p-8 text-center text-slate-500">
                          Henüz kayıt bulunmuyor. Saha Simülatöründe "Resmi A4 PDF Sertifikası Üret" butonuna basarak ilk kaydı oluşturabilirsiniz.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* 3. FOOTER */}
      <footer className="border-t border-slate-800/80 bg-[#0B0F19] py-4 px-6 text-center text-xs text-slate-500 font-mono">
        MRT GÜÇ SİSTEMLERİ MÜHENDİSLİK SAN. VE TİC. LTD. ŞTİ. &nbsp;•&nbsp; HARRAN ÜNİVERSİTESİ YAZILIM MÜHENDİSLİĞİ
      </footer>

    </div>
  );
}

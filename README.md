# ⚽ ScoutEduard - Football Scouting Decision Support System (scout_dss)

[![Project Status](https://img.shields.io/badge/Status-Prototype%20%2F%20PoC%20(WIP)-orange?style=flat-square)](https://github.com/Umutcagn/scout-dss-football-analytics)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=flat-square)](https://streamlit.io/)
[![Methodology](https://img.shields.io/badge/Method-TOPSIS%20%7C%20Cosine%20Similarity-green?style=flat-square)](https://en.wikipedia.org/wiki/TOPSIS)

> [!NOTE]
> **Project Scope & Status:**  
> This project was developed as an exploratory **decision-support prototype (PoC / WIP)** to model multi-criteria decision making (**TOPSIS**) and vector similarity algorithms (**Cosine Similarity**) applied to sports performance analytics. It is presented as a demonstration of analytical modeling, ETL pipelines, and data-driven decision tools.


---

## 🌟 Temel Amaç ve İş Modeli

1. **Mühendislik & Analitik Yaklaşım**:
   - **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**: Oyuncuları ideal pozitif ve negatif çözümlere olan uzaklıklarına göre 0-100 puan skalasında sıralar.
   - **Cosine Similarity (Vektör Benzerliği)**: Referans bir hedef oyuncunun metrik vektörünü alarak, yaş ve bütçe kısıtlamalarına tam uyan en benzer 3 muadil oyuncuyu anında tespit eder.

2. **Sıfır Maliyet & Kesintisiz Çalışma**:
   - Canlı API maliyetleri, abonelikler ve rate-limit engellerine takılmamak için **tamamen yerel veri mimarisi** (Kaggle/StatsBomb açık veri şemalarına uygun CSV/SQLite ETL yapısı) ile çalışır.

3. **İçerik ve Portföy Çıktısı (Twitter / Raporlama)**:
   - Koyu tema (**Dark-Mode**), yüksek çözünürlüklü **Radar Grafikleri** ve **Oyuncu İstatistik Kartları** (PNG formatında tek tıkla indirme desteği).

---

## 📁 Proje Dizin Yapısı

```
scout_dss/
├── data/
│   ├── raw/                 # Ham sentetik veri seti (players.csv)
│   └── processed/           # Position-percentile (0-100) normalize edilmiş veriler
├── src/
│   ├── __init__.py
│   ├── data_generator.py    # En az 150 oyuncu, 5 ana mevki ve per-90 metrikleri üreteci
│   ├── normalizer.py        # Mevki bazlı Percentile (0-100) ve Z-Score normalizasyon motoru
│   ├── dss_engine.py        # TOPSIS Ağırlıklı Skorlama & Cosine Similarity benzerlik modülü
│   └── visualizer.py        # Dark-mode Radar Grafiği ve Oyuncu Kartı export modülü
├── app.py                   # Streamlit kullanıcı kontrol paneli
├── requirements.txt         # Proje bağımlılıkları
└── README.md                # Proje dokümantasyonu
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Bağımlılıkların Yüklenmesi
```bash
pip install -r requirements.txt
```

### 2. Veri Setinin Üretilmesi ve Normalize Edilmesi (Opsiyonel CLI)
Proje ilk açılışta verileri otomatik üretir, ancak manuel çalıştırmak isterseniz:
```bash
# Sentetik Veri Üretimi
python -m src.data_generator

# Percentile Normalizasyonu
python -m src.normalizer
```

### 3. Streamlit Kontrol Panelinin Başlatılması
```bash
streamlit run app.py
```

---

## 🧮 Matematiksel Model ve Algoritmalar

### 1. TOPSIS Uygunluk Skoru Formülü
Ağırlıklandırılmış karar matrisinde $V = [v_{ij}]$, ideal pozitif çözüm $A^+$ ve ideal negatif çözüm $A^-$ için göreli yakınlık skoru:
$$ C_i = \frac{S_i^-}{S_i^+ + S_i^-} \times 100 $$

### 2. Cosine Similarity Benzerlik Formülü
Hedef oyuncu vektörü $A$ ve aday oyuncu vektörü $B$ arasındaki açısal benzerlik:
$$ \text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} $$

---

## 🖼️ Ekran Görüntüleri ve Görseller
- **🏆 TOPSIS Leaderboard**: Filtrelenebilir ve mevki bazlı skor sıralaması.
- **🎯 Muadil Bulucu**: Hedef oyuncuya en yakın bütçe dostu 3 alternatif.
- **📥 Dark-Mode Radar & Kart Export**: PNG formatında yüksek çözünürlüklü grafik indirme.

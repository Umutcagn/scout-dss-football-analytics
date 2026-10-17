# ⚽ ScoutEduard - Football Scouting Decision Support System (scout_dss)

[![Project Status](https://img.shields.io/badge/Status-Prototype%20%2F%20PoC%20(WIP)-orange?style=flat-square)](https://github.com/Umutcagn/scout-dss-football-analytics)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=flat-square)](https://streamlit.io/)
[![Methodology](https://img.shields.io/badge/Method-TOPSIS%20%7C%20Cosine%20Similarity-green?style=flat-square)](https://en.wikipedia.org/wiki/TOPSIS)
[![Tests](https://github.com/Umutcagn/scout-dss-football-analytics/actions/workflows/tests.yml/badge.svg)](https://github.com/Umutcagn/scout-dss-football-analytics/actions/workflows/tests.yml)

> [!NOTE]
> **Project Scope & Status:**  
> This project was developed as an exploratory **decision-support prototype (PoC / WIP)** to model multi-criteria decision making (**TOPSIS**) and vector similarity algorithms (**Cosine Similarity**) applied to sports performance analytics. It is presented as a demonstration of analytical modeling, ETL pipelines, and data-driven decision tools.


---

## 🌟 Temel Amaç ve İş Modeli

1. **Mühendislik & Analitik Yaklaşım**:
   - **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**: Oyuncuları ideal pozitif ve negatif çözümlere olan uzaklıklarına göre 0-100 puan skalasında sıralar.
   - **Cosine Similarity (Vektör Benzerliği)**: Referans bir hedef oyuncunun metrik vektörünü alarak, yaş ve bütçe kısıtlamalarına tam uyan en benzer 3 muadil oyuncuyu anında tespit eder.

2. **Veri**: Top 5 lig oyuncuları için Understat 2025/26 sezon verisi, bir kısmı simüle edilmiş metriklerle tamamlanmış (bkz. [Veri Kaynağı](#-veri-kaynağı)).

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
│   ├── real_data_pipeline.py # Understat verisi + simüle metriklerle veri seti üretimi
│   ├── data_generator.py    # Tamamen sentetik veri üreteci (alternatif)
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
$$ \text{Similarity}(A, B) = \frac{(A-50) \cdot (B-50)}{\|A-50\| \|B-50\|} $$

Yüzdelikler önce medyana (50) göre ortalanır. Ham, hepsi pozitif yüzdelik vektörlerinde rastgele iki oyuncunun benzerliği bile ~0.87 çıkar ve oyuncuların %60–80'inin en iyi eşleşmesi ≥ 0.95 olur. Ortalama sonrasında medyan benzerlik ~0.44'e iner ve sonuç gerçekten ortalamanın üstünde/altında olunan alanların benzerliğini ölçer.

---

## 🖼️ Ekran Görüntüleri ve Görseller
- **🏆 TOPSIS Leaderboard**: Filtrelenebilir ve mevki bazlı skor sıralaması.
- **🎯 Muadil Bulucu**: Hedef oyuncuya en yakın bütçe dostu 3 alternatif.
- **📥 Dark-Mode Radar & Kart Export**: PNG formatında yüksek çözünürlüklü grafik indirme.

---

## 📊 Veri Kaynağı

Uygulamanın kullandığı veri seti (`data/raw/players.csv`, `src/real_data_pipeline.py` ile üretilir) **gerçek ve simüle edilmiş değerlerin karışımıdır**:

| Grup | Metrikler | Kaynak |
|---|---|---|
| Gerçek | xG/90, xA/90, kilit pas/90, şut başı xG, xG buildup/90, oynanan dakika, takım, lig | Understat 2025/26 (`soccerdata`) |
| Simüle | çalım, baskı, progresif pas, ikili mücadele, pas arası, top çalma, pas/şut isabeti, xT, Pack Rate, PADJ, ön alan top kazanımı, PPDA, PSxG | Mevkiye göre `np.random.uniform` |
| Mevki sabiti | Sofascore tarzı hücum/yaratıcılık/teknik/defans/taktik puanları | Mevki başına sabit değer |
| Kısmen tahmini | Yaş, piyasa değeri, mevki eşlemesi | Bir kısmı elle doğrulanmış, kalanı kural/rastgele tabanlı |

Bu nedenle uygulamadaki sıralamalar **yöntemi (TOPSIS, benzerlik) göstermek içindir**; gerçek scouting kararı için kullanılmamalıdır. Uygulama bunu üst kısımda uyarı olarak gösterir ve simüle metrikleri grafiklerde `(simüle)` / `(mevki sabiti)` olarak etiketler. "Veri Tutarlılık Kontrolü" butonu ~25 oyunculuk elle tutulan bir listeye ve basit sınır kurallarına dayanır; harici bir servise bağlanmaz.

---

## 🧪 Testler

```bash
pip install pandas numpy scipy scikit-learn pytest
python -m pytest tests -q
```

TOPSIS elle hesaplanmış bir örneğe ve bağımsız bir referans uygulamaya karşı, ağırlık duyarlılığı, ağırlıklı skor, benzerlik filtreleri (bütçe, yaş, mevki), mevki içi yüzdelik normalizasyonu ve metrik kaynak gruplarının tutarlılığı test edilir. Testler her push'ta GitHub Actions ile çalışır.

# 🎓 Skripsi & SOTA Academic Research Intelligence Toolkit

Toolkit terpadu untuk scraping repositori skripsi lokal (GitLab STIS & Executive Summary PDF), ekstraksi minat penelitian dosen resmi, penggabungan dataset paper SOTA internasional (ArXiv CS/SE/AI), serta sistem rekomendasi topik skripsi **Software Engineering (SE) & Data Engineering**.

---

## 📌 Alur Pipeline Data & Arsitektur

```
[ Git STIS / PDF Exec Summary ]    [ Web Profil Dosen STIS ]     [ ArXiv SOTA CS/SE Papers ]
              │                               │                               │
       (Scraping PDF/Git)           (Scraping Minat Dosen)          (Academic Papers Ingestion)
              ▼                               ▼                               ▼
 [hasil_executive_summary_dosen.csv]  [minat_dosen.csv]      [academic-papers-dataset]
              │                               │                               │
              └───────────────────────┬───────┴───────────────────────────────┘
                                      ▼
                        [ orchestrate_dataset.py ]
                                      ▼
                  [ dataset_unified_skripsi_dan_papers.csv ]
                                      ▼
                           [ plan_se_topics.py ]
                                      ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  1. rekomendasi_topik_skripsi_se.md (Blueprint & Matriks)   │
        │  2. rekomendasi_dosen_pembimbing.csv (Skor Kecocokan Dosen) │
        └─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Setup & Instalasi Lingkungan

### 1. Prasyarat Sistem
- **Python 3.10+** (Direkomendasikan Python 3.11 / 3.12 / 3.14)
- **Google Chrome** (Telah disediakan `chromedriver.exe` di root folder)

### 2. Instalasi Dependensi
Jalankan perintah berikut di terminal:
```bash
# 1. (Opsional) Buat dan aktifkan Virtual Environment
python -m venv venv
# Di Windows:
venv\Scripts\activate
# Di Linux/MacOS:
source venv/bin/activate

# 2. Install library yang dibutuhkan
pip install -r requirements.txt

# 3. Install browser engine untuk Playwright (jika menggunakan scraper GitLab)
playwright install chromium
```

---

## 🛠️ Panduan Menjalankan Script (Step-by-Step)

### Tahap 1: Scraping Data Minat Dosen Resmi STIS
Script ini mengambil profil seluruh dosen STIS dari 3 program studi (D-IV Komputasi Statistik, D-IV Statistika, dan D-III Statistika) beserta tag minat penelitiannya.

```bash
# Scrape seluruh dosen dari semua prodi (KS, S, D3) -> default: minat_dosen.csv
python scrape_minat_dosen.py --prodi all

# Atau scrape prodi tertentu saja:
python scrape_minat_dosen.py --prodi ks --output minat_dosen_ks.csv
```

---

### Tahap 2: Ekstraksi Data Bimbingan dari PDF Executive Summary
Mengekstrak judul skripsi, nama mahasiswa, dan dosen pembimbing dari dokumen PDF Executive Summary:

```bash
# Ekstraksi judul dan daftar isi PDF
python crawl_pdf_titles.py

# Ekstraksi pemetaan dosen pembimbing dan judul skripsi
python crawl_pdf_dosen.py
```
*Output:* `hasil_executive_summary_dosen.csv` dan `hasil_executive_summary_titles.csv`.

---

### Tahap 3: Scraping Skripsi dari GitLab STIS (Opsional / Pelengkap)
Untuk mengunduh metadata dan deskripsi README dari repositori GitLab:

```bash
python scrape_skripsi.py --group ks/skripsi2021 --out hasil_2021.json
```

---

### Tahap 4: Orkestrasi Dataset Terpadu (Lokal + Global)
Menggabungkan seluruh skripsi lokal terdahulu dengan ribuan paper riset SOTA internasional dari ArXiv (Domain: *Software Engineering, Distributed Systems, Cryptography/Security, Database/ETL, AI/ML*):

```bash
python orchestrate_dataset.py
```
*Output:* `dataset_unified_skripsi_dan_papers.csv` dan `dataset_unified_skripsi_dan_papers.json`.

---

### Tahap 5: Menghasilkan Rekomendasi Topik & Dosen Pembimbing
Script inti yang menganalisis kecocokan kepakaran **72 Dosen STIS** dengan **6 Pilar Utama Rekayasa Perangkat Lunak & Data Engineering**:

```bash
python plan_se_topics.py
```

*Output yang Dihasilkan:*
1. **[rekomendasi_topik_skripsi_se.md](rekomendasi_topik_skripsi_se.md)**:
   - Blueprint strategi skripsi SE dengan subsistem Data Science/AI.
   - Formula rancang bangun & evaluasi metrik rekayasa (*latency, throughput, fault tolerance*).
   - Rujukan paper ArXiv SOTA 2025/2026.
   - Rekomendasi dosen pembimbing per pilar lengkap dengan bukti rekam jejak bimbingan.
2. **[rekomendasi_dosen_pembimbing.csv](rekomendasi_dosen_pembimbing.csv)**:
   - Tabel matriks kecocokan skor tiap dosen pada setiap domain sistem.

---

## 🏛️ 6 Pilar Rekayasa Perangkat Lunak & Data Engineering

| No | Pilar Rekayasa (Fokus Anda) | Subsistem Data / Kasus Nyata | Rekomendasi Dosen Pembimbing |
| :-: | :--- | :--- | :--- |
| **1** | **Data Engineering & Lineage (ETL)** | Geospatial Data Fusion, Remote Sensing, Web Scraping | Dr. Eng. Arie Wahyu Wijayanto, Prof. Setia Pramana, Dr. Drs. Waris Marsisno, Lutfi Rahmatuti Maghfiroh |
| **2** | **MLOps & Automated Serving Pipeline**| Zero-Shot Segment Any Change, Time-Series Forecasting | Dr. Eng. Arie Wahyu Wijayanto, Erna Nurmawati, S.S.T., M.T., Rani Nooraeni, Dr. Robert Kurniawan |
| **3** | **Package Engineering & Reusable Modules** | Small Area Estimation (SAE), PyMC Neo-Normal Distribution | Dr. Achmad Syahrul Choir, Dr. Azka Ubaidillah, Dr. Cucu Sumarni |
| **4** | **Compiler, Tooling & AST Engineering** | Dynamic Questionnaire Layout, Code Generator, AST Parser | Ibnu Santoso, S.S.T., M.T. |
| **5** | **Software Quality & Testing Testbed** | Automated Diagnostic, Trajectory Benchmark, QFD | Yunarso Anang, Ph.D. |
| **6** | **Distributed Microservices & Security** | OpenAPI Backend, Strangler Fig Migration, SIEM Wazuh | Farid Ridho, S.S.T., M.T., Nori Wilantika, S.S.T., M.T.I., Firdaus, MBA |

---

## 📁 Struktur Repositori

```
.
├── .gitignore                              # Konfigurasi ignore file dataset besar & temporary
├── requirements.txt                        # Daftar dependensi library Python
├── chromedriver.exe                        # Binary Chrome WebDriver untuk automasi browser
├── THIRD_PARTY_NOTICES.chromedriver        # Lisensi pihak ketiga ChromeDriver
│
├── scrape_minat_dosen.py                   # Scraper profil & minat penelitian dosen (KS, S, D3)
├── crawl_pdf_titles.py                     # Parser daftar isi PDF Executive Summary
├── crawl_pdf_dosen.py                      # Parser dosen pembimbing & judul dari PDF
├── scrape_skripsi.py                       # Scraper GitLab STIS berbasis Playwright
├── preprocess_skripsi.py                   # Preprocessing & standardisasi skripsi lokal
├── preprocess_academic_papers.py           # Ingestion & filter paper ArXiv internasional
├── orchestrate_dataset.py                  # Integrasi dataset lokal + internasional
├── plan_se_topics.py                       # Engine rekomendasi topik SE + scoring kecocokan dosen
│
├── minat_dosen.csv                         # Data hasil scraping minat penelitian dosen
├── hasil_executive_summary_dosen.csv       # Data riwayat bimbingan skripsi dosen
├── rekomendasi_topik_skripsi_se.md         # Laporan blueprint rekomendasi topik & dosen
└── rekomendasi_dosen_pembimbing.csv        # Tabel skor kecocokan dosen per domain
```

---

## 💡 Tips Strategis Saat Pengajuan Proposal

- **Posisikan Diri sebagai System / Data Engineer:** Tegaskan kepada dosen pembimbing bahwa fokus penelitian Anda adalah **arsitektur software, throughput pipeline, data lineage, latensi sistem, atau reusabilitas package**, bukan sekadar melatih model prediksi.
- **Bawa Rancangan Arsitektur:** Lampirkan diagram sistem (*C4 Model, Sequence Diagram, atau Data Pipeline Flowchart*) saat bimbingan awal.
- **Gunakan Bukti SOTA:** Kutip referensi paper ArXiv 2025/2026 yang sudah terangkum di `rekomendasi_topik_skripsi_se.md` sebagai dasar urgensi dan orisinalitas riset.
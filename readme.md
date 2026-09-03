# 🎓 Skripsi & SOTA Academic Research Intelligence Toolkit

Toolkit terpadu untuk scraping repositori skripsi lokal (GitLab STIS & PDF Executive Summary), ekstraksi minat penelitian dosen resmi dari 3 prodi, penggabungan dataset paper SOTA internasional (ArXiv CS/SE/AI), serta sistem rekomendasi topik skripsi dengan **skema klasifikasi dua label utama: Data Science & Software Engineering**.

---

## 🏷️ Arsitektur Klasifikasi Label Topik

Dataset menggunakan dua **label utama** dengan sistem sub-label hierarkis:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Label Utama 1 ─ DATA SCIENCE                                           │
│  (Topik analitik, pemodelan, dan kecerdasan buatan)                     │
│                                                                         │
│    ├── Machine Learning & Predictive Modeling                           │
│    ├── NLP, LLM & Text Mining                                           │
│    ├── Computer Vision & Remote Sensing                                 │
│    ├── Time Series & Forecasting                                        │
│    ├── Spatial & Spatio-Temporal Analysis                               │
│    └── Small Area Estimation (SAE)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Label Utama 2 ─ SOFTWARE ENGINEERING                                   │
│  (Semua topik rekayasa sistem, termasuk System Information,             │
│   Computer Science generik, dan semua varian pengembangan software)     │
│                                                                         │
│    ├── Backend, Microservices & Web API                                 │
│    ├── Frontend & Modern Web Architecture                               │
│    ├── Mobile Application & CAPI Systems                                │
│    ├── Enterprise Systems & Gov-Tech  ← System Information masuk sini  │
│    ├── Data Engineering, ETL & Big Data Storage                         │
│    ├── Web Scraping & Data Ingestion Engine                             │
│    ├── Automation, Pipeline & Orchestration                             │
│    ├── UI/UX, UCD & Usability Engineering                               │
│    ├── Statistical Software & Package Engineering                       │
│    ├── Software Security & Defensive Engineering                        │
│    ├── Software Testing & Automated QA                                  │
│    └── Developer Tooling & Static Analysis                              │
└─────────────────────────────────────────────────────────────────────────┘
```

> **Catatan:** Skripsi yang bersifat **lintas topik** (misal: MLOps, Data Pipeline AI) akan mendapatkan **multi-label** — yaitu `"Data Science; Software Engineering"` — secara otomatis.

---

## 📊 Kolom Label di Dataset Output

| Kolom | Tipe | Contoh Nilai |
| :--- | :--- | :--- |
| `main_label` | `str` | `"Data Science"` / `"Software Engineering"` / `"Data Science; Software Engineering"` |
| `sub_labels` | `str` | `"Machine Learning & Predictive Modeling; Backend, Microservices & Web API"` |
| `se_automation_tags` | `str` | Sub-label Software Engineering yang match (backward-compat) |
| `ai_analytics_tags` | `str` | Sub-label Data Science yang match (backward-compat) |
| `application_sector_tags` | `str` | Sektor aplikasi (BPS, Kemiskinan, Ekonomi, dll.) |

---

## 📌 Alur Pipeline Data & Arsitektur

```
[ Git STIS / PDF Exec Summary ]    [ Web Profil Dosen STIS ]     [ ArXiv SOTA Papers ]
              │                               │                         │
       (scrape_skripsi.py /          (scrape_minat_dosen.py)    (academic-papers-dataset/
       crawl_pdf_dosen.py)                   │                    create_dataset.py)
              ▼                              ▼                         ▼
 [hasil_executive_summary_dosen.csv]  [minat_dosen.csv]     [data/academic_papers.csv]
              │                               │                         │
              └───────────────────────┬───────┴─────────────────────────┘
                                      ▼
                     [ preprocess_skripsi.py ] + [ preprocess_academic_papers.py ]
                          │ assign_main_label() → main_label + sub_labels
                                      ▼
                           [ orchestrate_dataset.py ]
                                      ▼
                 [ dataset_unified_skripsi_dan_papers.csv ]
                          main_label | sub_labels | discipline | ...
                                      ▼
                           [ plan_se_topics.py ]
                                      ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  1. rekomendasi_topik_skripsi_se.md (Blueprint & Matriks)   │
        │  2. rekomendasi_dosen_pembimbing.csv (Skor Kecocokan Dosen) │
        └─────────────────────────────────────────────────────────────┘
```

---

## 📁 Struktur Repositori Lengkap

```
.
├── .gitignore                              # File/folder besar diabaikan (data, PDF, JSON)
├── requirements.txt                        # Dependensi Python (Playwright, BeautifulSoup, Requests)
├── chromedriver.exe                        # Chrome WebDriver binary untuk scraping GitLab
├── THIRD_PARTY_NOTICES.chromedriver        # Lisensi pihak ketiga ChromeDriver
├── readme.md                              # Dokumen panduan ini
│
│── ─────── DATA INGESTION ──────────────────────────────────────────
│
├── scrape_skripsi.py                       # Scraper repositori skripsi GitLab STIS (Playwright)
├── crawl_pdf_titles.py                     # Parser daftar isi dari PDF Executive Summary
├── crawl_pdf_dosen.py                      # Ekstraksi pasangan dosen pembimbing & judul dari PDF
├── scrape_minat_dosen.py                   # Scraper profil & minat penelitian dosen (KS, S, D3)
│
│── ─────── DATA PREPROCESSING & LABELING ───────────────────────────
│
├── preprocess_skripsi.py                   # Standardisasi, tagging & assign main_label + sub_labels
│                                           #   └ TAXONOMY_DATA_SCIENCE  → label "Data Science"
│                                           #   └ TAXONOMY_SOFTWARE_ENGINEERING → label "Software Engineering"
│                                           #   └ assign_main_label() → logika multi-label otomatis
├── preprocess_academic_papers.py           # Ingestion, filter & tagging paper ArXiv internasional
├── fill_empty_description.py               # Pengisian deskripsi kosong menggunakan fallback
├── orchestrate_dataset.py                  # Penggabungan seluruh sumber dataset menjadi satu CSV
│                                           #   └ Membaca main_label dari preprocess_skripsi
│                                           #   └ Kolom baru: main_label, sub_labels
│
│── ─────── RECOMMENDATION ENGINE ───────────────────────────────────
│
├── plan_se_topics.py                       # Engine utama: pemetaan 72 dosen × 6 pilar rekayasa
│
│── ─────── SUBFOLDER: PAPER FETCHER ────────────────────────────────
│
└── academic-papers-dataset/
    ├── create_dataset.py                   # Fetch paper terbaru dari API ArXiv (multi-kategori)
    ├── explore_dataset.py                  # Eksplorasi & analisis dataset paper yang sudah ada
    ├── requirements.txt                    # Dependensi khusus (arxiv, datasets, huggingface)
    ├── README.md                           # Dokumentasi skema dataset paper
    ├── .gitattributes                      # Konfigurasi LFS / line ending
    └── data/                              # [.gitignore] file data besar, di-regenerate lokal
        ├── academic_papers.csv
        ├── academic_papers.parquet
        ├── academic_papers_cleaned.csv
        ├── academic_papers_cleaned.json
        ├── train.parquet
        └── test.parquet
```

---

## 🚀 Setup & Instalasi Lingkungan

### Prasyarat Sistem
- **Python 3.10+** (Direkomendasikan 3.11 / 3.12 / 3.14)
- **Google Chrome** (binary `chromedriver.exe` sudah disertakan di root)

### Instalasi
```bash
# 1. (Opsional) Buat Virtual Environment
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux/MacOS

# 2. Install dependensi utama
pip install -r requirements.txt

# 3. Install browser engine Playwright (wajib untuk scraper GitLab)
playwright install chromium
```

---

## 🛠️ Panduan Menjalankan Setiap Script (Runbook Lengkap)

---

### Langkah A — Fetch Paper SOTA dari ArXiv
Script ini mengambil ribuan paper terbaru dari API ArXiv (kategori: cs.SE, cs.CR, cs.DB, cs.DC, cs.AI, cs.CL, cs.CV, cs.LG) dan menyimpannya ke subfolder `academic-papers-dataset/data/`.

> ⚠️ **Jalankan sekali saja** karena proses fetch memerlukan koneksi internet dan cukup memakan waktu (~5–10 menit).

```bash
cd academic-papers-dataset

# Install dependensi khusus subfolder ini
pip install -r requirements.txt

# Fetch paper terbaru (default: 500 paper/kategori)
python create_dataset.py

# Atau customisasi jumlah paper per kategori:
python create_dataset.py --per-category 1000

# Eksplorasi dataset yang sudah ada:
python explore_dataset.py
```

**Output yang dihasilkan** (`academic-papers-dataset/data/`):

| File | Keterangan |
| :--- | :--- |
| `academic_papers.csv` | Dataset mentah hasil fetch API ArXiv |
| `academic_papers.parquet` | Format Parquet (efisien memori) |
| `academic_papers_cleaned.csv` | Dataset setelah deduplikasi & pembersihan |
| `academic_papers_cleaned.json` | Format JSON dari versi cleaned |
| `train.parquet` / `test.parquet` | Split untuk kebutuhan ML/NLP |

---

### Langkah B — Scraping Minat Penelitian Dosen Resmi STIS
Scraping profil seluruh dosen dari 3 program studi: **D-IV Komputasi Statistik (ks)**, **D-IV Statistika (s)**, dan **D-III Statistika (d3)**.

```bash
# Scrape seluruh prodi sekaligus (default & direkomendasikan)
python scrape_minat_dosen.py --prodi all

# Scrape prodi tertentu saja:
python scrape_minat_dosen.py --prodi ks   # D-IV Komputasi Statistik (19 dosen)
python scrape_minat_dosen.py --prodi s    # D-IV Statistika (38 dosen)
python scrape_minat_dosen.py --prodi d3   # D-III Statistika (15 dosen)

# Atur delay antar-request (default: 0.4 detik, naikan jika kena rate limit):
python scrape_minat_dosen.py --prodi all --delay 1.0 --output minat_dosen.csv
```

**Output:** `minat_dosen.csv` — kolom: `nama`, `kode`, `prodi`, `minat_penelitian`

---

### Langkah C — Ekstraksi Data Bimbingan dari PDF Executive Summary
Mengekstrak pasangan dosen pembimbing ↔ judul skripsi dari file PDF Executive Summary STIS.

> 📋 Pastikan file `Executive Summary - DIV Komputasi Statistik.pdf` ada di root folder.

```bash
# Ekstraksi daftar isi & judul skripsi
python crawl_pdf_titles.py

# Ekstraksi pemetaan dosen pembimbing ↔ judul skripsi
python crawl_pdf_dosen.py
```

**Output:**
- `hasil_executive_summary_titles.csv` — seluruh judul skripsi
- `hasil_executive_summary_dosen.csv` — pasangan `dosen ↔ judul ↔ mahasiswa`

---

### Langkah D — (Opsional) Scraping Skripsi dari GitLab STIS
Untuk mengunduh metadata skripsi lengkap (README, abstract) dari repositori GitLab:

```bash
# Ganti <TAHUN> sesuai angkatan yang diinginkan
python scrape_skripsi.py --group ks/skripsi2024 --out hasil_2024.json
python scrape_skripsi.py --group ks/skripsi2023 --out hasil_2023.json
```

**Argumen penting:**
- `--group` : Path grup GitLab (contoh: `ks/skripsi2021`)
- `--out` : Nama file output JSON
- `--delay` : Jeda antar-request (default: 1.0 detik)

> 🔐 Jika repo bersifat private/perlu login, lihat bagian `Kalau butuh login` di bawah.

---

### Langkah E — Preprocessing & Pelabelan Otomatis
Standardisasi kolom, normalisasi teks, dan assign **label utama + sub-label** secara otomatis:

```bash
# Preprocessing & labeling skripsi lokal
# → Menghasilkan kolom: main_label, sub_labels, se_automation_tags, ai_analytics_tags
python preprocess_skripsi.py

# Preprocessing paper ArXiv internasional
python preprocess_academic_papers.py

# (Opsional) Isi kolom deskripsi/abstrak yang masih kosong
python fill_empty_description.py
```

**Logika assign_main_label():**

| Kondisi | `main_label` |
| :--- | :--- |
| Hanya match `TAXONOMY_DATA_SCIENCE` | `"Data Science"` |
| Hanya match `TAXONOMY_SOFTWARE_ENGINEERING` | `"Software Engineering"` |
| Match kedua taksonomi (overlap/MLOps) | `"Data Science; Software Engineering"` |
| Tidak match keduanya | `"Software Engineering"` *(fallback)* |

---

### Langkah F — Orkestrasi Dataset Terpadu
Menggabungkan skripsi lokal STIS + paper internasional ArXiv menjadi satu dataset terpadu:

```bash
python orchestrate_dataset.py
```

**Output:**
- `dataset_unified_skripsi_dan_papers.csv` *(~16 MB)*
- `dataset_unified_skripsi_dan_papers.json` *(~18 MB)*

Kolom baru yang ditambahkan:

| Kolom | Keterangan |
| :--- | :--- |
| `main_label` | Label utama: `Data Science` / `Software Engineering` / keduanya |
| `sub_labels` | Sub-label detail yang match dari taksonomi |
| `discipline` | Sama dengan `main_label` (kompatibel dengan `plan_se_topics.py`) |

---

### Langkah G — Generate Rekomendasi Topik & Dosen Pembimbing ⭐
Script inti pipeline. Menganalisis kecocokan **72 dosen STIS** (dari 3 prodi) terhadap **6 Pilar Rekayasa Perangkat Lunak & Data Engineering** berdasarkan:
1. Profil minat penelitian resmi dosen di portal STIS.
2. Riwayat nyata judul bimbingan skripsi terdahulu.
3. Relevansi paper ArXiv SOTA 2025/2026.

```bash
python plan_se_topics.py
```

**Output yang Dihasilkan:**
1. **`rekomendasi_topik_skripsi_se.md`** — laporan lengkap: blueprint 6 pilar topik, paper SOTA rujukan, dan rekomendasi dosen + bukti bimbingan nyata.
2. **`rekomendasi_dosen_pembimbing.csv`** — tabel matriks skor kesesuaian tiap dosen per domain rekayasa.

---

## 🏛️ 6 Pilar Rekayasa Perangkat Lunak & Data Engineering

Paradigma utama: **Anda = System / Data / MLOps Engineer (Cangkang Utama)**, sedangkan algoritma ML/DL/Geospasial/NLP menjadi **subsistem pemrosesan datanya**.

| No | Pilar Rekayasa (Fokus Anda) | Subsistem Data / AI | Dosen Pembimbing Selaras |
| :-: | :--- | :--- | :--- |
| **1** | **Data Engineering, ETL & Lineage Pipeline** | Geospatial Fusion, Remote Sensing, Web Scraping | Dr. Eng. Arie Wahyu Wijayanto, Prof. Setia Pramana, Dr. Drs. Waris Marsisno, Lutfi Rahmatuti Maghfiroh |
| **2** | **MLOps & Automated Inference Serving** | Zero-Shot Segmentasi Citra, Nowcasting, Time-Series | Dr. Eng. Arie Wahyu Wijayanto, Erna Nurmawati, S.S.T., M.T., Rani Nooraeni, Dr. Robert Kurniawan |
| **3** | **Package Engineering & Reusable Modules** | Small Area Estimation (SAE), PyMC/R Distributions | Dr. Achmad Syahrul Choir, Dr. Azka Ubaidillah, Dr. Cucu Sumarni |
| **4** | **Compiler, Tooling & AST Engineering** | Dynamic Questionnaire Layout, Code Generator | Ibnu Santoso, S.S.T., M.T. |
| **5** | **Software Quality & Testing Testbed** | Automated Diagnostic, Trajectory Benchmark, QFD | Yunarso Anang, Ph.D. |
| **6** | **Distributed Microservices & Security** | OpenAPI Backend, Strangler Fig Migration, SIEM | Farid Ridho, S.S.T., M.T., Nori Wilantika, S.S.T., M.T.I., Firdaus, MBA |

---

## 🔐 Kalau Perlu Login ke GitLab STIS

Jika grup repositori bersifat private, tambahkan blok berikut sebelum loop scraping di `scrape_skripsi.py`:

```python
page.goto(f"{BASE_URL}/users/sign_in")
page.fill("#user_login", os.environ["GITLAB_USER"])
page.fill("#user_password", os.environ["GITLAB_PASSWORD"])
page.click("button[type=submit]")
page.wait_for_load_state("networkidle")
```

> ⚠️ **Jangan hardcode password di script.** Gunakan environment variable atau file `.env` yang di-gitignore.

---

## 💡 Tips Strategis Pengajuan Proposal ke Dosen

- **Positioning:** Selalu tegaskan ke dosen bahwa fokus riset Anda adalah **arsitektur software, throughput pipeline, data lineage, atau reusabilitas package** — bukan sekadar melatih model.
- **Bawa Diagram:** Lampirkan sketsa arsitektur sistem (*C4 Model, Sequence Diagram, atau Data Pipeline Flowchart*) saat bimbingan pertama.
- **Bukti SOTA:** Gunakan rujukan paper ArXiv 2025/2026 yang sudah terangkum di `rekomendasi_topik_skripsi_se.md` sebagai dasar urgensi ilmiah.
- **Label yang Tepat:** Jika topik Anda lintas domain (misal MLOps pipeline), manfaatkan multi-label `"Data Science; Software Engineering"` untuk menjangkau dosen dari kedua bidang.
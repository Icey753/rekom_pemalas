import json
import re
import pandas as pd
from pathlib import Path

def clean_text(text):
    """Membersihkan whitespace dan newline ganda."""
    if not text or pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_title_and_details_from_gitlab(readme, description, fallback_title):
    """
    Mengekstrak judul asli, pembimbing, dan penulis dari readme atau description GitLab jika tersedia.
    """
    clean_readme = clean_text(readme)
    clean_desc = clean_text(description)
    
    judul = ""
    author = ""
    supervisor = ""
    
    # Coba ekstrak Judul dari README
    if readme:
        match_judul = re.search(r'Judul\s+(?:Skripsi|Penelitian)\s*:\s*([^\n\r\#\.\(\)]+)', readme, re.IGNORECASE)
        if match_judul:
            judul = match_judul.group(1).strip()
            
        # Cari penulis / developer / pembimbing jika ada
        match_dev = re.search(r'(?:Developer|Penulis|Oleh)\s*:\s*([^\n\r\#\.]+)', readme, re.IGNORECASE)
        if match_dev:
            author = match_dev.group(1).strip()
            
        match_pembimbing = re.search(r'(?:Pembimbing|Dosen Pembimbing)\s*:\s*([^\n\r\#\.]+)', readme, re.IGNORECASE)
        if match_pembimbing:
            supervisor = match_pembimbing.group(1).strip()
            
    # Jika judul belum ketemu, cek dari description
    if not judul and description:
        match_desc_judul = re.search(r'Judul\s+(?:Skripsi|Penelitian)\s*:\s*(.*)', description, re.IGNORECASE)
        if match_desc_judul:
            judul = match_desc_judul.group(1).strip()
        elif len(description.split()) > 5 and not description.lower().startswith(('codeigniter', 'repository', 'berikut data')):
            judul = description.strip()

    # Jika masih belum ketemu, gunakan fallback title dari slug repository
    if not judul:
        # Ganti dash/underscore jadi spasi
        judul = fallback_title.replace('-', ' ').replace('_', ' ').strip()
        
    return clean_text(judul), clean_text(author), clean_text(supervisor)

# ==========================================
# TAKSONOMI KATEGORI / TAXONOMY MAPPING
# ==========================================
#
# ARSITEKTUR LABEL:
#   Label Utama 1 → DATA SCIENCE
#       Sub-label : ML, NLP/LLM, Computer Vision, Time Series, Spatial, SAE
#   Label Utama 2 → SOFTWARE ENGINEERING
#       Sub-label : Backend, Frontend, Mobile, Enterprise/SysInfo, Data Eng,
#                   Scraping, Automation, UI/UX, Package Eng, Security,
#                   Testing, Tooling
# ==========================================

# ------------------------------------------
# LABEL UTAMA 1: DATA SCIENCE
# ------------------------------------------
TAXONOMY_DATA_SCIENCE = {
    "Machine Learning & Predictive Modeling": [
        "machine learning", "klasifikasi", "clustering", "random forest",
        "xgboost", "lightgbm", "svm", "support vector", "neural network",
        "decision tree", "kmeans", "dbscan", "biclustering", "regresi", "boosting", "glmm"
    ],
    "NLP, LLM & Text Mining": [
        "nlp", "text mining", "sentimen", "sentiment", "large language model",
        "llm", "topic modeling", "lda", "bert", "sbert", "bm25", "transformer",
        "chatbot", "question answering", "text augmentation", "word2vec", "ner",
        "named entity", "summarization", "hate speech", "hoaks", "natural language"
    ],
    "Computer Vision & Remote Sensing": [
        "citra", "satelit", "remote sensing", "landsat", "sentinel", "yolo",
        "object detection", "segmentasi citra", "cnn", "penginderaan jauh",
        "nightlight", "viirs", "ndvi", "vision-language", "u-net", "land use"
    ],
    "Time Series & Forecasting": [
        "peramalan", "forecasting", "time series", "deret waktu", "arima",
        "sarima", "var", "garch", "lstm", "prophet", "dekomposisi", "gstar-gls-svr"
    ],
    "Spatial & Spatio-Temporal Analysis": [
        "spasial", "spatial", "gwr", "spatial autoregressive", "sar", "sem",
        "gstar", "spatio-temporal", "pemetaan", "gis", "poi", "point of interest", "geospasial"
    ],
    "Small Area Estimation (SAE)": [
        "small area estimation", "sae", "fay-herriot", "pendugaan area kecil",
        "hierarchical bayes", "ebp", "m-quantile", "area level", "unit level", "sae.projection"
    ],
}

# ------------------------------------------
# LABEL UTAMA 2: SOFTWARE ENGINEERING
# Sub-label mencakup: Backend, Frontend, Mobile,
# Enterprise/System Information, Computer Science generik, dll.
# ------------------------------------------
TAXONOMY_SOFTWARE_ENGINEERING = {
    "Backend, Microservices & Web API": [
        "backend", "microservice", "microservices", "webapi", "rest api",
        "openapi", "swagger", "graphql", "grpc", "service-oriented",
        "spring ai", "express", "fastapi", "laravel", "codeigniter", "django", "flask", "api"
    ],
    "Frontend & Modern Web Architecture": [
        "frontend", "react", "vue", "next.js", "angular", "headless cms",
        "single page application", "spa", "pwa", "progressive web", "tailwind", "ui components"
    ],
    "Mobile Application & CAPI Systems": [
        "android", "kotlin", "flutter", "react native", "capi", "mobile app",
        "offline-first", "sync", "hybrid incremental", "keludstat", "sipadu mobile"
    ],
    "Enterprise Systems & Gov-Tech (System Information)": [
        "sistem informasi", "monitoring", "evaluasi", "e-sakip", "posyandu",
        "kepegawaian", "arsip", "pengadaan", "tugas belajar", "manajemen talenta",
        "sipodas", "simantap", "simamov", "manajemen survei", "sim rt", "siman",
        "information system", "computer science", "ilmu komputer"
    ],
    "Data Engineering, ETL & Big Data Storage": [
        "data engineering", "data fusion", "etl", "data warehouse",
        "data lake", "arsitektur penyimpanan", "big data", "hadoop",
        "spark", "mongodb", "postgresql", "elasticsearch", "redis", "query optimization"
    ],
    "Web Scraping & Data Ingestion Engine": [
        "scraping", "crawler", "crawling", "selenium", "playwright",
        "beautifulsoup", "scrapy", "harvesting", "data ingestion", "twint", "puppeteer"
    ],
    "Automation, Pipeline & Orchestration": [
        "pipeline", "orchestration", "orkestrasi", "otomasi", "workflow",
        "airflow", "n8n", "cron", "automated", "otomatisasi", "job scheduler",
        "task runner", "etl pipeline", "data pipeline", "stream processing"
    ],
    "UI/UX, UCD & Usability Engineering": [
        "user-centered design", "ucd", "design thinking", "usability testing",
        "sus score", "heuristics", "information architecture", "figma", "wireframe", "user interface"
    ],
    "Statistical Software & Package Engineering": [
        "r package", "python package", "pembangunan package", "paket program", "r-package",
        "neodistr", "hbsaems", "bambi", "pymc", "framework pembangunan", "modul r", "shiny", "gui"
    ],
    "Software Security & Defensive Engineering": [
        "guardrail", "runtime security", "vulnerability", "attack", "injection",
        "jailbreak", "adversarial", "privacy", "defense", "interceptor", "malware",
        "hardening", "keamanan", "audit keamanan", "siem", "privasi", "cyber"
    ],
    "Software Testing & Automated QA": [
        "testing", "benchmark", "diagnostic", "fault localization", "bug", "fuzzing",
        "repair", "verification", "conformance", "flaky test", "quality assurance",
        "standar kualitas", "qfd", "testbed"
    ],
    "Developer Tooling & Static Analysis": [
        "static analysis", "ast", "refactoring", "code generation", "linter",
        "cli tool", "plugin", "parser", "syntax tree", "library", "module",
        "ide extension", "developer tool"
    ],
}

# Alias backward-compat: SE_AND_AUTOMATION tetap menunjuk ke TAXONOMY_SOFTWARE_ENGINEERING
# dan AI_AND_ANALYTICS tetap menunjuk ke TAXONOMY_DATA_SCIENCE
TAXONOMY_SE_AND_AUTOMATION = TAXONOMY_SOFTWARE_ENGINEERING
TAXONOMY_AI_AND_ANALYTICS = TAXONOMY_DATA_SCIENCE

TAXONOMY_SECTORS = {
    "BPS & Survey Operations": [
        "bps", "survei", "sensus", "capi", "sipadu", "kompre", "kepegawaian", 
        "pembinaan statistik", "mitra statistik", "manajemen dokumen", "allstats", "fasih"
    ],
    "Kemiskinan & Kesejahteraan Sosial": [
        "kemiskinan", "stunting", "bansos", "pkh", "pemberdayaan perempuan", 
        "desa prima", "sdgs", "kesejahteraan", "rentan miskin", "disabilitas", "unmet need"
    ],
    "Ekonomi, Inflasi & Bisnis": [
        "inflasi", "pdrb", "pertumbuhan ekonomi", "ekonomi", "komoditas", 
        "wisatawan", "pariwisata", "pasar", "ekspor", "impor", "harga saham", "ihk"
    ],
    "Pertanian, Pangan & Lingkungan": [
        "padi", "jagung", "tanaman", "panen", "emisi metana", "tpa", "ubinan",
        "lingkungan hidup", "kualitas udara", "iklim", "tutupan lahan", "eceng gondok", 
        "kekeringan", "mangrove", "carbon", "sampah", "air tanah", "tanah longsor"
    ],
    "Kesehatan & Epidemiologi": [
        "malaria", "stunting", "kesehatan", "penyakit", "covid", "posyandu", 
        "balita", "prevalensi", "pneumonia"
    ],
    "Akademik & Kampus STIS": [
        "stis", "magang", "lomba", "kemahasiswaan", "ujian komprehensif", 
        "dosen", "mahasiswa", "pkl", "rohis"
    ]
}

def tag_categories(text, taxonomy_dict):
    """Mencocokkan kata kunci teks dengan taksonomi."""
    text_lower = text.lower()
    matched = []
    for category, keywords in taxonomy_dict.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) if len(kw) <= 4 else (kw in text_lower) for kw in keywords):
            matched.append(category)
    return matched


def assign_main_label(text):
    """
    Menentukan main_label dan sub_labels berdasarkan teks.

    Aturan:
    - Jika cocok dengan TAXONOMY_DATA_SCIENCE → main_label mengandung "Data Science"
    - Jika cocok dengan TAXONOMY_SOFTWARE_ENGINEERING → main_label mengandung "Software Engineering"
    - Jika keduanya cocok → multi-label (list berisi keduanya)
    - Jika tidak ada → fallback "Software Engineering" (Computer Science generik)

    Returns:
        main_labels (list[str]): Label utama, bisa lebih dari satu jika overlap.
        sub_labels (list[str]): Semua sub-label yang match dari kedua taksonomi.
    """
    ds_tags = tag_categories(text, TAXONOMY_DATA_SCIENCE)
    se_tags = tag_categories(text, TAXONOMY_SOFTWARE_ENGINEERING)

    main_labels = []
    if ds_tags:
        main_labels.append("Data Science")
    if se_tags:
        main_labels.append("Software Engineering")
    if not main_labels:
        # Fallback: Computer Science / topik tanpa kategori spesifik
        main_labels.append("Software Engineering")

    sub_labels = ds_tags + se_tags
    return main_labels, sub_labels

def preprocess_all_datasets():
    records = []
    
    # -------------------------------------------------------------
    # 1. Olah data Executive Summary PDF Titles (2023 - 2024)
    # -------------------------------------------------------------
    csv_file = Path("hasil_executive_summary_titles.csv")
    if csv_file.exists():
        df_exec = pd.read_csv(csv_file)
        for _, row in df_exec.iterrows():
            judul = clean_text(row.get('judul', ''))
            penulis = clean_text(row.get('penulis', ''))
            pembimbing = clean_text(row.get('pembimbing', ''))
            halaman = str(row.get('halaman_dokumen', '')).strip()
            
            if not judul:
                continue
                
            full_context = f"{judul} {penulis} {pembimbing}"

            # Label utama baru
            main_labels, sub_labels = assign_main_label(full_context)

            # Backward-compat tags
            se_tags = tag_categories(full_context, TAXONOMY_SOFTWARE_ENGINEERING)
            ai_tags = tag_categories(full_context, TAXONOMY_DATA_SCIENCE)
            sector_tags = tag_categories(full_context, TAXONOMY_SECTORS)

            records.append({
                "id": f"EXEC_{row.get('no', len(records)+1)}",
                "source": "executive_summary_pdf",
                "year": 2024,
                "title": judul,
                "author": penulis.title() if penulis else "",
                "supervisor": pembimbing.title() if pembimbing else "",
                "description": "",
                "readme_snippet": "",
                # ── Label baru ──────────────────────────────────────────────
                "main_label": main_labels,            # ['Data Science'] / ['Software Engineering'] / keduanya
                "sub_labels": sub_labels,             # sub-label spesifik yang match
                # ── Backward-compat ─────────────────────────────────────────
                "se_automation_tags": se_tags,
                "ai_analytics_tags": ai_tags,
                "application_sector_tags": sector_tags,
                "all_tags": list(set(se_tags + ai_tags + sector_tags)),
                "full_text_for_search": f"[Tahun 2024] Judul: {judul} | Penulis: {penulis} | Pembimbing: {pembimbing} | Label: {', '.join(main_labels)} | Tags: {', '.join(sub_labels + sector_tags)}",
                "raw_reference": f"Hal. {halaman} pada Executive Summary 2023-2024"
            })
            
    # -------------------------------------------------------------
    # 2. Olah data GitLab Repositories (2017 - 2021)
    # -------------------------------------------------------------
    json_file = Path("hasil_semua.json")
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            gitlab_data = json.load(f)
            
        for idx, item in enumerate(gitlab_data, 1):
            group = item.get('group', '')
            match_year = re.search(r'skripsi(\d{4})', group)
            year = int(match_year.group(1)) if match_year else None
            
            raw_title = item.get('title', '')
            readme = item.get('readme', '')
            desc = item.get('description', '')
            
            judul, author, supervisor = extract_title_and_details_from_gitlab(readme, desc, raw_title)
            desc_clean = clean_text(desc)
            readme_snippet = clean_text(readme)[:300] if readme else ""
            
            if not judul:
                continue
                
            full_context = f"{judul} {desc_clean} {clean_text(readme)}"

            # Label utama baru
            main_labels, sub_labels = assign_main_label(full_context)

            # Backward-compat tags
            se_tags = tag_categories(full_context, TAXONOMY_SOFTWARE_ENGINEERING)
            ai_tags = tag_categories(full_context, TAXONOMY_DATA_SCIENCE)
            sector_tags = tag_categories(full_context, TAXONOMY_SECTORS)

            records.append({
                "id": f"GITLAB_{year}_{idx}",
                "source": "gitlab_stis",
                "year": year,
                "title": judul,
                "author": author.title() if author else "",
                "supervisor": supervisor.title() if supervisor else "",
                "description": desc_clean,
                "readme_snippet": readme_snippet,
                # ── Label baru ──────────────────────────────────────────────
                "main_label": main_labels,            # ['Data Science'] / ['Software Engineering'] / keduanya
                "sub_labels": sub_labels,             # sub-label spesifik yang match
                # ── Backward-compat ─────────────────────────────────────────
                "se_automation_tags": se_tags,
                "ai_analytics_tags": ai_tags,
                "application_sector_tags": sector_tags,
                "all_tags": list(set(se_tags + ai_tags + sector_tags)),
                "full_text_for_search": f"[Tahun {year}] Judul: {judul} | Deskripsi: {desc_clean} | Label: {', '.join(main_labels)} | Tags: {', '.join(sub_labels + sector_tags)}",
                "raw_reference": item.get('url', '')
            })

    # Konversi ke DataFrame & Deduplikasi
    df_result = pd.DataFrame(records)
    df_result.drop_duplicates(subset=['title'], inplace=True)
    df_result.sort_values(by=['year', 'title'], ascending=[False, True], inplace=True)
    
    # Simpan output
    output_csv = Path("dataset_skripsi_lengkap.csv")
    output_json = Path("dataset_skripsi_lengkap.json")
    
    # Untuk CSV simpan list tags sebagai string separated semicolon
    df_csv = df_result.copy()
    df_csv['main_label'] = df_csv['main_label'].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    df_csv['sub_labels'] = df_csv['sub_labels'].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    df_csv['se_automation_tags'] = df_csv['se_automation_tags'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    df_csv['ai_analytics_tags'] = df_csv['ai_analytics_tags'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    df_csv['application_sector_tags'] = df_csv['application_sector_tags'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    df_csv['all_tags'] = df_csv['all_tags'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    
    df_csv.to_csv(output_csv, index=False, encoding='utf-8-sig')
    df_result.to_json(output_json, orient='records', indent=2, force_ascii=False)
    
    print("="*60)
    print("Preprocessing Selesai!")
    print(f"Total Skripsi Terkumpul: {len(df_result)}")
    print(f"Output CSV : {output_csv.resolve()}")
    print(f"Output JSON: {output_json.resolve()}")
    print("="*60)
    
    # Statistik Singkat
    print("\nDistribusi Berdasarkan Tahun:")
    print(df_result['year'].value_counts(dropna=False).sort_index())

    print("\n" + "="*60)
    print("DISTRIBUSI LABEL UTAMA (main_label)")
    print("="*60)
    label_counts = df_result['main_label'].explode().value_counts()
    print(label_counts)

    print("\nTop 5 Sub-label Data Science:")
    ds_exploded = df_result['ai_analytics_tags'].explode().value_counts()
    print(ds_exploded[ds_exploded.index != ''].head(5))

    print("\nTop 5 Sub-label Software Engineering:")
    se_exploded = df_result['se_automation_tags'].explode().value_counts()
    print(se_exploded[se_exploded.index != ''].head(5))

if __name__ == '__main__':
    preprocess_all_datasets()

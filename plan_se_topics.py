"""
SE Topic & Multi-Domain Lecturer Recommendation System
Arsitektur:
- Cangkang Utama: Software Engineering (SE) & Data Engineering (ETL, Pipeline, Distributed Architecture, Security, MLOps, Automated Tooling)
- Subsistem Cerdas: Data Science / Machine Learning / Remote Sensing / NLP / Time Series sebagai mesin pemrosesan data riil.

Menghubungkan:
1. dataset_unified_skripsi_dan_papers.csv (SOTA ArXiv Papers & Skripsi Lokal)
2. minat_dosen.csv (72 Dosen dari Seluruh Prodi: KS, D-IV Statistika, D-III Statistika)
3. hasil_executive_summary_dosen.csv (Riwayat Bimbingan Nyata)
"""

import pandas as pd
import json
import re
from pathlib import Path

DATASET_CSV = "dataset_unified_skripsi_dan_papers.csv"
MINAT_DOSEN_CSV = "minat_dosen.csv"
BIMBINGAN_DOSEN_CSV = "hasil_executive_summary_dosen.csv"
OUTPUT_REPORT_MD = "rekomendasi_topik_skripsi_se.md"
OUTPUT_DOSEN_CSV = "rekomendasi_dosen_pembimbing.csv"

# 6 Pilar SE + Data Engineering & MLOps Infrastructure
SE_DOMAINS = {
    "1. Data Engineering, ETL Pipeline & Data Lineage (cs.DB & Big Data Architecture)": {
        "id_key": "data_engineering",
        "cangkang_se": "Automated ETL/ELT Pipeline, Data Lakehouse Ingestion Engine, Data Quality Gatekeeper, Lineage & Provenance Tracker, Schema Migration Validator",
        "peran_subsistem": "Menjalankan pipeline data scraping/ingestion, augmentasi data sintetis, pembersihan anomali data otomatis, dan sinkronisasi data multisumber sebelum masuk database.",
        "primary_cats": ["Databases & Data Management", "Software Engineering", "cs.DB", "cs.SE"],
        "keywords": [
            "pipeline", "etl", "database", "traceab", "provenance", "lineage", "ingestion", "synthetic", 
            "data quality", "lakehouse", "datawarehouse", "nosql", "sdmx", "data engineering", "data mart", 
            "scraping", "crawler", "data fusion", "big data", "manajemen data", "spasial", "multisumber", "data integration"
        ],
        "evaluasi_se": "Data Ingestion Throughput (MB/s), Pipeline Latency, Lineage Resolution Speed, Data Corruption Prevention Rate, Fault Tolerance",
        "rumus_judul": "Rancang Bangun Pipeline Terotomasi untuk [Ingestion / Augmentasi Data Multisumber] dengan Mekanisme [Traceability Audit / Data Lineage / Quality Gate]",
        "contoh_judul_aplikatif": "Rancang Bangun Pipeline ETL Terotomasi untuk Ingestion Data Geospasial Multisumber dengan Mekanisme Data Lineage dan Validasi Anomali Data"
    },
    "2. MLOps, Model Serving & Automated Pipeline Orchestration (cs.DC & cs.LG)": {
        "id_key": "mlops_orchestration",
        "cangkang_se": "Model Serving Gateway, Streaming Feature Store, Automated Inference Pipeline, Distributed Task Orchestrator, Zero-Downtime Model Deployer",
        "peran_subsistem": "Mengorkestrasi inferensi model Machine Learning/Deep Learning (misal: Segment Any Change citra satelit, Nowcasting, Time-Series forecasting, Text Mining) dalam arsitektur terdistribusi.",
        "primary_cats": ["Distributed, Parallel & Cluster Computing", "Machine Learning", "cs.DC", "cs.SE"],
        "keywords": [
            "orchestrat", "workflow", "distributed", "event-driven", "microservice", "stream", "broker", 
            "concurrency", "state machine", "serving", "inference", "deep learning", "machine learning", 
            "remote sensing", "citra satelit", "nowcasting", "peramalan", "forecasting", "model serving", "cluster"
        ],
        "evaluasi_se": "Serving Latency (p95/p99 ms), Request Throughput (RPS), Worker Concurrency Scaling, Inference Failure Recovery Time",
        "rumus_judul": "Arsitektur Distributed Pipeline & Model Serving Gateway Berbasis [Event-Driven / Worker Queue] untuk Otomasi Inferensi [Model AI / Kasus Nyata]",
        "contoh_judul_aplikatif": "Arsitektur Distributed Pipeline Berbasis Message Broker untuk Otomasi Inferensi Segmentasi Citra Satelit Multi-Temporal"
    },
    "3. Software Security, API Guardrail & Defensive Engineering (cs.CR & Secure SE)": {
        "id_key": "security",
        "cangkang_se": "Runtime Guardrail, Middleware Interceptor, Vulnerability Scanner, Token-Level Sanitizer, Access Control Policy Engine, Audit Logger",
        "peran_subsistem": "Mendeteksi serangan injeksi, anomali input, jailbreak prompt pada LLM, kebocoran data sensitif, audit kepatuhan, atau penyalahgunaan API layanan publik.",
        "primary_cats": ["Software Engineering", "Cryptography and Security", "cs.CR", "cs.SE"],
        "keywords": [
            "guardrail", "runtime", "security", "vulnerability", "attack", "injection", "jailbreak", 
            "adversarial", "safe", "privacy", "defense", "interceptor", "shield", "malware", "hardening", 
            "keamanan", "audit", "siem", "privasi", "cyber"
        ],
        "evaluasi_se": "Overhead Latensi (< 1.5%), Attack Detection Recall, Throughput Degradation, Resource (CPU/RAM) Utilization",
        "rumus_judul": "Rancang Bangun [Tipe Middleware/Security Engine] untuk Mitigasi [Risiko Serangan/Kebocoran] pada [Platform Layanan / API]",
        "contoh_judul_aplikatif": "Rancang Bangun Middleware Runtime Guardrail untuk Intersepsi dan Sanitasi Streaming API pada Aplikasi Layanan Publik"
    },
    "4. Software Testing, Automated QA & Diagnostic Systems (cs.SE Quality)": {
        "id_key": "testing_quality",
        "cangkang_se": "Automated Test Suite Generator, Fault Localization Framework, Flaky Test Detector, Execution Trajectory Diagnostic Tool, Data Validation Harness",
        "peran_subsistem": "Menganalisis kode sumber, log eksekusi, atau trajectory langkah sistem cerdas (Agent/RAG) untuk menemukan letak kegagalan fungsi/bug.",
        "primary_cats": ["Software Engineering", "cs.SE"],
        "keywords": [
            "testing", "benchmark", "diagnostic", "evaluat", "fault", "bug", "trajectory", "fuzzing", 
            "repair", "verification", "conformance", "flaky", "quality", "kualitas", "standar", "qfd", "audit", "evaluasi"
        ],
        "evaluasi_se": "Fault Detection Rate, Execution Time per Test, Code Coverage Increase, Reduction of Manual Triage Time",
        "rumus_judul": "Pengembangan Framework Pengujian Otomatis dan Diagnostik Kegagalan pada [Tipe Sistem / Pipeline / Modul Layanan]",
        "contoh_judul_aplikatif": "Pengembangan Platform Testbed Diagnostik Otomatis untuk Evaluasi Keandalan Pemanggilan Tool pada Sistem Multi-Service"
    },
    "5. Developer Tooling, Package Engineering & Static Analysis (cs.SE Tooling)": {
        "id_key": "tooling_packages",
        "cangkang_se": "Python/R Reusable Package, AST / Control-Flow Graph Parser, CLI Code Auditor, IDE Extension, Semantic Code Search Engine",
        "peran_subsistem": "Menyediakan pustaka komputasi statistik modular (distribusi baru, Small Area Estimation framework, data transformer) atau tool analisis statis developer.",
        "primary_cats": ["Software Engineering", "cs.SE"],
        "keywords": [
            "tool", "ide", "extension", "static analysis", "ast", "refactoring", "developer", "repository", 
            "code generation", "linter", "cli", "plugin", "parser", "syntax tree", "package", "library", 
            "module", "r-package", "gui", "interface", "neodistr", "pymc", "bambi", "hbsaems"
        ],
        "evaluasi_se": "Parsing Time per KLOC, Package Memory Footprint, Precision/Recall Anomaly Detection, System Usability Scale (SUS)",
        "rumus_judul": "Pengembangan [Pustaka Modular / CLI Tool / Plugin IDE] untuk [Fungsi Otomasi / Analisis / Komputasi] Berbasis [Arsitektur Tertentu]",
        "contoh_judul_aplikatif": "Pembangunan Software Package Python/R Modular untuk Otomasi Pipeline Estimasi Statistik dengan Arsitektur Extensible Plugin"
    },
    "6. Intelligent Distributed Systems & Enterprise Services (cs.DC & Enterprise SE)": {
        "id_key": "enterprise_microservices",
        "cangkang_se": "Microservices Architecture, RESTful/OpenAPI Backend, Strangler Fig Migration Pattern, Event-Driven Message Router",
        "peran_subsistem": "Mengoordinasikan berbagai modul layanan organisasi (presensi, RPS, evaluasi kinerja, chatbot asisten) dalam arsitektur *high-availability*.",
        "primary_cats": ["Distributed, Parallel & Cluster Computing", "Software Engineering", "cs.DC", "cs.SE"],
        "keywords": [
            "microservice", "backend", "frontend", "sistem informasi", "web", "android", "mobile", 
            "strangler fig", "domain-driven design", "openapi", "restful", "rest api", "service", 
            "arsitektur", "aplikasi", "manajemen", "posyandu", "bimbingan konseling"
        ],
        "evaluasi_se": "Service Response Time (p95), Database Query Latency, Horizontal Scalability, Modular Code Coupling/Cohesion",
        "rumus_judul": "Rancang Bangun Sistem Informasi Berbasis [Arsitektur Microservices / Distributed Backend] untuk Otomasi [Proses Bisnis Organisasi]",
        "contoh_judul_aplikatif": "Pembangunan Backend Sistem Terdistribusi Berbasis Microservices dan OpenAPI untuk Integrasi Layanan Publik Statistik"
    }
}

def clean_lecturer_display_name(raw_name):
    clean = re.sub(r'^Lihat Profil\s*', '', str(raw_name), flags=re.IGNORECASE).strip()
    return clean

def extract_searchable_name(display_name):
    """Menghilangkan gelar depan & belakang untuk matching fleksibel ke daftar bimbingan."""
    clean = re.sub(r'^(Prof\.|Dr\.|Eng\.|Drs\.|Ir\.)\s*', '', display_name, flags=re.IGNORECASE).strip()
    clean = re.sub(r',\s*.*$', '', clean).strip() # hilangkan gelar belakang
    clean = re.sub(r'^(Dr\.\s*Eng\.|Dr\.\s*Drs\.)\s*', '', clean, flags=re.IGNORECASE).strip()
    return clean.strip()

def match_bimbingan_titles(lecturer_clean_name, df_bimbingan):
    """Mencari semua judul bimbingan dosen berdasarkan nama yang fleksibel."""
    raw_upper = lecturer_clean_name.upper()
    words = [w for w in re.findall(r'[A-Za-z]+', raw_upper) if len(w) > 2 and w not in ['PROF', 'DR', 'ENG', 'SST', 'SSI', 'MSC', 'PHD', 'STAT', 'MSTAT', 'MSI', 'MBA', 'MTI', 'DRS', 'STIS']]
    
    matched_titles = []
    for _, row in df_bimbingan.iterrows():
        b_dosen = str(row['dosen']).upper()
        # Direct match or word overlap match
        if raw_upper in b_dosen or b_dosen in raw_upper:
            matched_titles.append(row['judul'])
        elif len(words) >= 2 and all(w in b_dosen for w in words[:2]):
            matched_titles.append(row['judul'])
            
    return list(set(matched_titles))

def load_data():
    print(f"[*] Membaca dataset papers dari {DATASET_CSV}...")
    df_unified = pd.read_csv(DATASET_CSV)
    
    print(f"[*] Membaca data minat dosen dari {MINAT_DOSEN_CSV}...")
    df_minat = pd.read_csv(MINAT_DOSEN_CSV)
    
    print(f"[*] Membaca data riwayat bimbingan dari {BIMBINGAN_DOSEN_CSV}...")
    df_bimbingan = pd.read_csv(BIMBINGAN_DOSEN_CSV)
    
    return df_unified, df_minat, df_bimbingan

def find_matched_papers(foreign_df, domain_info):
    """Mencari paper ArXiv yang relevan dengan pilar domain sistem."""
    kw_regex = '|'.join([re.escape(k) for k in domain_info['keywords'][:10]])
    
    title_matches = foreign_df[foreign_df['title'].str.contains(kw_regex, case=False, na=False)].copy()
    abstract_matches = foreign_df[foreign_df['abstract_or_summary'].str.contains(kw_regex, case=False, na=False)].copy()
    
    combined = pd.concat([title_matches, abstract_matches]).drop_duplicates(subset=['id']).copy()
    combined['is_title_match'] = combined['title'].str.contains(kw_regex, case=False, na=False)
    combined = combined.sort_values(by=['is_title_match', 'year'], ascending=[False, False])
    
    return combined.head(5).to_dict(orient='records'), len(combined)

def analyze_lecturer_compatibility(df_minat, df_bimbingan):
    """
    Menghitung skor kesesuaian 72 dosen terhadap 6 pilar SE & Data Engineering.
    Dosen ML / Data Mining / Remote Sensing diakomodasi untuk topik di mana Anda menjadi Data Engineer / System Builder-nya.
    """
    lecturer_profiles = []

    for _, row in df_minat.iterrows():
        raw_name = row['nama']
        kode = row['kode']
        prodi = row.get('prodi', 'ks')
        minat_str = str(row['minat_penelitian']) if pd.notna(row['minat_penelitian']) else ""
        
        display_name = clean_lecturer_display_name(raw_name)
        clean_name = extract_searchable_name(display_name)
        
        bimbingan_titles = match_bimbingan_titles(clean_name, df_bimbingan)
        
        domain_scores = {}
        domain_evidence = {}
        
        for domain_name, d_info in SE_DOMAINS.items():
            keywords = d_info['keywords']
            
            # 1. Skor Minat Dosen (Bobot: 3.5 per keyword match)
            minat_matches = []
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', minat_str, re.IGNORECASE) or (len(kw) > 4 and kw.lower() in minat_str.lower()):
                    minat_matches.append(kw)
            minat_matches = list(set(minat_matches))
            minat_score = len(minat_matches) * 3.5
            
            # 2. Skor Riwayat Bimbingan Mahasiswa (Bobot: 2.5 per judul relevan)
            matched_titles = []
            for t in bimbingan_titles:
                t_matches = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', str(t), re.IGNORECASE) or (len(kw) > 4 and kw.lower() in str(t).lower())]
                if t_matches:
                    matched_titles.append((t, list(set(t_matches))))
                    
            bimbingan_score = len(matched_titles) * 2.5
            
            # Booster khusus ranah rekayasa sistem / komputasi
            domain_booster = 0.0
            if "Software Engineering" in minat_str or "Pengembangan sistem" in minat_str:
                domain_booster += 2.0
            if "Big Data" in minat_str or "Data Engineering" in minat_str or "Database Management" in minat_str:
                domain_booster += 1.5
                
            total_score = minat_score + bimbingan_score + domain_booster
            
            domain_scores[domain_name] = round(total_score, 1)
            domain_evidence[domain_name] = {
                "minat_kw": minat_matches,
                "bimbingan_count": len(matched_titles),
                "sample_bimbingan": [t[0] for t in matched_titles[:3]]
            }

        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0] if sorted_domains else "-"
        max_score = sorted_domains[0][1] if sorted_domains else 0.0

        lecturer_profiles.append({
            "kode": kode,
            "prodi": prodi,
            "display_name": display_name,
            "clean_name": clean_name,
            "minat_raw": minat_str,
            "total_bimbingan_count": len(bimbingan_titles),
            "domain_scores": domain_scores,
            "domain_evidence": domain_evidence,
            "primary_domain": primary_domain,
            "max_score": max_score,
            "all_bimbingan_sample": bimbingan_titles[:5]
        })

    return lecturer_profiles

def build_lecturer_recommendations_csv(lecturer_profiles):
    """Menyimpan tabel rekomendasi lengkap ke format CSV."""
    rows = []
    for p in lecturer_profiles:
        row = {
            "kode": p['kode'],
            "nama_dosen": p['display_name'],
            "prodi": p['prodi'],
            "total_bimbingan": p['total_bimbingan_count'],
            "fokus_rekomendasi_utama": p['primary_domain'],
            "skor_maksimal": p['max_score'],
            "minat_penelitian": p['minat_raw']
        }
        for d_name, score in p['domain_scores'].items():
            short_k = SE_DOMAINS[d_name]['id_key']
            row[f"skor_{short_k}"] = score
        rows.append(row)
        
    df_out = pd.DataFrame(rows)
    df_out = df_out.sort_values(by="skor_maksimal", ascending=False)
    df_out.to_csv(OUTPUT_DOSEN_CSV, index=False)
    print(f"[OK] Data rekomendasi dosen tersimpan di '{OUTPUT_DOSEN_CSV}'")
    return df_out

def build_combined_report(df_unified, lecturer_profiles):
    """Membangun laporan terpadu: Blueprint SE/Data Engineering + Rekomendasi 72 Dosen."""
    foreign_df = df_unified[df_unified['origin'] == 'foreign'].copy()
    
    lines = []
    lines.append("# 🏛️ Blueprint Topik Skripsi Software & Data Engineering + Rekomendasi Dosen")
    lines.append("")
    lines.append("> **Paradigma Inti:** Anda memposisikan diri sebagai **System / Data / MLOps Engineer (Cangkang Utama)** yang membangun pipeline, middleware, atau arsitektur sistem terdistribusi, di mana algoritma Data Science / ML / Geospasial / NLP menjadi **subsistem pemrosesan datanya**.")
    lines.append("")
    lines.append("---")
    
    # Matriks Strategi Topik
    lines.append("## 💡 Formula SE / Data Engineering + Domain Data Science")
    lines.append("Dengan memposisikan diri sebagai **Software / Data Engineer**, Anda bisa membidik dosen-dosen pakar ML/Data Mining/Spasial tanpa khawatir proposal ditolak:")
    lines.append("")
    lines.append("| No | Peran Anda (Cangkang Utama SE / Data Eng) | Subsistem Algoritma (Domain Kasus) | Target Dosen Pembimbing yang Sangat Selaras |")
    lines.append("| :-: | :--- | :--- | :--- |")
    lines.append("| 1 | **Data Engineering, ETL & Data Lineage** | Geospatial Fusion, Remote Sensing, Web Scraping | **Dr. Eng. Arie Wahyu Wijayanto, Lutfi Rahmatuti, Waris Marsisno** |")
    lines.append("| 2 | **MLOps & Automated Inference Serving** | Zero-Shot Segment Any Change, LLM, Computer Vision | **Prof. Setia Pramana, Dr. Eng. Lya Hulliyyatus Suadaa, Rani Nooraeni** |")
    lines.append("| 3 | **Package Engineering & Reusable Modules** | Small Area Estimation, PyMC Distributions, Bayesian | **Dr. Achmad Syahrul Choir, Dr. Azka Ubaidillah, Dr. Cucu Sumarni** |")
    lines.append("| 4 | **Compiler / Tooling & AST Engineering** | Dynamic Questionnaire, Code Generator, Logic Parser | **Ibnu Santoso, S.S.T., M.T.** |")
    lines.append("| 5 | **Software Quality & Testing Testbed** | Automated Diagnostic, QFD, Multi-Agent Conformance | **Yunarso Anang, Ph.D.** |")
    lines.append("| 6 | **Distributed Microservices & Security** | OpenAPI Backend, Security Hardening, SIEM Wazuh | **Farid Ridho, Firdaus, Nori Wilantika** |")
    lines.append("")
    lines.append("---")
    
    # Detail Per Pilar
    lines.append("## 🏆 6 Pilar Bidang Rekayasa, Rujukan SOTA & Rekomendasi Dosen Pembimbing")
    lines.append("")
    
    for domain_name, info in SE_DOMAINS.items():
        matched_papers, total_count = find_matched_papers(foreign_df, info)
        
        # Cari dosen dengan skor tertinggi di domain ini
        ranked_lecturers = sorted(
            lecturer_profiles, 
            key=lambda x: x['domain_scores'].get(domain_name, 0), 
            reverse=True
        )
        top_lecturers = [l for l in ranked_lecturers if l['domain_scores'].get(domain_name, 0) > 0][:4]
        
        lines.append(f"### 📂 {domain_name}")
        lines.append(f"- **Cangkang Software / Data Engine (Fokus Anda):** `{info['cangkang_se']}`")
        lines.append(f"- **Peran Subsistem Data/AI:** {info['peran_subsistem']}")
        lines.append(f"- **Metrik Evaluasi Rekayasa (SE/Data Eng):** `{info['evaluasi_se']}`")
        lines.append(f"- **Template Judul Skripsi:** *{info['rumus_judul']}*")
        lines.append(f"- **Contoh Judul Aplikatif:** *{info['contoh_judul_aplikatif']}*")
        lines.append("")
        
        lines.append("#### 👨‍🏫 Rekomendasi Dosen Pembimbing yang Sangat Cocok:")
        if top_lecturers:
            for idx, doc in enumerate(top_lecturers, 1):
                ev = doc['domain_evidence'][domain_name]
                score = doc['domain_scores'][domain_name]
                prodi_label = doc['prodi'].upper()
                lines.append(f"{idx}. **{doc['display_name']}** [Prodi: `{prodi_label}`] (Skor Kesesuaian: `{score} pt`)")
                lines.append(f"   - **Keahlian / Minat Penelitian:** `{doc['minat_raw'] if doc['minat_raw'] else 'Terdata di Bimbingan'}`")
                if ev['sample_bimbingan']:
                    lines.append(f"   - **Bukti Judul Bimbingan Terkait:**")
                    for sm in ev['sample_bimbingan']:
                        lines.append(f"     - *\"{sm}\"*")
                else:
                    lines.append(f"   - **Catatan:** Selaras kuat dari profil kepakaran riset dosen.")
                lines.append("")
        else:
            lines.append("- *Dosen umum peminatan sistem dan komputasi.*")
            lines.append("")
            
        lines.append("#### 📚 Paper ArXiv Terkait (Sebagai Landasan SOTA 2025/2026):")
        for i, p in enumerate(matched_papers, 1):
            short_abs = str(p['abstract_or_summary'])[:200].replace('\n', ' ') + "..."
            lines.append(f"{i}. **[{p['title']}]({p['url_or_reference']})** ({p['year']})")
            lines.append(f"   - *Authors:* {p['authors']}")
            lines.append(f"   - *Core Engineering:* {short_abs}\n")
            
        lines.append("---\n")

    # Daftar Lengkap 72 Dosen
    lines.append("## 📋 Daftar Pemetaan Lengkap 72 Dosen STIS (KS, Statistika D-IV & D-III)")
    lines.append("")
    lines.append("| No | Nama Dosen | Prodi | Bimbingan Terdata | Rekomendasi Pilar Utama | Minat Penelitian |")
    lines.append("| :-: | :--- | :-: | :-: | :--- | :--- |")
    
    sorted_all_lecturers = sorted(lecturer_profiles, key=lambda x: x['max_score'], reverse=True)
    for i, doc in enumerate(sorted_all_lecturers, 1):
        clean_minat = doc['minat_raw'][:75] + "..." if len(doc['minat_raw']) > 75 else doc['minat_raw']
        if not clean_minat:
            clean_minat = "-"
        pilar_short = doc['primary_domain'].split('.')[0] if '.' in doc['primary_domain'] else doc['primary_domain'][:25]
        lines.append(f"| {i} | **{doc['display_name']}** | {doc['prodi'].upper()} | {doc['total_bimbingan_count']} judul | {pilar_short} | {clean_minat} |")
        
    lines.append("")
    lines.append("---")
    lines.append("## 🎯 Panduan Strategi Pengajuan Proposal:")
    lines.append("1. **Jika Menghadap Dosen Pakar Geospasial / Remote Sensing (Contoh: Dr. Eng. Arie Wahyu, Pak Waris, Bu Fitri):**")
    lines.append("   - **Fokus Anda:** Membangun *Data Engineering Pipeline (Multi-Source Data Fusion, Automated Tile Ingestion, Data Lakehouse)*.")
    lines.append("   - **Pesan ke Dosen:** *\"Saya merancang arsitektur pipeline otomatis untuk preprocessing dan ingestion datanya, agar model remote sensing dapat berjalan secara streaming/terjadwal.\"*")
    lines.append("2. **Jika Menghadap Dosen Pakar AI / NLP / Generative (Contoh: Prof. Setia Pramana, Dr. Eng. Lya Hulliyyatus):**")
    lines.append("   - **Fokus Anda:** Membangun *MLOps Inference Serving Engine, RAG Cache Middleware, atau Stream Interceptor*.")
    lines.append("   - **Pesan ke Dosen:** *\"Fokus penelitian saya pada optimalisasi serving pipeline, latensi throughput sistem, dan data lineage hasil inferensi AI.\"*")
    lines.append("3. **Jika Menghadap Dosen Pakar Pure SE / Software Quality (Contoh: Pak Yunarso Anang, Pak Farid Ridho, Bu Nori):**")
    lines.append("   - **Fokus Anda:** Pengujian kualitas sistem (*Automated Testbed, Security Hardening, Microservices Architecture*).")
    
    with open(OUTPUT_REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"[OK] Laporan rekomendasi terstruktur SE & Dosen berhasil disimpan di '{OUTPUT_REPORT_MD}'")

def main():
    df_unified, df_minat, df_bimbingan = load_data()
    print("[*] Menganalisis kecocokan profil 72 dosen terhadap 6 pilar SE/Data Engineering...")
    lecturer_profiles = analyze_lecturer_compatibility(df_minat, df_bimbingan)
    
    print("[*] Membuat CSV rekomendasi dosen...")
    build_lecturer_recommendations_csv(lecturer_profiles)
    
    print("[*] Membangun laporan Markdown komprehensif...")
    build_combined_report(df_unified, lecturer_profiles)
    print("[+] Selesai dengan sukses!")

if __name__ == "__main__":
    main()

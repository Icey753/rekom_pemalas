import json
import re
import pandas as pd
from pathlib import Path
from preprocess_skripsi import preprocess_all_datasets, assign_main_label
from preprocess_academic_papers import preprocess_academic_papers

def clean_text(text):
    if not text or pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def orchestrate_unified_dataset():
    print("="*70)
    print("MEMULAI ORKESTRASI DATASET RISET (LOKAL SKRIPSI + FOREIGN ARXIV)")
    print("="*70)

    # 1. Jalankan / Pastikan Preprocessing masing-masing dataset sudah dieksekusi
    print("\n[1/3] Memastikan dataset lokal skripsi ter-update...")
    preprocess_all_datasets()
    
    print("\n[2/3] Memastikan dataset arXiv academic papers ter-update...")
    preprocess_academic_papers()

    # 2. Baca kedua dataset bersih
    print("\n[3/3] Menggabungkan dan menyelaraskan skema (Unified Orchestration)...")
    skripsi_csv = Path("dataset_skripsi_lengkap.csv")
    arxiv_csv = Path("academic-papers-dataset/data/academic_papers_cleaned.csv")
    
    df_skripsi = pd.read_csv(skripsi_csv)
    df_arxiv = pd.read_csv(arxiv_csv)
    
    unified_records = []
    
    # -------------------------------------------------------------
    # Olah Dataset Lokal (Skripsi STIS / BPS)
    # -------------------------------------------------------------
    for _, row in df_skripsi.iterrows():
        paper_id = clean_text(row.get('id', ''))
        title = clean_text(row.get('title', ''))
        year = row.get('year')
        year = int(year) if pd.notna(year) else None
        authors = clean_text(row.get('author', ''))
        supervisor = clean_text(row.get('supervisor', ''))
        desc = clean_text(row.get('description', ''))
        readme = clean_text(row.get('readme_snippet', ''))
        
        # Gabungkan deskripsi dan readme sebagai konten abstrak lokal
        content_text = desc if desc else readme
        
        se_tags = clean_text(row.get('se_automation_tags', ''))
        ai_tags = clean_text(row.get('ai_analytics_tags', ''))
        sec_tags = clean_text(row.get('application_sector_tags', ''))
        all_tags = clean_text(row.get('all_tags', ''))
        
        # Tentukan disiplin utama berdasarkan main_label baru
        main_labels_raw = row.get('main_label', '')
        if pd.isna(main_labels_raw) or not main_labels_raw:
            main_labels_list = ["Software Engineering"]
        elif isinstance(main_labels_raw, str):
            main_labels_list = [m.strip() for m in main_labels_raw.split(';') if m.strip()]
        else:
            main_labels_list = ["Software Engineering"]

        sub_labels_raw = row.get('sub_labels', '')
        if pd.isna(sub_labels_raw) or not sub_labels_raw:
            sub_labels_str = ""
        elif isinstance(sub_labels_raw, str):
            sub_labels_str = sub_labels_raw
        else:
            sub_labels_str = str(sub_labels_raw)

        # Tentukan discipline display
        if "Data Science" in main_labels_list and "Software Engineering" in main_labels_list:
            discipline = "Data Science & Software Engineering"
        elif "Data Science" in main_labels_list:
            discipline = "Data Science"
        elif "Software Engineering" in main_labels_list:
            discipline = "Software Engineering"
        else:
            discipline = "Software Engineering"  # fallback
            
        unified_records.append({
            "id": paper_id,
            "origin": "local",  # Label: local vs foreign
            "source": clean_text(row.get('source', '')),
            "language": "id",
            "year": year,
            "title": title,
            "authors": authors,
            "supervisor": supervisor,
            "abstract_or_summary": content_text,
            # ── Label utama baru ──────────────────────────────────────────
            "main_label": "; ".join(main_labels_list),   # 'Data Science' / 'Software Engineering' / keduanya
            "sub_labels": sub_labels_str,                # sub-label detail
            # ── Backward-compat ───────────────────────────────────────────
            "discipline": discipline,
            "primary_category": ai_tags.split(';')[0].strip() if ai_tags else (se_tags.split(';')[0].strip() if se_tags else "Applied Computing"),
            "se_automation_tags": se_tags,
            "ai_analytics_tags": ai_tags,
            "application_sector_tags": sec_tags,
            "all_tags": all_tags,
            "url_or_reference": clean_text(row.get('raw_reference', '')),
            "search_corpus": f"[LOKAL - {year}] {title} | {authors} | Pembimbing: {supervisor} | Label: {'; '.join(main_labels_list)} | {content_text} | Tags: {all_tags}"
        })
        
    # -------------------------------------------------------------
    # Olah Dataset Global / Foreign (ArXiv Academic Papers)
    # -------------------------------------------------------------
    for _, row in df_arxiv.iterrows():
        paper_id = clean_text(row.get('paper_id', ''))
        title = clean_text(row.get('title', ''))
        year = row.get('year')
        year = int(year) if pd.notna(year) else None
        authors = clean_text(row.get('authors', ''))
        abstract = clean_text(row.get('abstract', ''))
        primary_cat_name = clean_text(row.get('primary_category_name', ''))
        primary_cat_code = clean_text(row.get('primary_category_code', ''))
        discipline = clean_text(row.get('discipline', ''))
        all_cat_names = clean_text(row.get('all_category_names', ''))
        all_cat_codes = clean_text(row.get('all_category_codes', ''))
        url = clean_text(row.get('url', ''))
        
        # Klasifikasikan ke tag SE / AI jika cocok
        se_tag = primary_cat_name if discipline == "Software Engineering & Systems" else ""
        ai_tag = primary_cat_name if discipline in ["Artificial Intelligence & Data Science", "Statistical Computing & Methodology"] else ""
        
        unified_records.append({
            "id": f"ARXIV_{paper_id}",
            "origin": "foreign",  # Label: local vs foreign
            "source": "arxiv",
            "language": "en",
            "year": year,
            "title": title,
            "authors": authors,
            "supervisor": "",
            "abstract_or_summary": abstract,
            # ── Label utama baru: assign via assign_main_label dari konten paper ─
            "main_label": discipline if discipline else "Software Engineering",
            "sub_labels": primary_cat_name,
            # ── Backward-compat ───────────────────────────────────────────────────
            "discipline": discipline,
            "primary_category": f"{primary_cat_code} - {primary_cat_name}",
            "se_automation_tags": se_tag,
            "ai_analytics_tags": ai_tag,
            "application_sector_tags": "Academic Research / Global",
            "all_tags": all_cat_names,
            "url_or_reference": url,
            "search_corpus": f"[FOREIGN - {year}] {title} | {primary_cat_name} | {discipline} | {abstract}"
        })

    # Konversi ke DataFrame Unified
    df_unified = pd.DataFrame(unified_records)
    
    # Simpan Hasil Orkestrasi
    out_csv = Path("dataset_unified_skripsi_dan_papers.csv")
    out_json = Path("dataset_unified_skripsi_dan_papers.json")
    
    df_unified.to_csv(out_csv, index=False, encoding='utf-8-sig')
    df_unified.to_json(out_json, orient='records', indent=2, force_ascii=False)
    
    print("\n" + "="*70)
    print("ORKESTRASI SELESAI!")
    print(f"Total Dataset Gabungan : {len(df_unified)} records")
    print(f"  - Lokal (Skripsi STIS/BPS) : {len(df_unified[df_unified['origin'] == 'local'])} records")
    print(f"  - Foreign (ArXiv Papers)   : {len(df_unified[df_unified['origin'] == 'foreign'])} records")
    print(f"Output CSV  : {out_csv.resolve()}")
    print(f"Output JSON : {out_json.resolve()}")
    print("="*70)

    print("\nDistribusi Berdasarkan Origin & Disiplin:")
    print(pd.crosstab(df_unified['origin'], df_unified['discipline']))

    print("\nDistribusi Label Utama (main_label):")
    print(df_unified['main_label'].value_counts())

if __name__ == '__main__':
    orchestrate_unified_dataset()

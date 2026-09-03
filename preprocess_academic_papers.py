import json
import re
import ast
import pandas as pd
from pathlib import Path

# Mapping Kode Kategori Resmi arXiv ke Nama Kategori Manusia & Rumpun Bidang
ARXIV_CATEGORY_MAP = {
    # Software Engineering, System, Architecture & DevOps
    "cs.SE": {"name": "Software Engineering", "discipline": "Software Engineering & Systems"},
    "cs.DC": {"name": "Distributed, Parallel & Cluster Computing", "discipline": "Software Engineering & Systems"},
    "cs.DB": {"name": "Databases & Data Management", "discipline": "Software Engineering & Systems"},
    "cs.OS": {"name": "Operating Systems", "discipline": "Software Engineering & Systems"},
    "cs.PL": {"name": "Programming Languages & Compilers", "discipline": "Software Engineering & Systems"},
    "cs.AR": {"name": "Hardware & Architecture", "discipline": "Software Engineering & Systems"},
    "cs.NI": {"name": "Networking and Internet Architecture", "discipline": "Software Engineering & Systems"},
    "cs.CR": {"name": "Cryptography and Security", "discipline": "Software Engineering & Systems"},
    "cs.PF": {"name": "Performance", "discipline": "Software Engineering & Systems"},
    
    # Human-Computer Interaction & Interfaces
    "cs.HC": {"name": "Human-Computer Interaction (UI/UX)", "discipline": "HCI & Information Systems"},
    "cs.CY": {"name": "Computers and Society", "discipline": "HCI & Information Systems"},
    "cs.DL": {"name": "Digital Libraries", "discipline": "HCI & Information Systems"},
    "cs.GR": {"name": "Graphics", "discipline": "HCI & Information Systems"},
    "cs.MM": {"name": "Multimedia", "discipline": "HCI & Information Systems"},
    
    # AI, NLP, Vision, IR & Robotics
    "cs.AI": {"name": "Artificial Intelligence", "discipline": "Artificial Intelligence & Data Science"},
    "cs.CL": {"name": "Computation and Language (NLP & LLMs)", "discipline": "Artificial Intelligence & Data Science"},
    "cs.CV": {"name": "Computer Vision and Pattern Recognition", "discipline": "Artificial Intelligence & Data Science"},
    "cs.LG": {"name": "Machine Learning (CS)", "discipline": "Artificial Intelligence & Data Science"},
    "cs.IR": {"name": "Information Retrieval & Web Mining", "discipline": "Artificial Intelligence & Data Science"},
    "cs.RO": {"name": "Robotics & Automation", "discipline": "Artificial Intelligence & Data Science"},
    "cs.NE": {"name": "Neural and Evolutionary Computing", "discipline": "Artificial Intelligence & Data Science"},
    "cs.MA": {"name": "Multiagent Systems", "discipline": "Artificial Intelligence & Data Science"},
    "cs.SI": {"name": "Social and Information Networks", "discipline": "Artificial Intelligence & Data Science"},
    "cs.SD": {"name": "Sound and Audio Processing", "discipline": "Artificial Intelligence & Data Science"},
    "cs.DS": {"name": "Data Structures and Algorithms", "discipline": "Theoretical CS & Math"},
    "cs.CC": {"name": "Computational Complexity", "discipline": "Theoretical CS & Math"},
    "cs.LO": {"name": "Logic in Computer Science", "discipline": "Theoretical CS & Math"},
    
    # Statistics & Applied Mathematics
    "stat.ML": {"name": "Machine Learning (Stats)", "discipline": "Statistical Computing & Methodology"},
    "stat.ME": {"name": "Statistical Methodology (SAE, Spasial, Bayes)", "discipline": "Statistical Computing & Methodology"},
    "stat.AP": {"name": "Applications of Statistics", "discipline": "Statistical Computing & Methodology"},
    "stat.CO": {"name": "Computation in Statistics", "discipline": "Statistical Computing & Methodology"},
    "stat.TH": {"name": "Statistics Theory", "discipline": "Statistical Computing & Methodology"},
    "math.ST": {"name": "Statistical Theory", "discipline": "Statistical Computing & Methodology"},
    "math.PR": {"name": "Probability", "discipline": "Statistical Computing & Methodology"},
    "math.OC": {"name": "Optimization and Control", "discipline": "Statistical Computing & Methodology"},
    "math.NA": {"name": "Numerical Analysis", "discipline": "Statistical Computing & Methodology"},
    
    # Economics & Quantitative Finance
    "econ.EM": {"name": "Econometrics", "discipline": "Economics & Quantitative Analysis"},
    "econ.GN": {"name": "General Economics", "discipline": "Economics & Quantitative Analysis"},
    "econ.TH": {"name": "Theoretical Economics", "discipline": "Economics & Quantitative Analysis"},
    "q-fin.ST": {"name": "Statistical Finance", "discipline": "Economics & Quantitative Analysis"},
    "q-fin.CP": {"name": "Computational Finance", "discipline": "Economics & Quantitative Analysis"},
    
    # Electrical Eng & Systems
    "eess.IV": {"name": "Image and Video Processing", "discipline": "Engineering & Applied Sciences"},
    "eess.SP": {"name": "Signal Processing", "discipline": "Engineering & Applied Sciences"},
    "eess.SY": {"name": "Systems and Control", "discipline": "Engineering & Applied Sciences"},
    "eess.AS": {"name": "Audio and Speech Processing", "discipline": "Engineering & Applied Sciences"},
}

def clean_text(text):
    """Membersihkan newline, tab, dan spasi berlebih."""
    if not text or pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_categories(cat_str):
    """
    Mengubah format categories seperti \"['cs.AI' 'cs.CL']\" atau \"['cs.AI', 'cs.CL']\" menjadi python list.
    """
    if not cat_str or pd.isna(cat_str):
        return []
    # Ekstrak semua token berformat petik tunggal/ganda
    matches = re.findall(r"['\"]([^'\"]+)['\"]", str(cat_str))
    if matches:
        return [m.strip() for m in matches if m.strip()]
    
    cleaned = re.sub(r"[\[\]\'\"]", " ", str(cat_str))
    tokens = re.split(r'[\s,]+', cleaned)
    return [t.strip() for t in tokens if t.strip()]

def parse_authors(authors_str):
    """Mengubah format array string penulis menjadi list nama bersih."""
    if not authors_str or pd.isna(authors_str):
        return []
    matches = re.findall(r"['\"]([^'\"]+)['\"]", str(authors_str))
    if matches:
        return [m.strip() for m in matches if m.strip()]
    cleaned = re.sub(r"[\[\]\'\"]", "", str(authors_str))
    return [a.strip() for a in cleaned.split(',') if a.strip()]

def preprocess_academic_papers():
    raw_csv = Path("academic-papers-dataset/data/academic_papers.csv")
    if not raw_csv.exists():
        print(f"Error: File {raw_csv} tidak ditemukan.")
        return

    print("Membaca dan memproses dataset academic_papers.csv...")
    df = pd.read_csv(raw_csv)
    
    processed_records = []
    
    for idx, row in df.iterrows():
        arxiv_id = clean_text(row.get('arxiv_id', ''))
        title = clean_text(row.get('title', ''))
        abstract = clean_text(row.get('abstract', ''))
        authors_list = parse_authors(row.get('authors', ''))
        categories_list = parse_categories(row.get('categories', ''))
        primary_cat = clean_text(row.get('primary_category', ''))
        published = clean_text(row.get('published', ''))
        url = clean_text(row.get('url', ''))
        doi = clean_text(row.get('doi', ''))
        
        # Ekstrak tahun publish
        year_match = re.search(r'(\d{4})', published)
        year = int(year_match.group(1)) if year_match else None
        
        # Mapping primary category info
        cat_info = ARXIV_CATEGORY_MAP.get(primary_cat, {
            "name": primary_cat,
            "discipline": "Other / Interdisciplinary"
        })
        primary_cat_name = cat_info["name"]
        discipline = cat_info["discipline"]
        
        # List semua kategori dengan nama keterangannya
        all_cat_names = [ARXIV_CATEGORY_MAP.get(c, {}).get("name", c) for c in categories_list]
        
        # Text gabungan untuk perbandingan / pencarian kecocokan ide judul
        search_text = f"Title: {title} | Primary: {primary_cat} ({primary_cat_name}) | Discipline: {discipline} | Abstract: {abstract}"
        
        processed_records.append({
            "paper_id": arxiv_id,
            "title": title,
            "year": year,
            "primary_category_code": primary_cat,
            "primary_category_name": primary_cat_name,
            "discipline": discipline,
            "all_category_codes": categories_list,
            "all_category_names": all_cat_names,
            "abstract": abstract,
            "authors": authors_list,
            "url": url,
            "doi": doi,
            "search_text": search_text
        })
        
    df_clean = pd.DataFrame(processed_records)
    
    # Deduplikasi judul jika ada
    df_clean.drop_duplicates(subset=['title'], inplace=True)
    
    # Simpan dalam format CSV dan JSON
    out_dir = Path("academic-papers-dataset/data")
    out_csv = out_dir / "academic_papers_cleaned.csv"
    out_json = out_dir / "academic_papers_cleaned.json"
    
    # Untuk CSV simpan kolom array sebagai string semicolon
    df_csv = df_clean.copy()
    df_csv['all_category_codes'] = df_csv['all_category_codes'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    df_csv['all_category_names'] = df_csv['all_category_names'].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
    df_csv['authors'] = df_csv['authors'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    
    df_csv.to_csv(out_csv, index=False, encoding='utf-8-sig')
    df_clean.to_json(out_json, orient='records', indent=2, force_ascii=False)
    
    print("="*60)
    print("Preprocessing academic_papers.csv Selesai!")
    print(f"Total Papers Terproses: {len(df_clean)}")
    print(f"Output CSV : {out_csv.resolve()}")
    print(f"Output JSON: {out_json.resolve()}")
    print("="*60)
    
    print("\nDistribusi Berdasarkan Rumpun Disiplin (Discipline):")
    print(df_clean['discipline'].value_counts())
    
    print("\nTop 10 Kategori Utama (Primary Category):")
    print(df_clean['primary_category_name'].value_counts().head(10))

if __name__ == '__main__':
    preprocess_academic_papers()

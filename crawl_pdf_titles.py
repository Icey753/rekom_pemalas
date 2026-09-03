import os
import re
import json
import pdfplumber
import pandas as pd

def crawl_executive_summary_titles(
    pdf_path: str = "Executive Summary - DIV Komputasi Statistik.pdf",
    output_json: str = "hasil_executive_summary_titles.json",
    output_csv: str = "hasil_executive_summary_titles.csv",
    start_page: int = 3,
    end_page: int = 17  # Halaman 3-17 adalah daftar isi unik berdasarkan nama mahasiswa
):
    """
    Mengekstrak judul, penulis (mahasiswa), pembimbing (dosen), dan rentang halaman dokumen
    dari daftar isi Executive Summary bagian mahasiswa (Halaman 3 sampai 17) menggunakan pdfplumber.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File PDF '{pdf_path}' tidak ditemukan.")

    print(f"Membuka file: {pdf_path}")
    print(f"Mengekstrak daftar isi mahasiswa dari halaman {start_page} hingga {end_page}...")

    full_lines = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pdf_pages = len(pdf.pages)
        max_end = min(end_page, total_pdf_pages)
        
        for p in range(start_page - 1, max_end):
            text = pdf.pages[p].extract_text()
            if not text:
                continue
            
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            for l in lines:
                # Abaikan baris header / judul daftar isi dan nomor romawi halaman
                if l in [
                    "DAFTAR ISI",
                    "(Diurutkan Berdasarkan Nama Mahasiswa)",
                    "(Diurutkan Berdasarkan Nama Pembimbing)",
                    "(Diurutkan Berdasarkan Nama Dosen)"
                ]:
                    continue
                if re.match(r"^[ivxlcdm]+$", l.lower()):
                    continue
                
                full_lines.append((p + 1, l))

    raw_entries = []
    current_entry = None

    for page_num, line in full_lines:
        # Cek apakah baris merupakan nama penulis & pembimbing (Format: Penulis & Pembimbing)
        # Menghindari false positive pada judul tertentu (misal: DeLone & McLean)
        if " & " in line and "DeLone & McLean" not in line and not re.search(r"\d+\s*-\s*\d+", line):
            if current_entry:
                raw_entries.append(current_entry)
            current_entry = {
                "raw_author_advisor": line,
                "halaman_dokumen": None,
                "title_lines": [],
                "halaman_pdf_daftar_isi": page_num
            }
        else:
            # Cari jika ada pola rentang halaman (misal: "1 - 10" atau "1221 - 1230")
            match = re.search(r"(\d+\s*-\s*\d+)", line)
            if match:
                page_str = match.group(1)
                clean_line = line.replace(page_str, "").strip()
                if current_entry:
                    current_entry["halaman_dokumen"] = page_str
                    if clean_line:
                        current_entry["title_lines"].append(clean_line)
            else:
                if current_entry:
                    current_entry["title_lines"].append(line)

    if current_entry:
        raw_entries.append(current_entry)

    # Bersihkan dan format entri
    extracted_data = []
    for idx, item in enumerate(raw_entries, 1):
        parts = item["raw_author_advisor"].split(" & ")
        penulis = parts[0].strip()
        pembimbing = parts[1].strip() if len(parts) > 1 else ""
        judul = " ".join(item["title_lines"]).strip()
        
        extracted_data.append({
            "no": idx,
            "penulis": penulis,
            "pembimbing": pembimbing,
            "judul": judul,
            "halaman_dokumen": item["halaman_dokumen"],
            "halaman_pdf_daftar_isi": item["halaman_pdf_daftar_isi"]
        })

    print(f"Berhasil mengekstrak {len(extracted_data)} entri skripsi unik (tanpa duplikasi)!")

    # Simpan ke JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    print(f"Hasil disimpan ke JSON: {output_json}")

    # Simpan ke CSV
    df = pd.DataFrame(extracted_data)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Hasil disimpan ke CSV: {output_csv}")

    return extracted_data

if __name__ == "__main__":
    data = crawl_executive_summary_titles()
    print("\n--- Ringkasan Data ---")
    print(f"Total skripsi unik: {len(data)}")
    print(f"Contoh data pertama : [{data[0]['penulis']}] - {data[0]['judul'][:60]}...")
    print(f"Contoh data terakhir: [{data[-1]['penulis']}] - {data[-1]['judul'][:60]}...")

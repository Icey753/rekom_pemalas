"""
Isi field 'description' yang kosong pakai paragraf pertama dari 'readme'
yang udah ada di file JSON hasil scraping. Gak perlu buka browser lagi,
gak nyentuh data yang description-nya udah keisi.

Cara pakai:
    python fill_empty_description.py --in hasil_2017.json --out hasil_2017.json
"""

import argparse
import json
import re


GITLAB_BOILERPLATE_MARKERS = [
    "to make it easy for you to get started",
    "recommended next steps",
    "add files using the command line",
    "get started with gitlab",
    "readme.md is where you can write a long description",
]


def is_gitlab_default_readme(readme_text: str) -> bool:
    """Deteksi README yang masih template default GitLab (belum diisi mahasiswa)."""
    lower = readme_text.lower()
    return any(marker in lower for marker in GITLAB_BOILERPLATE_MARKERS)


def extract_first_paragraph(readme_text: str) -> str:
    """Ambil kalimat/paragraf pertama yang informatif dari README (skip heading/judul)."""
    if not readme_text:
        return ""

    if is_gitlab_default_readme(readme_text):
        return ""  # README masih boilerplate, gak ada konten asli buat diambil

    lines = [l.strip() for l in readme_text.split("\n") if l.strip()]

    # Skip baris yang keliatan kayak heading (biasanya judul singkat, huruf kapital
    # di awal tiap kata, atau baris pertama yang cuma duplikat judul project)
    for line in lines:
        # Heuristik simpel: heading GitLab README biasanya pendek (<60 karakter)
        # dan gak diakhiri titik. Paragraf isi biasanya lebih panjang.
        if len(line) > 60 or (len(line) > 20 and line.endswith((".", "!", "?"))):
            # Potong sampai kalimat pertama aja biar ringkas (opsional)
            return line

    # Fallback: kalau gak ketemu yang match heuristik, pakai baris terpanjang
    if lines:
        return max(lines, key=len)
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", required=True, help="file JSON hasil scraping")
    parser.add_argument("--out", dest="outfile", required=True, help="file output (boleh sama dengan --in)")
    args = parser.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    filled_count = 0
    for entry in data:
        desc = entry.get("description", "").strip()
        if not desc:
            readme = entry.get("readme", "")
            new_desc = extract_first_paragraph(readme)
            if new_desc:
                entry["description"] = new_desc
                filled_count += 1
                print(f"  Diisi: {entry.get('title', entry.get('project_path'))}")

    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSelesai. {filled_count} description kosong berhasil diisi dari README.")
    print(f"Sisanya (README juga kosong/gak ada teks) tetap dibiarkan kosong.")


if __name__ == "__main__":
    main()
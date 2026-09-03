"""
Scraper Minat Penelitian Dosen - Politeknik Statistika STIS
=============================================================

Ambil nama dosen + minat penelitian dari stis.ac.id/dosen/{prodi}
Default prodi: ks (Komputasi Statistik). Ganti PRODI kalau mau prodi lain
(cek slug-nya di URL, misal stis.ac.id/dosen/st untuk Statistika).

Cara pakai:
    python scrape_minat_dosen.py
    python scrape_minat_dosen.py --prodi ks --output minat_dosen_ks.csv

Output: CSV dengan kolom: nama, kode, minat_penelitian
(minat_penelitian berupa list item digabung dengan " | ")
"""

import argparse
import csv
import re
import time
import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://stis.ac.id"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def get_dosen_list(prodi: str):
    """Ambil daftar (nama, kode, url_detail) dari halaman list dosen."""
    url = f"{BASE_URL}/dosen/{prodi}"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    dosen_list = []
    for a in soup.select("a[href*='/detail/']"):
        href = a.get("href", "")
        match = re.search(r"/detail/([A-Za-z0-9]+)", href)
        if not match:
            continue
        kode = match.group(1)
        nama = a.get_text(strip=True).replace("Lihat Profil ", "").strip()
        detail_url = href if href.startswith("http") else BASE_URL + href
        dosen_list.append({"nama": nama, "kode": kode, "url": detail_url})

    # dedupe (kadang ada duplikat href kalau gambar & teks sama-sama <a>)
    seen = set()
    unique_list = []
    for d in dosen_list:
        if d["kode"] not in seen:
            seen.add(d["kode"])
            unique_list.append(d)
    return unique_list


def get_minat_penelitian(detail_url: str):
    """Ambil list minat penelitian dari halaman detail dosen."""
    resp = requests.get(detail_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Cari heading yang teksnya mengandung "Minat Penelitian"
    target_heading = None
    for tag in soup.find_all(re.compile("^h[1-6]$")):
        if "minat penelitian" in tag.get_text(strip=True).lower():
            target_heading = tag
            break

    if target_heading is None:
        return []

    # Ambil elemen <ul>/<ol> pertama setelah heading tsb
    minat = []
    for sibling in target_heading.find_next_siblings():
        if sibling.name in ("ul", "ol"):
            minat = [li.get_text(strip=True) for li in sibling.find_all("li")]
            break
        # kalau ketemu heading lain duluan sebelum nemu list, berhenti (berarti section kosong)
        if re.match(r"^h[1-6]$", sibling.name or ""):
            break

    return minat


def main():
    parser = argparse.ArgumentParser(description="Scrape minat penelitian dosen STIS")
    parser.add_argument("--prodi", default="all", help="Slug prodi: ks (D-IV KS), s (D-IV Statistika), d3 (D-III Statistika), atau all (default: all)")
    parser.add_argument("--output", default="minat_dosen.csv", help="Nama file CSV output")
    parser.add_argument("--delay", type=float, default=0.4, help="Delay antar request (detik), default 0.4")
    args = parser.parse_args()

    prodi_list = ["ks", "s", "d3"] if args.prodi.lower() == "all" else [args.prodi.lower()]
    
    all_dosen = []
    seen_kode = set()

    for prodi in prodi_list:
        print(f"[1/2] Mengambil daftar dosen dari /dosen/{prodi} ...")
        try:
            d_list = get_dosen_list(prodi)
            print(f"      Ditemukan {len(d_list)} dosen di prodi '{prodi}'.")
            for d in d_list:
                if d["kode"] not in seen_kode:
                    seen_kode.add(d["kode"])
                    d["prodi"] = prodi
                    all_dosen.append(d)
        except Exception as e:
            print(f"   ! Gagal mengambil list dosen prodi {prodi}: {e}")

    if not all_dosen:
        print("Tidak ada dosen ditemukan. Cek slug prodi atau struktur halaman berubah.")
        sys.exit(1)

    print(f"\n[2/2] Mengambil minat penelitian untuk total {len(all_dosen)} dosen unik ...")
    rows = []
    for i, d in enumerate(all_dosen, 1):
        try:
            minat = get_minat_penelitian(d["url"])
        except requests.RequestException as e:
            print(f"   ! Gagal ambil {d['nama']} ({d['kode']}): {e}")
            minat = []
        minat_str = " | ".join(minat) if minat else ""
        rows.append({
            "nama": d["nama"], 
            "kode": d["kode"], 
            "prodi": d.get("prodi", ""),
            "minat_penelitian": minat_str
        })
        print(f"   ({i}/{len(all_dosen)}) [{d.get('prodi', '')}] {d['nama']}: {len(minat)} minat")
        time.sleep(args.delay)

    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["nama", "kode", "prodi", "minat_penelitian"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSelesai! Total {len(rows)} dosen dari prodi {prodi_list} tersimpan di: {args.output}")


if __name__ == "__main__":
    main()
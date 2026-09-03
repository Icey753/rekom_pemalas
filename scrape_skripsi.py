"""
Scraper judul + README skripsi KS dari git.stis.ac.id/ks
Pakai Playwright (server-rendered page, tapi ada elemen yg lazy-load via JS)

Cara pakai (satu grup):
    python scrape_skripsi.py --group ks/skripsi2021 --out hasil_2021.json

Cara pakai (banyak grup/tahun sekaligus):
    python scrape_skripsi.py --groups ks/skripsi2017 ks/skripsi2018 ks/skripsi2019 ks/skripsi2020 ks/skripsi2021 --out hasil_semua.json

Atau langsung semua tahun 2017-2021 pakai shortcut:
    python scrape_skripsi.py --years 2017 2018 2019 2020 2021 --out hasil_semua.json
"""

import argparse
import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://git.stis.ac.id"


def get_projects_in_group(page, group_path: str) -> list[dict]:
    """
    Ambil daftar project (repo) di dalam satu grup, misal 'ks/skripsi2021'.
    Return list of dict {path, title, description}.

    Handle dua hal:
    1. Pagination client-side (tombol Next href="#", update via JS) — loop klik
       sampai tombol Next hilang/disabled.
    2. Nested subgroup (grup di dalam grup) — rekursif masuk ke subgroup itu.
    """
    url = f"{BASE_URL}/{group_path}"
    page.goto(url, wait_until="networkidle")

    projects = []
    seen_paths = set()  # jaga2 dedup kalau ada row kepencet dobel

    page_num = 1
    while True:
        # Tunggu row-row muncul di halaman saat ini
        page.wait_for_selector("li[data-testid^='group-overview-item']", timeout=10000)
        rows = page.locator("li[data-testid^='group-overview-item']").all()
        print(f"    halaman {page_num}: {len(rows)} row")

        for row in rows:
            link = row.locator("a[data-testid='group-name']").first
            href = link.get_attribute("href")
            title = link.inner_text().strip()
            item_type = row.get_attribute("itemtype") or ""

            desc_el = row.locator("[data-testid='group-description']")
            description = desc_el.inner_text().strip() if desc_el.count() > 0 else ""

            if not href:
                continue
            path = href.lstrip("/")

            if path in seen_paths:
                continue
            seen_paths.add(path)

            if "SoftwareSourceCode" in item_type:
                projects.append({"path": path, "title": title, "description": description})
            else:
                print(f"    -> nemu subgroup: {path}, masuk rekursif...")
                projects.extend(get_projects_in_group(page, path))

        # Cek tombol Next — kalau ada dan aktif, klik & lanjut ke halaman berikutnya
        next_btn = page.locator("[data-testid='gl-pagination-next']")
        if next_btn.count() == 0:
            break  # gak ada tombol next sama sekali -> cuma 1 halaman

        # Cek apakah tombol Next dalam kondisi disabled (biasanya parent <li> dapat class "disabled")
        parent_li = next_btn.locator("xpath=ancestor::li[@data-testid='gl-pagination-li']").first
        is_disabled = "disabled" in (parent_li.get_attribute("class") or "")
        if is_disabled:
            break  # udah di halaman terakhir

        next_btn.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)  # jaga2 extra buat render JS selesai
        page_num += 1

    return projects


def get_title_and_readme(page, project_path: str) -> dict:
    """Buka satu project, ambil README (rendered HTML -> text). Judul diambil dari caller (list grup)."""
    url = f"{BASE_URL}/{project_path}"
    page.goto(url, wait_until="networkidle")

    # README di GitLab instance ini dirender di dalam div.project-show-wiki -> div.md
    readme_selectors = [".project-show-wiki .md", "div.md", "article.file-content", "#readme", ".readme-holder"]
    readme_text = ""
    for sel in readme_selectors:
        el = page.locator(sel)
        if el.count() > 0:
            readme_text = el.first.inner_text().strip()
            if readme_text:
                break

    return {
        "project_path": project_path,
        "title": project_path.split("/")[-1],  # fallback, akan ditimpa caller kalau ada
        "readme": readme_text,
        "url": url,
    }


def main():
    parser = argparse.ArgumentParser()
    group_args = parser.add_mutually_exclusive_group(required=True)
    group_args.add_argument("--group", help="satu grup, contoh: ks/skripsi2021")
    group_args.add_argument("--groups", nargs="+", help="banyak grup sekaligus, pisah spasi")
    group_args.add_argument("--years", nargs="+", type=int,
                             help="shortcut: --years 2017 2018 2019 -> otomatis jadi ks/skripsiTAHUN")
    parser.add_argument("--out", required=True, help="path output json (gabungan semua grup)")
    parser.add_argument("--delay", type=float, default=1.0, help="delay antar request (detik)")
    args = parser.parse_args()

    # Tentuin daftar grup yang mau di-scrape
    if args.group:
        groups = [args.group]
    elif args.groups:
        groups = args.groups
    else:  # args.years
        groups = [f"ks/skripsi{y}" for y in args.years]

    all_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for group_path in groups:
            print(f"\n=== Grup: {group_path} ===")
            try:
                projects = get_projects_in_group(page, group_path)
            except Exception as e:
                print(f"  GAGAL buka grup {group_path} -> {e}")
                continue

            print(f"Ketemu {len(projects)} project di grup {group_path}")

            for proj in projects:
                path = proj["path"]
                try:
                    data = get_title_and_readme(page, path)
                    data["title"] = proj["title"] or data["title"]  # judul dari list grup lebih bersih
                    data["description"] = proj["description"]
                    data["group"] = group_path  # biar tau ini dari tahun/grup mana
                    all_results.append(data)
                    print(f"  OK: {data['title']}")
                except Exception as e:
                    print(f"  GAGAL: {path} -> {e}")
                time.sleep(args.delay)  # sopan ke server, hormatin crawl-delay

        browser.close()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nSelesai. Total {len(all_results)} project dari {len(groups)} grup disimpan ke {args.out}")


if __name__ == "__main__":
    main()
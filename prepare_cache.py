# -*- coding: utf-8 -*-
"""Generate cache JSON dari Excel untuk deploy Vercel (hindari timeout preprocessing)."""

from search_engine import get_engine, EXCEL_PATH, CACHE_PATH


def main():
    if not EXCEL_PATH.exists():
        print(f"ERROR: File tidak ditemukan -> {EXCEL_PATH}")
        print("Letakkan hasil_scraping_kompas.xlsx di folder data/ terlebih dahulu.")
        return 1

    print("Memproses data berita (stemming + stopword)...")
    engine = get_engine()
    engine.load()
    engine.save_cache()
    print(f"Cache tersimpan -> {CACHE_PATH}")
    print(f"Total artikel: {engine.total_articles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

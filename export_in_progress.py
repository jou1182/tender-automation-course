# -*- coding: utf-8 -*-
"""
Al-Rawaf Tender Exporter - Cookie Edition
=========================================
Uses session cookies extracted from local Chrome to bypass login.
"""
import os
import sys
import time
import json
import shutil
import logging
import requests
from pathlib import Path

logger = logging.getLogger("Exporter")

# ── Paths ──────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).parent.resolve()
DOWNLOAD_DIR = ROOT_DIR / "output"
ARCHIVE_DIR  = DOWNLOAD_DIR / "archive"
OUT_XLSX     = DOWNLOAD_DIR / "in_progress_tenders.xlsx"
STATUS_FILE  = DOWNLOAD_DIR / "export_status.txt"
COOKIES_FILE = DOWNLOAD_DIR / "portal_cookies.json"

config_path = ROOT_DIR / "selectors.json"
if config_path.exists():
    config = json.loads(config_path.read_text(encoding="utf-8"))
    BASE_URL = config.get("portal_url", "https://your-portal.example.com")
    EXPORT_URL = BASE_URL + config.get("export_path", "/ar/tendering/export_to_excel_in_progress_tender/")
else:
    BASE_URL   = "https://your-portal.example.com"
    EXPORT_URL = BASE_URL + "/ar/tendering/export_to_excel_in_progress_tender/"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def ensure_dirs():
    for d in (DOWNLOAD_DIR, ARCHIVE_DIR):
        d.mkdir(parents=True, exist_ok=True)

def download_via_cookies() -> bool:
    if not COOKIES_FILE.exists():
        logger.error(f"Cookies file not found at: {COOKIES_FILE}")
        return False

    session = requests.Session()
    try:
        cookies_data = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        for cookie in cookies_data:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', '.example.com'))
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        return False

    logger.info("📡 Attempting download using provided session cookies...")
    try:
        resp = session.get(EXPORT_URL, headers=HEADERS, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 5000:
            ts = time.strftime("%Y-%m-%d_%H%M")
            archive = ARCHIVE_DIR / f"in_progress_tenders_{ts}.xlsx"
            archive.write_bytes(resp.content)
            if OUT_XLSX.exists(): OUT_XLSX.unlink()
            shutil.copy(str(archive), str(OUT_XLSX))
            logger.info(f"✅ Success! File saved: {OUT_XLSX.name}")
            return True
        else:
            logger.error(f"❌ Download failed. Status: {resp.status_code}, Size: {len(resp.content)} bytes")
            if resp.status_code == 403:
                logger.error("Session expired. Please run 'Update_Server_Session.bat' on your Desktop.")
            return False
    except Exception as e:
        logger.error(f"Network error: {e}")
        return False

def main():
    ensure_dirs()
    ok = download_via_cookies()
    STATUS_FILE.write_text("success" if ok else "failed", encoding="utf-8")
    return ok

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    sys.exit(0 if main() else 1)

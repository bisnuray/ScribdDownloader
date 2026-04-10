"""
Author: Bisnu Ray
https://t.me/itsSmartDev
"""

import re
import json
import requests

COOKIE_FILE = "cookie.json"

def load_cookies(file_path: str = COOKIE_FILE) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {c["name"]: c["value"] for c in raw if "name" in c and "value" in c}
    raise ValueError("Unsupported cookie format. Must be a dict or list of {name, value}.")


def extract_info(data: dict) -> dict:
    doc = data.get("document", {})
    return {
        "title": doc.get("title", "N/A"),
        "access_key": doc.get("access_key", "N/A"),
        "author_name": doc.get("author", {}).get("name", "N/A"),
        "receipt_url": data.get("receipt_url", "N/A"),
    }


def parse_document_id(url: str) -> str | None:
    match = re.search(r"scribd\.com/(?:document|doc|presentation)/(\d+)", url)
    return match.group(1) if match else None


def get_download_link(scribd_url: str, cookie_file: str = COOKIE_FILE) -> dict:
    doc_id = parse_document_id(scribd_url)
    if not doc_id:
        return {"error": "Invalid Scribd URL. Must contain /document/, /doc/, or /presentation/."}

    cookies = load_cookies(cookie_file)
    session = requests.Session()
    session.cookies.update(cookies)

    url1 = f"https://www.scribd.com/doc-page/download-receipt-modal-props/{doc_id}"
    print(f"[1] GET {url1}")
    r1 = session.get(url1)
    r1.raise_for_status()
    info = extract_info(r1.json())
    print(f'    Title      : {info["title"]}')
    print(f'    Author     : {info["author_name"]}')
    print(f'    Access Key : {info["access_key"]}')
    print(f'    Receipt URL: {info["receipt_url"]}')

    url2 = f'https://www.scribd.com/document_downloads/{doc_id}/?secret_password={info["access_key"]}&extension=pdf'
    print(f"\n[2] GET {url2}")
    r2 = session.get(url2, allow_redirects=False)
    print(f"    Status : {r2.status_code}")

    if r2.status_code not in (301, 302):
        return {"error": f"Expected redirect, got {r2.status_code}", "body": r2.text[:300]}

    redirect1 = r2.headers.get("Location")
    if not redirect1:
        return {"error": "No Location header in step-2 response."}
    print(f"    Redirect → {redirect1}")

    print(f"\n[3] GET {redirect1}")
    r3 = session.get(redirect1, allow_redirects=False)
    print(f"    Status : {r3.status_code}")

    if r3.status_code not in (301, 302):
        print("    (No further redirect — treating this as the final URL)")
        return {**info, "download_url": redirect1, "doc_id": doc_id}

    final_url = r3.headers.get("Location")
    if not final_url:
        return {"error": "No Location header in step-3 response."}
    print(f"    Redirect → {final_url}")

    return {**info, "download_url": final_url, "doc_id": doc_id}


if __name__ == "__main__":
    scribd_url = input("Enter Scribd URL: ").strip()

    print("\n" + "─" * 60)
    try:
        result = get_download_link(scribd_url)
        print("\n" + "─" * 60)
        if "error" in result:
            print(f'[✗] Error: {result["error"]}')
            if "body" in result:
                print(f'    Response body preview:\n{result["body"]}')
        else:
            print("[✓] Done!")
            print(f'    Title       : {result["title"]}')
            print(f'    Author      : {result["author_name"]}')
            print(f'    Receipt URL : {result["receipt_url"]}')
            print(f'    Download URL: {result["download_url"]}')
    except requests.HTTPError as e:
        print(f"[✗] HTTP error: {e}")
    except FileNotFoundError:
        print(f"[✗] Cookie file not found: {COOKIE_FILE}")
    except Exception as e:
        print(f"[✗] Unexpected error: {e}")
    print("─" * 60)

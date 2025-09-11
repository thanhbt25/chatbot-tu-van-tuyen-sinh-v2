import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://diemthi.vnexpress.net/index/detail/sbd/{sbd}/year/{year}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_scores(sbd: str, year: int = 2025):
    url = BASE_URL.format(sbd=sbd, year=year)
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class": "e-table"})
    if not table:
        return None

    scores = {"sbd": sbd}
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            mon = cols[0].get_text(strip=True)
            diem = cols[1].get_text(strip=True)
            scores[mon] = diem
    return scores

def save_to_csv(results, filename="diemthi_2025.csv"):
    all_subjects = set()
    for r in results:
        all_subjects.update(r.keys())
    all_subjects.discard("sbd")
    fieldnames = ["sbd"] + sorted(all_subjects)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

if __name__ == "__main__":
    results = []
    year = 2025
    max_empty = 50   # số SBD liên tiếp không có dữ liệu => coi như hết cụm
    cluster = 1

    while cluster <= 34:  # giả định cụm từ 01 đến 34
        empty_count = 0
        sbd_number = 1
        print(f"=== Bắt đầu quét cụm {cluster:02d} ===")

        while empty_count < max_empty:
            sbd = f"{cluster:02d}{sbd_number:06d}"
            print(f"Đang lấy {sbd} ...", end=" ")
            data = get_scores(sbd, year)
            if data:
                print("✅ Có dữ liệu")
                results.append(data)
                empty_count = 0  # reset khi có dữ liệu
            else:
                print("❌ Không có")
                empty_count += 1

            sbd_number += 1
            time.sleep(0.5)  # nghỉ nửa giây để tránh bị chặn

        print(f"--- Hết cụm {cluster:02d}, chuyển sang cụm tiếp theo ---")
        cluster += 1

    if results:
        save_to_csv(results)
        print(f"✅ Đã lưu {len(results)} thí sinh vào diemthi_2025.csv")
    else:
        print("❌ Không có dữ liệu nào.")

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re

# Cấu hình Selenium và ChromeDriver
chrome_options = Options()
chrome_options.add_argument("--ignore-ssl-errors=true")
chrome_options.add_argument("--allow-insecure-localhost")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def read_school_links():
    with open("danh_sach_truong.txt", "r", encoding="utf-8") as f:
        schools = []
        for line in f:
            if line.strip():
                try:
                    name, link = line.strip().rsplit(", ", 1)
                    schools.append({"name": name, "link": link})
                except ValueError:
                    print(f"Bỏ qua dòng không đúng định dạng: {line.strip()}")
        return schools


def get_year_button(driver, year):
    """Tìm và click nút chọn năm, xử lý trường hợp bị che phủ."""
    try:
        # Chờ nút dropdown "select_year" xuất hiện và có thể click được
        dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span#select2-select_year-container"))
        )
        dropdown.click()
        time.sleep(1)

        # Chờ nút chọn năm cụ thể xuất hiện và có thể click được
        year_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[text()='Năm {year}']"))
        )
        
        # Thử click bình thường, nếu không được thì dùng JavaScript click
        try:
            year_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", year_button)
        
        time.sleep(2)
        
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Lỗi khi tìm hoặc click nút năm {year}: {e}")
        raise

def scrape_benchmarks_table(soup, school_name, school_code, year):
    """Trích xuất dữ liệu từ bảng điểm chuẩn"""
    benchmarks = []
    rows = soup.select("tr.university__benchmark")
    for row in rows:
        try:
            cells = row.select("td")
            major_name_tag = cells[1].select_one("strong a")
            major_name = major_name_tag.text.strip() if major_name_tag else ""
            major_code_tag = cells[1].select_one("span:last-child")
            major_code = major_code_tag.text.strip() if major_code_tag else ""

            score_tag = cells[2].select_one("span")
            score = score_tag.text.strip() if score_tag else ""

            subjects_tags = cells[3].select("a")
            subjects = ", ".join([tag.text.strip() for tag in subjects_tags]) if subjects_tags else ""

            tuition = cells[4].text.strip()
            notes = cells[5].text.strip()

            benchmarks.append({
                "Tên trường": school_name,
                "Mã trường": school_code,
                "Năm": year,
                "Tên ngành": major_name,
                "Mã ngành": major_code,
                "Điểm chuẩn": score,
                "Tổ hợp môn": subjects,
                "Học phí (VNĐ)": tuition,
                "Ghi chú": notes
            })
        except IndexError:
            continue
    return benchmarks

def save_to_csv(data, filename="diem_chuan_dai_hoc.csv"):
    """Lưu dữ liệu vào file CSV"""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n--- Đã lưu dữ liệu vào file: {filename} ---")
    else:
        print("\n--- Không có dữ liệu để lưu ---")

def scrape_all_benchmarks():
    """Chức năng chính để cào dữ liệu điểm chuẩn"""
    schools_to_scrape = read_school_links()
    if not schools_to_scrape:
        print("Không tìm thấy danh sách trường để cào. Vui lòng kiểm tra file 'danh_sach_truong.txt'.")
        return []
    
    all_benchmarks = []
    years_to_scrape = [2025, 2024, 2023, 2022, 2021]

    try:
        for school in schools_to_scrape:
            print(f"Đang xử lý trường: {school['name']}")
            try:
                driver.get(school['link'])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.university__header-info"))
                )
                time.sleep(2)
                
                # Lấy MÃ TRƯỜNG
                soup_header = BeautifulSoup(driver.page_source, "html.parser")
                code_tag = soup_header.select_one("span.university__header-code")
                if code_tag:
                    code_text = code_tag.find(text=True, recursive=False).strip()
                    school_code = re.sub(r"Mã trường:\s*", "", code_text).strip()
                else:
                    school_code = "N/A"
                    print(f"  - Không tìm thấy mã trường cho {school['name']}. Dùng 'N/A'.")

                for year in years_to_scrape:
                    try:
                        print(f"  - Lấy dữ liệu năm {year}...")
                        get_year_button(driver, year)
                        
                        while True:
                            soup = BeautifulSoup(driver.page_source, "html.parser")
                            new_benchmarks = scrape_benchmarks_table(soup, school['name'], school_code, year)
                            
                            # Kiểm tra xem có dữ liệu mới được thêm vào không
                            if not new_benchmarks:
                                break
                            
                            current_count = len(all_benchmarks)
                            newly_added = [bm for bm in new_benchmarks if bm not in all_benchmarks]

                            if not newly_added:
                                # Nếu không có dữ liệu mới, thoát vòng lặp
                                break

                            all_benchmarks.extend(newly_added)
                            print(f"    + Đã thêm {len(newly_added)} ngành. Tổng cộng: {len(all_benchmarks)}")
                            
                            try:
                                load_more_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_loadmore"))
                                )
                                # Dùng JavaScript click để chắc chắn hơn
                                driver.execute_script("arguments[0].click();", load_more_button)
                                time.sleep(3)
                            except (TimeoutException, NoSuchElementException):
                                # Không còn nút "Xem thêm", thoát vòng lặp
                                break
                    
                    except Exception as e:
                        print(f"  - Lỗi khi cào dữ liệu năm {year} của trường {school['name']}: {e}. Bỏ qua năm này.")
                        # Tiếp tục vòng lặp sang năm khác
                        continue
                
            except Exception as e:
                print(f"Lỗi khi xử lý trường {school['name']}: {e}. Lưu dữ liệu và tiếp tục.")
                save_to_csv(all_benchmarks)
                continue # Tiếp tục vòng lặp sang trường tiếp theo
    
    finally:
        # Lưu dữ liệu lần cuối trước khi thoát
        driver.quit()
        
    return all_benchmarks

# Chạy chương trình chính
all_benchmark_data = scrape_all_benchmarks()
save_to_csv(all_benchmark_data)
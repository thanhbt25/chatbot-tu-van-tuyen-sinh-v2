from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_all_school_links_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--ignore-ssl-errors=true")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://diemthi.vnexpress.net/tra-cuu-dai-hoc")

    schools = []

    def scrape_schools():
        soup = BeautifulSoup(driver.page_source, "html.parser")
        new_schools = []
        for a in soup.select("li.lookup__result .lookup__result-name a"):
            href = a["href"]
            name = a.find("strong").text.strip()
            link = "https://diemthi.vnexpress.net" + href
            new_schools.append({"name": name, "link": link})
        return new_schools

    try:
        schools = scrape_schools()
        print(f"Đã lấy {len(schools)} trường ban đầu.")

        while True:
            old_count = len(schools)

            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_loadmore"))
                )

                # Scroll tới nút
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(0.5)

                # Thử click nhiều lần nếu bị lỗi
                success = False
                for _ in range(3):  # thử tối đa 3 lần
                    try:
                        load_more_button.click()
                        success = True
                        break
                    except ElementNotInteractableException:
                        print("Nút chưa tương tác được, thử lại...")
                        time.sleep(2)

                if not success:
                    print("Click thất bại sau 3 lần thử. Kết thúc.")
                    break

                # Chờ số lượng trường tăng
                WebDriverWait(driver, 10).until(
                    lambda d: len(scrape_schools()) > old_count
                )

                schools = scrape_schools()
                print(f"Đã lấy thêm, tổng cộng: {len(schools)}")

            except TimeoutException:
                print("Không load thêm được trường mới nữa. Kết thúc.")
                break

    finally:
        driver.quit()

    return schools

def save_schools_to_txt(schools, filename="danh_sach_truong.txt"):
    """
    Hàm này lưu danh sách trường vào một file .txt.
    Mỗi dòng sẽ chứa Tên trường và Link, cách nhau bằng dấu phẩy.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for school in schools:
            f.write(f"{school['name']}, {school['link']}\n")
    print(f"Đã lưu danh sách trường vào file: {filename}")

# Chạy chương trình chính
all_schools = get_all_school_links_selenium()
print("\n--- Kết quả cuối cùng ---")
print(f"Tổng số trường đã lấy được: {len(all_schools)}")
# Lưu danh sách ra file nếu cần
save_schools_to_txt(all_schools)
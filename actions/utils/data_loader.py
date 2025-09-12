import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_CSV_PATH = os.path.join(BASE_DIR, '../../public/diem_chuan_dai_hoc.csv')
SCORE_2023_CSV_PATH = os.path.join(BASE_DIR, '../../public/diem_thi_thpt_2023_to_hop.csv')
SCORE_2024_CSV_PATH = os.path.join(BASE_DIR, '../../public/diem_thi_thpt_2025_to_hop.csv')
SCORE_2025_CSV_PATH = os.path.join(BASE_DIR, '../../public/diem_thi_thpt_2025_to_hop.csv')

try:
    benchmark_df = pd.read_csv(BENCHMARK_CSV_PATH)
    score_2023_df = pd.read_csv(SCORE_2023_CSV_PATH)
    score_2024_df = pd.read_csv(SCORE_2024_CSV_PATH)
    score_2025_df = pd.read_csv(SCORE_2025_CSV_PATH)
except FileNotFoundError as e:
    print(f"Lỗi: Không tìm thấy file CSV. Chi tiết: {e}")
    benchmark_df = pd.DataFrame()
    score_2023_df = pd.DataFrame()
    score_2024_df = pd.DataFrame()
    score_2025_df = pd.DataFrame()

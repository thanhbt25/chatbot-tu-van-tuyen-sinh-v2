import numpy as np
from actions.utils.data_loader import benchmark_df, score_2024_df, score_2025_df 

def predict_cutoff(school: str, major: str) -> float:
    """
    Dự đoán điểm chuẩn năm 2025 bằng hồi quy tuyến tính.
    Trả về số điểm float (hoặc None nếu không đủ dữ liệu).
    """
    print(benchmark_df.columns)
    record = benchmark_df[(benchmark_df["ten_truong"] == school) & (benchmark_df["ten_nganh"] == major)]
    if record.empty or record["nam"].nunique() < 2:
        return None

    X = record["nam"].values.reshape(-1, 1)
    y = record["diem_chuan"].values
    coef = np.polyfit(X.flatten(), y, 1)
    poly1d_fn = np.poly1d(coef)
    return float(poly1d_fn(2025))


def estimate_by_simulation(subject_combination: str, quota: int = 100) -> float:
    """
    Mô phỏng xét tuyển theo phân phối điểm thi 2025.
    Trả về cutoff (float).
    """
    column_name = f"diem_{subject_combination}"
    if column_name not in score_2025_df.columns:
        return None

    subset = score_2025_df[column_name].dropna().values
    if len(subset) == 0:
        return None

    sorted_scores = np.sort(subset)[::-1]
    cutoff = sorted_scores[min(quota - 1, len(sorted_scores) - 1)]
    return float(cutoff)


def estimate_by_normalization(subject_combination: str, school: str, major: str) -> float:
    """
    Điều chỉnh điểm chuẩn 2024 dựa trên chênh lệch trung bình điểm toàn quốc 2024 vs 2025.
    Trả về cutoff sau chuẩn hóa (float).
    """
    col_name = f"diem_{subject_combination}"
    if col_name not in score_2024_df.columns or col_name not in score_2025_df.columns:
        return None

    subset_2024 = score_2024_df[col_name].dropna().values
    subset_2025 = score_2025_df[col_name].dropna().values
    if len(subset_2024) == 0 or len(subset_2025) == 0:
        return None

    mean_2024, mean_2025 = np.mean(subset_2024), np.mean(subset_2025)
    record = benchmark_df[
        (benchmark_df["ten_truong"] == school) &
        (benchmark_df["ten_nganh"] == major) &
        (benchmark_df["nam"] == 2024)
    ]
    if record.empty:
        return None

    cutoff_2024 = record.iloc[0]["diem_chuan"]
    cutoff_adjusted = cutoff_2024 + (mean_2025 - mean_2024)
    return float(cutoff_adjusted)

def estimate_cutoff_multi(school: str, major: str, subject_combination: str, quota: int = 200) -> float:
    """
    Ensemble: kết hợp nhiều chiến lược theo trọng số.
    """
    results = []
    weights = {}

    # baseline (2024)
    record_latest = benchmark_df[
        (benchmark_df["ten_truong"] == school) &
        (benchmark_df["ten_nganh"] == major) &
        (benchmark_df["nam"] == 2024)
    ]
    if not record_latest.empty:
        baseline = record_latest.iloc[0]["diem_chuan"]
        results.append(("baseline_2024", baseline))
        weights["baseline_2024"] = 0.2

    # regression
    reg_pred = predict_cutoff(school, major)
    if reg_pred:
        results.append(("regression", reg_pred))
        weights["regression"] = 0.2

    # simulation
    cutoff_sim = estimate_by_simulation(subject_combination, quota)
    if cutoff_sim:
        results.append(("simulation", cutoff_sim))
        weights["simulation"] = 0.3

    # normalization
    cutoff_norm = estimate_by_normalization(subject_combination, school, major)
    if cutoff_norm:
        results.append(("normalization", cutoff_norm))
        weights["normalization"] = 0.4

    if results:
        # Tính trung bình có trọng số
        total_weight = sum(weights.get(name, 0.25) for name, _ in results)
        avg_cutoff = sum(val * weights.get(name, 0.25) for name, val in results) / total_weight
        return avg_cutoff
    
    return None
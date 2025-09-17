from .data_loader import score_2025_df
import pandas as pd 

def compute_admission_probability(user_score: float, cutoff: float) -> float:
    """
    Ước lượng tỉ lệ đỗ dựa trên khoảng cách user_score - cutoff.

    Quy tắc:
    - >= cutoff + 1.0 → 100%
    - cutoff → 50%
    - <= cutoff - 1.0 → ~0%
    """
    margin = user_score - cutoff
    if user_score == 30.0:
        return 100.0
    if margin >= 1:
        return 100.0
    elif margin <= -2:
        return 0.0
    else:
        # tuyến tính từ 0 → 100 theo khoảng [-2, +1]
        return round((margin + 2) / 3 * 100, 2)
    
def score_percentage_rank(user_score: float, subject_combination: str) -> float: 
    """
    Return ra top % mà người dùng đang ở 
    Công thức: (số người > user_score) / tổng số người 
    Chú ý: xếp hạng theo tổ hợp 
    """
    name_score = 'diem_' + subject_combination
    print(score_2025_df.columns)

    # lấy cột điểm
    df_group = score_2025_df[[name_score]].copy()

    # ép kiểu toàn bộ sang float (bỏ giá trị không convert được)
    df_group[name_score] = pd.to_numeric(df_group[name_score], errors="coerce")
    df_group = df_group.dropna(subset=[name_score])

    # đảm bảo cột đúng kiểu float
    print(df_group[name_score].dtype)

    larger_score_students = (df_group[name_score] > float(user_score)).sum()
    total_students = len(df_group)

    print(f"larger score students are {larger_score_students} and total students are {total_students}")
    if total_students == 0: 
        return 0.0

    return round(larger_score_students / total_students, 5)



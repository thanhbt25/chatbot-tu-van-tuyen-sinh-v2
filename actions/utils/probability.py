from .data_loader import score_2025_df

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
    df_group = score_2025_df[score_2025_df[name_score].notna()]

    larger_score_students = (df_group[name_score] > user_score).sum()
    total_students = len(df_group)

    if total_students == 0: 
        return 0.0

    return round(larger_score_students / total_students, 2)


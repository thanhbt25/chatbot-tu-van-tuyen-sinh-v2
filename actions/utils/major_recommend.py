import pandas as pd
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAJORS_AGGREGATED_PATH = os.path.join(BASE_DIR, '../../public/majors_aggregated.csv')

# =====================
# Các tham số weight
# =====================
W_SCORE = 0.2
W_SUBJECT = 0.5
W_FINANCE = 0.2
W_COMBINATION = 0.1  # thêm trọng số tổ hợp môn

# =====================
# Hàm chuẩn hóa môn khtn / khxh
# =====================
def expand_subjects(subjects):
    expanded = []
    for subj in subjects:
        if subj == "khtn":  # Toán + Lý + Hóa
            expanded.extend(["toan", "vat_li", "hoa_hoc"])
        elif subj == "khxh":  # Văn + Sử + Địa
            expanded.extend(["ngu_van", "lich_su", "dia_li"])
        else:
            expanded.append(subj)
    return expanded

# =====================
# Tính độ phù hợp cluster
# =====================
def calculate_fit(user, major_row):
    # Score fit
    score_fit = 1 / (1 + abs(user.get("score", 0) - major_row["avg_score"]))

    needed_subjects = json.loads(major_row["needed_subjects"])
    liked = expand_subjects(user.get("liked_subject", []))
    disliked = expand_subjects(user.get("disliked_subject", []))

    # Subject fit: tính tỉ lệ môn thích trùng
    total_needed = sum(needed_subjects.values())
    like_match = sum(needed_subjects.get(subj, 0) for subj in liked)
    subject_fit = like_match / max(1, total_needed)

    # Trừ điểm nếu có môn bị ghét
    dislike_penalty = 0
    for subj in disliked:
        if subj in needed_subjects and needed_subjects[subj] > 0:
            dislike_penalty += needed_subjects[subj] / max(1, total_needed)
    subject_fit = max(0, subject_fit - dislike_penalty)

    # Finance fit
    finance_req = user.get("finance_requirement")
    if finance_req is None:
        finance_fit = 1.0
    elif finance_req >= major_row["avg_fee"]:
        finance_fit = 1.0
    else:
        diff = abs(finance_req - major_row["avg_fee"]) / 5_000_000
        finance_fit = max(0, 1 - diff)

    # Combination fit (nếu người dùng có chọn tổ hợp môn)
    comb_fit = 1.0
    user_combs = user.get("subject_combination", [])
    if user_combs:
        major_combs = json.loads(major_row["common_combinations"]).keys()
        match_count = sum(1 for c in user_combs if c in major_combs)
        comb_fit = match_count / max(1, len(user_combs))

    total_score = (
        W_SCORE * score_fit +
        W_SUBJECT * subject_fit +
        W_FINANCE * finance_fit +
        W_COMBINATION * comb_fit
    )
    return total_score

# =====================
# Recommend clusters
# =====================
def recommend_clusters(user, top_n=2):
    df = pd.read_csv(MAJORS_AGGREGATED_PATH)
    results = []
    for _, row in df.iterrows():
        fit = calculate_fit(user, row)
        results.append({
            "cluster_id": row["cluster_id"],
            "representative_major": row["representative_major"],
            "sample_majors": json.loads(row["sample_majors"]),
            "avg_score": row["avg_score"],
            "avg_fee": row["avg_fee"],
            "major_category": json.loads(row["major_categories"]),
            "fit_score": round(fit, 4)
        })

    # Sắp xếp giảm dần
    results = sorted(results, key=lambda x: x["fit_score"], reverse=True)
    return results[:top_n]

# =====================
# Demo
# =====================
if __name__ == "__main__":
    user_input = {
        "score": 29.0,
        "liked_subject": ["toan", "tieng_anh"],
        "disliked_subject": ["ngu_van", "khxh"],  # sẽ giảm điểm thay vì 0
        "finance_requirement": 30000000.0,
        "subject_combination": ["A01", "D01"]
    }

    clusters = recommend_clusters(user_input, top_n=2)
    for c in clusters:
        print(f"Cluster: {c['representative_major']} ({c['fit_score']})")
        print(f"Ngành lớn: {', '.join(c['major_category'].keys())}")
        print(f"Ngành chi tiết: {', '.join(c['sample_majors'])}")
        print("---")

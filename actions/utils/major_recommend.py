import pandas as pd
import os 
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAJORS_AGGREGATED_PATH = os.path.join(BASE_DIR, '../../public/majors_aggregated.csv')

# =====================
# Các tham số weight
# =====================
W_SCORE = 0.2
W_SUBJECT = 0.6
W_FINANCE = 0.2

LIKE_WEIGHT = 1.0
DISLIKE_WEIGHT = -1.0

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
# Hàm tính độ phù hợp
# =====================
def calculate_fit(user, major_row):
    # --- Score fit ---
    score_fit = 1 / (1 + abs(user["score"] - major_row["avg_score"]))  # càng gần càng tốt

    # --- Subject fit ---
    needed_subjects = json.loads(major_row["needed_subjects"])
    liked = expand_subjects(user.get("liked_subject", []))
    disliked = expand_subjects(user.get("disliked_subject", []))

    subject_score = 0.0
    for subj in liked:
        if subj in needed_subjects:
            subject_score += LIKE_WEIGHT * needed_subjects[subj]
    for subj in disliked:
        if subj in needed_subjects:
            subject_score += DISLIKE_WEIGHT * needed_subjects[subj]

    # Chuẩn hóa về [0,1]
    subject_fit = (subject_score - (-1000)) / (1000 - (-1000))
    subject_fit = max(0, min(1, subject_fit))

    # --- Finance fit ---
    if user["finance_requirement"] >= major_row["avg_fee"]:
        finance_fit = 1.0
    else:
        diff = abs(user["finance_requirement"] - major_row["avg_fee"]) / 5_000_000
        finance_fit = max(0, 1 - diff)

    # --- Tổng hợp ---
    total_score = (
        W_SCORE * score_fit + W_SUBJECT * subject_fit + W_FINANCE * finance_fit
    )
    return total_score


# =====================
# Hàm recommend
# =====================
def recommend(user, top_n=5):
    df = pd.read_csv(MAJORS_AGGREGATED_PATH)

    results = []
    for _, row in df.iterrows():
        fit = calculate_fit(user, row)
        results.append({
            "major": row["major"],
            "score": round(fit, 4),
            "avg_score": row["avg_score"],
            "avg_fee": row["avg_fee"]
        })

    # Sắp xếp giảm dần theo score
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# =====================
# Demo
# =====================
if __name__ == "__main__":
    # Input user giả định
    user_input = {
        "score": 29.0,
        "liked_subject": ["toan", "tieng_anh"],
        "disliked_subject": ["ngu_van", "khxh"],  # sẽ expand ra văn + sử + địa
        "finance_requirement": 30000000.0
    }

    majors = recommend(user_input, top_n=5)
    print("Top ngành phù hợp:")
    for m in majors:
        print(m)

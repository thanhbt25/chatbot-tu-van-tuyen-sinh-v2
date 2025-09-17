# Sử dụng trên Google Colab 
import pandas as pd
import os
import json
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np 

BASE_DIR = "/content/drive/MyDrive"

INPUT_PATH = os.path.join(BASE_DIR, "diem_chuan_dai_hoc.csv")
TOHOPMON_PATH = os.path.join(BASE_DIR, "tohopmon.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "majors_aggregated.csv")

# ===== Đọc dữ liệu =====
benchmark_df = pd.read_csv(INPUT_PATH)
tohopmon_df = pd.read_csv(TOHOPMON_PATH)

# Tạo dict map {ma_to_hop: [mon1, mon2, mon3]}
tohop_map = {}
for _, row in tohopmon_df.iterrows():
    subjects = [str(row["mon1"]), str(row["mon2"]), str(row["mon3"])]
    subjects = [m for m in subjects if m != "nan"]  # bỏ missing
    tohop_map[row["ma_to_hop"]] = subjects

# ===== Làm sạch dữ liệu điểm chuẩn =====
benchmark_df["hoc_phi"] = (
    benchmark_df["hoc_phi"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.extract(r"(\d+)")
    .astype(float)
)

benchmark_df["diem_chuan"] = pd.to_numeric(benchmark_df["diem_chuan"], errors="coerce")

# ===== Sinh embedding cho tên ngành =====
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
majors_texts = benchmark_df["ten_nganh"].fillna("").tolist()
embeddings = model.encode(majors_texts, convert_to_numpy=True, show_progress_bar=True, batch_size=64)
# ===== Clustering bằng KMeans =====
n_clusters = max(2, len(benchmark_df) // 50)  # heuristic: 1 cluster ~10 ngành
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
benchmark_df["cluster"] = kmeans.fit_predict(embeddings)

# ===== Gom nhóm theo cluster =====
aggregated = []
for cluster_id, group in benchmark_df.groupby("cluster"):
    majors = group["ten_nganh"].tolist()
    # centroid embedding
    centroid = kmeans.cluster_centers_[cluster_id]
    # chọn major gần nhất với centroid
    cluster_embeddings = embeddings[group.index]
    idx = np.argmin(np.linalg.norm(cluster_embeddings - centroid, axis=1))
    rep_major = group.iloc[idx]["ten_nganh"]

    avg_score = group["diem_chuan"].mean()
    avg_fee = group["hoc_phi"].mean()

    # gom tất cả tổ hợp môn và đếm frequency môn học
    subjects_freq = {}
    for combos in group["to_hop_mon"].dropna():
        for code in str(combos).split(","):
            code = code.strip()
            if code in tohop_map:
                for subj in tohop_map[code]:
                    subjects_freq[subj] = subjects_freq.get(subj, 0) + 1

    aggregated.append({
        "major": rep_major,
        "avg_score": round(avg_score, 2) if pd.notna(avg_score) else None,
        "avg_fee": round(avg_fee, 0) if pd.notna(avg_fee) else None,
        "needed_subjects": json.dumps(subjects_freq, ensure_ascii=False)
    })

result_df = pd.DataFrame(aggregated)

# ===== Xuất ra file =====
result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ Đã lưu file ngành đã gom nhóm: {OUTPUT_PATH}")

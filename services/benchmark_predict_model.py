import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import joblib

# ---------- 0. Config file paths ----------
from actions.utils.data_loader import (
    BENCHMARK_CSV_PATH,
    SCORE_2023_CSV_PATH,
    SCORE_2024_CSV_PATH,
    SCORE_2025_CSV_PATH,
)

students_paths = {
    2023: SCORE_2023_CSV_PATH,
    2024: SCORE_2024_CSV_PATH,
    2025: SCORE_2025_CSV_PATH,
}

# ---------- 1. Load cutoffs ----------
cutoffs = pd.read_csv(BENCHMARK_CSV_PATH).rename(
    columns={
        "ten_truong": "school_name",
        "ma_truong": "school_code",
        "nam": "year",
        "ten_nganh": "major_name",
        "ma_nganh": "major_code",
        "diem_chuan": "cutoff",
        "to_hop_mon": "subject_groups",
    }
)
cutoffs["year"] = cutoffs["year"].astype(int)

# ---------- 2. Tính thống kê từ điểm thi ----------
sg_stats_list = []
for year, path in students_paths.items():
    print(f"Processing students file for year {year}")
    s = pd.read_csv(path)
    s["year"] = year

    diem_cols = [c for c in s.columns if c.startswith("diem_")]
    for col in diem_cols:
        arr = s[col].dropna().values
        if len(arr) == 0:
            continue
        sg_stats_list.append(
            {
                "year": year,
                "subject_group": col.replace("diem_", ""),
                "n_students": int(len(arr)),
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr, ddof=0)),
                "p75": float(np.percentile(arr, 75)),
                "p90": float(np.percentile(arr, 90)),
                "p10": float(np.percentile(arr, 10)),
            }
        )

sg_stats = pd.DataFrame(sg_stats_list)
print("Sample stats:", sg_stats.head(5))

# ---------- 3. Parse subject groups ----------
def parse_subject_groups(s):
    if pd.isna(s):
        return []
    parts = [x.strip() for x in str(s).replace("，", ",").split(",") if x.strip() != ""]
    return parts

cutoffs["sg_list"] = cutoffs["subject_groups"].apply(parse_subject_groups)

# ---------- 4. Map cutoff rows -> sg_stats ----------
feature_rows = []
for idx, row in cutoffs.iterrows():
    year, sgs = row["year"], row["sg_list"]
    feat = {
        "idx": idx,
        "school_code": row.get("school_code"),
        "major_code": row.get("major_code"),
        "year": year,
        "cutoff": row.get("cutoff", np.nan),
    }

    if len(sgs) == 0:
        feat.update({k: np.nan for k in [
            "n_students_sg_mean", "mean_sg_mean", "median_sg_mean",
            "std_sg_mean", "p75_sg_mean", "p90_sg_mean", "p10_sg_mean"
        ]})
        feat["n_sg_count"] = 0
    else:
        matched = sg_stats[(sg_stats["year"] == year) & (sg_stats["subject_group"].isin(sgs))]
        if matched.empty:
            matched = sg_stats[sg_stats["subject_group"].isin(sgs)]

        feat.update({
            "n_students_sg_mean": matched["n_students"].mean() if not matched.empty else np.nan,
            "mean_sg_mean": matched["mean"].mean() if not matched.empty else np.nan,
            "median_sg_mean": matched["median"].mean() if not matched.empty else np.nan,
            "std_sg_mean": matched["std"].mean() if not matched.empty else np.nan,
            "p75_sg_mean": matched["p75"].mean() if not matched.empty else np.nan,
            "p90_sg_mean": matched["p90"].mean() if not matched.empty else np.nan,
            "p10_sg_mean": matched["p10"].mean() if not matched.empty else np.nan,
            "n_sg_count": matched.shape[0],
        })
    feature_rows.append(feat)

features_df = pd.DataFrame(feature_rows).set_index("idx")
data = pd.concat([cutoffs, features_df], axis=1)

# ---------- 5. Lag feature ----------
prev = cutoffs.rename(
    columns={"cutoff": "cutoff_prev_year", "year": "year", "school_code": "school_code", "major_code": "major_code"}
).copy()
prev["year"] = prev["year"] + 1
data = data.merge(
    prev[["school_code", "major_code", "year", "cutoff_prev_year"]],
    on=["school_code", "major_code", "year"],
    how="left",
)
data["cutoff_prev_year"] = data["cutoff_prev_year"].fillna(data["cutoff"].median())

# ---------- 6. Feature engineering ----------
data["year_diff_from_base"] = data["year"] - data["year"].min()
data["n_subject_groups"] = data["sg_list"].apply(len)

feature_cols = [
    "n_students_sg_mean", "mean_sg_mean", "median_sg_mean", "std_sg_mean",
    "p75_sg_mean", "p90_sg_mean", "p10_sg_mean",
    "cutoff_prev_year", "year_diff_from_base", "n_subject_groups",
    "school_code", "major_code"
]

data["school_code"] = data["school_code"].astype("category")
data["major_code"] = data["major_code"].astype("category")

train_df = data.dropna(subset=["cutoff"]).copy()
train_df["year"] = train_df["year"].astype(int)

# ---------- 7. Train/test split ----------
X_train = train_df[train_df["year"] <= 2024][feature_cols]
y_train = train_df[train_df["year"] <= 2024]["cutoff"]

X_test = train_df[train_df["year"] == 2025][feature_cols]
y_test = train_df[train_df["year"] == 2025]["cutoff"]

if X_test.empty:  # fallback nếu không có dữ liệu 2025
    X_train, X_test, y_train, y_test = train_test_split(
        train_df[feature_cols], train_df["cutoff"], test_size=0.2, random_state=42
    )

# ---------- 8. LightGBM ----------
categorical_feats = ["school_code", "major_code"]
lgb_train = lgb.Dataset(X_train, label=y_train, categorical_feature=categorical_feats, free_raw_data=False)
lgb_val = lgb.Dataset(X_test, label=y_test, categorical_feature=categorical_feats, reference=lgb_train, free_raw_data=False)

params = {
    "objective": "regression",
    "metric": "rmse",
    "boosting": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_data_in_leaf": 20,
    "seed": 42,
    "verbose": -1,
}

model = lgb.train(
    params,
    lgb_train,
    num_boost_round=2000,
    valid_sets=[lgb_train, lgb_val],
    valid_names=["train", "valid"],
    early_stopping_rounds=100,
    verbose_eval=100,
)

# ---------- 9. Evaluate ----------
y_pred = model.predict(X_test, num_iteration=model.best_iteration)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
print(f"Test RMSE: {rmse:.4f}, MAE: {mae:.4f}")

fi = pd.DataFrame({
    "feature": model.feature_name(),
    "importance": model.feature_importance()
}).sort_values("importance", ascending=False)
print(fi.head(20))

joblib.dump(model, "lgb_cutoff_model_by_sg_stats.joblib")

# ---------- 10. Predict missing ----------
to_pred = data[data["cutoff"].isna()].copy()
if not to_pred.empty:
    preds = model.predict(to_pred[feature_cols], num_iteration=model.best_iteration)
    to_pred["pred_cutoff"] = preds
    print(to_pred[["school_code", "major_code", "year", "pred_cutoff"]].head())
else:
    print("Không có hàng cần predict trong 'data' (cutoff đầy đủ).")

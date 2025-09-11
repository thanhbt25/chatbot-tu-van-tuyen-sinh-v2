from actions.utils.data_loader import benchmark_df

def check_subject_combination(school: str, major: str, subject_combination: str) -> bool:
    """
    Kiểm tra ngành có hỗ trợ tổ hợp môn này không.
    """
    records = benchmark_df[
        (benchmark_df["ten_truong"] == school) &
        (benchmark_df["ten_nganh"] == major)
    ]
    if records.empty:
        return False

    for combos in records["to_hop_mon"].dropna().values:
        combos_list = [c.strip().upper() for c in combos.split(",")]
        if subject_combination.upper() in combos_list:
            return True
    return False
def clean_file_before_comma(input_file: str, output_file: str):
    results = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # lấy phần trước dấu phẩy
            if "," in line:
                part = line.split(",")[0]
            else:
                part = line

            results.append('- ' + part.lower())

    # ghi ra file mới
    with open(output_file, "w", encoding="utf-8") as f:
        for item in results:
            f.write(item + "\n")


if __name__ == "__main__":
    input_file = "../../public/danh_sach_truong.txt"
    output_file ="schoool_clean.txt"
    clean_file_before_comma(input_file, output_file)

import re 

def extract_number(text: str) -> float | None:
    """
    Lấy số (float) đầu tiên tìm thấy trong chuỗi.
    Nếu không có số nào thì trả về None.
    """
    match = re.search(r"\d+(\.\d+)?", text)
    if match:
        return float(match.group())
    return None
import pandas as pd
import os
import unidecode
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rapidfuzz import process, fuzz
from services.gemini_response import paraphrase_response

# Đọc file với đường dẫn tuyệt đối
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../public/diem_chuan_dai_hoc.csv')
# Sử dụng try-except để xử lý lỗi nếu file không tồn tại
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file CSV tại đường dẫn {CSV_PATH}. Vui lòng kiểm tra lại.")
    df = pd.DataFrame() # Tạo DataFrame rỗng để tránh lỗi

def normalize(text: str) -> str:
    """Chuẩn hoá chuỗi để so khớp, loại bỏ dấu và các từ khóa không cần thiết."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = unidecode.unidecode(text)  # loại bỏ dấu tiếng việt
    text = text.replace("truong", "").replace("dai hoc", "").replace("dh", "").replace("dại học", "") # loại bỏ các từ không cần thiết 
    return text.strip() # loại bỏ khoảng trắng ở đầu hoặc cuối chuỗi 

def get_major(school: str) -> List[str]:
    """Lấy danh sách các ngành học của một trường."""
    if df.empty:
        return []
    filtered_df = df[df['ten_truong'] == school]
    print(f"Debug Info - Filtered DataFrame for school '{school}':\n{filtered_df}")
    if not filtered_df.empty:
        return filtered_df['ten_nganh'].unique().tolist(), filtered_df['ma_nganh'].unique().tolist()
    return []

def find_best_match(user_input: str, threshold: int = 70) -> str:
    """Tìm trường phù hợp nhất với input của người dùng."""
    if df.empty or not user_input:
        return None
    
    schools = df['ten_truong'].unique()
    normalized_schools = {s: normalize(s) for s in schools}
    
    best_match = process.extractOne(
        normalize(user_input),
        normalized_schools,
        scorer=fuzz.token_set_ratio
    ) # Trả về (match, score, index)
    # hàm thực hiện 3 việc: tìm kiếm (lấy 1 chuỗi đầu vào - param 1), so khớp (so sánh chuỗi đó với từng chuỗi trong danh sách (param 2), trả về (chỉ trả về một kết quả phù hợp nhất ))
    print(f"Debug Info - Best match details: {best_match}")
    if best_match and best_match[1] >= threshold:
        return best_match[2]
        
    return None

def find_top_matches(user_input: str, limit: int = 3, threshold: int = 50) -> List[str]:
    """Trả về top N trường giống nhất với một ngưỡng nhất định."""
    if df.empty or not user_input:
        return []
        
    schools = df['ten_truong'].unique()
    normalized_schools = {s: normalize(s) for s in schools}
    
    matches = process.extract(
        normalize(user_input),
        normalized_schools,
        scorer=fuzz.token_set_ratio,
        limit=limit
    ) # tương tự phần trên nhưng mà lấy nhiều kết quả ( = limit )
    
    # Lọc các kết quả có điểm số dưới ngưỡng
    return [m[0] for m in matches if m[1] >= threshold]

def output_results(school: str) -> str:
    """Tạo chuỗi phản hồi đã định dạng với danh sách các ngành và mã ngành của một trường."""
    majors, major_codes = get_major(school)

    if majors and major_codes:
        # Ghép mã ngành với tên ngành
        major_list_str = "\n".join([f"- {code}: {name}" for code, name in zip(major_codes, majors)])
        return f"Các ngành của {school} là:\n{major_list_str}"
    else:
        return f"Không tìm thấy ngành học cho trường {school}."

class ActionMajor(Action):
    def name(self) -> Text:
        return "action_find_major"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        school = tracker.get_slot("school")
        
        print(f"Debug Info - School (user input): {school}")

        best_match_school = find_best_match(school)
        print(f"Debug Info - Best match school: {best_match_school}")

        if not best_match_school:
            suggestions = find_top_matches(school)
            
            if suggestions:
                suggestion_text = "\n".join([f"- {s}" for s in suggestions])
                dispatcher.utter_message(
                    text=f"Xin lỗi, mình không tìm thấy trường chính xác cho '{school}'. Có phải ý bạn là một trong các trường sau không?\n{suggestion_text}"
                )
            else:
                dispatcher.utter_message(
                    text=f"Xin lỗi, mình không tìm thấy trường nào phù hợp với tên '{school}'. Vui lòng thử lại với một tên trường khác hoặc hỏi mình về một chủ đề khác nhé."
                )
            
            return []
        else:
            response = output_results(best_match_school)
            # user_messenge = tracker.latest_message.get("text")
            # improve_response = paraphrase_response(user_messenge, response)
            dispatcher.utter_message(text=response)

        return []
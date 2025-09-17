import pandas as pd
import os
import unidecode
import re 
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rapidfuzz import process, fuzz
from services.gemini_response import paraphrase_response

# Đọc file với đường dẫn tuyệt đối
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../public/diem_chuan_dai_hoc.csv')
BENCHMARK_PREDICTION_PATH = os.path.join(BASE_DIR, '../public/predictions_2026.csv')

# Sử dụng try-except để xử lý lỗi nếu file không tồn tại
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file CSV tại {CSV_PATH}")
    df = pd.DataFrame()

try:
    predicted_df = pd.read_csv(BENCHMARK_PREDICTION_PATH)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file CSV tại {BENCHMARK_PREDICTION_PATH}")
    predicted_df = pd.DataFrame()


def normalize(text: str) -> str:
    """Chuẩn hoá chuỗi để so khớp, loại bỏ dấu và các từ khóa không cần thiết."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = unidecode.unidecode(text)
    # Thêm các từ khóa tiếng Việt phổ biến để loại bỏ
    text = re.sub(r'\b(truong|trường|dai hoc|daihoc|dh|dại học|dai-hoc|dh)\b', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text) # giữ chữ latin và số, thay ký tự khác bằng space 
    return ' '.join(text.split()) # gom lại các khoảng trắng

def get_benchmark(school: str, major: str, year: int):
    """Lấy điểm chuẩn của một ngành tại một trường trong một năm cụ thể."""
    if df.empty or not school or not major or not year:
        return None
    filtered_df = df[(df['ten_truong'] == school) & 
                     (df['ten_nganh'] == major) & 
                     (df['nam'] == year)]
    if not filtered_df.empty:
        return filtered_df['diem_chuan'].values[0], filtered_df['to_hop_mon'].values[0], filtered_df['ghi_chu'].values[0]
    return None, None, None 

def get_predicted_benchmark(school: str, major: str, year: int = 2026):
    """
    Lấy dữ liệu điểm chuẩn dự đoán cho năm 2026
    """
    if predicted_df.empty or not school or not major:
        return None
    
    # Lọc để lấy mã trường và mã ngành
    school_major_code_filtered = df[
        (df['ten_truong'] == school) & (df['ten_nganh'] == major)
    ]
    
    if school_major_code_filtered.empty:
        return None  # Không tìm thấy ngành-trường này trong dữ liệu gốc
    
    school_code = school_major_code_filtered['ma_truong'].iloc[0]
    major_code  = school_major_code_filtered['ma_nganh'].iloc[0]

    # Lọc trên predicted_df
    filtered_df = predicted_df[
        (predicted_df['school_code'] == school_code) &
        (predicted_df['major_code'] == major_code)
    ]
    
    if not filtered_df.empty:
        return filtered_df['predicted_cutoff'].values[0]
    
    return None


def output_year(school: str, major: str, year: int) -> str:
    """Tạo chuỗi phản hồi cho một năm cụ thể."""
    if year == 2026:
        benchmark = get_predicted_benchmark(school, major, year)
        if benchmark is not None:
            return f"Năm {year}: Dự đoán điểm chuẩn khoảng {round(benchmark, 2)}.\n"
        else:
            return f"Năm {year}: Xin lỗi, hiện chưa có dữ liệu dự đoán.\n"

    # Với các năm 2025 trở xuống → lấy dữ liệu thật trong cơ sở dữ liệu
    benchmark, subject_combination, note = get_benchmark(school, major, year)
    if benchmark is not None:
        if note is None or pd.isna(note):
            return f"Năm {year}: Điểm chuẩn: {benchmark} với tổ hợp môn xét tuyển {subject_combination}\n"
        else:
            return f"Năm {year}: Điểm chuẩn: {benchmark} với tổ hợp môn xét tuyển {subject_combination}, điều kiện {note}\n"
    return f"Năm {year}: Không tìm thấy điểm chuẩn.\n"

def output_all_years(school: str, major: str) -> str:
    """Tạo chuỗi phản hồi cho tất cả các năm của một ngành."""
    if df.empty:
        return ""
    result = ""
    for year in sorted(df['nam'].unique()):
        result += output_year(school, major, year)
    return result

def find_best_school_match(user_input: str, threshold: int = 70) -> str:
    """Tìm trường phù hợp nhất với input của người dùng."""
    if df.empty or not user_input:
        return None
    
    schools = df['ten_truong'].unique().tolist()
    
    best_match = process.extractOne(
        normalize(user_input),
        schools,
        scorer=fuzz.token_set_ratio,
        processor=normalize,
        score_cutoff=threshold
    )

    print('Best school match:', best_match)  # Debug print
     # extractOne trả về (match, score, idx) hoặc None
    if best_match:
        return best_match[0] # Trả về tên gốc
    return None

def find_best_major_match(school: str, user_major_input: str, threshold: int = 70) -> str:
    """Tìm ngành phù hợp nhất với input của người dùng trong một trường cụ thể."""
    if df.empty or not school or not user_major_input:
        return None

    majors_in_school = df[df['ten_truong'] == school]['ten_nganh'].unique().tolist()
    
    best_match = process.extractOne(
        normalize(user_major_input),
        majors_in_school,
        scorer=fuzz.token_set_ratio,
        processor=normalize,
        score_cutoff=threshold
    )
    
    print("Best major match: ", best_match)
    if best_match:
        return best_match[0] # Trả về tên gốc
    return None

def find_top_schools(user_input: str, limit: int = 3, threshold: int = 50) -> List[str]:
    """Trả về top N trường giống nhất với một ngưỡng nhất định."""
    if df.empty or not user_input:
        return []
        
    schools = df['ten_truong'].unique().tolist()

    matches = process.extract(
        normalize(user_input),
        schools,
        scorer=fuzz.token_set_ratio,
        processor=normalize,
        limit=limit
    )
    
    return [m[0] for m in matches if m[1] >= threshold]

def find_top_majors(school: str, user_input: str, limit: int = 3, threshold: int = 50) -> List[str]:
    """Trả về top N ngành giống nhất trong một trường."""
    if df.empty or not school or not user_input:
        return []

    majors_in_school = df[df['ten_truong'] == school]['ten_nganh'].unique()
    
    matches = process.extract(
        normalize(user_input),
        majors_in_school,
        scorer=fuzz.token_set_ratio,
        processor=normalize,
        limit=limit
    )
    
    return [m[0] for m in matches if m[1] >= threshold]

class ActionBenchmark(Action):
    def name(self) -> Text:
        return "action_benchmark"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")
        year = tracker.get_slot("year")

        print(f"Debug Info - Slots: school={school}, major={major}, year={year}")
        response = ""
        
        best_school_match = find_best_school_match(school)

        if not best_school_match:
            suggestions = find_top_schools(school)
            if suggestions:
                suggestion_text = "\n".join([f"- {s}" for s in suggestions])
                dispatcher.utter_message(
                    text=f"Mình không tìm thấy trường chính xác cho '{school}'. Ý bạn là một trong các trường sau không?\n{suggestion_text}"
                )
            else:
                dispatcher.utter_message(
                    text=f"Mình không tìm thấy trường nào phù hợp với tên '{school}'. Vui lòng thử lại với tên trường khác."
                )
            return []

        best_major_match = find_best_major_match(best_school_match, major)

        if not best_major_match:
            suggestions = find_top_majors(best_school_match, major)
            if suggestions:
                suggestion_text = "\n".join([f"- {s}" for s in suggestions])
                dispatcher.utter_message(
                    text=f"Mình không tìm thấy ngành chính xác cho '{major}' trong {best_school_match}. Ý bạn là một trong các ngành sau không?\n{suggestion_text}"
                )
            else:
                dispatcher.utter_message(
                    text=f"Mình không tìm thấy ngành nào phù hợp với tên '{major}' trong {best_school_match}. Bạn có thể hỏi mình các ngành trong {school}. Cứ tự nhiên nhé!"
                )
            return []

        response = f"Điểm chuẩn của ngành {best_major_match} tại {best_school_match} như sau:\n"

        if year:
            response += output_year(best_school_match, best_major_match, int(year))
        else:
            response += output_all_years(best_school_match, best_major_match)

        # chỉ phần trả lời mới cải thiện cho tự nhiên hơn, nếu thiếu hoặc sai thông tin thì vẫn giữ code cứng như cũ 
        user_messenge = tracker.latest_message.get("text")
        improve_response = paraphrase_response(user_question=user_messenge, bot_answer=response)
        dispatcher.utter_message(text=improve_response)
        return []

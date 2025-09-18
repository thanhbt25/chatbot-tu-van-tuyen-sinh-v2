from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.probability import compute_admission_probability
from services.gemini_response import paraphrase_response
from actions.actions_benchmark import get_predicted_benchmark, find_best_major_match, find_best_school_match, get_benchmark


class ActionAdmissionProbability(Action):
    def name(self) -> Text:
        return "action_admission_probability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")
        score = tracker.get_slot("score")
        year = tracker.get_slot("year")

        print(f"school: {school}, major: {major}, score: {score}, year: {year}")
        response = ""

        # 1. Kiểm tra dữ liệu đầu vào
        if not school or not major or not score:
            dispatcher.utter_message(text="Vui lòng cung cấp đầy đủ trường, ngành và điểm.")
            return []

        try:
            score = float(score)
        except ValueError:
            dispatcher.utter_message(text="Điểm nhập không hợp lệ.")
            return []

        if year is None: 
            year = 2026
        else: 
            try:
                year = int(year)
            except ValueError:
                dispatcher.utter_message(text="Năm không hợp lệ.")
                return []
            
        if year == 2027:
            dispatcher.utter_message(text="Năm bạn tra đang nhiều hơn 2 năm so với hiện, hãy tính thời điểm thi gần nhất")
            return []

        # 2. Chuẩn hóa tên trường
        best_school_match = find_best_school_match(school)
        if not best_school_match: 
            dispatcher.utter_message(text="Xin lỗi, mình không thể tìm thấy trường này. Bạn hãy xem xét lại nhé!")
            return []

        # 3. Chuẩn hóa tên ngành (phải dùng best_school_match, không dùng school gốc)
        best_major_match = find_best_major_match(best_school_match, major)
        if not best_major_match:
            dispatcher.utter_message(
                text=f"Xin lỗi bạn, mình không tìm thấy ngành {major} của trường {best_school_match}. Bạn hãy xem xét lại nhé!"
            )
            return []   
        
        # 4. Lấy cutoff
        if year <= 2025: 
            cutoff = get_benchmark(school=best_school_match, major=best_major_match, year=year)
        else: 
            cutoff = get_predicted_benchmark(
                school=best_school_match, 
                major=best_major_match, 
                year=year
            )
        print("Cutoff dự đoán:", cutoff)

        # 5. Tính xác suất
        if cutoff:
            prob = compute_admission_probability(score, cutoff)
            if prob <= 0: 
                response = "Khả năng đỗ của bạn gần như bằng không. Mình nghĩ bạn nên chọn một ngành khác hoặc trường khác phù hợp với điểm của mình hơn."
            elif prob < 50:
                response = f"Xác suất đỗ ước tính của bạn xấp xỉ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn có khả năng đỗ nhưng vẫn chưa hoàn toàn chắc chắn. Hãy thử thêm lựa chọn khác nhé."
            elif prob < 95: 
                response = f"Xác suất đỗ ước tính của bạn xấp xỉ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn có khả năng đỗ rất cao, nhưng vẫn nên để thêm vài lựa chọn khác để an toàn."
            else: 
                response = f"Xác suất đỗ ước tính ≈ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn hoàn toàn chắc chắn đỗ trường này, chúc mừng bạn nhé!"
        else:
            response = "Không đủ dữ liệu để tính xác suất đỗ."

        # 6. Paraphrase để trả lời tự nhiên hơn (nếu API lỗi thì fallback response gốc)
        user_message = tracker.latest_message.get("text")
        try:
            improve_response = paraphrase_response(
                user_question=user_message, 
                bot_answer=response
            )
        except Exception as e:
            print(f"Lỗi paraphrase: {e}")
            improve_response = response

        dispatcher.utter_message(text=improve_response)
        return []

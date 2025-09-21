import pandas as pd 
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict
from actions.utils.data_loader import BENCHMARK_CSV_PATH

from services.gemini_response import paraphrase_response
from actions.actions_benchmark import find_best_major_match, find_best_school_match

class ActionGetTuitionFee(Action):
    def name(self) -> Text:
        return "action_get_tuition_fee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list[Dict[Text, Any]]:

        # Lấy entity từ tracker
        school= tracker.get_slot("school")
        major = tracker.get_slot("major")
        year = tracker.get_slot("year")

        print(f"debug: school: {school}, major: {major}, year: {year}")

        # Default year nếu không có
        if not year:
            year = "2025"

        response = ""

        best_school_match = find_best_school_match(school)
        if best_school_match is None: 
            dispatcher.utter_message(text="Xin lỗi tôi không tìm thấy trường phù hợp")
            return []

        best_major_match = find_best_major_match(best_school_match, major)
        if best_major_match is None:
            dispatcher.utter_message(text=f"Xin lỗi tôi không tìm thấy ngành phù hợp của trường {best_school_match}")
            return []

        try:
            df = pd.read_csv(BENCHMARK_CSV_PATH)

            # Lọc dữ liệu theo điều kiện
            result = df[
                (df["ten_truong"].str.contains(best_school_match, case=False, na=False)) &
                (df["ten_nganh"].str.contains(best_major_match, case=False, na=False)) &
                (df["nam"] == int(year))
            ]

            print(result)

            if not result.empty:
                hoc_phi = result.iloc[0]["hoc_phi"]
                print(hoc_phi)
                response = f"Học phí ngành {major} tại {school} năm {year} là: {hoc_phi} VND/năm."
            else:
                response = "Xin lỗi, mình không tìm thấy thông tin học phí cho ngành bạn hỏi."

        except Exception as e:
            response = f"Có lỗi xảy ra khi truy xuất dữ liệu: {e}. Hãy liên lạc với quản trị viên để sửa lỗi sớm nhất có thể nhé!"
        
        user_messenge = tracker.latest_message.get("text")
        improve_response = paraphrase_response(user_question=user_messenge, bot_answer=response)
        dispatcher.utter_message(text=improve_response)

        return []

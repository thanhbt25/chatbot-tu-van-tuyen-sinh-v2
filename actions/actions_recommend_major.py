from rasa_sdk import Action, Tracker 
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union

from actions.utils.major_recommend import recommend
from services.gemini_response import paraphrase_response


def parse_subjects(subject_input: Union[str, List[str], None]) -> List[str]:
    """
    Chuẩn hóa input môn học về dạng list[str].
    - "Toán, Lý, Hóa" -> ["Toán", "Lý", "Hóa"]
    - ["Toán", "Anh"] -> ["Toán", "Anh"]
    - None -> []
    """
    if not subject_input:
        return []
    if isinstance(subject_input, list):
        return [s.strip() for s in subject_input if s and s.strip()]
    if isinstance(subject_input, str):
        # Thay ; bằng , để tránh trường hợp phân cách khác nhau
        subjects = [s.strip() for s in subject_input.replace(";", ",").split(",")]
        return [s for s in subjects if s]
    return []


class ActionMajorRecommender(Action):
    def name(self) -> Text:
        return "action_major_recommender"
    
    def run(
        self, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # ===== Lấy slot từ người dùng =====
        score_raw = tracker.get_slot("score")
        liked_subject_raw = tracker.get_slot("liked_subject")
        disliked_subject_raw = tracker.get_slot("disliked_subject")
        finance_requirement_raw = tracker.get_slot("finance_requirement")

        # ===== Xử lý dữ liệu =====
        # Điểm (score) -> float hoặc None
        try:
            score = float(score_raw) if score_raw else None
        except ValueError:
            score = None

        try: 
            finance_requirement = float(finance_requirement_raw) if finance_requirement_raw else None
        except ValueError: 
            finance_requirement = None 

        # Môn học -> list[str]
        liked_subjects = parse_subjects(liked_subject_raw)
        disliked_subjects = parse_subjects(disliked_subject_raw)

        # Gom lại input cho recommend
        user_input = {
            "score": score, 
            "liked_subjects": liked_subjects,
            "disliked_subjects": disliked_subjects,
            "finance_requirement": finance_requirement
        }

        # ===== Gọi recommend & paraphrase =====
        user_message = tracker.latest_message.get("text") 
        response = recommend(user_input, top_n=5)
        improve_response = paraphrase_response(user_message, response)

        # ===== Trả kết quả cho user =====
        dispatcher.utter_message(text=improve_response)
        return []

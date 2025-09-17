from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.prediction import estimate_cutoff_multi
from actions.utils.probability import compute_admission_probability
from services.gemini_response import paraphrase_response

class ActionAdmissionProbability(Action):
    def name(self) -> Text:
        return "action_admission_probability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        school = tracker.get_slot("school")
        major = tracker.get_slot("major")
        score = tracker.get_slot("score")
        subject_combination = tracker.get_slot("subject_combination") or "A00"
        quota = tracker.get_slot("quota") or 100

        response = ""

        if not school or not major or not score:
            response = "Vui lòng cung cấp đầy đủ trường, ngành và điểm."
            return []

        try:
            score = float(score)
        except ValueError:
            response = "Điểm nhập không hợp lệ."
            return []

        if quota == None: 
            cutoff = estimate_cutoff_multi(school, major, subject_combination)
        else: 
            cutoff = estimate_cutoff_multi(school, major, subject_combination, quota)

        if cutoff:
            prob = compute_admission_probability(score, cutoff)
            if prob <= 0: 
                response = "Khả năng đỗ của bạn gần như bằng không. Mình nghĩ bạn nên chọn một ngành khác hoặc trường khác phù hợp với điểm của mình hơn. Bạn có thể hỏi mình thêm về vấn đề này nhé."
            elif prob < 50:
                response = f"Xác suất đỗ ước tính của bạn xấp xỉ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn có khả năng đỗ nhưng vẫn chưa hoàn toàn chắc chắn. Hãy thử thêm lựa chọn khác nhé."
            elif prob < 95: 
                response = f"Xác suất đỗ ước tính của bạn xấp xỉ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn có khẳ năng đỗ rất cao, nếu có thể thì hãy cứ thêm một số lựa chọn khác đề phòng nhé."
            else: 
                response = f"Xác suất đỗ ước tính ≈ {prob}% (cutoff ≈ {round(cutoff,2)}). Bạn hoàn toàn chắc chắn đỗ trường này, chúc mừng bạn nhé!"
        else:
            response = "Không đủ dữ liệu để tính xác suất đỗ."

        user_messenge = tracker.latest_message.get("text")
        improve_response = paraphrase_response(user_question=user_messenge, bot_answer=response)
        dispatcher.utter_message(text=improve_response)
        return []

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from actions.utils.prediction import estimate_cutoff_multi
from actions.utils.probability import compute_admission_probability

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

        if not school or not major or not score:
            dispatcher.utter_message(text="Vui lòng cung cấp đầy đủ trường, ngành và điểm.")
            return []

        try:
            score = float(score)
        except ValueError:
            dispatcher.utter_message(text="Điểm nhập không hợp lệ.")
            return []

        cutoff = estimate_cutoff_multi(score, school, major, subject_combination, int(quota), return_avg_only=True)

        if cutoff:
            prob = compute_admission_probability(score, cutoff)
            dispatcher.utter_message(text=f"Xác suất đỗ ước tính ≈ {prob}% (cutoff ≈ {round(cutoff,2)})")
        else:
            dispatcher.utter_message(text="Không đủ dữ liệu để tính xác suất đỗ.")

        return []
